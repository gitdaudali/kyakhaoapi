"""merge heads

Revision ID: 10fe6a765dc9
Revises: add_faq_table, b4970b5c526b
Create Date: 2025-10-15 16:17:20.290430

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10fe6a765dc9'
down_revision = ('add_faq_table', 'b4970b5c526b')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
