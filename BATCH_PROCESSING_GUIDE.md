# 修改為純批次處理模式的指南

## 📋 當前狀態確認

✅ **PropulseIQ 已經是批次處理架構**
- 所有用戶請求的 API 端點都只查詢資料庫
- 沒有任何 API 會即時調用 AI
- AI 分析完全由 Celery 背景任務處理

## 🔧 建議的優化修改

### 方案 A：更頻繁的批次處理（推薦）

如果您希望新聞更快被分析，但仍保持批次處理，可以：

#### 1. 修改 Celery 排程頻率

將 `backend/app/tasks/celery_app.py` 的第 35 行改為：

```python
# 原本：每小時執行一次
"schedule": crontab(minute=0),  # 每小時整點執行

# 改為：每 15 分鐘執行一次
"schedule": crontab(minute="*/15"),  # 每 15 分鐘執行

# 或：每 5 分鐘執行一次（更積極）
"schedule": crontab(minute="*/5"),  # 每 5 分鐘執行
```

#### 2. 增加批次處理數量

在 `.env` 檔案中：

```bash
# 原本：每次處理 5 篇
AI_BATCH_SIZE=5

# 改為：每次處理 20 篇（根據 API 配額調整）
AI_BATCH_SIZE=20
```

### 方案 B：移除手動觸發功能（確保純批次）

#### 1. 移除手動觸發任務（可選）

編輯 `backend/app/tasks/analysis_tasks.py`，註解掉或刪除 `analyze_single_article` 函數：

```python
# 第 175 行開始的函數可以刪除或註解
# @celery_app.task(name="app.tasks.analysis_tasks.analyze_single_article")
# def analyze_single_article(article_id: int):
#     """手動觸發單篇分析"""
#     pass
```

#### 2. 確保沒有公開 API（已完成）

目前沒有以下類型的 API，保持這個狀態：

```python
# ❌ 不要加入這種 API
@router.post("/articles/{article_id}/analyze")  # 即時分析
@router.post("/admin/trigger-analysis")  # 手動觸發
```

### 方案 C：新增爬蟲整合點

如果您有新聞爬蟲系統，建議新增一個**僅供爬蟲使用**的內部 API：

#### 創建新檔案：`backend/app/api/crawler.py`

```python
"""
Crawler API
僅供內部爬蟲系統使用，不對外公開
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.article import Article
from app.schemas.article import ArticleCreate
from app.config import settings

router = APIRouter()

# 內部 API Key 驗證
def verify_crawler_key(x_crawler_key: str = Header(...)):
    if x_crawler_key != settings.CRAWLER_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True

@router.post("/ingest")
def ingest_article(
    article: ArticleCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_crawler_key)
):
    """
    爬蟲系統新增新聞（不會即時分析）
    分析將由 Celery 任務自動處理
    """
    # 檢查 URL 是否已存在
    existing = db.query(Article).filter(Article.url == article.url).first()
    if existing:
        return {"status": "duplicate", "article_id": existing.id}

    # 新增文章（不觸發分析）
    new_article = Article(
        title=article.title,
        source=article.source,
        url=article.url,
        published_at=article.published_at,
        category=article.category,
        raw_content=article.raw_content
    )

    db.add(new_article)
    db.commit()
    db.refresh(new_article)

    return {
        "status": "created",
        "article_id": new_article.id,
        "message": "文章已加入隊列，將於下次批次處理時分析"
    }
```

然後在 `backend/app/main.py` 註冊（不公開到文檔）：

```python
# 在 main.py 中加入
from app.api import crawler

app.include_router(
    crawler.router,
    prefix="/internal/crawler",
    tags=["Internal - Crawler"],
    include_in_schema=False  # 不顯示在 API 文檔中
)
```

在 `.env` 中加入：

```bash
CRAWLER_API_KEY=your-secure-crawler-api-key-here
```

### 方案 D：優化批次處理效能

#### 1. 並行處理多篇新聞

修改 `backend/app/services/ai_analyzer.py` 的 `batch_analyze` 方法，改用異步處理：

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def batch_analyze(self, articles: list) -> list:
    """
    批次分析多篇新聞（並行處理）
    """
    results = []

    # 使用線程池並行處理
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(self.analyze_sentiment, title, content)
            for article_id, title, content in articles
        ]

        for (article_id, title, content), future in zip(articles, futures):
            try:
                result = future.result(timeout=60)
                if result:
                    results.append({
                        'article_id': article_id,
                        'sentiment_score': result['sentiment_score'],
                        'confidence': result['confidence'],
                        'keywords': result['keywords'],
                        'analysis_reason': result['reason'],
                        'model_version': self.model
                    })
            except Exception as e:
                logger.error(f"Failed to analyze article {article_id}: {e}")
                continue

    return results
