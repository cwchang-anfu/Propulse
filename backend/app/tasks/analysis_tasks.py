"""
Analysis Tasks
分析相關的 Celery 任務
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.article import Article
from app.models.sentiment import SentimentScore
from app.models.report import MonthlyReport
from app.services.ai_analyzer import AIAnalyzer
from app.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.analysis_tasks.analyze_pending_articles")
def analyze_pending_articles():
    """
    分析尚未處理的新聞文章
    每小時執行一次
    """
    db = SessionLocal()

    try:
        logger.info("Starting to analyze pending articles...")

        # 查詢尚未分析的文章
        pending_articles = db.query(Article).outerjoin(
            SentimentScore, Article.id == SentimentScore.article_id
        ).filter(
            SentimentScore.id == None,  # 沒有情緒分數
            Article.raw_content != None  # 有原文內容
        ).limit(settings.AI_BATCH_SIZE).all()

        if not pending_articles:
            logger.info("No pending articles to analyze")
            return {"status": "success", "analyzed": 0}

        logger.info(f"Found {len(pending_articles)} articles to analyze")

        # 準備分析數據
        articles_data = [
            (article.id, article.title, article.raw_content)
            for article in pending_articles
        ]

        # 使用 AI 分析器批次分析
        analyzer = AIAnalyzer()
        results = analyzer.batch_analyze(articles_data)

        # 儲存分析結果
        for result in results:
            sentiment = SentimentScore(
                article_id=result['article_id'],
                sentiment_score=result['sentiment_score'],
                confidence=result['confidence'],
                keywords=result['keywords'],
                analysis_reason=result['analysis_reason'],
                model_version=result['model_version']
            )
            db.add(sentiment)

        db.commit()

        logger.info(f"Successfully analyzed {len(results)} articles")

        return {
            "status": "success",
            "analyzed": len(results),
            "pending": len(pending_articles)
        }

    except Exception as e:
        logger.error(f"Error analyzing articles: {e}")
        db.rollback()
        raise

    finally:
        db.close()


@celery_app.task(name="app.tasks.analysis_tasks.generate_monthly_report")
def generate_monthly_report():
    """
    生成月度報告
    每月 1 日執行
    """
    db = SessionLocal()

    try:
        # 計算上個月的年月
        today = datetime.now()
        if today.month == 1:
            year = today.year - 1
            month = 12
        else:
            year = today.year
            month = today.month - 1

        logger.info(f"Generating monthly report for {year}-{month:02d}")

        # 檢查報告是否已存在
        existing_report = db.query(MonthlyReport).filter(
            MonthlyReport.year == year,
            MonthlyReport.month == month
        ).first()

        if existing_report:
            logger.info(f"Report for {year}-{month:02d} already exists")
            return {"status": "skipped", "reason": "Report already exists"}

        # 計算月份範圍
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # 查詢該月的情緒統計
        stats = db.query(
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

        # 分析趨勢方向（與上上個月比較）
        if month == 1:
            prev_year = year - 1
            prev_month = 11
        elif month == 2:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 2

        prev_report = db.query(MonthlyReport).filter(
            MonthlyReport.year == prev_year,
            MonthlyReport.month == prev_month
        ).first()

        trend_direction = "stable"
        if prev_report and stats.avg_sentiment:
            if stats.avg_sentiment > prev_report.avg_sentiment + 0.1:
                trend_direction = "up"
            elif stats.avg_sentiment < prev_report.avg_sentiment - 0.1:
                trend_direction = "down"

        # 提取關鍵主題（取最常見的關鍵字）
        # TODO: 實作更複雜的關鍵主題分析
        key_topics = {"note": "關鍵主題分析待實作"}

        # 建立報告
        report = MonthlyReport(
            year=year,
            month=month,
            avg_sentiment=float(stats.avg_sentiment) if stats.avg_sentiment else 0.0,
            article_count=stats.article_count or 0,
            optimistic_count=stats.optimistic_count or 0,
            pessimistic_count=stats.pessimistic_count or 0,
            neutral_count=stats.neutral_count or 0,
            trend_direction=trend_direction,
            key_topics=key_topics
        )

        db.add(report)
        db.commit()

        logger.info(f"Successfully generated monthly report for {year}-{month:02d}")

        return {
            "status": "success",
            "year": year,
            "month": month,
            "avg_sentiment": report.avg_sentiment,
            "article_count": report.article_count
        }

    except Exception as e:
        logger.error(f"Error generating monthly report: {e}")
        db.rollback()
        raise

    finally:
        db.close()


@celery_app.task(name="app.tasks.analysis_tasks.cleanup_old_raw_content")
def cleanup_old_raw_content():
    """
    清理舊的原文內容（法律合規）
    保留 N 天後清空 raw_content
    每天執行一次
    """
    db = SessionLocal()

    try:
        logger.info("Starting to cleanup old raw content...")

        # 計算截止日期
        cutoff_date = datetime.now() - timedelta(days=settings.RAW_CONTENT_RETENTION_DAYS)

        # 查詢需要清理的文章
        articles_to_cleanup = db.query(Article).filter(
            Article.crawled_at < cutoff_date,
            Article.raw_content != None
        ).all()

        if not articles_to_cleanup:
            logger.info("No articles to cleanup")
            return {"status": "success", "cleaned": 0}

        logger.info(f"Found {len(articles_to_cleanup)} articles to cleanup")

        # 清空 raw_content
        count = 0
        for article in articles_to_cleanup:
            article.raw_content = None
            count += 1

        db.commit()

        logger.info(f"Successfully cleaned {count} articles")

        return {
            "status": "success",
            "cleaned": count
        }

    except Exception as e:
        logger.error(f"Error cleaning up raw content: {e}")
        db.rollback()
        raise

    finally:
        db.close()


@celery_app.task(name="app.tasks.analysis_tasks.analyze_single_article")
def analyze_single_article(article_id: int):
    """
    分析單篇文章（手動觸發用）

    Args:
        article_id: 文章 ID
    """
    db = SessionLocal()

    try:
        logger.info(f"Analyzing article {article_id}")

        # 查詢文章
        article = db.query(Article).filter(Article.id == article_id).first()

        if not article:
            logger.error(f"Article {article_id} not found")
            return {"status": "error", "message": "Article not found"}

        if not article.raw_content:
            logger.error(f"Article {article_id} has no content")
            return {"status": "error", "message": "Article has no content"}

        # 檢查是否已經分析過
        existing_sentiment = db.query(SentimentScore).filter(
            SentimentScore.article_id == article_id
        ).first()

        if existing_sentiment:
            logger.info(f"Article {article_id} already analyzed")
            return {"status": "skipped", "message": "Article already analyzed"}

        # 使用 AI 分析器
        analyzer = AIAnalyzer()
        result = analyzer.analyze_sentiment(article.title, article.raw_content)

        if not result:
            logger.error(f"Failed to analyze article {article_id}")
            return {"status": "error", "message": "Analysis failed"}

        # 儲存分析結果
        sentiment = SentimentScore(
            article_id=article_id,
            sentiment_score=result['sentiment_score'],
            confidence=result['confidence'],
            keywords=result['keywords'],
            analysis_reason=result['reason'],
            model_version=analyzer.model
        )

        db.add(sentiment)
        db.commit()

        logger.info(f"Successfully analyzed article {article_id}")

        return {
            "status": "success",
            "article_id": article_id,
            "sentiment_score": result['sentiment_score']
        }

    except Exception as e:
        logger.error(f"Error analyzing article {article_id}: {e}")
        db.rollback()
        raise

    finally:
        db.close()
