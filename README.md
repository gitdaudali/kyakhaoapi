# Cup Streaming API

A modern, high-performance video streaming platform built with FastAPI, featuring comprehensive user management, content streaming, subscription billing, monetization, and FAQ management capabilities.

## 🚀 Features

### Core Features
- **User Authentication & Management**: JWT-based authentication with user registration, login, and profile management
- **Video Upload & Streaming**: Support for multiple video formats with AWS S3 integration
- **Content Management**: Organize videos, TV shows, and series with metadata
- **Social Features**: User interactions, reviews, and content discovery
- **Analytics & Metrics**: Track views, engagement, and user behavior
- **Background Processing**: Celery-based task queue for video processing

### Advanced Features
- **Subscription Management**: Complete subscription system with Stripe integration
- **Monetization**: Ad campaigns, revenue tracking, and performance analytics
- **User Policies**: Policy management and user acceptance tracking
- **FAQ System**: Comprehensive FAQ management with admin controls
- **Enhanced Error Handling**: Standardized API responses with detailed error messages
- **Rate Limiting**: Built-in rate limiting and retry mechanisms
- **Client Validation**: Device and app version validation

### Technical Features
- **API Documentation**: Interactive Swagger UI and ReDoc documentation
- **Database Migrations**: Alembic for database schema management
- **Standardized Responses**: Unified API response format across all endpoints
- **Code Quality**: Pre-commit hooks, linting, and type checking
- **Security**: Enhanced security with header validation and OAuth support

## 🏗️ Project Structure

