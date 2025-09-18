"""
Email utility functions for sending emails using Jinja2 templates.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import settings
from app.utils.template_utils import EmailData, render_email_template


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
    text_content: str = "",
) -> None:
    """
    Send email using SMTP.

    Args:
        email_to: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content of the email
    """
    if not settings.EMAILS_ENABLED:
        print(f"Email disabled. Would send to {email_to}: {subject}")
        return

    if not all(
        [
            settings.SMTP_HOST,
            settings.SMTP_USER,
            settings.SMTP_PASSWORD,
            settings.FROM_EMAIL,
        ]
    ):
        raise ValueError("Email configuration is incomplete")

    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>"
    msg["To"] = email_to

    # Add text content if provided
    if text_content:
        text_part = MIMEText(text_content, "plain")
        msg.attach(text_part)

    # Add HTML content if provided
    if html_content:
        html_part = MIMEText(html_content, "html")
        msg.attach(html_part)

    # Send email
    try:
        if settings.SMTP_SSL:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            if settings.SMTP_TLS:
                server.starttls()

        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.FROM_EMAIL, email_to, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {email_to}")
    except Exception as e:
        print(f"Failed to send email to {email_to}: {str(e)}")
        raise


def create_password_reset_email(
    user_email: str, reset_token: str, user_name: str = None
) -> EmailData:
    """
    Create password reset email content using template.

    Args:
        user_email: User's email address
        reset_token: Password reset token
        user_name: User's name (optional)

    Returns:
        EmailData object with subject and html_content
    """
    username = user_name or user_email.split("@")[0]
    subject = f"{settings.PROJECT_NAME} - Password Reset Request"

    html_content = render_email_template(
        template_name="password_reset.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": user_email,
            "reset_token": reset_token,
            "valid_hours": settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
        },
    )

    return EmailData(html_content=html_content, subject=subject)


def create_email_verification_email(
    user_email: str, verification_token: str, user_name: str = None
) -> EmailData:
    """
    Create email verification email content using template.

    Args:
        user_email: User's email address
        verification_token: Email verification token
        user_name: User's name (optional)

    Returns:
        EmailData object with subject and html_content
    """
    username = user_name or user_email.split("@")[0]
    subject = f"{settings.PROJECT_NAME} - Verify Your Email Address"

    html_content = render_email_template(
        template_name="email_verification.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": user_email,
            "verification_token": verification_token,
            "valid_hours": settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS,
        },
    )

    return EmailData(html_content=html_content, subject=subject)


def create_registration_otp_email(
    user_email: str, otp_code: str, user_name: str = None
) -> EmailData:
    """
    Create registration OTP email content using template.

    Args:
        user_email: User's email address
        otp_code: 6-digit OTP code
        user_name: User's name (optional)

    Returns:
        EmailData object with subject and html_content
    """
    username = user_name or user_email.split("@")[0]
    subject = f"{settings.PROJECT_NAME} - Welcome! Verify Your Email"

    html_content = render_email_template(
        template_name="register_user.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": user_email,
            "otp_code": otp_code,
        },
    )

    return EmailData(html_content=html_content, subject=subject)


def create_password_reset_otp_email(
    user_email: str, otp_code: str, user_name: str = None
) -> EmailData:
    """
    Create password reset OTP email content using template.

    Args:
        user_email: User's email address
        otp_code: 6-digit OTP code
        user_name: User's name (optional)

    Returns:
        EmailData object with subject and html_content
    """
    username = user_name or user_email.split("@")[0]
    subject = f"{settings.PROJECT_NAME} - Password Reset Code"

    html_content = render_email_template(
        template_name="password_reset.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": user_email,
            "otp_code": otp_code,
        },
    )

    return EmailData(html_content=html_content, subject=subject)
