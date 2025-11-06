"""
Article Schemas
新聞文章相關的 Pydantic Schemas
"""
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class ArticleBase(BaseModel):
    """新聞文章基礎 Schema"""
    title: str
    source: str
    url: str
    published_at: datetime
    category: Optional[str] = None


class ArticleCreate(ArticleBase):
    """建立新聞文章 Schema"""
    raw_content: Optional[str] = None


class ArticleUpdate(BaseModel):
    """更新新聞文章 Schema"""
    title: Optional[str] = None
    category: Optional[str] = None
    raw_content: Optional[str] = None


class ArticlePublicResponse(BaseModel):
    """
    新聞文章公開回應 Schema
    法律合規：不包含完整原文
    """
    id: int
    title_short: str  # 只顯示前 20 字
    source: str
    url: str
    published_at: datetime
    category: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    sentiment_color: Optional[str] = None
    keywords: Optional[list] = None

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """新聞文章列表回應 Schema"""
    total: int
    page: int
    page_size: int
    items: list[ArticlePublicResponse]