```
Cup_Streaming/
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   ├── env.py                 # Alembic environment configuration
│   └── script.py.mako         # Migration template
├── app/                       # Main application package
│   ├── api/                   # API routes and endpoints
│   │   ├── v1/               # API version 1
│   │   │   ├── api.py        # Main API router
│   │   │   ├── admin/        # Admin API endpoints
│   │   │   │   ├── api.py    # Admin router
│   │   │   │   └── endpoints/ # Admin endpoint modules
│   │   │   │       ├── content.py # Content admin endpoints
│   │   │   │       ├── faq.py     # FAQ admin endpoints
│   │   │   │       ├── genre.py   # Genre admin endpoints
│   │   │   │       ├── monetization.py # Monetization admin endpoints
│   │   │   │       ├── people.py  # People admin endpoints
│   │   │   │       ├── policy.py  # Policy admin endpoints
│   │   │   │       ├── streaming.py # Streaming admin endpoints
│   │   │   │       ├── upload.py  # Upload admin endpoints
│   │   │   │       └── user.py   # User admin endpoints
│   │   │   └── endpoints/    # Public endpoint modules
│   │   │       ├── auth.py   # Authentication endpoints
│   │   │       ├── content.py # Content management endpoints
│   │   │       ├── faq.py    # FAQ endpoints
│   │   │       ├── policy.py # Policy endpoints
│   │   │       ├── streaming.py # Streaming endpoints
│   │   │       ├── stripe.py # Stripe payment endpoints
│   │   │       ├── subscriptions.py # Subscription endpoints
│   │   │       ├── user_policy.py # User policy endpoints
│   │   │       └── users.py  # User management endpoints
│   ├── core/                 # Core application components
│   │   ├── auth.py           # Authentication utilities
│   │   ├── celery_app.py     # Celery configuration
│   │   ├── config.py         # Application settings
│   │   ├── database.py       # Database configuration
│   │   ├── deps.py           # Dependency injection
│   │   ├── messages.py       # Application messages
│   │   └── response_handler.py # Standardized response handling
│   ├── middleware/           # Custom middleware
│   │   └── rate_limit.py     # Rate limiting middleware
│   ├── models/               # SQLAlchemy models
│   │   ├── base.py           # Base model class
│   │   ├── content.py        # Content-related models
│   │   ├── faq.py           # FAQ models
│   │   ├── monetization.py   # Monetization models
│   │   ├── policy.py         # Policy models
│   │   ├── streaming.py      # Streaming models
│   │   ├── subscription.py   # Subscription models
│   │   ├── token.py          # Token models
│   │   ├── user.py           # User models
│   │   └── verification.py   # Email verification models
│   ├── schemas/              # Pydantic schemas
│   │   ├── admin.py          # Admin schemas
│   │   ├── auth.py           # Authentication schemas
│   │   ├── content.py        # Content schemas
│   │   ├── faq.py           # FAQ schemas
│   │   ├── google_oauth.py   # Google OAuth schemas
│   │   ├── policy.py         # Policy schemas
│   │   ├── streaming.py      # Streaming schemas
│   │   ├── subscription.py   # Subscription schemas
│   │   ├── user_policy.py    # User policy schemas
│   │   └── user.py           # User schemas
│   ├── tasks/                # Celery background tasks
│   │   └── email_tasks.py    # Email-related tasks
│   └── utils/                # Utility functions
│       ├── admin/            # Admin utilities
│       │   ├── monetization_utils.py # Monetization utilities
│       │   └── policy_utils.py # Policy utilities
│       ├── auth_utils.py     # Authentication utilities
│       ├── content_utils.py  # Content processing utilities
│       ├── email_utils.py    # Email utilities
│       ├── google_oauth_utils.py # Google OAuth utilities
│       ├── policy_utils.py   # Policy utilities
│       ├── retry_helper.py   # Retry mechanism utilities
│       ├── s3_utils.py       # AWS S3 utilities
│       ├── streaming_utils.py # Streaming utilities
│       ├── subscription_utils.py # Subscription utilities
│       ├── template_utils.py # Template utilities
│       ├── token_utils.py    # Token utilities
│       ├── user_policy_utils.py # User policy utilities
│       ├── user_utils.py     # User utilities
│       └── video_processing.py # Video processing utilities
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

## 🔗 API Endpoints

### Authentication & User Management (`/api/v1/auth`)

#### User Registration & Login
- **POST** `/register` - Register new user account with email verification
  - **Request Body**: `{email, password}`
  - **Response**: Success message with OTP sent for email verification
  - **Features**: Email validation, password hashing, OTP generation

- **POST** `/login` - Authenticate user and get access tokens
  - **Request Body**: `{email, password, remember_me}`
  - **Response**: User data with access and refresh tokens
  - **Features**: JWT token generation, device tracking, account status validation

- **POST** `/refresh` - Refresh access token using refresh token
  - **Request Body**: `{refresh_token}`
  - **Response**: New access and refresh token pair
  - **Features**: Token rotation, device validation

- **POST** `/logout` - Logout user and revoke tokens
  - **Request Body**: `{refresh_token, logout_all_devices}`
  - **Response**: Logout confirmation with device count
  - **Features**: Single device or all devices logout

#### Password Management
- **POST** `/password/reset` - Request password reset via email
  - **Request Body**: `{email}`
  - **Response**: OTP sent confirmation
  - **Features**: OTP generation, email sending

- **POST** `/password/reset/confirm` - Confirm password reset with OTP
  - **Request Body**: `{email, otp_code, new_password, new_password_confirm, logout_all_devices}`
  - **Response**: Password reset confirmation
  - **Features**: OTP validation, password strength check, token revocation

- **POST** `/change-password` - Change password for authenticated user
  - **Request Body**: `{current_password, new_password}`
  - **Response**: Password change confirmation
  - **Features**: Current password verification, secure password update

#### Email Verification
- **POST** `/verify-otp` - Verify email address with OTP
  - **Request Body**: `{email, otp_code}`
  - **Response**: Email verification confirmation
  - **Features**: OTP validation, account activation

#### Social Authentication
- **POST** `/social/google` - Google OAuth authentication
  - **Request Body**: `{access_token}`
  - **Response**: User data with tokens and new user flag
  - **Features**: Google token verification, account linking, new user creation

#### User Information
- **GET** `/me` - Get current user information
  - **Headers**: `Authorization: Bearer <token>`
  - **Response**: Complete user profile data
  - **Features**: JWT token validation, user data retrieval

- **GET** `/token-info` - Get current token information
  - **Headers**: `Authorization: Bearer <token>`
  - **Response**: Token metadata and expiration details
  - **Features**: Token validation, expiration info

### User Profile Management (`/api/v1/users`)

#### Profile Updates
- **PATCH** `/profile` - Update user profile with optional avatar
  - **Request Body**: `FormData {first_name?, last_name?, avatar?}`
  - **Response**: Updated profile data
  - **Features**: File upload to S3, profile validation, avatar management

#### Search History Management
- **POST** `/search-history` - Add search query to history
  - **Request Body**: `{search_query}`
  - **Response**: Search history entry created
  - **Features**: Duplicate handling, search count tracking

- **GET** `/search-history` - Get paginated search history
  - **Query Params**: `page, size`
  - **Response**: Paginated search history list
  - **Features**: Pagination, recent searches first

- **GET** `/search-history/recent` - Get recent searches for autocomplete
  - **Query Params**: `limit`
  - **Response**: Recent search suggestions
  - **Features**: Autocomplete support, configurable limit

- **DELETE** `/search-history/{search_history_id}` - Delete specific search entry
  - **Response**: Deletion confirmation
  - **Features**: Individual entry removal

- **DELETE** `/search-history` - Clear all search history
  - **Response**: Bulk deletion confirmation
  - **Features**: Complete history cleanup

### Content Management (`/api/v1/content`)

#### Content Discovery
- **GET** `/discovery` - Get content discovery data with sections
  - **Query Params**: `include_featured, include_trending, include_most_reviewed, include_new_releases, page, size, content_type, genre_id`
  - **Response**: Featured, trending, most reviewed, and new releases sections
  - **Features**: Multiple content sections, genre filtering, pagination

- **GET** `/search` - Search content with minimal response
  - **Query Params**: `q, page, size, content_type, genre_id, year, rating_min, rating_max, sort_by, sort_order`
  - **Response**: Ultra-minimal content list for fast search
  - **Features**: Full-text search, advanced filtering, sorting

#### Content Lists
- **GET** `/` - Get paginated content list
  - **Query Params**: `page, size, content_type, genre_id, year, rating_min, rating_max, status, sort_by, sort_order`
  - **Response**: Paginated content list with filtering
  - **Features**: Advanced filtering, sorting, pagination

- **GET** `/featured` - Get featured content
  - **Query Params**: `page, size, content_type, genre_id, sort_by, sort_order`
  - **Response**: Featured content list
  - **Features**: Featured content filtering, pagination

- **GET** `/trending` - Get trending content
  - **Query Params**: `page, size, content_type, genre_id, sort_by, sort_order`
  - **Response**: Trending content list
  - **Features**: Trending algorithm, pagination

- **GET** `/most-reviewed-last-month` - Get most reviewed content from last month
  - **Query Params**: `page, size, min_rating, min_reviews, content_type, genre_id`
  - **Response**: Most reviewed content list
  - **Features**: Time-based filtering, review count filtering

#### Content Details
- **GET** `/{content_id}` - Get detailed content information
  - **Response**: Complete content details with cast, crew, genres
  - **Features**: Full content metadata, relationship data

#### Genre Management
- **GET** `/genres/` - Get genres list
  - **Query Params**: `page, size, is_active, search, sort_by, sort_order`
  - **Response**: Paginated genres list
  - **Features**: Genre filtering, search, pagination

- **GET** `/genres/with-movies` - Get genres with first 4 movies
  - **Query Params**: `page, size, is_active, search, sort_by, sort_order`
  - **Response**: Genres with sample movies for cards
  - **Features**: Genre cards with movie previews

- **GET** `/genres/{genre_id}` - Get genre by ID
  - **Response**: Detailed genre information
  - **Features**: Complete genre metadata

- **GET** `/genres/slug/{slug}` - Get genre by slug
  - **Response**: Detailed genre information
  - **Features**: SEO-friendly genre access

#### Cast & Crew
- **GET** `/{content_id}/cast` - Get content cast
  - **Query Params**: `page, size, is_main_cast, search, department, sort_by, sort_order`
  - **Response**: Paginated cast list
  - **Features**: Cast filtering, department filtering, search

- **GET** `/{content_id}/crew` - Get content crew
  - **Query Params**: `page, size, department, job_title, search, sort_by, sort_order`
  - **Response**: Paginated crew list
  - **Features**: Crew filtering, job title filtering, search

- **GET** `/{content_id}/cast-crew` - Get both cast and crew
  - **Response**: Combined cast and crew data
  - **Features**: Single request for complete credits

#### Reviews System
- **GET** `/{content_id}/reviews` - Get content reviews
  - **Query Params**: `page, size, rating_min, rating_max, is_featured, language, search, user_id, sort_by, sort_order`
  - **Response**: Paginated reviews list
  - **Features**: Advanced review filtering, rating filters, user filtering

- **GET** `/reviews/{review_id}` - Get specific review
  - **Response**: Detailed review information
  - **Features**: Individual review access

- **POST** `/{content_id}/reviews` - Create content review
  - **Request Body**: `{title, content, rating, language, is_featured}`
  - **Response**: Created review data
  - **Features**: One review per user per content, rating validation

- **PUT** `/reviews/{review_id}` - Update review
  - **Request Body**: `{title?, content?, rating?, language?, is_featured?}`
  - **Response**: Updated review data
  - **Features**: User can only update own reviews

- **DELETE** `/reviews/{review_id}` - Delete review
  - **Response**: Deletion confirmation
  - **Features**: User can only delete own reviews

- **GET** `/{content_id}/reviews/stats` - Get review statistics
  - **Response**: Comprehensive review statistics
  - **Features**: Rating distribution, review counts, averages

#### People Management
- **GET** `/people/{person_id}` - Get person details
  - **Response**: Complete person information
  - **Features**: Person metadata, biography, filmography

### Streaming (`/api/v1/streaming`)

#### Streaming Channels
- **GET** `/channels` - Get streaming channels
  - **Query Params**: `page, size, category, language, country, quality, search, sort_by, sort_order`
  - **Response**: Paginated streaming channels list
  - **Features**: Channel filtering, quality filtering, search

### Subscriptions (`/api/v1/subscriptions`)

#### Subscription Management
- **GET** `/my-subscription` - Get current user's subscription info
  - **Response**: Complete subscription information
  - **Features**: Active subscription details, billing info

- **GET** `/my-subscriptions` - Get all user subscriptions
  - **Response**: List of all user subscriptions
  - **Features**: Subscription history

- **GET** `/active` - Get active subscription
  - **Response**: Currently active subscription with payments
  - **Features**: Active subscription details

- **POST** `/create` - Create new subscription
  - **Request Body**: `{plan, price_id, payment_method_id}`
  - **Response**: Created subscription data
  - **Features**: Subscription creation, payment processing

- **POST** `/cancel/{subscription_id}` - Cancel subscription
  - **Request Body**: `{cancel_at_period_end}`
  - **Response**: Cancellation confirmation
  - **Features**: Immediate or end-of-period cancellation

- **PUT** `/update/{subscription_id}` - Update subscription plan
  - **Request Body**: `{new_price_id, proration_behavior}`
  - **Response**: Updated subscription data
  - **Features**: Plan changes, proration handling

- **GET** `/check-access` - Check premium access
  - **Response**: Access status and plan details
  - **Features**: Premium feature access validation

### Payment Processing (`/api/v1/stripe`)

#### Checkout & Payments
- **GET** `/` - Display subscription purchase form
  - **Response**: HTML form for subscription purchase
  - **Features**: User-friendly purchase interface

- **POST** `/checkout` - Create Stripe checkout session
  - **Response**: Checkout session URL
  - **Features**: Stripe integration, secure payment processing

- **POST** `/checkout-simple` - Create simple checkout (testing)
  - **Request Body**: `{user_email, plan_type}`
  - **Response**: Checkout URL
  - **Features**: Testing without authentication, existing subscription check

- **GET** `/success` - Handle successful payment
  - **Query Params**: `session_id`
  - **Response**: Success page with subscription details
  - **Features**: Payment verification, subscription creation

- **GET** `/cancel` - Handle canceled payment
  - **Response**: Cancellation message
  - **Features**: Payment cancellation handling

- **POST** `/create-subscription` - Manually create subscription
  - **Request Body**: `{user_email, stripe_session_id}`
  - **Response**: Subscription creation confirmation
  - **Features**: Manual subscription creation for testing

- **GET** `/config` - Get Stripe publishable key
  - **Response**: Stripe configuration for frontend
  - **Features**: Frontend integration support

- **POST** `/webhook` - Handle Stripe webhooks
  - **Request Body**: Stripe webhook payload
  - **Response**: Webhook processing confirmation
  - **Features**: Real-time payment updates, subscription status sync

### User Interactions

#### Favorites (`/api/v1/favorites`)
- **GET** `/` - Get user's favorite content
  - **Query Params**: `period`
  - **Response**: Favorites separated by movies and TV shows
  - **Features**: Content categorization, period filtering

- **POST** `/{content_id}` - Add content to favorites
  - **Response**: Addition confirmation
  - **Features**: Duplicate prevention, content validation

- **DELETE** `/{content_id}` - Remove content from favorites
  - **Response**: Removal confirmation
  - **Features**: Safe removal, content validation

#### Watchlist (`/api/v1/watchlist`)
- **GET** `/` - Get user's watchlist
  - **Query Params**: `period`
  - **Response**: Watchlist separated by movies and TV shows
  - **Features**: Content categorization, period filtering

- **POST** `/{content_id}` - Add content to watchlist
  - **Response**: Addition confirmation
  - **Features**: Duplicate prevention, content validation

- **DELETE** `/{content_id}` - Remove content from watchlist
  - **Response**: Removal confirmation
  - **Features**: Safe removal, content validation

#### Continue Watching (`/api/v1/continue-watching`)
- **GET** `/` - Get continue watching content
  - **Response**: Content user was watching
  - **Features**: Resume watching functionality

#### Recently Watched (`/api/v1/recently-watched`)
- **GET** `/` - Get recently watched content
  - **Response**: Recently watched content list
  - **Features**: Watch history tracking

#### Watch History (`/api/v1/watch-history`)
- **GET** `/` - Get detailed watch history
  - **Response**: Complete watch history with timestamps
  - **Features**: Detailed viewing tracking

#### Recommendations (`/api/v1/recommendations`)
- **GET** `/` - Get personalized recommendations
  - **Response**: Recommended content based on user preferences
  - **Features**: AI-powered recommendations

#### Home Screen (`/api/v1/home`)
- **GET** `/` - Get home screen content
  - **Response**: Personalized home screen data
  - **Features**: Customized content discovery

### FAQ System (`/api/v1/faq`)

#### FAQ Management
- **GET** `/` - Get paginated FAQ list
  - **Query Params**: `page, size, search, category, featured_only, sort_by, sort_order`
  - **Response**: Paginated FAQ list
  - **Features**: Search, category filtering, featured FAQs

- **GET** `/{faq_id}` - Get specific FAQ
  - **Response**: Detailed FAQ information
  - **Features**: View count tracking, detailed FAQ access

- **GET** `/categories/list` - Get FAQ categories
  - **Response**: List of available FAQ categories
  - **Features**: Category navigation

- **GET** `/featured/list` - Get featured FAQs
  - **Query Params**: `page, size, search, category, sort_by, sort_order`
  - **Response**: Featured FAQ list
  - **Features**: Featured content highlighting

### User Policies (`/api/v1/policies`)

#### Policy Management
- **GET** `/` - Get active user policies
  - **Response**: Current active policies
  - **Features**: Policy versioning, acceptance tracking

- **POST** `/accept` - Accept user policy
  - **Request Body**: `{policy_id, version}`
  - **Response**: Acceptance confirmation
  - **Features**: Policy acceptance tracking, version validation

### Statistics & Analytics (`/api/v1/stats`)

#### Analytics
- **GET** `/` - Get platform statistics
  - **Response**: Platform-wide statistics
  - **Features**: Content metrics, user metrics, engagement data

### Content Categories (`/api/v1/content-categories`)

#### Category Management
- **GET** `/` - Get content categories
  - **Response**: Available content categories
  - **Features**: Category navigation, content organization

### User Profiles (`/api/v1/profiles`)

#### Profile Management
- **GET** `/` - Get user profiles
  - **Response**: User profile information
  - **Features**: Profile customization, user preferences

### Account Management (`/api/v1/account`)

#### Account Operations
- **GET** `/` - Get account information
  - **Response**: Complete account details
  - **Features**: Account overview, settings access

---

## 🔧 Admin API Endpoints

### Admin Content Management (`/api/v1/admin/content`)

#### Content CRUD Operations
- **POST** `/` - Create new content
  - **Request Body**: Content creation data
  - **Response**: Created content details
  - **Features**: Content creation, validation, metadata management

- **GET** `/` - Get paginated content list for admin
  - **Query Params**: Advanced filtering and pagination
  - **Response**: Admin content list with full metadata
  - **Features**: Admin-specific filtering, bulk operations

- **GET** `/{content_id}` - Get content details for admin
  - **Response**: Complete content information for editing
  - **Features**: Full content metadata, admin-specific data

- **PUT** `/{content_id}` - Update content
  - **Request Body**: Updated content data
  - **Response**: Updated content details
  - **Features**: Content updates, validation, metadata management

- **DELETE** `/{content_id}` - Delete content
  - **Response**: Deletion confirmation
  - **Features**: Soft delete, content removal

#### TV Show Management
- **GET** `/tv-shows` - Get TV shows for admin
  - **Response**: TV shows list with admin data
  - **Features**: TV show specific management

- **POST** `/tv-shows` - Create TV show
  - **Request Body**: TV show creation data
  - **Response**: Created TV show details
  - **Features**: TV show creation, season/episode management

#### Content Status Management
- **POST** `/{content_id}/publish` - Publish content
  - **Response**: Publishing confirmation
  - **Features**: Content publishing, status updates

- **POST** `/{content_id}/unpublish` - Unpublish content
  - **Response**: Unpublishing confirmation
  - **Features**: Content unpublishing, status updates

- **POST** `/{content_id}/feature` - Toggle featured status
  - **Response**: Feature status update
  - **Features**: Featured content management

- **POST** `/{content_id}/trending` - Toggle trending status
  - **Response**: Trending status update
  - **Features**: Trending content management

### Admin User Management (`/api/v1/admin/users`)

#### User CRUD Operations
- **POST** `/` - Create new user
  - **Request Body**: User creation data
  - **Response**: Created user details
  - **Features**: User creation, role assignment

- **GET** `/` - Get paginated users list
  - **Query Params**: User filtering and pagination
  - **Response**: Admin users list
  - **Features**: User management, role filtering

- **GET** `/{user_id}` - Get user details for admin
  - **Response**: Complete user information
  - **Features**: User details, activity tracking

- **PUT** `/{user_id}` - Update user
  - **Request Body**: Updated user data
  - **Response**: Updated user details
  - **Features**: User updates, role management

- **DELETE** `/{user_id}` - Delete user
  - **Response**: Deletion confirmation
  - **Features**: User removal, data cleanup

#### User Status Management
- **POST** `/{user_id}/activate` - Activate user
  - **Response**: Activation confirmation
  - **Features**: User activation, status updates

- **POST** `/{user_id}/suspend` - Suspend user
  - **Response**: Suspension confirmation
  - **Features**: User suspension, access control

- **POST** `/{user_id}/role` - Update user role
  - **Request Body**: `{role}`
  - **Response**: Role update confirmation
  - **Features**: Role management, permission updates

### Admin FAQ Management (`/api/v1/admin/faq`)

#### FAQ CRUD Operations
- **POST** `/` - Create new FAQ
  - **Request Body**: FAQ creation data
  - **Response**: Created FAQ details
  - **Features**: FAQ creation, categorization

- **GET** `/` - Get paginated FAQ list for admin
  - **Query Params**: FAQ filtering and pagination
  - **Response**: Admin FAQ list
  - **Features**: FAQ management, status filtering

- **GET** `/{faq_id}` - Get FAQ details for admin
  - **Response**: Complete FAQ information
  - **Features**: FAQ editing, metadata access

- **PUT** `/{faq_id}` - Update FAQ
  - **Request Body**: Updated FAQ data
  - **Response**: Updated FAQ details
  - **Features**: FAQ updates, content management

- **DELETE** `/{faq_id}` - Delete FAQ
  - **Response**: Deletion confirmation
  - **Features**: FAQ removal, soft delete

### Admin Genre Management (`/api/v1/admin/genres`)

#### Genre CRUD Operations
- **POST** `/` - Create new genre
  - **Request Body**: Genre creation data
  - **Response**: Created genre details
  - **Features**: Genre creation, slug generation

- **GET** `/` - Get paginated genres list
  - **Query Params**: Genre filtering and pagination
  - **Response**: Admin genres list
  - **Features**: Genre management, status filtering

- **GET** `/{genre_id}` - Get genre details for admin
  - **Response**: Complete genre information
  - **Features**: Genre editing, metadata access

- **PUT** `/{genre_id}` - Update genre
  - **Request Body**: Updated genre data
  - **Response**: Updated genre details
  - **Features**: Genre updates, content management

- **DELETE** `/{genre_id}` - Delete genre
  - **Response**: Deletion confirmation
  - **Features**: Genre removal, content reassignment

### Admin People Management (`/api/v1/admin/people`)

#### People CRUD Operations
- **POST** `/` - Create new person
  - **Request Body**: Person creation data
  - **Response**: Created person details
  - **Features**: Person creation, metadata management

- **GET** `/` - Get paginated people list
  - **Query Params**: People filtering and pagination
  - **Response**: Admin people list
  - **Features**: People management, search functionality

- **GET** `/{person_id}` - Get person details for admin
  - **Response**: Complete person information
  - **Features**: Person editing, filmography access

- **PUT** `/{person_id}` - Update person
  - **Request Body**: Updated person data
  - **Response**: Updated person details
  - **Features**: Person updates, metadata management

- **DELETE** `/{person_id}` - Delete person
  - **Response**: Deletion confirmation
  - **Features**: Person removal, content cleanup

### Admin Streaming Management (`/api/v1/admin/streaming-channels`)

#### Streaming Channel CRUD Operations
- **POST** `/` - Create new streaming channel
  - **Request Body**: Channel creation data
  - **Response**: Created channel details
  - **Features**: Channel creation, stream URL management

- **GET** `/` - Get paginated channels list
  - **Query Params**: Channel filtering and pagination
  - **Response**: Admin channels list
  - **Features**: Channel management, status filtering

- **GET** `/{channel_id}` - Get channel details for admin
  - **Response**: Complete channel information
  - **Features**: Channel editing, stream management

- **PUT** `/{channel_id}` - Update channel
  - **Request Body**: Updated channel data
  - **Response**: Updated channel details
  - **Features**: Channel updates, stream URL management

- **DELETE** `/{channel_id}` - Delete channel
  - **Response**: Deletion confirmation
  - **Features**: Channel removal, stream cleanup

### Admin Monetization (`/api/v1/admin/monetization`)

#### Revenue Management
- **GET** `/revenue` - Get revenue analytics
  - **Response**: Revenue statistics and trends
  - **Features**: Revenue tracking, analytics

- **GET** `/campaigns` - Get ad campaigns
  - **Response**: Campaign list and performance
  - **Features**: Campaign management, performance tracking

- **POST** `/campaigns` - Create ad campaign
  - **Request Body**: Campaign creation data
  - **Response**: Created campaign details
  - **Features**: Campaign creation, targeting setup

### Admin Policy Management (`/api/v1/admin/policies`)

#### Policy CRUD Operations
- **POST** `/` - Create new policy
  - **Request Body**: Policy creation data
  - **Response**: Created policy details
  - **Features**: Policy creation, versioning

- **GET** `/` - Get paginated policies list
  - **Query Params**: Policy filtering and pagination
  - **Response**: Admin policies list
  - **Features**: Policy management, version tracking

- **PUT** `/{policy_id}` - Update policy
  - **Request Body**: Updated policy data
  - **Response**: Updated policy details
  - **Features**: Policy updates, version management

### Admin File Upload (`/api/v1/admin/upload`)

#### File Management
- **POST** `/content` - Upload content files
  - **Request Body**: Multipart file upload
  - **Response**: Upload confirmation with URLs
  - **Features**: File upload to S3, content association

- **POST** `/avatar` - Upload user avatar
  - **Request Body**: Multipart file upload
  - **Response**: Avatar URL
  - **Features**: Avatar upload, image processing

- **POST** `/banner` - Upload banner image
  - **Request Body**: Multipart file upload
  - **Response**: Banner URL
  - **Features**: Banner upload, image optimization

## 📝 API Usage Examples

### Authentication Flow

#### 1. User Registration
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Registration successful. Please check your email for verification code.",
  "data": {
    "email": "user@example.com",
    "otp_sent_at": "2024-01-15T10:30:00Z"
  }
}
```

