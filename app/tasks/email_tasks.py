"""
Celery tasks for email operations.
"""

from celery import current_task

from app.core.celery_app import celery_app
from app.utils.email_utils import (
    create_email_verification_email,
    create_password_reset_email,
    send_email,
)


@celery_app.task(name="send_email_task", max_retries=3, default_retry_delay=60)
def send_email_task(
    email_to: str, subject: str, html_content: str, text_content: str = ""
):
    """
    Celery task to send email.

    Args:
        email_to: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content of the email
    """
    try:
        send_email(
            email_to=email_to,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )
        return {"status": "success", "email_to": email_to}
    except Exception as exc:
        # Retry the task
        raise current_task.retry(exc=exc)


@celery_app.task(
    name="send_password_reset_email", max_retries=3, default_retry_delay=60
)
def send_password_reset_email_task(
    email_to: str, reset_token: str, user_name: str = None
):
    """
    Celery task to send password reset email.

    Args:
        email_to: User's email address
        reset_token: Password reset token
        user_name: User's name (optional)
    """
    try:
        subject, html_content = create_password_reset_email(
            user_email=email_to,
            reset_token=reset_token,
            user_name=user_name,
        )

        send_email(
            email_to=email_to,
            subject=subject,
            html_content=html_content,
        )
        return {"status": "success", "email_to": email_to, "type": "password_reset"}
    except Exception as exc:
        raise current_task.retry(exc=exc)


@celery_app.task(name="send_email_verification", max_retries=3, default_retry_delay=60)
def send_email_verification_task(
    email_to: str, verification_token: str, user_name: str = None
):
    """
    Celery task to send email verification email.

    Args:
        email_to: User's email address
        verification_token: Email verification token
        user_name: User's name (optional)
    """
    try:
        subject, html_content = create_email_verification_email(
            user_email=email_to, verification_token=verification_token
        )

        send_email(
            email_to=email_to,
            subject=subject,
            html_content=html_content,
        )
        return {"status": "success", "email_to": email_to, "type": "email_verification"}
    except Exception as exc:
        raise current_task.retry(exc=exc)
