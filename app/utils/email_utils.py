"""
Email utility functions for sending emails.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import settings


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
) -> tuple[str, str]:
    """
    Create password reset email content.

    Args:
        user_email: User's email address
        reset_token: Password reset token
        user_name: User's name (optional)

    Returns:
        Tuple of (subject, html_content)
    """
    display_name = user_name or user_email.split("@")[0]

    subject = "Password Reset Request - Cup Streaming"

    # Simple HTML email template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Password Reset</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4f46e5; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9fafb; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #4f46e5; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Cup Streaming</h1>
            </div>
            <div class="content">
                <h2>Password Reset Request</h2>
                <p>Hello {display_name},</p>
                <p>We received a request to reset your password for your Cup Streaming account.</p>
                <p>To reset your password, please use the following token:</p>
                <div style="background-color: #e5e7eb; padding: 15px; border-radius: 6px; font-family: monospace; font-size: 18px; text-align: center; margin: 20px 0;">
                    {reset_token}
                </div>
                <p>This token will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS} hour(s).</p>
                <p>If you did not request this password reset, please ignore this email.</p>
                <p>For security reasons, do not share this token with anyone.</p>
            </div>
            <div class="footer">
                <p>This email was sent from Cup Streaming. If you have any questions, please contact support.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return subject, html_content


def create_email_verification_email(
    user_email: str, verification_token: str, user_name: str = None
) -> tuple[str, str]:
    """
    Create email verification email content.

    Args:
        user_email: User's email address
        verification_token: Email verification token
        user_name: User's name (optional)

    Returns:
        Tuple of (subject, html_content)
    """
    display_name = user_name or user_email.split("@")[0]

    subject = "Verify Your Email - Cup Streaming"

    # Simple HTML email template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Email Verification</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4f46e5; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9fafb; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #4f46e5; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
            .footer {{ padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Cup Streaming</h1>
            </div>
            <div class="content">
                <h2>Verify Your Email Address</h2>
                <p>Hello {display_name},</p>
                <p>Welcome to Cup Streaming! Please verify your email address to complete your account setup.</p>
                <p>To verify your email, please use the following token:</p>
                <div style="background-color: #e5e7eb; padding: 15px; border-radius: 6px; font-family: monospace; font-size: 18px; text-align: center; margin: 20px 0;">
                    {verification_token}
                </div>
                <p>This token will expire in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} hour(s).</p>
                <p>If you did not create an account with us, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>This email was sent from Cup Streaming. If you have any questions, please contact support.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return subject, html_content