#### 2. Email Verification
```bash
curl -X POST "http://localhost:8000/api/v1/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp_code": "123456"
  }'
```

#### 3. User Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "remember_me": false
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "user@example.com",
      "first_name": null,
      "last_name": null,
      "is_active": true,
      "profile_status": "active"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "expires_in": 1800,
      "refresh_expires_in": 604800
    }
  }
}
```

### Content Discovery

#### 1. Get Content Discovery Data
```bash
curl -X GET "http://localhost:8000/api/v1/content/discovery?include_featured=true&include_trending=true&page=1&size=10"
```

**Response:**
```json
{
  "sections": [
    {
      "title": "Featured Content",
      "description": "Handpicked content for you",
      "items": [
        {
          "id": "123e4567-e89b-12d3-a456-426614174000",
          "title": "The Great Movie",
          "poster_url": "https://example.com/poster.jpg",
          "trailer_url": "https://example.com/trailer.mp4",
          "content_type": "movie",
          "release_date": "2024-01-01",
          "rating": 8.5
        }
      ],
      "pagination": {
        "page": 1,
        "size": 10,
        "total": 50,
        "pages": 5,
        "has_next": true,
        "has_prev": false
      }
    }
  ],
  "genres": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "name": "Action",
      "slug": "action",
      "cover_image_url": "https://example.com/action.jpg"
    }
  ],
  "total_sections": 1,
  "page": 1,
  "size": 10,
  "generated_at": "2024-01-15T10:30:00Z"
}
```

#### 2. Search Content
```bash
curl -X GET "http://localhost:8000/api/v1/content/search?q=action&content_type=movie&page=1&size=20"
```

#### 3. Get Content Details
```bash
curl -X GET "http://localhost:8000/api/v1/content/123e4567-e89b-12d3-a456-426614174000"
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "The Great Movie",
  "description": "An amazing movie about...",
  "content_type": "movie",
  "poster_url": "https://example.com/poster.jpg",
  "backdrop_url": "https://example.com/backdrop.jpg",
  "trailer_url": "https://example.com/trailer.mp4",
  "release_date": "2024-01-01",
  "runtime": 120,
  "rating": 8.5,
  "genres": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "name": "Action",
      "slug": "action"
    }
  ],
  "cast": [
    {
      "person": {
        "id": "123e4567-e89b-12d3-a456-426614174002",
        "name": "John Doe",
        "profile_image_url": "https://example.com/john.jpg"
      },
      "character_name": "Hero",
      "is_main_cast": true
    }
  ],
  "crew": [
    {
      "person": {
        "id": "123e4567-e89b-12d3-a456-426614174003",
        "name": "Jane Smith",
        "profile_image_url": "https://example.com/jane.jpg"
      },
      "job_title": "Director",
      "department": "Directing"
    }
  ]
}
```

### User Interactions

#### 1. Add to Favorites
```bash
curl -X POST "http://localhost:8000/api/v1/favorites/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 2. Add to Watchlist
```bash
curl -X POST "http://localhost:8000/api/v1/watchlist/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 3. Create Review
```bash
curl -X POST "http://localhost:8000/api/v1/content/123e4567-e89b-12d3-a456-426614174000/reviews" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Great Movie!",
    "content": "This movie was absolutely fantastic...",
    "rating": 5.0,
    "language": "en"
  }'
