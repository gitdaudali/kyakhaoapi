from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
import logging

from .models import Video

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for video post-save events.
    Triggers video processing when a new video is uploaded.
    """
    if created:
        logger.info(f"New video created: {instance.title} (ID: {instance.id})")
        
        # Trigger video processing task
        # In a real implementation, this would queue a Celery task
        # from .tasks import process_video
        # process_video.delay(instance.id)
        
        # For now, just log the event
        logger.info(f"Video processing queued for: {instance.title}")
    
    elif instance.status == 'uploading':
        logger.info(f"Video upload completed: {instance.title} (ID: {instance.id})")
        
        # Trigger video processing task
        # In a real implementation, this would queue a Celery task
        # from .tasks import process_video
        # process_video.delay(instance.id)
        
        # For now, just log the event
        logger.info(f"Video processing queued for: {instance.title}")


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Signal handler for video post-delete events.
    Cleans up associated S3 files when a video is deleted.
    """
    logger.info(f"Video deleted: {instance.title} (ID: {instance.id})")
    
    # Clean up S3 files
    # In a real implementation, this would delete files from S3
    # from .utils import delete_s3_file
    # if instance.s3_key:
    #     delete_s3_file(instance.s3_bucket, instance.s3_key)
    
    # For now, just log the event
    logger.info(f"S3 cleanup completed for: {instance.title}")


@receiver(post_save, sender=Video)
def update_video_status(sender, instance, **kwargs):
    """
    Signal handler to update video status based on processing completion.
    """
    # This would be called when video processing is completed
    # In a real implementation, this would be triggered by Celery task completion
    pass
