"""
Sentiment API
情緒分析相關 API
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.database import get_db
from app.models.article import Article
from app.models.sentiment import SentimentScore
from app.schemas.sentiment import (
    SentimentCurrentResponse,
    SentimentTrendResponse,
    SentimentTrendListResponse
)
from app.api.deps import get_current_active_user, check_subscription_tier
from app.models.user import User

router = APIRouter()


@router.get("/current", response_model=SentimentCurrentResponse)
def get_current_sentiment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    取得當前市場情緒指數（本月平均）

    Args:
        db: 資料庫 Session
        current_user: 當前使用者

    Returns:
        當前市場情緒指數
    """
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)

    # 查詢本月的情緒分數
    result = db.query(
        func.avg(SentimentScore.sentiment_score).label('avg_score'),
        func.count(SentimentScore.id).label('count')
    ).join(Article).filter(
        Article.published_at >= start_of_month
    ).first()

    avg_score = float(result.avg_score) if result.avg_score else 0.0
    article_count = result.count or 0

    # 判斷情緒標籤
    if avg_score <= -0.5:
        label = "極度悲觀"
        color = "#ef4444"
    elif avg_score <= -0.2:
        label = "偏向悲觀"
        color = "#fb923c"
    elif avg_score <= 0.2:
        label = "中性觀望"
        color = "#94a3b8"
    elif avg_score <= 0.5:
        label = "偏向樂觀"
        color = "#86efac"
    else:
        label = "極度樂觀"
        color = "#22c55e"

    return {
        "current_score": round(avg_score, 2),
        "current_label": label,
        "current_color": color,
        "article_count": article_count,
        "period": now.strftime("%Y-%m"),
        "last_updated": now
    }


@router.get("/trend", response_model=SentimentTrendListResponse)
def get_sentiment_trend(
    months: int = Query(6, ge=1, le=36, description="回溯月數"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    取得情緒趨勢數據

    免費用戶：6 個月
    Pro 用戶：12 個月
    Business/Enterprise：36 個月

    Args:
        months: 回溯月數
        db: 資料庫 Session
        current_user: 當前使用者

    Returns:
        情緒趨勢列表
    """
    # 檢查訂閱等級限制
    max_months = {
        "free": 6,
        "pro": 12,
        "business": 36,
        "enterprise": 36
    }

    user_max_months = max_months.get(current_user.subscription_tier.value, 6)
    if months > user_max_months:
        months = user_max_months

    # 計算開始日期
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)

    # 查詢每月的情緒統計
    monthly_stats = db.query(
        extract('year', Article.published_at).label('year'),
        extract('month', Article.published_at).label('month'),
        func.avg(SentimentScore.sentiment_score).label('avg_sentiment'),
        func.count(SentimentScore.id).label('article_count'),
        func.sum(func.case((SentimentScore.sentiment_score > 0.2, 1), else_=0)).label('optimistic_count'),
        func.sum(func.case((SentimentScore.sentiment_score < -0.2, 1), else_=0)).label('pessimistic_count'),
        func.sum(func.case(
            (SentimentScore.sentiment_score >= -0.2, func.case((SentimentScore.sentiment_score <= 0.2, 1), else_=0)),
            else_=0
        )).label('neutral_count')
    ).join(Article).filter(
        Article.published_at >= start_date,
        Article.published_at <= end_date
    ).group_by('year', 'month').order_by('year', 'month').all()

    # 轉換為回應格式
    trends = []
    for stat in monthly_stats:
        trends.append({
            "date": f"{int(stat.year)}-{int(stat.month):02d}",
            "avg_sentiment": round(float(stat.avg_sentiment), 2) if stat.avg_sentiment else 0.0,
            "article_count": stat.article_count or 0,
            "optimistic_count": stat.optimistic_count or 0,
            "pessimistic_count": stat.pessimistic_count or 0,
            "neutral_count": stat.neutral_count or 0
        })

    return {
        "trends": trends,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }


@router.get("/monthly/{year}/{month}", response_model=SentimentTrendResponse)
def get_monthly_sentiment(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    取得指定月份的情緒統計

    Args:
        year: 年份
        month: 月份
        db: 資料庫 Session
        current_user: 當前使用者

    Returns:
        指定月份的情緒統計
    """
    # 計算月份範圍
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    # 查詢該月的情緒統計
    result = db.query(
        func.avg(SentimentScore.sentiment_score).label('avg_sentiment'),
        func.count(SentimentScore.id).label('article_count'),
        func.sum(func.case((SentimentScore.sentiment_score > 0.2, 1), else_=0)).label('optimistic_count'),
        func.sum(func.case((SentimentScore.sentiment_score < -0.2, 1), else_=0)).label('pessimistic_count'),
        func.sum(func.case(
            (SentimentScore.sentiment_score >= -0.2, func.case((SentimentScore.sentiment_score <= 0.2, 1), else_=0)),
            else_=0
        )).label('neutral_count')
    ).join(Article).filter(
        Article.published_at >= start_date,
        Article.published_at < end_date
    ).first()

    return {
        "date": f"{year}-{month:02d}",
        "avg_sentiment": round(float(result.avg_sentiment), 2) if result.avg_sentiment else 0.0,
        "article_count": result.article_count or 0,
        "optimistic_count": result.optimistic_count or 0,
        "pessimistic_count": result.pessimistic_count or 0,
        "neutral_count": result.neutral_count or 0
    }