```

### Subscription Management

#### 1. Create Checkout Session
```bash
curl -X POST "http://localhost:8000/api/v1/stripe/checkout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "session_id": "cs_test_1234567890"
}
```

#### 2. Get Subscription Info
```bash
curl -X GET "http://localhost:8000/api/v1/subscriptions/my-subscription" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "has_active_subscription": true,
  "current_plan": "premium_monthly",
  "subscription_status": "active",
  "current_period_end": "2024-02-15T10:30:00Z",
  "trial_ends_at": null,
  "amount": 9.99,
  "currency": "usd"
}
```

### Admin Operations

#### 1. Create Content (Admin)
```bash
curl -X POST "http://localhost:8000/api/v1/admin/content" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Movie",
    "description": "A new movie description",
    "content_type": "movie",
    "release_date": "2024-06-01",
    "runtime": 120,
    "content_rating": "PG-13",
    "genres": ["123e4567-e89b-12d3-a456-426614174001"]
  }'
```

#### 2. Get Users List (Admin)
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users?page=1&size=20&role=user" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

### Error Handling

All API endpoints return standardized error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "email",
    "message": "Invalid email format"
  }
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

## 🚀 API Rate Limiting & Best Practices

### Rate Limiting
The API implements rate limiting to ensure fair usage and prevent abuse:

- **Authentication endpoints**: 5 requests per minute per IP
- **Content endpoints**: 100 requests per minute per user
- **Admin endpoints**: 200 requests per minute per admin user
- **File upload endpoints**: 10 requests per minute per user

### Best Practices

#### 1. Authentication
- Always include the `Authorization: Bearer <token>` header for protected endpoints
- Implement token refresh logic to handle expired access tokens
- Store refresh tokens securely and use them to get new access tokens

#### 2. Error Handling
- Check HTTP status codes and handle errors appropriately
- Implement retry logic with exponential backoff for transient errors
- Log errors for debugging and monitoring

#### 3. Pagination
- Use pagination for list endpoints to avoid large response payloads
- Default page size is 20, maximum is 100
- Always check `has_next` and `has_prev` for navigation

#### 4. Content Filtering
- Use query parameters to filter content by type, genre, year, etc.
- Implement search functionality with the `/search` endpoint
- Cache frequently accessed content to improve performance

#### 5. File Uploads
- Validate file types and sizes before upload
- Use multipart/form-data for file uploads
- Handle upload progress and errors gracefully

#### 6. Subscription Management
- Check subscription status before accessing premium features
- Handle subscription expiration and renewal
- Implement proper webhook handling for Stripe events

### SDK Examples

#### JavaScript/TypeScript
```javascript
// Authentication
const login = async (email, password) => {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return response.json();
};

