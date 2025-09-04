# Cup Streaming API

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A robust Django REST API for the Cup Streaming platform, featuring comprehensive user authentication, profile management, and secure API endpoints with JWT token-based authentication.

## 🚀 Features

- **🔐 Secure Authentication**: JWT-based authentication with refresh tokens
- **👤 User Management**: Complete user registration, login, and profile management
- **📧 Email Verification**: Mandatory email verification with secure tokens
- **🔒 Password Security**: Password reset functionality with secure token generation
- **🛡️ Role-Based Access**: User roles and permission management
- **📊 Activity Tracking**: User activity logging and monitoring
- **🌐 Social Authentication**: Google and Facebook OAuth integration
- **🎥 Video Management**: Complete video CRUD operations with AWS S3 integration
- **📈 Health Monitoring**: API health checks and monitoring endpoints
- **🔧 Webhook Support**: External integration capabilities
- **📱 CORS Support**: Cross-origin resource sharing for frontend integration

## 🏗️ Architecture

```
cup-streaming/
├── apps/
│   ├── authentication/     # User authentication & JWT management
│   ├── users/             # User profiles & activity tracking
│   ├── videos/            # Video management & S3 integration
│   └── api/               # Core API endpoints & utilities
├── core/                  # Django project settings & configuration
├── static/                # Static files
├── media/                 # User uploaded files
├── templates/             # HTML templates
└── logs/                  # Application logs
```

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Redis (optional, for caching)
- Git

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cup-streaming.git
cd cup-streaming
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://postgres:#Trigonometry1@localhost:5432/cup-entertainment

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@cupstreaming.com

# Frontend URL
FRONTEND_URL=http://localhost:3000

# AWS S3 Configuration (for video storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_REGION_NAME=us-east-1
AWS_S3_BUCKET_NAME=your-video-bucket-name

# AWS MediaConvert Configuration (for video processing)
AWS_MEDIACONVERT_ENDPOINT=https://mediaconvert.us-east-1.amazonaws.com
AWS_MEDIACONVERT_ROLE_ARN=arn:aws:iam::123456789012:role/MediaConvert_Role
AWS_MEDIACONVERT_QUEUE_ARN=arn:aws:mediaconvert:us-east-1:123456789012:queues/Default

# Celery Configuration (for video processing)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

### 5. Database Setup

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid access token in the Authorization header.

### Token Structure

- **Access Token**: Short-lived (15 minutes) for API requests
- **Refresh Token**: Long-lived (24 hours) for token renewal

### Authentication Flow

1. **Register/Login** → Receive access and refresh tokens
2. **API Requests** → Include access token in Authorization header
3. **Token Expiry** → Use refresh token to get new access token
4. **Logout** → Revoke refresh token

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1/
```

### Response Format

All API responses follow a standardized format:

```json
{
  "code": 200,
  "message": "Success message",
  "data": {
    // Response data
  }
}
```

### Error Response Format

```json
{
  "code": 400,
  "message": "Error description",
  "data": null
}
```

## 🔑 Authentication Endpoints

### User Registration

**POST** `/auth/register/`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}
```

**Response:**
```json
{
  "code": 201,
  "message": "User registered successfully. Please check your email for verification.",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "username",
      "role": "user",
      "isEmailVerified": false
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
}
```

### User Login

**POST** `/auth/login/`

Authenticate user and receive tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "username",
      "role": "user",
      "isEmailVerified": true
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
}
```

### Token Refresh

**POST** `/auth/token/refresh/`

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Token refreshed successfully",
  "data": {
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
}
```

### User Logout

**POST** `/auth/logout/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Logout successful",
  "data": null
}
```

### Password Reset Request

**POST** `/auth/password/reset/`

