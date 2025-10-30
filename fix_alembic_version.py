"""Script to fix Alembic version mismatch by updating the alembic_version table."""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Database connection - match your alembic/env.py settings
DB_USER = "postgres"
DB_PASSWORD = "root123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "cup3"

database_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def fix_alembic_version(new_revision="c059e264fcf2"):
    """
    Fix the Alembic version table by setting it to a valid revision.
    
    Args:
        new_revision: The revision to set (default is the current head)
    """
    print(f"Connecting to database: postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    engine = create_engine(database_url)
    
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
                print("[ERROR] alembic_version table does not exist! Creating it...")
                conn.execute(text("""
                    CREATE TABLE alembic_version (
                        version_num VARCHAR(32) NOT NULL,
                        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                    );
                """))
                conn.commit()
                print("[SUCCESS] Created alembic_version table")
            
            # Get current version
            result = conn.execute(text("SELECT version_num FROM alembic_version;"))
            current_version = result.scalar()
            
            print(f"[INFO] Current database revision: {current_version}")
            print(f"[INFO] Setting revision to: {new_revision}")
            
            # Update the version
            if current_version:
                conn.execute(text("UPDATE alembic_version SET version_num = :new_rev;"), 
                           {"new_rev": new_revision})
            else:
                conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:new_rev);"), 
                           {"new_rev": new_revision})
            
            conn.commit()
            
            # Verify
            result = conn.execute(text("SELECT version_num FROM alembic_version;"))
            updated_version = result.scalar()
            
            print(f"[SUCCESS] Successfully updated to revision: {updated_version}")
            print("\n[INFO] Next steps:")
            print("   1. Run 'alembic current' to verify the revision")
            print("   2. Run 'alembic heads' to see the current head")
            print("   3. If you have new models (announcement, task, popup), create a new migration:")
            print("      'alembic revision --autogenerate -m \"add announcement task popup tables\"'")
            print("   4. Run 'alembic upgrade head' to apply any pending migrations")
            
    except Exception as e:
        print(f"[ERROR] Error fixing database: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        engine.dispose()
    
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fix Alembic version mismatch")
    parser.add_argument("--revision", "-r", default="c059e264fcf2", 
                       help="Revision to set (default: current head)")
    args = parser.parse_args()
    
    fix_alembic_version(args.revision)

