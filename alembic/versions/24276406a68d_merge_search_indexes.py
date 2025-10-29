"""merge search indexes

Revision ID: 24276406a68d
Revises: add_search_indexes, 4d79bac7d1bc
Create Date: 2025-10-28 16:29:38.394294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24276406a68d'
down_revision = ('add_search_indexes', '4d79bac7d1bc')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
