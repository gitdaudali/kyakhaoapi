"""Script to check and fix Alembic version mismatch."""
import sys
import importlib.util
from pathlib import Path
from sqlalchemy import create_engine, text

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def get_url():
    """Get database URL from alembic/env.py."""
    env_path = project_root / "alembic" / "env.py"
    spec = importlib.util.spec_from_file_location("alembic_env", env_path)
    alembic_env = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(alembic_env)
    return alembic_env.get_url()

def check_alembic_version():
    """Check current Alembic version in database."""
    db_url = get_url()
    print(f"Connecting to database: postgresql://***:***@{db_url.split('@')[1] if '@' in db_url else db_url}")
    
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Check if alembic_version table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ alembic_version table does not exist!")
                return None
            
            # Get current version
            result = conn.execute(text("SELECT version_num FROM alembic_version;"))
            current_version = result.scalar()
            
            print(f"✅ Current database revision: {current_version}")
            return current_version
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        engine.dispose()


if __name__ == "__main__":
    check_alembic_version()
