from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData
from sqlmodel import SQLModel
from app.core.config import settings
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

# Synchronize metadata between SQLModel and Base for foreign key resolution
# This ensures that tables in both metadata objects can reference each other
def sync_metadata():
    """Synchronize metadata between SQLModel and Base for foreign key resolution."""
    # Import User model to ensure it's registered in SQLModel.metadata
    from app.models.user import User  # noqa: F401
    
    # Copy users table from SQLModel.metadata to Base.metadata if it exists
    # This allows Base.metadata models (like Cart) to reference users table
    if 'users' in SQLModel.metadata.tables and 'users' not in Base.metadata.tables:
        users_table = SQLModel.metadata.tables['users']
        users_table.tometadata(Base.metadata, schema=None)
    
    # Import Base models to ensure they're registered
    # Import these lazily to avoid circular import issues
    from app.models.food import Dish, Cuisine, Restaurant, Mood, Reservation  # noqa: F401
    
    # Copy Base.metadata tables to SQLModel.metadata if not already present
    # This ensures SQLModel models can reference Base models via foreign keys
    for table in Base.metadata.tables.values():
        if table.name not in SQLModel.metadata.tables:
            table.tometadata(SQLModel.metadata)

# Alias for backward compatibility with main.py
def merge_metadata():
    """Alias for sync_metadata - merges Base.metadata into SQLModel.metadata."""
    sync_metadata()

# Note: sync_metadata() is NOT called at module level to avoid circular imports
# It should be called after all models are imported, typically in the app lifespan

# Build database URL for asyncpg
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Parse SSL mode from URL or default to require for Neon

parsed = urlparse(database_url)
query_params = parse_qs(parsed.query)
ssl_mode = query_params.get("sslmode", ["require"])[0]

# Remove sslmode from URL (asyncpg handles SSL via connect_args)
query_params.pop("sslmode", None)
if query_params:
    new_query = urlencode(query_params, doseq=True)
    parsed = parsed._replace(query=new_query)
else:
    parsed = parsed._replace(query="")
database_url = urlunparse(parsed)

# Configure SSL for asyncpg
# For Neon PostgreSQL, use ssl=True (simple boolean)
# The channel_binding error is a SQLAlchemy/asyncpg compatibility issue
# that may require SQLAlchemy update or workaround
connect_args = {}
if ssl_mode == "require" or ssl_mode == "prefer":
    # For Neon PostgreSQL and other cloud providers requiring SSL
    connect_args["ssl"] = True
elif ssl_mode == "disable":
    connect_args["ssl"] = False
else:
    # For other modes, default to SSL enabled
    connect_args["ssl"] = True

engine = create_async_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=3,
    max_overflow=5,
    pool_timeout=30,
    echo=settings.DEBUG,
    connect_args=connect_args,
)

# Create async SessionLocal class
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()
