from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData
from sqlmodel import SQLModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

# Synchronize SQLModel.metadata with Base.metadata for foreign key resolution
# This ensures that tables in SQLModel.metadata (like users) are available
# when Base.metadata models (like Cart) try to reference them
def sync_metadata():
    """Copy SQLModel tables to Base.metadata so foreign keys can resolve."""
    # Import User model to ensure it's registered in SQLModel.metadata
    from app.models.user import User  # noqa: F401
    
    # Copy users table from SQLModel.metadata to Base.metadata if it exists
    # This allows Cart model (in Base.metadata) to reference users table
    # Note: use_alter=True in Cart model defers validation, but we still need
    # the table to exist in Base.metadata for proper foreign key resolution
    if 'users' in SQLModel.metadata.tables and 'users' not in Base.metadata.tables:
        users_table = SQLModel.metadata.tables['users']
        # Create a copy of the table in Base.metadata
        users_table.tometadata(Base.metadata, schema=None)

# Call sync_metadata after Base is created
# This must happen before Cart models are imported/used
sync_metadata()

# Build database URL

database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# For local development, disable SSL via connect_args (asyncpg doesn't support ssl=disable in URL)
# Check if we're connecting to localhost/127.0.0.1
is_local = any(host in database_url for host in ["localhost", "127.0.0.1"])

# Remove any ssl parameters from URL (we'll handle it via connect_args)
if "?ssl=" in database_url or "&ssl=" in database_url:
    import re
    database_url = re.sub(r'[?&]ssl=[^&]*', '', database_url)
    if '?' not in database_url and '&' in database_url:
        database_url = database_url.replace('&', '?', 1)

# Create async engine for SQLModel
# For localhost connections, use minimal connection args to avoid SSL issues
connect_args = {}
if is_local:
    # Disable SSL for localhost (required for asyncpg)
    connect_args["ssl"] = False

# Print connection details (without password) - using print so it shows immediately


engine = create_async_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,  # Increased back to 5 minutes
    pool_size=3,       # Reduced to minimum for testing
    max_overflow=5,    # Reduced overflow
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
