from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import MetaData
from sqlmodel import SQLModel
from app.core.config import settings
from sqlmodel import SQLModel
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
    from app.models import Dish, Cuisine, Restaurant, Mood, Reservation  # noqa: F401
    
    # Copy Base.metadata tables to SQLModel.metadata if not already present
    # This ensures SQLModel models can reference Base models via foreign keys
    for table in Base.metadata.tables.values():
        if table.name not in SQLModel.metadata.tables:
            table.tometadata(SQLModel.metadata)

# Call sync_metadata after Base is created
# This must happen before models that reference each other are imported/used
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
