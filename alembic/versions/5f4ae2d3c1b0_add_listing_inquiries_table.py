"""add listing inquiries table

Revision ID: 5f4ae2d3c1b0
Revises: 12370e613e98
Create Date: 2025-11-11 13:45:00.000000
"""

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "5f4ae2d3c1b0"
down_revision = "12370e613e98"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "listing_inquiries",
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("listing_id", sa.UUID(), nullable=False),
        sa.Column("message", sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=False),
        sa.Column("preferred_move_in_date", sqlmodel.sql.sqltypes.AutoString(length=32), nullable=True),
        sa.Column("contact_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_listing_inquiries_is_deleted"),
        "listing_inquiries",
        ["is_deleted"],
        unique=False,
    )
    op.create_index(
        op.f("ix_listing_inquiries_listing_id"),
        "listing_inquiries",
        ["listing_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_listing_inquiries_listing_id"), table_name="listing_inquiries")
    op.drop_index(op.f("ix_listing_inquiries_is_deleted"), table_name="listing_inquiries")
    op.drop_table("listing_inquiries")



