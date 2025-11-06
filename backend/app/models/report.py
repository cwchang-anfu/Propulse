"""
Monthly Report Model
月度報告資料模型
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class MonthlyReport(Base):
    """月度報告資料表"""
    __tablename__ = "monthly_reports"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    avg_sentiment = Column(Float)  # 平均情緒分數
    article_count = Column(Integer)  # 文章總數
    optimistic_count = Column(Integer)  # 樂觀文章數
    pessimistic_count = Column(Integer)  # 悲觀文章數
    neutral_count = Column(Integer)  # 中性文章數
    trend_direction = Column(String(20))  # up, down, stable
    key_topics = Column(JSON)  # 關鍵主題與詞彙
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    # 唯一約束：每個年月只能有一份報告
    __table_args__ = (
        UniqueConstraint('year', 'month', name='uq_year_month'),
    )

    def __repr__(self):
        return f"<MonthlyReport(year={self.year}, month={self.month}, avg_sentiment={self.avg_sentiment:.2f})>"

    def to_dict(self):
        """轉換為字典格式"""
        return {
            "id": self.id,
            "year": self.year,
            "month": self.month,
            "avg_sentiment": self.avg_sentiment,
            "article_count": self.article_count,
            "optimistic_count": self.optimistic_count,
            "pessimistic_count": self.pessimistic_count,
            "neutral_count": self.neutral_count,
            "trend_direction": self.trend_direction,
            "key_topics": self.key_topics,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None
        }


class APIUsageLog(Base):
    """API 使用記錄資料表"""
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    endpoint = Column(String(200))
    request_count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<APIUsageLog(user_id={self.user_id}, endpoint={self.endpoint}, count={self.request_count})>"
