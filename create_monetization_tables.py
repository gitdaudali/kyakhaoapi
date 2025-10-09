#!/usr/bin/env python3
"""
Script to create monetization tables in PostgreSQL database.
Run this script to set up the required tables for the monetization APIs.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings
from app.models.monetization import AdCampaign, AdCampaignStat, MonetizationActivity
from app.core.database import Base

async def create_tables():
    """Create all monetization tables in the database."""
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        pool_pre_ping=True,
        pool_recycle=300,
        echo=True,
    )
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            # Create monetization tables
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Monetization tables created successfully!")
            
            # Verify tables exist
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('ad_campaigns', 'ad_campaign_stats', 'monetization_activity')
                ORDER BY table_name;
            """))
            
            tables = result.fetchall()
            print(f"📋 Created tables: {[table[0] for table in tables]}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("🚀 Creating monetization tables...")
    asyncio.run(create_tables())
    print("✅ Done!")
