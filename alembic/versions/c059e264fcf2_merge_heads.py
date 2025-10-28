"""merge heads

Revision ID: c059e264fcf2
Revises: 4d79bac7d1bc, bfcd9a2c9430
Create Date: 2025-10-28 16:06:53.797155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c059e264fcf2'
down_revision = ('4d79bac7d1bc', 'bfcd9a2c9430')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
