"""merge heads

Revision ID: cc007c0a1e4f
Revises: 20251030_add_ad_slots, ba867e291173
Create Date: 2025-10-30 02:26:08.365016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc007c0a1e4f'
down_revision = ('20251030_add_ad_slots', 'ba867e291173')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
