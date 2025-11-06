"""
Articles API
新聞文章相關 API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.article import Article
from app.models.sentiment import SentimentScore
from app.schemas.article import ArticlePublicResponse, ArticleListResponse
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=ArticleListResponse)
def get_articles(
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(10, ge=1, le=100, description="每頁數量"),
    source: Optional[str] = Query(None, description="新聞來源篩選"),
    sentiment_type: Optional[str] = Query(None, description="情緒類型篩選：optimistic, pessimistic, neutral"),
    sort_by: str = Query("latest", description="排序方式：latest, most_optimistic, most_pessimistic"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    取得新聞列表（支援分頁、篩選、排序）

    Args:
        page: 頁碼
        page_size: 每頁數量
        source: 新聞來源篩選
        sentiment_type: 情緒類型篩選
        sort_by: 排序方式
        db: 資料庫 Session
        current_user: 當前使用者

    Returns:
        新聞列表
    """
    # 基礎查詢
    query = db.query(Article).join(SentimentScore, Article.id == SentimentScore.article_id, isouter=True)

    # 套用篩選
    if source:
        query = query.filter(Article.source == source)

    if sentiment_type:
        if sentiment_type == "optimistic":
            query = query.filter(SentimentScore.sentiment_score > 0.2)
        elif sentiment_type == "pessimistic":
            query = query.filter(SentimentScore.sentiment_score < -0.2)
        elif sentiment_type == "neutral":
            query = query.filter(
                SentimentScore.sentiment_score >= -0.2,
                SentimentScore.sentiment_score <= 0.2
            )

    # 套用排序
    if sort_by == "latest":
        query = query.order_by(desc(Article.published_at))
    elif sort_by == "most_optimistic":
        query = query.order_by(desc(SentimentScore.sentiment_score))
    elif sort_by == "most_pessimistic":
        query = query.order_by(SentimentScore.sentiment_score)

    # 計算總數
    total = query.count()

    # 分頁
    articles = query.offset((page - 1) * page_size).limit(page_size).all()

    # 轉換為公開格式（不包含 raw_content）
    items = []
    for article in articles:
        item = {
            "id": article.id,
            "title_short": article.title[:20] + "..." if len(article.title) > 20 else article.title,
            "source": article.source,
            "url": article.url,
            "published_at": article.published_at,
            "category": article.category,
            "sentiment_score": None,
            "sentiment_label": None,
            "sentiment_color": None,
            "keywords": None
        }

        # 加入情緒資料
        if article.sentiment_score:
            item["sentiment_score"] = article.sentiment_score.sentiment_score
            item["sentiment_label"] = article.sentiment_score.get_sentiment_label()
            item["sentiment_color"] = article.sentiment_score.get_sentiment_color()
            item["keywords"] = article.sentiment_score.keywords

        items.append(item)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/{article_id}", response_model=ArticlePublicResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    取得單篇新聞詳情（不含完整原文）

    Args:
        article_id: 新聞 ID
        db: 資料庫 Session
        current_user: 當前使用者

    Returns:
        新聞詳情
    """
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    # 轉換為公開格式（不包含 raw_content）
    result = {
        "id": article.id,
        "title_short": article.title[:20] + "..." if len(article.title) > 20 else article.title,
        "source": article.source,
        "url": article.url,
        "published_at": article.published_at,
        "category": article.category,
        "sentiment_score": None,
        "sentiment_label": None,
        "sentiment_color": None,
        "keywords": None
    }

    # 加入情緒資料
    if article.sentiment_score:
        result["sentiment_score"] = article.sentiment_score.sentiment_score
        result["sentiment_label"] = article.sentiment_score.get_sentiment_label()
        result["sentiment_color"] = article.sentiment_score.get_sentiment_color()
        result["keywords"] = article.sentiment_score.keywords

    return result
