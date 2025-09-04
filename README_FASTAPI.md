# Cup Streaming - FastAPI Version

A modern, high-performance video streaming platform built with FastAPI, SQLAlchemy, and PostgreSQL.

## 🚀 Features

- **FastAPI Backend**: Modern, fast web framework with automatic API documentation
- **JWT Authentication**: Secure user authentication with JWT tokens
- **Video Management**: Upload, manage, and stream videos
- **User Management**: User registration, profiles, and permissions
- **Analytics**: Track video views and user engagement
- **S3 Integration**: AWS S3 support for video storage
- **PostgreSQL Database**: Robust relational database backend
- **Redis Support**: Caching and session management
- **Async Operations**: High-performance asynchronous operations

## 🏗️ Architecture

```
app/
├── core/           # Core configuration and utilities
│   ├── config.py   # Application settings
│   ├── database.py # Database configuration
│   └── auth.py     # Authentication utilities
├── models/         # SQLAlchemy database models
│   ├── user.py     # User model
│   └── video.py    # Video and related models
├── schemas/        # Pydantic request/response schemas
│   ├── user.py     # User schemas
│   └── video.py    # Video schemas
└── api/            # API endpoints
    └── v1/         # API version 1
        ├── api.py  # Main router
        └── endpoints/
            ├── auth.py   # Authentication endpoints
            ├── users.py  # User management endpoints
            └── videos.py # Video management endpoints
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (optional)
- AWS S3 account (optional)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cup-streaming-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_fastapi.txt
   ```

3. **Environment Configuration**
   Create a `.env` file with your configuration:
   ```env
   SECRET_KEY=your-secret-key-here
   DB_NAME=cup_streaming
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   REDIS_URL=redis://localhost:6379
   AWS_ACCESS_KEY_ID=your-aws-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret
   AWS_REGION=us-east-1
   S3_BUCKET=your-bucket-name
   ```

4. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb cup_streaming
   
   # Run migrations (if using Alembic)
   alembic upgrade head
   ```

5. **Run the Application**
   ```bash
   # Option 1: Using the startup script
   python start_fastapi.py
   
   # Option 2: Direct uvicorn
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔐 Authentication

The API uses JWT tokens for authentication:

1. **Register**: `POST /api/v1/auth/register`
2. **Login**: `POST /api/v1/auth/login`
3. **Use Token**: Include `Authorization: Bearer <token>` in headers

## 📹 Video Management

### Endpoints

- `GET /api/v1/videos/` - List videos
- `POST /api/v1/videos/` - Upload video
- `GET /api/v1/videos/{id}` - Get video details
- `PUT /api/v1/videos/{id}` - Update video
- `DELETE /api/v1/videos/{id}` - Delete video
- `POST /api/v1/videos/{id}/like` - Like video
- `DELETE /api/v1/videos/{id}/like` - Unlike video

### Video Upload Flow

1. Create video metadata via API
2. Upload video file to S3
3. Update video with S3 details
4. Set status to "ready"

## 👥 User Management

### Endpoints

- `GET /api/v1/users/` - List users (admin only)
- `GET /api/v1/users/{id}` - Get user profile
- `PUT /api/v1/users/{id}` - Update user profile
- `DELETE /api/v1/users/{id}` - Delete user (admin only)

## 🔧 Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Quality
```bash
# Install linting tools
pip install black isort flake8

# Format code
black app/
isort app/

# Lint code
flake8 app/
```

## 🚀 Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_fastapi.txt .
RUN pip install -r requirements_fastapi.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 Performance Features

- **Async Operations**: Non-blocking I/O operations
- **Database Optimization**: Efficient SQLAlchemy queries
- **Caching**: Redis-based caching support
- **Connection Pooling**: Database connection optimization
- **Background Tasks**: Celery integration for heavy operations

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt password encryption
- **CORS Protection**: Configurable cross-origin policies
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆚 Migration from Django

This FastAPI version maintains feature parity with the original Django application:

- ✅ User authentication and management
- ✅ Video CRUD operations
- ✅ View tracking and analytics
- ✅ Like/unlike functionality
- ✅ S3 integration
- ✅ Database models and relationships
- ✅ API endpoints and permissions

### Key Differences

- **Framework**: Django → FastAPI
- **ORM**: Django ORM → SQLAlchemy
- **Serialization**: Django Serializers → Pydantic
- **Authentication**: Django Auth → JWT
- **Performance**: Synchronous → Asynchronous
- **Documentation**: Manual → Auto-generated OpenAPI

## 📞 Support

For questions and support, please open an issue in the repository.