// Get content with authentication
const getContent = async (contentId, token) => {
  const response = await fetch(`/api/v1/content/${contentId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};
```

#### Python
```python
import requests

# Authentication
def login(email, password):
    response = requests.post(
        'http://localhost:8000/api/v1/auth/login',
        json={'email': email, 'password': password}
    )
    return response.json()

# Get content with authentication
def get_content(content_id, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'http://localhost:8000/api/v1/content/{content_id}',
        headers=headers
    )
    return response.json()
```

## 🎯 Key Features

### Subscription Management
- **Stripe Integration**: Complete payment processing with Stripe
- **Subscription Plans**: Multiple subscription tiers and pricing
- **Billing Management**: Automated billing and invoice generation
- **Payment Methods**: Support for multiple payment methods

### Monetization
- **Ad Campaigns**: Create and manage advertising campaigns
- **Revenue Tracking**: Monitor revenue and performance metrics
- **Analytics**: Detailed analytics and reporting
- **Performance Monitoring**: Track campaign performance and engagement

### User Policies
- **Policy Management**: Create and manage user policies
- **Acceptance Tracking**: Track user policy acceptance
- **Version Control**: Policy versioning and updates
- **Compliance**: Ensure regulatory compliance

### FAQ System
- **Question Management**: Create and manage FAQ entries
- **Categorization**: Organize FAQs by categories
- **Search**: Full-text search capabilities
- **Admin Controls**: Comprehensive admin management interface


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

## 🧪 Testing

The project includes comprehensive unit tests

### Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/unit/auth/test_auth_endpoints.py

# Run tests with coverage
pytest --cov=app tests/

# Run tests in parallel
pytest -n auto

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Test Structure

```
tests/
├── conftest.py                    # fixtures and configuration
├── unit/                         # Unit tests
│   └── auth/                    # Authentication tests
│       └── test_auth_endpoints.py # Authentication endpoint tests
└── pytest.ini                   # Pytest configuration
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
- [ ] Run tests in CI/CD pipeline
