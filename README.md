# 🏠 PropulseIQ - 房市脈動智析系統

**PropulseIQ** (Property Pulse + Intelligence Quotient) 是一個使用 AI 分析台灣房地產新聞情緒的 SaaS 平台。系統對已爬取的新聞進行情感分析，產生市場情緒指數（-1 到 +1），並提供視覺化儀表板與趨勢預測。

## 🎯 核心特色

- **AI 情感分析**：使用 Claude API 分析新聞情緒，提供量化的市場情緒指數
- **法律合規**：不對外提供完整新聞內容，僅顯示標題摘要與分析結果
- **多層級訂閱**：支援 Free、Pro、Business、Enterprise 四種訂閱方案
- **即時更新**：每小時自動分析新爬取的新聞
- **歷史趨勢**：提供 6-36 個月的歷史情緒趨勢分析

## 📊 技術架構

### 後端技術棧
- **框架**: FastAPI (Python 3.11+)
- **資料庫**: PostgreSQL 15+
- **快取**: Redis 7+
- **任務隊列**: Celery
- **AI 服務**: Anthropic Claude API
- **認證**: JWT Token
- **ORM**: SQLAlchemy

### 前端技術棧
- **框架**: React 18 + TypeScript
- **UI**: TailwindCSS
- **圖表**: Recharts
- **狀態管理**: Zustand
- **HTTP**: Axios

### 部署架構
- **容器化**: Docker + Docker Compose
- **開發環境**: 一鍵啟動所有服務

## 🚀 快速開始

### 前置需求

- Docker & Docker Compose
- Node.js 20+ (僅限本地開發)
- Python 3.11+ (僅限本地開發)
- Anthropic API Key

### 1. 克隆專案

```bash
git clone <repository-url>
cd Propulse
```

### 2. 環境變數設定

複製環境變數範本並填入您的 API Key：

```bash
cp .env.example .env
```

編輯 `.env` 檔案，至少需要設定：

```env
# 必填：Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-xxxxx

# 選填：資料庫密碼（建議修改）
POSTGRES_PASSWORD=your_secure_password

# 選填：JWT Secret Key（建議修改）
SECRET_KEY=your-secret-key-here
```

### 3. 啟動服務

使用 Docker Compose 一鍵啟動所有服務：

```bash
docker-compose up -d
```

首次啟動會需要幾分鐘來建置映像檔。

### 4. 初始化資料庫

建立資料庫結構：

```bash
docker-compose exec backend alembic upgrade head
```

### 5. 建立測試數據

執行種子腳本建立測試用戶和文章：

```bash
docker-compose exec backend python seed_data.py
```

這會建立：
- 3 個測試用戶（free、pro、business 訂閱等級）
- 100 篇測試新聞文章與情緒分析結果

測試帳號：
```
free@example.com / password123 (Free 方案)
pro@example.com / password123 (Pro 方案)
business@example.com / password123 (Business 方案)
```

### 6. 存取應用程式

- **前端**: http://localhost:5173
- **後端 API 文檔**: http://localhost:8000/api/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📁 專案結構

```
Propulse/
├── backend/                    # FastAPI 後端
│   ├── app/
│   │   ├── models/            # SQLAlchemy 資料模型
│   │   ├── schemas/           # Pydantic Schemas
│   │   ├── api/               # API 端點
│   │   ├── services/          # 業務邏輯服務
│   │   ├── tasks/             # Celery 背景任務
│   │   ├── utils/             # 工具函數
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 資料庫連接
│   │   └── main.py            # FastAPI 應用入口
│   ├── alembic/               # 資料庫遷移
│   ├── requirements.txt       # Python 依賴
│   ├── Dockerfile
│   └── seed_data.py           # 測試數據腳本
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── components/        # React 組件
│   │   ├── pages/             # 頁面組件
│   │   ├── services/          # API 客戶端
│   │   ├── store/             # Zustand 狀態管理
│   │   ├── types/             # TypeScript 類型
│   │   ├── styles/            # 全域樣式
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 🔧 開發指南

### 本地開發（不使用 Docker）

#### 後端開發

```bash
cd backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
export DATABASE_URL="postgresql://postgres:password@localhost:5432/propulseiq"
export REDIS_URL="redis://localhost:6379/0"
export ANTHROPIC_API_KEY="your-key"

# 執行資料庫遷移
alembic upgrade head

# 啟動開發伺服器
uvicorn app.main:app --reload --port 8000

# 啟動 Celery Worker（另一個終端）
celery -A app.tasks.celery_app worker --loglevel=info

# 啟動 Celery Beat（另一個終端）
celery -A app.tasks.celery_app beat --loglevel=info
```

#### 前端開發

```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev

# 建置生產版本
npm run build
```

### API 文檔

啟動後端後，可以訪問：

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### 資料庫遷移

建立新的遷移腳本：

```bash
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

執行遷移：

```bash
docker-compose exec backend alembic upgrade head
```

回滾遷移：

```bash
docker-compose exec backend alembic downgrade -1
```

## 🔐 認證與授權

系統使用 JWT Token 進行認證：

1. 使用 `/api/v1/auth/login` 端點登入
2. 取得 `access_token`
3. 在後續請求的 `Authorization` Header 中加入：`Bearer <token>`

Token 預設有效期為 30 分鐘。

## 📊 訂閱方案限制

