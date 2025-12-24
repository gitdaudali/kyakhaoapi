"""Add recommendation engine tables

Revision ID: add_recommendation_engine
Revises: 375aa9ab5134
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_recommendation_engine'
down_revision: Union[str, None] = '375aa9ab5134'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create dietary_tags table
    op.create_table(
        'dietary_tags',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('identifier', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dietary_tags_identifier'), 'dietary_tags', ['identifier'], unique=True)
    op.create_index(op.f('ix_dietary_tags_is_deleted'), 'dietary_tags', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_dietary_tags_name'), 'dietary_tags', ['name'], unique=True)
    
    # Create dish_dietary_tags association table
    op.create_table(
        'dish_dietary_tags',
        sa.Column('dish_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dietary_tag_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['dish_id'], ['dishes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dietary_tag_id'], ['dietary_tags.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('dish_id', 'dietary_tag_id'),
        sa.UniqueConstraint('dish_id', 'dietary_tag_id', name='uq_dish_dietary_tag')
    )
    
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('min_budget', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('max_budget', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('preferred_dietary_tags', sa.String(length=500), nullable=True),
        sa.Column('preferred_spice_level', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_preferences_is_deleted'), 'user_preferences', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_user_preferences_user_id'), 'user_preferences', ['user_id'], unique=True)
    
    # Create user_interactions table
    op.create_table(
        'user_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dish_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interaction_type', sa.String(length=50), nullable=False),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('interaction_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['dish_id'], ['dishes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'dish_id', 'interaction_type', 'interaction_timestamp', name='uq_user_dish_interaction')
    )
    op.create_index(op.f('ix_user_interactions_dish_id'), 'user_interactions', ['dish_id'], unique=False)
    op.create_index(op.f('ix_user_interactions_interaction_timestamp'), 'user_interactions', ['interaction_timestamp'], unique=False)
    op.create_index(op.f('ix_user_interactions_interaction_type'), 'user_interactions', ['interaction_type'], unique=False)
    op.create_index(op.f('ix_user_interactions_is_deleted'), 'user_interactions', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_user_interactions_user_id'), 'user_interactions', ['user_id'], unique=False)
    
    # Add spice_level column to dishes table
    op.add_column('dishes', sa.Column('spice_level', sa.String(length=50), nullable=True))
    op.create_index(op.f('ix_dishes_spice_level'), 'dishes', ['spice_level'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove spice_level column from dishes
    op.drop_index(op.f('ix_dishes_spice_level'), table_name='dishes')
    op.drop_column('dishes', 'spice_level')
    
    # Drop user_interactions table
    op.drop_index(op.f('ix_user_interactions_user_id'), table_name='user_interactions')
    op.drop_index(op.f('ix_user_interactions_interaction_type'), table_name='user_interactions')
    op.drop_index(op.f('ix_user_interactions_interaction_timestamp'), table_name='user_interactions')
    op.drop_index(op.f('ix_user_interactions_is_deleted'), table_name='user_interactions')
    op.drop_index(op.f('ix_user_interactions_dish_id'), table_name='user_interactions')
    op.drop_table('user_interactions')
    
    # Drop user_preferences table
    op.drop_index(op.f('ix_user_preferences_user_id'), table_name='user_preferences')
    op.drop_index(op.f('ix_user_preferences_is_deleted'), table_name='user_preferences')
    op.drop_table('user_preferences')
    
    # Drop dish_dietary_tags association table
    op.drop_table('dish_dietary_tags')
    
    # Drop dietary_tags table
    op.drop_index(op.f('ix_dietary_tags_name'), table_name='dietary_tags')
    op.drop_index(op.f('ix_dietary_tags_is_deleted'), table_name='dietary_tags')
    op.drop_index(op.f('ix_dietary_tags_identifier'), table_name='dietary_tags')
    op.drop_table('dietary_tags')

