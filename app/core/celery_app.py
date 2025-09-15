"""
Celery application configuration for background tasks.
"""

from celery import Celery

from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "cup_streaming",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email_tasks",
    ],
)

# Configure Celery
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional configuration for better performance
celery_app.conf.update(
    task_always_eager=False,  # Set to True for testing
    task_eager_propagates=True,
    result_expires=3600,  # 1 hour
    task_ignore_result=False,
    task_store_eager_result=True,
)
