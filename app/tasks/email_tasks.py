"""
Celery tasks for email operations using Jinja2 templates.
"""

from celery import current_task

from app.core.celery_app import celery_app
from app.utils.email_utils import (
    create_email_verification_email,
    create_password_reset_email,
    create_registration_otp_email,
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
        email_data = create_password_reset_email(
            user_email=email_to,
            reset_token=reset_token,
            user_name=user_name,
        )

        send_email(
            email_to=email_to,
            subject=email_data.subject,
            html_content=email_data.html_content,
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
        email_data = create_email_verification_email(
            user_email=email_to,
            verification_token=verification_token,
            user_name=user_name,
        )

        send_email(
            email_to=email_to,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
        return {"status": "success", "email_to": email_to, "type": "email_verification"}
    except Exception as exc:
        raise current_task.retry(exc=exc)


@celery_app.task(
    name="send_registration_otp_email", max_retries=3, default_retry_delay=60
)
def send_registration_otp_email_task(
    email_to: str, otp_code: str, user_name: str = None
):
    """
    Celery task to send registration OTP email.

    Args:
        email_to: User's email address
        otp_code: 6-digit OTP code
        user_name: User's name (optional)
    """
    try:
        email_data = create_registration_otp_email(
            user_email=email_to, otp_code=otp_code, user_name=user_name
        )

        send_email(
            email_to=email_to,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
        return {"status": "success", "email_to": email_to, "type": "registration_otp"}
    except Exception as exc:
        raise current_task.retry(exc=exc)
