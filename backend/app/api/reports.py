"""
Reports API
報告相關 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.report import MonthlyReport
from app.schemas.report import MonthlyReportResponse, MonthlyReportListResponse
from app.api.deps import get_current_active_user, check_subscription_tier
from app.models.user import User

router = APIRouter()


@router.get("/monthly", response_model=MonthlyReportListResponse)
def get_monthly_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_subscription_tier("pro"))
):
    """
    取得月度報告列表（需要 Pro 以上方案）

    Args:
        db: 資料庫 Session
        current_user: 當前使用者（Pro 以上）

    Returns:
        月度報告列表
    """
    reports = db.query(MonthlyReport).order_by(
        desc(MonthlyReport.year),
        desc(MonthlyReport.month)
    ).all()

    return {
        "total": len(reports),
        "reports": reports
    }


@router.get("/monthly/{year}/{month}", response_model=MonthlyReportResponse)
def get_monthly_report(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_subscription_tier("pro"))
):
    """
    取得特定月份的報告（需要 Pro 以上方案）

    Args:
        year: 年份
        month: 月份
        db: 資料庫 Session
        current_user: 當前使用者（Pro 以上）

    Returns:
        月度報告
    """
    report = db.query(MonthlyReport).filter(
        MonthlyReport.year == year,
        MonthlyReport.month == month
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report for {year}-{month:02d} not found"
        )

    return report


@router.get("/export/{year}/{month}/{format}")
def export_report(
    year: int,
    month: int,
    format: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_subscription_tier("pro"))
):
    """
    匯出報告（需要 Pro 以上方案）

    支援格式：
    - pdf: PDF 格式（需要 Pro）
    - csv: CSV 格式（需要 Pro）
    - json: JSON 格式（需要 Pro）

    Args:
        year: 年份
        month: 月份
        format: 匯出格式
        db: 資料庫 Session
        current_user: 當前使用者（Pro 以上）

    Returns:
        匯出的報告檔案
    """
    report = db.query(MonthlyReport).filter(
        MonthlyReport.year == year,
        MonthlyReport.month == month
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report for {year}-{month:02d} not found"
        )

    # TODO: 實作實際的匯出邏輯
    if format == "json":
        return report.to_dict()
    elif format == "csv":
        # TODO: 實作 CSV 匯出
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="CSV export not implemented yet"
        )
    elif format == "pdf":
        # TODO: 實作 PDF 匯出
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF export not implemented yet"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Supported formats: json, csv, pdf"
        )
