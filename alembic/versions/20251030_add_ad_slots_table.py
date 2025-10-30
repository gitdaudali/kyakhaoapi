"""add ad_slots table

Revision ID: 20251030_add_ad_slots
Revises: dd332a9e41e5
Create Date: 2025-10-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251030_add_ad_slots'
down_revision = 'dd332a9e41e5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create SlotStatus enum if not exists (Postgres specific safe pattern)
    slot_status_enum = sa.Enum('active', 'paused', 'ended', 'draft', name='slotstatus_enum')
    ad_type_enum = sa.Enum('banner', 'video', 'native', 'interstitial', 'other', name='adtype_enum_lower')

    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Create enums safely for databases that support it
    if bind.dialect.name == 'postgresql':
        # Create SlotStatus enum
        if 'slotstatus_enum' not in insp.get_enums(schema=None):
            slot_status_enum.create(bind, checkfirst=True)
        # A lower-case adtype for slots (model uses python enum AdType values in lower-case strings)
        if 'adtype_enum_lower' not in insp.get_enums(schema=None):
            ad_type_enum.create(bind, checkfirst=True)

    # Create ad_slots table
    op.create_table(
        'ad_slots',
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        # Use lowercase enums for portability; on non-PG fallback to VARCHAR
        sa.Column('slot_type', sa.String(length=20), nullable=False),
        sa.Column('page_location', sa.String(length=100), nullable=True),
        sa.Column('campaign_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('ad_campaigns.id'), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('dimensions', sa.String(length=20), nullable=True),
        sa.Column('preview_image_url', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ad_slots_name'), 'ad_slots', ['name'], unique=False)
    op.create_index(op.f('ix_ad_slots_slot_type'), 'ad_slots', ['slot_type'], unique=False)
    op.create_index(op.f('ix_ad_slots_status'), 'ad_slots', ['status'], unique=False)
    op.create_index(op.f('ix_ad_slots_page_location'), 'ad_slots', ['page_location'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ad_slots_page_location'), table_name='ad_slots')
    op.drop_index(op.f('ix_ad_slots_status'), table_name='ad_slots')
    op.drop_index(op.f('ix_ad_slots_slot_type'), table_name='ad_slots')
    op.drop_index(op.f('ix_ad_slots_name'), table_name='ad_slots')
    op.drop_table('ad_slots')

    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        sa.Enum(name='slotstatus_enum').drop(bind, checkfirst=True)
        sa.Enum(name='adtype_enum_lower').drop(bind, checkfirst=True)


