"""
Article Model
新聞文章資料模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Article(Base):
    """新聞文章資料表（已爬取的數據）"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    source = Column(String(100), nullable=False, index=True)
    url = Column(String(1000), unique=True, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())
    category = Column(String(100))
    raw_content = Column(Text)  # 僅供分析用，不對外顯示

    # 關聯
    sentiment_score = relationship("SentimentScore", back_populates="article", uselist=False)

    # 複合索引
    __table_args__ = (
        Index('idx_published_source', 'published_at', 'source'),
    )

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title[:30]}..., source={self.source})>"

    def to_dict_public(self):
        """
        轉換為公開的字典格式（不包含 raw_content）
        法律合規：不對外提供完整原文
        """
        return {
            "id": self.id,
            "title": self.title[:20] + "..." if len(self.title) > 20 else self.title,
            "source": self.source,
            "url": self.url,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "category": self.category,
            # ❌ 不包含 raw_content
        }
