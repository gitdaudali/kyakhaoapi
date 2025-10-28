"""add user settings and account management

Revision ID: c063cff3718d
Revises: e101b8cce52d
Create Date: 2025-10-19 19:03:24.544048
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as psql

# revision identifiers, used by Alembic.
revision = "c063cff3718d"
down_revision = "e101b8cce52d"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # ========================
    # 1. user_settings table
    # ========================
    try:
        if "user_settings" not in inspector.get_table_names():
            op.create_table(
                "user_settings",
                sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
                sa.Column("user_id", sa.Uuid(), nullable=False),
                sa.Column("language", sa.String(), nullable=True),
                sa.Column("autoplay_next", sa.Boolean(), default=True),
                sa.Column("content_maturity_level", sa.String(), nullable=True),
                sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                sa.Column("updated_at", sa.DateTime(), onupdate=sa.func.now()),
                sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            )
    except Exception:
        pass

    # ========================
    # 2. user_profiles table
    # ========================
    try:
        if "user_profiles" not in inspector.get_table_names():
            op.create_table(
                "user_profiles",
                sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
                sa.Column("user_id", sa.Uuid(), nullable=False),
                sa.Column("profile_name", sa.String(), nullable=False),
                sa.Column("avatar", sa.String(), nullable=True),
                sa.Column("is_kid", sa.Boolean(), default=False),
                sa.Column("preferences", psql.JSON(), nullable=True),
                sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
                sa.Column("updated_at", sa.DateTime(), onupdate=sa.func.now()),
                sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            )
    except Exception:
        pass

    # ==========================================
    # 3. user_watch_progress table (add column)
    # ==========================================
    try:
        columns = [col["name"] for col in inspector.get_columns("user_watch_progress")]
        if "profile_id" not in columns:
            op.add_column("user_watch_progress", sa.Column("profile_id", sa.Uuid(), nullable=True))
    except Exception:
        pass

    # ==========================================
    # 4. user_content_interactions adjustments
    # ==========================================
    try:
        columns = [col["name"] for col in inspector.get_columns("user_content_interactions")]
        if "profile_id" not in columns:
            op.add_column("user_content_interactions", sa.Column("profile_id", sa.Uuid(), nullable=True))
    except Exception:
        pass

    # Safely recreate index
    try:
        op.drop_index("ix_user_content_interactions_profile_id", table_name="user_content_interactions")
    except Exception:
        pass

    try:
        op.create_index(
            "ix_user_content_interactions_profile_id",
            "user_content_interactions",
            ["profile_id"],
            unique=False,
        )
    except Exception:
        pass

    # Safely recreate foreign key
    try:
        fks = [fk["constrained_columns"] for fk in inspector.get_foreign_keys("user_content_interactions")]
        if not any("profile_id" in fk for fk in fks):
            op.create_foreign_key(
                None,
                "user_content_interactions",
                "user_profiles",
                ["profile_id"],
                ["id"],
            )
    except Exception:
        pass


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Drop FKs safely
    try:
        op.drop_constraint(
            "user_content_interactions_profile_id_fkey",
            "user_content_interactions",
            type_="foreignkey",
        )
    except Exception:
        pass

    # Drop index safely
    try:
        op.drop_index("ix_user_content_interactions_profile_id", table_name="user_content_interactions")
    except Exception:
        pass

    # Drop columns safely
    try:
        columns = [col["name"] for col in inspector.get_columns("user_content_interactions")]
        if "profile_id" in columns:
            op.drop_column("user_content_interactions", "profile_id")
    except Exception:
        pass

    try:
        columns = [col["name"] for col in inspector.get_columns("user_watch_progress")]
        if "profile_id" in columns:
            op.drop_column("user_watch_progress", "profile_id")
    except Exception:
        pass

    # Drop tables safely
    try:
        op.drop_table("user_profiles")
    except Exception:
        pass

    try:
        op.drop_table("user_settings")
    except Exception:
        pass