Request password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Password reset email sent successfully",
  "data": null
}
```

### Password Reset Confirm

**POST** `/auth/password/reset/confirm/`

Reset password using reset token.

**Request Body:**
```json
{
  "reset_token": "uuid-token-here",
  "new_password": "newsecurepassword123",
  "new_password_confirm": "newsecurepassword123"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Password reset successfully",
  "data": null
}
```

### Email Verification

**POST** `/auth/email/verify/`

Verify email address using verification token.

**Request Body:**
```json
{
  "verification_token": "uuid-token-here"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Email verified successfully",
  "data": null
}
```

## 👤 User Management Endpoints

### Get User Profile

**GET** `/auth/profile/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "code": 200,
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_email_verified": true,
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T12:00:00Z"
  }
}
```

### Update User Profile

**PUT** `/auth/profile/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "username": "johndoe"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Profile updated successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "is_email_verified": true
  }
}
```

### Change Password

**POST** `/auth/password/change/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Password changed successfully",
  "data": null
}
```

## 👥 User Administration Endpoints

### List All Users (Admin Only)

**GET** `/users/`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "code": 200,
  "message": "Users retrieved successfully",
  "data": [
    {
      "id": 1,
      "email": "user@example.com",
      "username": "username",
      "role": "user",
      "is_active": true,
      "date_joined": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get User Details (Admin Only)

**GET** `/users/{user_id}/`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "code": 200,
  "message": "User retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "role": "user",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T12:00:00Z"
  }
}
```

### Update User (Admin Only)

**PUT** `/users/{user_id}/`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
  "role": "admin",
  "is_active": true
}
```

**Response:**
```json
{
  "code": 200,
  "message": "User updated successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "role": "admin",
    "is_active": true
  }
}
```

### Delete User (Admin Only)

**DELETE** `/users/{user_id}/`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "code": 200,
  "message": "User deleted successfully",
  "data": null
}
```

## 📊 User Activity & Permissions

### Get User Activities

**GET** `/users/activities/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "code": 200,
  "message": "User activities retrieved successfully",
  "data": [
    {
      "id": 1,
      "activity_type": "login",
      "description": "User logged in",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### Get User Permissions (Admin Only)

**GET** `/users/permissions/`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "code": 200,
  "message": "User permissions retrieved successfully",
  "data": [
    {
      "id": 1,
      "user": 1,
      "permission": "can_view_users",
      "granted_by": 2,
      "granted_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## 🎥 Video Management Endpoints

The video management system provides comprehensive CRUD operations for video content with AWS S3 integration for file storage and processing.

### Video Model Overview

The Video model includes the following fields:
- `id` (UUID): Primary key
- `title` (CharField): Video title
- `description` (TextField): Video description
- `file_url` (URLField): S3 URL of the uploaded video
- `duration` (FloatField): Duration in seconds
- `thumbnail_url` (URLField): Thumbnail image URL
- `uploaded_by` (ForeignKey): User who uploaded the video
- `uploaded_at` (DateTimeField): Upload timestamp
- `updated_at` (DateTimeField): Last update timestamp
- `views_count` (IntegerField): Number of views
- `likes_count` (IntegerField): Number of likes
- `status` (CharField): Video processing status (uploading, processing, ready, failed)
- `file_size` (BigIntegerField): File size in bytes
- `resolution` (CharField): Video resolution
- `format` (CharField): Video format
- `s3_bucket` (CharField): S3 bucket name
- `s3_key` (CharField): S3 object key

### Video CRUD Operations

#### List Videos

**GET** `/videos/videos/`

**Headers:**
```
Authorization: Bearer <access_token> (optional)
```

**Query Parameters:**
- `search`: Search in title and description
- `ordering`: Sort by field (uploaded_at, views_count, likes_count, title)
- `status`: Filter by status (uploading, processing, ready, failed)
- `uploaded_by`: Filter by user ID
- `format`: Filter by video format
- `page`: Page number for pagination

**Response:**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/v1/videos/videos/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Sample Video",
      "description": "A sample video description",
      "thumbnail_url": "https://example.com/thumbnail.jpg",
      "duration": 120.5,
      "duration_formatted": "02:00:30",
      "views_count": 150,
      "likes_count": 25,
      "status": "ready",
      "uploaded_by": {
        "id": 1,
        "username": "user1",
        "email": "user1@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "uploaded_at": "2024-01-01T12:00:00Z",
      "file_size_formatted": "15.2 MB"
    }
  ]
}
```

#### Get Video Details

**GET** `/videos/videos/{video_id}/`

