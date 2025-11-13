"""add food domain tables

Revision ID: add_food_domain_20251112
Revises: de5d1ac06c9d
Create Date: 2025-11-12 14:30:00.000000
"""

from collections import namedtuple

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "add_food_domain_20251112"
down_revision = "de5d1ac06c9d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cuisines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("ix_cuisines_is_deleted", "cuisines", ["is_deleted"], unique=False)
    op.create_index("ix_cuisines_name", "cuisines", ["name"], unique=True)

    op.create_table(
        "moods",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("ix_moods_is_deleted", "moods", ["is_deleted"], unique=False)
    op.create_index("ix_moods_name", "moods", ["name"], unique=True)

    op.create_table(
        "restaurants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address_line", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state", sa.String(length=120), nullable=True),
        sa.Column("country", sa.String(length=120), nullable=True),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column("phone_number", sa.String(length=30), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("price_level", sa.Integer(), nullable=True),
    )
    op.create_index("ix_restaurants_city", "restaurants", ["city"], unique=False)
    op.create_index("ix_restaurants_is_deleted", "restaurants", ["is_deleted"], unique=False)
    op.create_index("ix_restaurants_latitude", "restaurants", ["latitude"], unique=False)
    op.create_index("ix_restaurants_longitude", "restaurants", ["longitude"], unique=False)
    op.create_index("ix_restaurants_name", "restaurants", ["name"], unique=False)
    op.create_index("ix_restaurants_rating", "restaurants", ["rating"], unique=False)

    op.create_table(
        "dishes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("restaurant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cuisine_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("featured_week", sa.Date(), nullable=True),
        sa.Column("calories", sa.Integer(), nullable=True),
        sa.Column("preparation_time_minutes", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cuisine_id"], ["cuisines.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_dishes_cuisine_id", "dishes", ["cuisine_id"], unique=False)
    op.create_index("ix_dishes_is_deleted", "dishes", ["is_deleted"], unique=False)
    op.create_index("ix_dishes_is_featured", "dishes", ["is_featured"], unique=False)
    op.create_index("ix_dishes_name", "dishes", ["name"], unique=False)
    op.create_index("ix_dishes_rating", "dishes", ["rating"], unique=False)
    op.create_index("ix_dishes_restaurant_id", "dishes", ["restaurant_id"], unique=False)

    op.create_table(
        "reservations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("restaurant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_name", sa.String(length=120), nullable=False),
        sa.Column("customer_email", sa.String(length=255), nullable=False),
        sa.Column("reservation_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("party_size", sa.Integer(), nullable=False),
        sa.Column("special_requests", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "restaurant_id",
            "reservation_time",
            "customer_email",
            name="uq_reservation_unique_slot",
        ),
    )
    op.create_index("ix_reservations_customer_email", "reservations", ["customer_email"], unique=False)
    op.create_index("ix_reservations_is_deleted", "reservations", ["is_deleted"], unique=False)
    op.create_index("ix_reservations_restaurant_id", "reservations", ["restaurant_id"], unique=False)
    op.create_index("ix_reservations_reservation_time", "reservations", ["reservation_time"], unique=False)

    op.create_table(
        "dish_moods",
        sa.Column("dish_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mood_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["dish_id"], ["dishes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mood_id"], ["moods.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("dish_id", "mood_id", name="pk_dish_mood"),
        sa.UniqueConstraint("dish_id", "mood_id", name="uq_dish_mood"),
    )


def downgrade() -> None:
    op.drop_table("dish_moods")
    op.drop_index("ix_reservations_reservation_time", table_name="reservations")
    op.drop_index("ix_reservations_restaurant_id", table_name="reservations")
    op.drop_index("ix_reservations_is_deleted", table_name="reservations")
    op.drop_index("ix_reservations_customer_email", table_name="reservations")
    op.drop_table("reservations")
    op.drop_index("ix_dishes_restaurant_id", table_name="dishes")
    op.drop_index("ix_dishes_rating", table_name="dishes")
    op.drop_index("ix_dishes_name", table_name="dishes")
    op.drop_index("ix_dishes_is_featured", table_name="dishes")
    op.drop_index("ix_dishes_is_deleted", table_name="dishes")
    op.drop_index("ix_dishes_cuisine_id", table_name="dishes")
    op.drop_table("dishes")
    op.drop_index("ix_restaurants_rating", table_name="restaurants")
    op.drop_index("ix_restaurants_name", table_name="restaurants")
    op.drop_index("ix_restaurants_longitude", table_name="restaurants")
    op.drop_index("ix_restaurants_latitude", table_name="restaurants")
    op.drop_index("ix_restaurants_is_deleted", table_name="restaurants")
    op.drop_index("ix_restaurants_city", table_name="restaurants")
    op.drop_table("restaurants")
    op.drop_index("ix_moods_name", table_name="moods")
    op.drop_index("ix_moods_is_deleted", table_name="moods")
    op.drop_table("moods")
    op.drop_index("ix_cuisines_name", table_name="cuisines")
    op.drop_index("ix_cuisines_is_deleted", table_name="cuisines")
    op.drop_table("cuisines")
