import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.models.user import User
from app.models.user_settings import UserSettings
from sqlalchemy import select

async def populate_sample_data():
    async for db in get_async_session():
        # Get a user
        user = await db.execute(select(User).limit(1))
        user = user.scalar_one_or_none()
        
        if user:
            # Create user settings
            settings = UserSettings(
                user_id=user.id,
                language="en",
                timezone="UTC",
                autoplay=True,
                email_notifications=True,
                push_notifications=True,
                marketing_emails=False,
                parental_controls_enabled=False,
                content_rating_limit=18,
                data_sharing=False,
                analytics_tracking=True
            )
            db.add(settings)
            
            # Add analytics data to user
            analytics_data = {
                "total_watch_time": 1200,
                "content_watched": 45,
                "favorite_genres": ["Action", "Drama", "Comedy"],
                "peak_watching_hours": [20, 21, 22],
                "device_usage": {"mobile": 60, "web": 30, "tv": 10},
                "current_month": {"watch_time": 120, "content_watched": 8},
                "previous_month": {"watch_time": 95, "content_watched": 6},
                "achievements": ["Binge Watcher", "Genre Explorer", "Night Owl"]
            }
            user.analytics_data = json.dumps(analytics_data)
            
            # Add activity log
            activity_data = [
                {
                    "id": "1",
                    "activity_type": "login",
                    "description": "User logged in",
                    "ip_address": "192.168.1.1",
                    "device_type": "mobile",
                    "device_name": "iPhone 15",
                    "location": "New York, NY",
                    "timestamp": "2023-12-01T10:00:00Z"
                },
                {
                    "id": "2",
                    "activity_type": "settings_change",
                    "description": "User updated language preference",
                    "ip_address": "192.168.1.1",
                    "device_type": "web",
                    "device_name": "Chrome Browser",
                    "location": "New York, NY",
                    "timestamp": "2023-11-30T15:00:00Z"
                }
            ]
            user.activity_log = json.dumps(activity_data)
            
            await db.commit()
            print("Sample data populated successfully!")
        else:
            print("No user found. Please create a user first.")

if __name__ == "__main__":
    asyncio.run(populate_sample_data())