**Headers:**
```
Authorization: Bearer <access_token> (optional)
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Sample Video",
  "description": "A sample video description",
  "file_url": "https://s3.amazonaws.com/bucket/videos/sample.mp4",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "duration": 120.5,
  "duration_formatted": "02:00:30",
  "views_count": 151,
  "likes_count": 25,
  "status": "ready",
  "uploaded_by": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "uploaded_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "file_size": 15925248,
  "file_size_formatted": "15.2 MB",
  "resolution": "1920x1080",
  "format": "mp4",
  "views": [
    {
      "id": 1,
      "viewer": {
        "id": 2,
        "username": "viewer1",
        "email": "viewer1@example.com",
        "first_name": "Jane",
        "last_name": "Smith"
      },
      "ip_address": "192.168.1.1",
      "viewed_at": "2024-01-01T13:00:00Z"
    }
  ],
  "likes": [
    {
      "id": 1,
      "user": {
        "id": 2,
        "username": "liker1",
        "email": "liker1@example.com",
        "first_name": "Jane",
        "last_name": "Smith"
      },
      "created_at": "2024-01-01T13:30:00Z"
    }
  ]
}
```

#### Upload Video

**POST** `/videos/videos/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```
title: Sample Video
description: A sample video description
video_file: [binary file data]
duration: 120.5
thumbnail_url: https://example.com/thumbnail.jpg
file_size: 15925248
resolution: 1920x1080
format: mp4
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Sample Video",
  "description": "A sample video description",
  "file_url": "https://s3.amazonaws.com/bucket/videos/550e8400-e29b-41d4-a716-446655440000.mp4",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "duration": 120.5,
  "duration_formatted": "02:00:30",
  "views_count": 0,
  "likes_count": 0,
  "status": "uploading",
  "uploaded_by": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "uploaded_at": "2024-01-01T12:00:00Z",
  "file_size_formatted": "15.2 MB"
}
```

#### Update Video

**PUT** `/videos/videos/{video_id}/`

**Headers:**
```
Authorization: Bearer <access_token> (owner only)
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```
title: Updated Video Title
description: Updated video description
video_file: [binary file data] (optional)
duration: 125.0
thumbnail_url: https://example.com/new-thumbnail.jpg
file_size: 16000000
resolution: 1920x1080
format: mp4
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated Video Title",
  "description": "Updated video description",
  "file_url": "https://s3.amazonaws.com/bucket/videos/550e8400-e29b-41d4-a716-446655440000.mp4",
  "thumbnail_url": "https://example.com/new-thumbnail.jpg",
  "duration": 125.0,
  "duration_formatted": "02:05:00",
  "views_count": 151,
  "likes_count": 25,
  "status": "uploading",
  "uploaded_by": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "uploaded_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T14:00:00Z",
  "file_size": 16000000,
  "file_size_formatted": "15.3 MB",
  "resolution": "1920x1080",
  "format": "mp4"
}
```

#### Delete Video

**DELETE** `/videos/videos/{video_id}/`

**Headers:**
```
Authorization: Bearer <access_token> (owner only)
```

**Response:**
```json
{
  "detail": "Video deleted successfully"
}
```

### Video Interaction Endpoints

#### Toggle Video Like

**POST** `/videos/videos/{video_id}/like/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (Like Added):**
```json
{
  "status": "liked"
}
```

**Response (Like Removed):**
```json
{
  "status": "unliked"
}
```

#### Get Video Views

**GET** `/videos/videos/{video_id}/views/`

**Headers:**
```
Authorization: Bearer <access_token> (optional)
```

**Response:**
```json
[
  {
    "id": 1,
    "viewer": {
      "id": 2,
      "username": "viewer1",
      "email": "viewer1@example.com",
      "first_name": "Jane",
      "last_name": "Smith"
    },
    "ip_address": "192.168.1.1",
    "viewed_at": "2024-01-01T13:00:00Z"
  }
]
```

#### Get Video Likes

**GET** `/videos/videos/{video_id}/likes/`

**Headers:**
```
Authorization: Bearer <access_token> (optional)
```

**Response:**
```json
[
  {
    "id": 1,
    "user": {
      "id": 2,
      "username": "liker1",
      "email": "liker1@example.com",
      "first_name": "Jane",
      "last_name": "Smith"
    },
    "created_at": "2024-01-01T13:30:00Z"
  }
]
```

### Alternative API Endpoints

#### List Videos (Alternative)

**GET** `/videos/list/`

**Headers:**
```
Authorization: Bearer <access_token> (optional)
```

**Query Parameters:**
- `search`: Search in title and description
- `ordering`: Sort by field
- `status`: Filter by status
- `uploaded_by`: Filter by user ID
- `format`: Filter by video format

#### Get Video Details (Alternative)

**GET** `/videos/detail/{video_id}/`

**Headers:**
```
Authorization: Bearer <access_token> (optional)
```

#### Create Video (Alternative)

**POST** `/videos/create/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### Update Video (Alternative)