| 功能 | Free | Pro | Business | Enterprise |
|------|------|-----|----------|------------|
| 當月情緒指數 | ✅ | ✅ | ✅ | ✅ |
| 最新 10 篇新聞 | ✅ | ✅ | ✅ | ✅ |
| 歷史數據 | - | 12 個月 | 36 個月 | 無限 |
| 月度報告 | - | ✅ | ✅ | ✅ |
| PDF 匯出 | - | ✅ | ✅ | ✅ |
| API 存取 | - | - | ✅ | ✅ |
| 每日請求限制 | 100 | 5,000 | 50,000 | 無限 |

## 🤖 AI 分析說明

### 情緒評分標準

- **-1.0 到 -0.5**: 極度悲觀（重大利空、市場崩盤）
- **-0.5 到 -0.2**: 悲觀（打房政策、買氣下滑）
- **-0.2 到 0.2**: 中性（數據報導、政策說明）
- **0.2 到 0.5**: 樂觀（交易回溫、利多消息）
- **0.5 到 1.0**: 極度樂觀（房價大漲、供不應求）

### Prompt 設計

系統使用精心設計的 Prompt 引導 Claude API 進行情感分析，包含：

- 明確的評分標準
- 新聞標題與內容
- 要求輸出 JSON 格式
- 包含信心度、關鍵字、分析原因

詳見：`backend/app/services/ai_analyzer.py`

## ⚖️ 法律合規

### 著作權保護措施

1. **不儲存完整內容**：
   - `raw_content` 欄位僅供內部分析使用
   - 分析後 30 天自動清空（可設定）

2. **對外僅提供摘要**：
   - 標題僅顯示前 20 字
   - 不透過 API 提供完整內容
   - 提供 Deep Link 回原網站

3. **版權聲明頁面**：
   - `/copyright` 路由提供完整聲明
   - 說明資料來源與合理使用
   - 提供 DMCA 侵權通知機制

## 🔄 背景任務

系統使用 Celery 執行以下定時任務：

- **每小時**：分析尚未處理的新聞（最多 5 篇/次）
- **每月 1 日凌晨 2 點**：生成上月報告
- **每天凌晨 3 點**：清理超過 30 天的原文內容

## 🧪 測試

### 執行單元測試

```bash
docker-compose exec backend pytest
```

### 手動測試 API

使用測試帳號登入後，可以測試各種 API 端點：

```bash
# 登入取得 Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=free@example.com&password=password123"

# 取得當前情緒
curl -X GET http://localhost:8000/api/v1/sentiment/current \
  -H "Authorization: Bearer <your-token>"

# 取得新聞列表
curl -X GET http://localhost:8000/api/v1/articles/ \
  -H "Authorization: Bearer <your-token>"
```

## 📝 環境變數說明

| 變數名稱 | 說明 | 預設值 |
|---------|------|--------|
| `DATABASE_URL` | PostgreSQL 連接字串 | - |
| `REDIS_URL` | Redis 連接字串 | - |
| `ANTHROPIC_API_KEY` | Claude API 金鑰 | - |
| `SECRET_KEY` | JWT 簽名密鑰 | - |
| `AI_BATCH_SIZE` | 每次分析的文章數量 | 5 |
| `AI_DAILY_QUOTA` | 每日 API 調用上限 | 1000 |
| `RAW_CONTENT_RETENTION_DAYS` | 原文保留天數 | 30 |

完整列表請參考 `.env.example`。

## 🐛 常見問題

### Q: 如何查看日誌？

```bash
# 查看所有服務日誌
docker-compose logs -f

# 查看特定服務日誌
docker-compose logs -f backend
docker-compose logs -f celery-worker
```

### Q: 如何重置資料庫？

```bash
docker-compose down -v  # 刪除 volumes
docker-compose up -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python seed_data.py
```

### Q: 前端無法連接後端？

檢查環境變數 `VITE_API_URL` 是否正確設定為 `http://localhost:8000`。

### Q: Celery 任務沒有執行？

確認 `celery-worker` 和 `celery-beat` 服務正常運行：

```bash
docker-compose ps
docker-compose logs celery-worker
```

## 🔒 安全性建議

### 生產環境部署

1. **修改預設密碼**：
   - 修改 PostgreSQL 密碼
   - 設定強密碼的 `SECRET_KEY`

2. **啟用 HTTPS**：
   - 使用 Nginx 或 Traefik 作為反向代理
   - 設定 SSL 憑證（Let's Encrypt）

3. **限制 CORS**：
   - 修改 `BACKEND_CORS_ORIGINS` 為實際域名

4. **環境變數管理**：
   - 不要提交 `.env` 到版本控制
   - 使用 Docker Secrets 或環境變數服務

5. **速率限制**：
   - 實作 API 速率限制（可使用 Redis）
   - 設定合理的 `API_RATE_LIMIT_*` 值

## 📚 延伸開發

### 待實作功能

- [ ] 地區別分析（北、中、南、東）
- [ ] 房型分析（套房、公寓、透天）
- [ ] 價格區間分析
- [ ] Email 週報訂閱
- [ ] 自訂警報（情緒指數達到閾值時通知）
- [ ] PDF 報告匯出
- [ ] CSV 數據匯出
- [ ] 圖表互動功能（縮放、篩選）
- [ ] 行動裝置 App

### 架構擴展

- 使用 Redis 實作 API 速率限制
- 加入 Prometheus + Grafana 監控
- 實作 WebSocket 即時更新
- 加入全文搜尋（Elasticsearch）
- 使用 CDN 加速前端資源

## 🤝 貢獻指南

歡迎提交 Issue 或 Pull Request！

## 📄 授權

本專案僅供學習與研究使用。

## 📧 聯絡方式

如有任何問題或建議，請透過 GitHub Issues 聯繫我們。

---

**PropulseIQ** - 讓數據驅動您的房地產投資決策 🚀
