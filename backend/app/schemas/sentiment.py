"""
Sentiment Schemas
情感分析相關的 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class SentimentScoreBase(BaseModel):
    """情感分析基礎 Schema"""
    sentiment_score: float = Field(..., ge=-1, le=1, description="情緒分數 (-1 到 1)")
    confidence: float = Field(..., ge=0, le=1, description="信心度 (0 到 1)")
    keywords: Optional[List[str]] = None
    analysis_reason: Optional[str] = None


class SentimentScoreCreate(SentimentScoreBase):
    """建立情感分析 Schema"""
    article_id: int
    model_version: Optional[str] = None


class SentimentScoreResponse(SentimentScoreBase):
    """情感分析回應 Schema"""
    id: int
    article_id: int
    analyzed_at: datetime
    model_version: Optional[str] = None
    sentiment_label: str
    sentiment_color: str

    class Config:
        from_attributes = True


class SentimentCurrentResponse(BaseModel):
    """當前市場情緒回應 Schema"""
    current_score: float
    current_label: str
    current_color: str
    article_count: int
    period: str  # e.g., "2025-11"
    last_updated: datetime


class SentimentTrendResponse(BaseModel):
    """情緒趨勢回應 Schema"""
    date: str  # YYYY-MM-DD 或 YYYY-MM
    avg_sentiment: float
    article_count: int
    optimistic_count: int
    pessimistic_count: int
    neutral_count: int


class SentimentTrendListResponse(BaseModel):
    """情緒趨勢列表回應 Schema"""
    trends: List[SentimentTrendResponse]
    start_date: str
    end_date: str
