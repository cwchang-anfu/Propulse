"""
Sentiment Score Model
情感分析結果資料模型
"""
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, CheckConstraint, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class SentimentScore(Base):
    """情感分析結果資料表"""
    __tablename__ = "sentiment_scores"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey('articles.id', ondelete='CASCADE'), nullable=False, index=True)
    sentiment_score = Column(Float, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    keywords = Column(JSON)  # 儲存關鍵字陣列
    analysis_reason = Column(Text)  # AI 分析原因說明
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    model_version = Column(String(50))  # 記錄使用的 AI 模型版本

    # 關聯
    article = relationship("Article", back_populates="sentiment_score")

    # 檢查約束：sentiment_score 必須在 -1 到 1 之間
    __table_args__ = (
        CheckConstraint('sentiment_score >= -1 AND sentiment_score <= 1', name='check_sentiment_range'),
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_confidence_range'),
    )

    def __repr__(self):
        return f"<SentimentScore(id={self.id}, article_id={self.article_id}, score={self.sentiment_score:.2f})>"

    def get_sentiment_label(self) -> str:
        """
        根據分數返回情緒標籤
        """
        if self.sentiment_score <= -0.5:
            return "極度悲觀"
        elif self.sentiment_score <= -0.2:
            return "悲觀"
        elif self.sentiment_score <= 0.2:
            return "中性"
        elif self.sentiment_score <= 0.5:
            return "樂觀"
        else:
            return "極度樂觀"

    def get_sentiment_color(self) -> str:
        """
        根據分數返回對應的顏色
        """
        if self.sentiment_score <= -0.5:
            return "#ef4444"  # 紅色
        elif self.sentiment_score <= -0.2:
            return "#fb923c"  # 橙色
        elif self.sentiment_score <= 0.2:
            return "#94a3b8"  # 灰色
        elif self.sentiment_score <= 0.5:
            return "#86efac"  # 淺綠
        else:
            return "#22c55e"  # 綠色
