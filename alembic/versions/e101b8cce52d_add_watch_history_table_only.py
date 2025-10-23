"""Add watch_history table only

Revision ID: e101b8cce52d
Revises: 2dc0e43555de
Create Date: 2025-10-23 11:43:19.659810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e101b8cce52d'
down_revision = '2dc0e43555de'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create watch_history table
    op.create_table('watch_history',
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('thumbnail_url', sa.Text(), nullable=False),
        sa.Column('last_watched_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('content_id', sa.UUID(), nullable=True),
        sa.Column('episode_id', sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_watch_history_content_id'), 'watch_history', ['content_id'], unique=False)
    op.create_index(op.f('ix_watch_history_episode_id'), 'watch_history', ['episode_id'], unique=False)
    op.create_index(op.f('ix_watch_history_is_deleted'), 'watch_history', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_watch_history_last_watched_at'), 'watch_history', ['last_watched_at'], unique=False)
    op.create_index(op.f('ix_watch_history_user_id'), 'watch_history', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_watch_history_user_id'), table_name='watch_history')
    op.drop_index(op.f('ix_watch_history_last_watched_at'), table_name='watch_history')
    op.drop_index(op.f('ix_watch_history_is_deleted'), table_name='watch_history')
    op.drop_index(op.f('ix_watch_history_episode_id'), table_name='watch_history')
    op.drop_index(op.f('ix_watch_history_content_id'), table_name='watch_history')
    
    # Drop table
    op.drop_table('watch_history')
