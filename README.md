# Cup Streaming API

A modern, high-performance video streaming platform built with FastAPI, featuring user authentication, content management, and real-time video streaming capabilities.

## 🚀 Features

- **User Authentication & Management**: JWT-based authentication with user registration, login, and profile management
- **Video Upload & Streaming**: Support for multiple video formats with AWS S3 integration
- **Content Management**: Organize videos, TV shows, and series with metadata
- **Social Features**: User interactions, reviews, and content discovery
- **Analytics & Metrics**: Track views, engagement, and user behavior
- **Background Processing**: Celery-based task queue for video processing
- **API Documentation**: Interactive Swagger UI and ReDoc documentation
- **Database Migrations**: Alembic for database schema management
- **Code Quality**: Pre-commit hooks, linting, and type checking

## 🏗️ Project Structure

```
Cup_Streaming/
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   ├── env.py                 # Alembic environment configuration
│   └── script.py.mako         # Migration template
├── app/                       # Main application package
│   ├── api/                   # API routes and endpoints
│   │   └── v1/               # API version 1
│   │       ├── api.py        # Main API router
│   │       └── endpoints/    # Individual endpoint modules
│   │           ├── auth.py   # Authentication endpoints
│   │           ├── content.py # Content management endpoints
│   │           └── users.py  # User management endpoints
│   ├── core/                 # Core application components
│   │   ├── auth.py           # Authentication utilities
│   │   ├── celery_app.py     # Celery configuration
│   │   ├── config.py         # Application settings
│   │   ├── database.py       # Database configuration
│   │   ├── deps.py           # Dependency injection
│   │   └── messages.py       # Application messages
│   ├── models/               # SQLAlchemy models
│   │   ├── base.py           # Base model class
│   │   ├── content.py        # Content-related models
│   │   ├── token.py          # Token models
│   │   ├── user.py           # User models
│   │   └── verification.py   # Email verification models
│   ├── schemas/              # Pydantic schemas
│   │   ├── auth.py           # Authentication schemas
│   │   ├── content.py        # Content schemas
│   │   └── user.py           # User schemas
│   ├── tasks/                # Celery background tasks
│   │   └── email_tasks.py    # Email-related tasks
│   └── utils/                # Utility functions
│       ├── auth_utils.py     # Authentication utilities
│       ├── content_utils.py  # Content processing utilities
│       ├── email_utils.py    # Email utilities
│       └── token_utils.py    # Token utilities
├── fixtures/                  # Database fixtures and sample data
│   ├── content/              # Content fixtures
│   ├── episodes/             # Episode fixtures
│   ├── genres/               # Genre fixtures
│   ├── interactions/         # User interaction fixtures
│   └── users/                # User fixtures
├── static/                   # Static files
│   └── swagger-ui.html       # Custom Swagger UI
├── alembic.ini              # Alembic configuration
├── celery_worker.py         # Celery worker entry point
├── docker-compose.yml       # Docker Compose configuration
├── docker-compose.dev.yml   # Development Docker Compose
├── docker-compose.prod.yml  # Production Docker Compose
├── Dockerfile               # Docker configuration
├── entrypoint.sh            # Docker entrypoint script
├── main.py                  # FastAPI application entry point
├── Makefile                 # Development commands
├── pyproject.toml           # Project configuration and dependencies
├── requirements.txt         # Python dependencies
├── seed_database.py         # Database seeding script
└── README.md                # This file
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- Redis 6 or higher
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Cup_Streaming
```

### 2. Create Virtual Environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Or install development dependencies
make install-dev
```

### 4. Environment Configuration

Create a `.env` file in the project root with the following variables:

```bash
# Database Configuration
DB_NAME=cup_streaming_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Security
DEBUG=true
HOST=0.0.0.0
PORT=8000
BASE_URL=http://localhost:8000
# Security
SECRET_KEY=cup-streaming

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET=your-s3-bucket

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_TLS=true
FROM_EMAIL=your_email@gmail.com
FROM_NAME=Cup Streaming
EMAILS_ENABLED=false

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
```

### 5. Database Setup

```bash
# Create PostgreSQL database
createdb cup_streaming_db

# Run database migrations
alembic upgrade head

# Seed the database with sample data (optional)
python seed_database.py
```

## 🚀 Running the Application

### Development Mode

```bash
# Using Makefile (recommended)
make run-dev

# Or directly with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python main.py
```

### Production Mode

```bash
# Using uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Using Docker
docker-compose up -d
```

### Background Services

```bash
# Start Redis (if not using Docker)
redis-server

# Start Celery worker
make celery-worker

# Start Celery Flower (monitoring)
make celery-flower

# Start Celery beat (scheduler)
make celery-beat
```

## 📋 Available Commands

The project includes a comprehensive Makefile with the following commands:

```bash
# Setup and Installation
make setup              # Complete development environment setup
make install            # Install production dependencies
make install-dev        # Install development dependencies

# Running the Application
make run                # Run the FastAPI application
make run-dev            # Run in development mode with auto-reload
make dev-all            # Start all development services

# Code Quality
make format             # Format code with black and isort
make lint               # Run linting checks
make check              # Run all checks (linting and tests)
make pre-commit         # Run pre-commit hooks on all files

# Testing
make test               # Run tests with pytest

# Background Services
make celery-worker      # Start Celery worker
make celery-flower      # Start Celery Flower monitoring
make celery-beat        # Start Celery beat scheduler
make redis-start        # Start Redis server

# Utilities
make clean              # Clean up temporary files
make help               # Show all available commands
```

## 🔧 Pre-commit Setup

Pre-commit hooks ensure code quality and consistency. Here's how to set them up:

### 1. Install Pre-commit

```bash
# Install pre-commit in your virtual environment
pip install pre-commit

# Or install development dependencies (includes pre-commit)
make install-dev
```

### 2. Install Pre-commit Hooks

```bash
# Install pre-commit hooks
make pre-commit-install

# Or manually
pre-commit install
```

### 3. Run Pre-commit on All Files

```bash
# Run pre-commit on all files
make pre-commit

# Or manually
pre-commit run --all-files
```

### Pre-commit Configuration

The project includes the following pre-commit hooks:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security linting
- **ruff**: Fast Python linter

## 📚 API Documentation

Once the application is running, you can access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc


## 🐳 Docker Support

The project includes comprehensive Docker configuration:

```bash
# Development with Docker
docker-compose -f docker-compose.dev.yml up -d

# Production with Docker
docker-compose -f docker-compose.prod.yml up -d

# Build custom image
docker build -t cup-streaming-api .
```


## 🔍 Code Quality

The project enforces high code quality standards:

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
mypy app/

# Run security checks
bandit -r app/

# Run all quality checks
make check
```

## 📊 Database Management

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

## 🚀 Deployment

### Environment Variables

Ensure all required environment variables are set in your production environment:

- Database credentials
- Secret keys
- AWS credentials (if using S3)
- Email configuration
- Redis configuration

### Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Configure production database
- [ ] Set up Redis instance
- [ ] Configure AWS S3 (if using)
- [ ] Set up email service
- [ ] Configure CORS origins
- [ ] Set up monitoring and logging
- [ ] Run database migrations
- [ ] Start background workers
