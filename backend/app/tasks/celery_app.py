"""
Celery Application Configuration
Celery 應用配置
"""
from celery import Celery
from celery.schedules import crontab
from app.config import settings

# 建立 Celery 應用
celery_app = Celery(
    "propulseiq",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.analysis_tasks"]
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Taipei",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 分鐘超時
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# 定時任務設定
celery_app.conf.beat_schedule = {
    # 每小時檢查並分析未分析的新聞
    "analyze-pending-articles": {
        "task": "app.tasks.analysis_tasks.analyze_pending_articles",
        "schedule": crontab(minute=0),  # 每小時整點執行
    },
    # 每月 1 日凌晨 2 點生成上月報告
    "generate-monthly-report": {
        "task": "app.tasks.analysis_tasks.generate_monthly_report",
        "schedule": crontab(hour=2, minute=0, day_of_month=1),
    },
    # 每天凌晨 3 點清理舊的原文內容
    "cleanup-old-content": {
        "task": "app.tasks.analysis_tasks.cleanup_old_raw_content",
        "schedule": crontab(hour=3, minute=0),
    },
}