**PUT** `/videos/update/{video_id}/`

**Headers:**
```
Authorization: Bearer <access_token> (owner only)
Content-Type: multipart/form-data
```

#### Delete Video (Alternative)

**DELETE** `/videos/delete/{video_id}/`

**Headers:**
```
Authorization: Bearer <access_token> (owner only)
```

#### Toggle Like (Alternative)

**POST** `/videos/like/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Video Upload Requirements

#### Supported File Formats
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WMV (.wmv)
- FLV (.flv)
- WebM (.webm)

#### File Size Limits
- Maximum file size: 500MB per video

#### Required Fields
- `title`: Video title (required)
- `video_file`: Video file (required)
- `duration`: Duration in seconds (required)

#### Optional Fields
- `description`: Video description
- `thumbnail_url`: Thumbnail image URL
- `file_size`: File size in bytes
- `resolution`: Video resolution
- `format`: Video format

### Video Processing Status

The video processing follows these statuses:

1. **uploading**: Video is being uploaded to S3
2. **processing**: Video is being processed (transcoding, thumbnail generation)
3. **ready**: Video is ready for viewing
4. **failed**: Video processing failed

### AWS S3 Integration

The video system integrates with AWS S3 for file storage:

#### S3 Configuration
```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_REGION_NAME=us-east-1
AWS_S3_BUCKET_NAME=your-bucket-name
```

#### S3 File Structure
```
bucket-name/
├── videos/
│   ├── {video-id}.mp4
│   ├── {video-id}.avi
│   └── ...
└── thumbnails/
    ├── {video-id}.jpg
    └── ...
```

#### Presigned URLs
For secure video streaming, the system can generate presigned URLs:

```python
# Example usage in code
from apps.videos.utils import generate_video_stream_url

result = generate_video_stream_url(video.s3_key, expiration=3600)
if result['success']:
    stream_url = result['url']
