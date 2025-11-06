"""
Report Schemas
報告相關的 Pydantic Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict


class MonthlyReportBase(BaseModel):
    """月度報告基礎 Schema"""
    year: int
    month: int
    avg_sentiment: Optional[float] = None
    article_count: Optional[int] = None
    optimistic_count: Optional[int] = None
    pessimistic_count: Optional[int] = None
    neutral_count: Optional[int] = None
    trend_direction: Optional[str] = None
    key_topics: Optional[Dict] = None


class MonthlyReportCreate(MonthlyReportBase):
    """建立月度報告 Schema"""
    pass


class MonthlyReportResponse(MonthlyReportBase):
    """月度報告回應 Schema"""
    id: int
    generated_at: datetime

    class Config:
        from_attributes = True


class MonthlyReportListResponse(BaseModel):
    """月度報告列表回應 Schema"""
    total: int
    reports: List[MonthlyReportResponse]


class ReportExportRequest(BaseModel):
    """報告匯出請求 Schema"""
    year: int
    month: int
    format: str  # pdf, csv, json
