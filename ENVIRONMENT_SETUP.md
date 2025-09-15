# Environment Configuration Setup

This document explains how to set up environment variables for the Cup Streaming project.

## Overview

All configuration values have been moved to environment variables for better security, flexibility, and deployment practices. No sensitive information is hardcoded in the Django settings.

## Quick Start

1. **Copy the development environment template:**
   ```bash
   cp env.development .env
   ```

2. **Update the `.env` file with your actual values** (especially the SECRET_KEY for production)

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

## Environment Files

### `env.example`
Complete documentation of all environment variables with descriptions. Use this as a reference for what variables are available.

### `env.development`
Development-ready environment configuration with safe defaults. Copy this to `.env` for local development.

### `.env` (Your local file)
Your personal environment configuration. **This file is ignored by git and should never be committed.**

## Required Environment Variables

### Core Django Settings
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `SITE_ID`: Django site ID (usually 1)

### Database Configuration
- `DB_NAME`: PostgreSQL database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)

### Email Configuration
- `EMAIL_BACKEND`: Email backend class
- `EMAIL_HOST`: SMTP server host
- `EMAIL_PORT`: SMTP server port
- `EMAIL_USE_TLS`: Use TLS for email (True/False)
- `EMAIL_HOST_USER`: SMTP username
- `EMAIL_HOST_PASSWORD`: SMTP password
- `DEFAULT_FROM_EMAIL`: Default from email address

### JWT Settings
- `JWT_ACCESS_TOKEN_LIFETIME_MINUTES`: Access token lifetime in minutes
- `JWT_REFRESH_TOKEN_LIFETIME_DAYS`: Refresh token lifetime in days
- `JWT_ROTATE_REFRESH_TOKENS`: Rotate refresh tokens (True/False)
- `JWT_BLACKLIST_AFTER_ROTATION`: Blacklist old tokens (True/False)
- `JWT_ALGORITHM`: JWT algorithm (default: HS256)

### API & CORS Settings
- `DRF_PAGE_SIZE`: Default pagination page size
- `DRF_ANON_THROTTLE_RATE`: Anonymous user rate limit
- `DRF_USER_THROTTLE_RATE`: Authenticated user rate limit
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
- `CORS_ALLOW_CREDENTIALS`: Allow credentials in CORS (True/False)

### AWS Configuration (Optional)
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_S3_REGION_NAME`: S3 region
- `AWS_S3_BUCKET_NAME`: S3 bucket name
- `AWS_MEDIACONVERT_ENDPOINT`: MediaConvert endpoint URL
- `AWS_MEDIACONVERT_ROLE_ARN`: MediaConvert IAM role ARN
- `AWS_MEDIACONVERT_QUEUE_ARN`: MediaConvert queue ARN

### Celery Configuration
- `CELERY_BROKER_URL`: Celery broker URL (Redis)
- `CELERY_RESULT_BACKEND`: Celery result backend URL
- `CELERY_ACCEPT_CONTENT`: Accepted content types
- `CELERY_TASK_SERIALIZER`: Task serializer format
- `CELERY_RESULT_SERIALIZER`: Result serializer format

### Social Authentication (Optional)
- `GOOGLE_OAUTH2_CLIENT_ID`: Google OAuth2 client ID
- `GOOGLE_OAUTH2_CLIENT_SECRET`: Google OAuth2 client secret
- `FACEBOOK_APP_ID`: Facebook app ID
- `FACEBOOK_APP_SECRET`: Facebook app secret

## Environment-Specific Configurations

### Development
- Use `env.development` as a starting point
- Set `DEBUG=True`
- Use local database and Redis
- Use console email backend for testing
- Use development-friendly CORS settings

### Staging
- Set `DEBUG=False`
- Use staging database
- Configure real email settings
- Use staging AWS resources
- Set appropriate security headers

### Production
- **Generate a new SECRET_KEY**
- Set `DEBUG=False`
- Configure production database
- Set up production email service
- Configure production AWS resources
- Enable all security settings
- Set strict CORS policies

## Security Best Practices

1. **Never commit `.env` files** - They are already in `.gitignore`
2. **Generate unique SECRET_KEY for each environment**
3. **Use environment-specific databases**
4. **Rotate secrets regularly**
5. **Use strong passwords and keys**
6. **Limit CORS origins in production**
7. **Enable all security headers in production**

## Generating a Secret Key

For production, generate a new secret key:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Or use online generator: https://djecrety.ir/

## Troubleshooting

### Missing Environment Variables
If you get errors about missing environment variables, check that:
1. Your `.env` file exists
2. The variable name matches exactly (case-sensitive)
3. There are no spaces around the `=` sign
4. String values don't need quotes unless they contain special characters

### Database Connection Issues
1. Ensure PostgreSQL is running
2. Check database credentials in `.env`
3. Verify database exists: `createdb cup_streaming_db`
4. Test connection manually

### Email Configuration Issues
1. For Gmail, use app passwords instead of regular passwords
2. Enable 2FA and generate an app-specific password
3. For development, use console backend to see emails in terminal

## Production Deployment

When deploying to production:

1. **Set environment variables in your hosting platform** (Heroku, AWS, etc.)
2. **Never use the development `.env` file in production**
3. **Use platform-specific environment variable management**
4. **Configure proper database and Redis instances**
5. **Set up monitoring and logging**

## Example Production Environment Setup

```bash
# On your production server or platform
export SECRET_KEY="your-production-secret-key"
export DEBUG="False"
export ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
export DB_HOST="your-production-db-host"
export DB_PASSWORD="your-production-db-password"
# ... other production values
```