```

### Video Analytics

The system tracks video analytics including:

#### View Tracking
- Automatic view count increment on video access
- IP address tracking
- User agent tracking
- Timestamp recording

#### Like Tracking
- User-specific like tracking
- Like count management
- Timestamp recording

#### Performance Metrics
- File size tracking
- Duration tracking
- Resolution tracking
- Format tracking

### Error Handling

#### Common Video Upload Errors

**File Too Large (400):**
```json
{
  "video_file": ["File size must be no more than 500MB."]
}
```

**Invalid File Format (400):**
```json
{
  "video_file": ["File type not supported. Allowed types: .mp4, .avi, .mov, .mkv, .wmv, .flv, .webm"]
}
```

**Invalid Duration (400):**
```json
{
  "duration": ["Duration must be greater than 0."]
}
```

**Permission Denied (403):**
```json
{
  "detail": "You do not have permission to perform this action"
}
```

**Video Not Found (404):**
```json
{
  "detail": "Video not found"
}
```

### Video Processing Pipeline

The video processing pipeline includes:

1. **Upload**: Video file uploaded to S3
2. **Validation**: File format and size validation
3. **Processing**: Video transcoding and thumbnail generation
4. **Storage**: Metadata stored in PostgreSQL
5. **Delivery**: Video available for streaming

### Future Enhancements

Planned features for the video system:

- **Adaptive Bitrate Streaming**: HLS/DASH support
- **Video Thumbnail Generation**: Automatic thumbnail creation
- **Video Transcoding**: Multiple resolution support
- **Video Analytics Dashboard**: Detailed viewing statistics
- **Video Categories**: Categorization and tagging
- **Video Comments**: User comments and discussions
- **Video Playlists**: User-created playlists
- **Video Recommendations**: AI-powered recommendations

## 🔧 System Endpoints

### Health Check

**GET** `/health/`

**Response:**
```json
{
  "code": 200,
  "message": "API is healthy",
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

### API Information

**GET** `/info/`

**Response:**
```json
{
  "code": 200,
  "message": "API information retrieved successfully",
  "data": {
    "name": "Cup Streaming API",
    "version": "1.0.0",
    "description": "API for Cup Streaming platform",
    "endpoints": {
      "authentication": "/api/v1/auth/",
      "users": "/api/v1/users/",
      "videos": "/api/v1/videos/",
      "health": "/api/v1/health/"
    }
  }
}
```

### Protected Endpoint Example

**GET** `/protected/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "code": 200,
  "message": "Protected data retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "role": "user"
  }
}
```

### Webhook Endpoint

**POST** `/webhook/`

**Request Body:**
```json
{
  "event": "user.created",
  "data": {
    "user_id": 1,
    "email": "user@example.com"
  }
}
```

**Response:**
```json
{
  "code": 200,
  "message": "Webhook processed successfully",
  "data": {
    "received": true
  }
}
```

## 🚨 Error Handling

### Common HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

### Error Response Examples

**Validation Error (400):**
```json
{
  "code": 400,
  "message": "Invalid input data",
  "data": {
    "email": ["This field is required."],
    "password": ["This password is too short."]
  }
}
```

**Authentication Error (401):**
```json
{
  "code": 401,
  "message": "Authentication credentials were not provided",
  "data": null
}
```

**Permission Error (403):**
```json
{
  "code": 403,
  "message": "You do not have permission to perform this action",
  "data": null
}
```

**Not Found Error (404):**
```json
{
  "code": 404,
  "message": "User not found",
  "data": null
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `*` |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `EMAIL_BACKEND` | Email backend | `django.core.mail.backends.console.EmailBackend` |
| `FRONTEND_URL` | Frontend URL for email links | `http://localhost:3000` |
| `AWS_ACCESS_KEY_ID` | AWS access key for S3 | Required for video uploads |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for S3 | Required for video uploads |
| `AWS_S3_REGION_NAME` | AWS S3 region | `us-east-1` |
| `AWS_S3_BUCKET_NAME` | AWS S3 bucket for videos | Required for video uploads |
| `AWS_MEDIACONVERT_ENDPOINT` | AWS MediaConvert endpoint | Required for video processing |
| `AWS_MEDIACONVERT_ROLE_ARN` | AWS MediaConvert role ARN | Required for video processing |
| `AWS_MEDIACONVERT_QUEUE_ARN` | AWS MediaConvert queue ARN | Required for video processing |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend | `redis://localhost:6379/0` |

### Database Configuration

The project uses PostgreSQL as the primary database. Configure your database connection in the `.env` file:

```env
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### Email Configuration

For production, configure a proper email backend:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.authentication
python manage.py test apps.users
python manage.py test apps.videos
python manage.py test apps.api
```

### Test Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

## 🚀 Deployment

### Production Settings

1. Set `DEBUG=False` in production
2. Configure proper `ALLOWED_HOSTS`
3. Use a production database
4. Set up proper email backend
5. Configure static file serving
6. Set up SSL/TLS certificates

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
```

### Environment Variables for Production

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-production-secret-key
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

## 📝 API Rate Limiting

The API implements rate limiting to prevent abuse:

- **Anonymous users**: 100 requests per hour
- **Authenticated users**: 1000 requests per hour

## 🔒 Security Features

- JWT token-based authentication
- Password hashing with Django's built-in hashers
- CSRF protection
- XSS protection
- Content Security Policy (CSP)
- Secure headers configuration
- Rate limiting
- Input validation and sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Email: support@cupstreaming.com
- Documentation: [API Docs](https://docs.cupstreaming.com)

## 🙏 Acknowledgments

- Django REST Framework for the excellent API framework
- Django Allauth for social authentication
- JWT for secure token-based authentication
- PostgreSQL for reliable database support

---

**Made with ❤️ by the Cup Streaming Team**