```

#### 2. 新增進度監控

在 `backend/app/tasks/analysis_tasks.py` 中加入進度追蹤：

```python
@celery_app.task(name="app.tasks.analysis_tasks.analyze_pending_articles", bind=True)
def analyze_pending_articles(self):
    """
    分析尚未處理的新聞文章
    支援進度追蹤
    """
    db = SessionLocal()

    try:
        # 查詢待處理文章數量
        total_pending = db.query(Article).outerjoin(
            SentimentScore, Article.id == SentimentScore.article_id
        ).filter(
            SentimentScore.id == None,
            Article.raw_content != None
        ).count()

        logger.info(f"Total pending articles: {total_pending}")

        # 更新任務狀態
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': total_pending}
        )

        # ... 處理邏輯 ...

    finally:
        db.close()
```

## 📊 推薦配置

### 適合大量新聞的配置

```bash
# .env
AI_BATCH_SIZE=20                    # 每次處理 20 篇
AI_BATCH_INTERVAL_MINUTES=5         # 每 5 分鐘執行
AI_DAILY_QUOTA=2000                 # 每日限額 2000 次
AI_MAX_RETRIES=3                    # 失敗重試 3 次
```

```python
# celery_app.py
"analyze-pending-articles": {
    "task": "app.tasks.analysis_tasks.analyze_pending_articles",
    "schedule": crontab(minute="*/5"),  # 每 5 分鐘
},
```

### 適合小量新聞的配置

```bash
# .env
AI_BATCH_SIZE=10                    # 每次處理 10 篇
AI_BATCH_INTERVAL_MINUTES=30        # 每 30 分鐘執行
AI_DAILY_QUOTA=500                  # 每日限額 500 次
```

```python
# celery_app.py
"analyze-pending-articles": {
    "task": "app.tasks.analysis_tasks.analyze_pending_articles",
    "schedule": crontab(minute="*/30"),  # 每 30 分鐘
},
```

## 🔍 驗證批次處理模式

### 1. 檢查沒有即時 API

確認 `backend/app/api/` 下沒有以下模式的端點：

```bash
grep -r "analyze.*now\|trigger.*analysis\|process.*immediate" backend/app/api/
# 應該沒有結果
```

### 2. 監控 Celery 任務

```bash
# 查看 Celery 日誌
docker-compose logs -f celery-worker

# 查看任務執行狀態
docker-compose exec celery-worker celery -A app.tasks.celery_app inspect active
```

### 3. 測試批次處理流程

```python
# 測試腳本：test_batch_processing.py
from app.database import SessionLocal
from app.models.article import Article
from datetime import datetime

db = SessionLocal()

# 1. 新增測試文章
article = Article(
    title="測試新聞：房市交易熱絡",
    source="測試來源",
    url=f"https://test.com/{datetime.now().timestamp()}",
    published_at=datetime.now(),
    raw_content="測試內容：房地產市場交易量大幅增加。"
)
db.add(article)
db.commit()

print(f"✅ 已新增測試文章 ID: {article.id}")
print("⏳ 等待 Celery 任務處理（根據排程時間）...")
print("📊 處理完成後可查詢 sentiment_scores 表確認")

db.close()
```

## ⚡ 效能優化建議

### 1. 資料庫索引優化

確保以下索引存在（已在 schema 中）：

```sql
-- 查詢未分析文章
CREATE INDEX idx_articles_analyzed ON articles(id)
WHERE NOT EXISTS (SELECT 1 FROM sentiment_scores WHERE article_id = articles.id);

-- 查詢待清理內容
CREATE INDEX idx_articles_cleanup ON articles(crawled_at)
WHERE raw_content IS NOT NULL;
```

### 2. Redis 快取查詢結果

在 `backend/app/api/sentiment.py` 中加入快取：

```python
import redis
import json

redis_client = redis.from_url(settings.REDIS_URL)

@router.get("/current", response_model=SentimentCurrentResponse)
def get_current_sentiment(db: Session = Depends(get_db)):
    # 檢查快取
    cache_key = "sentiment:current"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # 查詢資料庫
    result = # ... 原本的查詢邏輯 ...

    # 儲存快取（5 分鐘）
    redis_client.setex(cache_key, 300, json.dumps(result))

    return result
```

## 📝 總結

### 當前狀態
✅ **已經是純批次處理架構**
- 用戶請求不會觸發 AI 分析
- 所有分析由 Celery 自動處理

### 建議修改優先順序

1. **必要**：調整 Celery 排程頻率（方案 A）
2. **建議**：新增爬蟲整合 API（方案 C）
3. **可選**：移除手動觸發函數（方案 B）
4. **優化**：並行處理與快取（方案 D）

### 不需要修改的部分

- ✅ API 端點設計（已經正確）
- ✅ 資料庫架構（已經支援批次處理）
- ✅ 前端實作（只查詢資料庫）
- ✅ 認證系統（與處理模式無關）

---

**結論**：您的 PropulseIQ 系統已經是批次處理架構，只需要調整排程頻率和批次大小即可！
