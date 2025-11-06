"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-11-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=True),
        sa.Column('subscription_tier', sa.Enum('free', 'pro', 'business', 'enterprise', name='subscriptiontier'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create articles table
    op.create_table('articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('url', sa.String(length=1000), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('crawled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('raw_content', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )
    op.create_index(op.f('ix_articles_published_at'), 'articles', ['published_at'])
    op.create_index(op.f('ix_articles_source'), 'articles', ['source'])
    op.create_index('idx_published_source', 'articles', ['published_at', 'source'])

    # Create sentiment_scores table
    op.create_table('sentiment_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('keywords', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('analysis_reason', sa.Text(), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.CheckConstraint('sentiment_score >= -1 AND sentiment_score <= 1', name='check_sentiment_range'),
        sa.CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_confidence_range'),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sentiment_scores_analyzed_at'), 'sentiment_scores', ['analyzed_at'])
    op.create_index(op.f('ix_sentiment_scores_article_id'), 'sentiment_scores', ['article_id'])
    op.create_index(op.f('ix_sentiment_scores_sentiment_score'), 'sentiment_scores', ['sentiment_score'])

    # Create monthly_reports table
    op.create_table('monthly_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('avg_sentiment', sa.Float(), nullable=True),
        sa.Column('article_count', sa.Integer(), nullable=True),
        sa.Column('optimistic_count', sa.Integer(), nullable=True),
        sa.Column('pessimistic_count', sa.Integer(), nullable=True),
        sa.Column('neutral_count', sa.Integer(), nullable=True),
        sa.Column('trend_direction', sa.String(length=20), nullable=True),
        sa.Column('key_topics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('year', 'month', name='uq_year_month')
    )

    # Create api_usage_logs table
    op.create_table('api_usage_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.String(length=200), nullable=True),
        sa.Column('request_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_api_usage_logs_user_id_created_at', 'api_usage_logs', ['user_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('ix_api_usage_logs_user_id_created_at', table_name='api_usage_logs')
    op.drop_table('api_usage_logs')
    op.drop_table('monthly_reports')
    op.drop_index(op.f('ix_sentiment_scores_sentiment_score'), table_name='sentiment_scores')
    op.drop_index(op.f('ix_sentiment_scores_article_id'), table_name='sentiment_scores')
    op.drop_index(op.f('ix_sentiment_scores_analyzed_at'), table_name='sentiment_scores')
    op.drop_table('sentiment_scores')
    op.drop_index('idx_published_source', table_name='articles')
    op.drop_index(op.f('ix_articles_source'), table_name='articles')
    op.drop_index(op.f('ix_articles_published_at'), table_name='articles')
    op.drop_table('articles')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
