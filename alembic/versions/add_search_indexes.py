"""
Add helpful indexes for main search

Revision ID: add_search_indexes
Revises: 
Create Date: 2025-10-28
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_search_indexes"
down_revision = "bfcd9a2c9430"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Basic btree indexes to speed up ILIKE and sorting
    op.create_index("ix_contents_title", "contents", ["title"], unique=False)
    op.create_index("ix_contents_content_type", "contents", ["content_type"], unique=False)
    op.create_index("ix_contents_release_date", "contents", ["release_date"], unique=False)
    op.create_index("ix_contents_platform_rating", "contents", ["platform_rating"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_contents_platform_rating", table_name="contents")
    op.drop_index("ix_contents_release_date", table_name="contents")
    op.drop_index("ix_contents_content_type", table_name="contents")
    op.drop_index("ix_contents_title", table_name="contents")


