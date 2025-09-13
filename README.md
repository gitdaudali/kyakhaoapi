# Cup Streaming Platform

A modern, high-performance video streaming platform with both Django and FastAPI implementations.

## 🚀 Features

- **Dual Backend Support**: Both Django REST Framework and FastAPI implementations
- **JWT Authentication**: Secure user authentication with JWT tokens
- **Video Management**: Upload, manage, and stream videos
- **User Management**: User registration, profiles, and permissions
- **Analytics**: Track video views and user engagement
- **PostgreSQL Database**: Robust relational database backend
- **Social Authentication**: Google and Facebook OAuth integration
- **Async Operations**: High-performance asynchronous operations (FastAPI)

## 🏗️ Project Structure

```
Cup_Streaming/
├── django/                 # Django REST Framework implementation
│   ├── core/              # Django project settings
│   ├── apps/              # Django applications
│   │   ├── authentication/ # User authentication
│   │   ├── users/         # User management
│   │   ├── videos/        # Video management
│   │   └── api/           # API utilities
│   ├── manage.py          # Django management script
│   ├── start_django.py    # Django startup script
│   └── requirements.txt   # Django dependencies
├── fastapi/               # FastAPI implementation
│   ├── app/               # FastAPI application
│   │   ├── core/          # Core configuration
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── api/           # API endpoints
│   ├── main.py            # FastAPI main application
│   ├── start_fastapi.py   # FastAPI startup script
│   └── requirements.txt   # FastAPI dependencies
├── start_projects.py      # Main project launcher
└── requirements.txt       # Combined dependencies
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (optional)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Cup_Streaming
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Install all dependencies
   pip install -r requirements.txt

   # Or install project-specific dependencies
   pip install -r django/requirements.txt    # For Django only
   pip install -r fastapi/requirements.txt   # For FastAPI only
   ```

4. **Environment Configuration**
   Create a `.env` file with your configuration:
   ```env
   SECRET_KEY=your-secret-key-here
   DB_NAME=cup_streaming
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   REDIS_URL=redis://localhost:6379
   ```

5. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb cup_streaming
   ```

6. **Run the Application**
   ```bash
   # Use the main launcher
   python start_projects.py

   # Or start individual projects
   cd django && python start_django.py      # Django on port 8000
   cd fastapi && python start_fastapi.py    # FastAPI on port 8001
   ```

## 🚀 Quick Start

### Django Project
- **URL**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/v1/

### FastAPI Project
- **URL**: http://localhost:8001
- **Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 📚 API Documentation

### Django Project (Port 8000)
- **Admin Panel**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/v1/
- **Browsable API**: http://localhost:8000/api/v1/

### FastAPI Project (Port 8001)
- **Interactive API Docs**: http://localhost:8001/docs
- **ReDoc Documentation**: http://localhost:8001/redoc
- **OpenAPI Schema**: http://localhost:8001/openapi.json
- **Health Check**: http://localhost:8001/health

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
- **Connection Pooling**: Database connection optimization
- **Background Tasks**: Celery integration for heavy operations

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt password encryption
- **CORS Protection**: Configurable cross-origin policies
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM protection

## 🗄️ Database

This application uses PostgreSQL for robust data management:

- **Database**: PostgreSQL with connection pooling
- **Models**: User, Video, VideoView, VideoLike
- **UUID Support**: Native PostgreSQL UUID support
- **Auto-migration**: Tables are created automatically on startup
- **Connection**: Configured via environment variables

## 🚀 Complete Setup & Run Guide

### Step 1: Navigate to Project Directory
```bash
# Windows PowerShell
cd "C:\Users\DIGITAL ZONE\Downloads\cup-streaming-main (2) (1)\cup-streaming-main\cup-streaming-main"

# Verify you're in the right directory
ls
# Should see: main.py, requirements_fastapi.txt, app/, etc.
```

### Step 2: Install Dependencies
```bash
# Install FastAPI dependencies
pip install -r requirements_fastapi.txt

# Or install individually if requirements file fails
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart

# Verify installation
pip list | findstr fastapi
```

### Step 3: PostgreSQL Database Setup

#### 3.1: Install PostgreSQL (if not installed)
```bash
# Download from: https://www.postgresql.org/download/windows/
# Or using chocolatey
choco install postgresql

# Or using winget
winget install PostgreSQL.PostgreSQL
```

#### 3.2: Start PostgreSQL Service
```bash
# Start PostgreSQL service
net start postgresql-x64-14

# Or using services.msc
services.msc
# Find "postgresql" service and start it
```

#### 3.3: Create Database and User
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE "cup-entertainment";

# Create user (optional)
CREATE USER cup_user WITH PASSWORD 'password123';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE "cup-entertainment" TO cup_user;

# Exit psql
\q
```

#### 3.4: Test Database Connection
```bash
# Test connection
psql -U postgres -d cup-entertainment -c "SELECT version();"

# Or test with Python
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', database='cup-entertainment', user='postgres', password='#Trigonometry1'); print('Database connected successfully!')"
```

### Step 4: Configure Database Credentials
```bash
# Check current database configuration
type app\core\config.py

# The current settings are:
# DB_NAME: "cup-entertainment"
# DB_USER: "postgres"
# DB_PASSWORD: "#Trigonometry1"
# DB_HOST: "localhost"
# DB_PORT: "5432"
```

### Step 5: Run the Application

#### 5.1: Basic Run Commands
```bash
# Option 1: Using uvicorn directly
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Option 2: Using Python module
py -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Option 3: With detailed logging
py -m uvicorn main:app --host 127.0.0.1 --port 8000 --log-level info

# Option 4: Using startup script
python start_fastapi.py

# Option 5: Run on different port (if 8000 is busy)
uvicorn main:app --reload --host 127.0.0.1 --port 8001
py -m uvicorn main:app --host 127.0.0.1 --port 8001 --log-level info
```

#### 5.2: Production Run Commands
```bash
# Without reload (production)
uvicorn main:app --host 127.0.0.1 --port 8000

# With multiple workers
uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4

# Using gunicorn (if installed)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```

### Step 5: Access the API
Once running, access:
- **API Documentation**: http://127.0.0.1:8000/docs
- **ReDoc Documentation**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json

### Step 6: Test Database Connectivity

#### 6.1: Test PostgreSQL Connection
```bash
# Test basic connection
psql -U postgres -h localhost -p 5432 -c "SELECT version();"

# Test specific database
psql -U postgres -d cup-entertainment -c "SELECT current_database();"

# Test with Python
python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        database='cup-entertainment',
        user='postgres',
        password='#Trigonometry1'
    )
    print('✅ Database connected successfully!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

#### 6.2: Test FastAPI Application
```bash
# Test health endpoint
curl http://127.0.0.1:8000/health

# Or using PowerShell
Invoke-WebRequest -Uri http://127.0.0.1:8000/health -UseBasicParsing

# Test API documentation
# Open browser: http://127.0.0.1:8000/docs
```

#### 6.3: Verify Database Tables Created
```bash
# Check if tables were created
psql -U postgres -d cup-entertainment -c "\dt"

# Should see tables like:
# users_user
# videos_video
# videos_video_view
# videos_video_like
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Port Already in Use
```bash
# Error: [Errno 10048] error while attempting to bind on address
# Solution: Use a different port
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

#### 2. PostgreSQL Connection Failed
```bash
# Error: password authentication failed for user "postgres"
# Solution 1: Check PostgreSQL service is running
net start postgresql-x64-14
# or
services.msc

# Solution 2: Reset PostgreSQL password
psql -U postgres
ALTER USER postgres PASSWORD '#Trigonometry1';

# Solution 3: Check pg_hba.conf file
# Edit: C:\Program Files\PostgreSQL\14\data\pg_hba.conf
# Change: md5 to trust for local connections

# Solution 4: Test connection manually
psql -U postgres -h localhost -p 5432

# Solution 5: Check if database exists
psql -U postgres -l
# Should see "cup-entertainment" in the list
```

#### 3. Module Import Error
```bash
# Error: Could not import module "main"
# Solution: Make sure you're in the correct directory
cd "C:\Users\DIGITAL ZONE\Downloads\cup-streaming-main (2) (1)\cup-streaming-main\cup-streaming-main"
```

#### 4. Missing Dependencies
```bash
# Error: No module named 'fastapi'
# Solution: Install dependencies
pip install -r requirements_fastapi.txt
```

#### 5. Database Tables Not Created
```bash
# Solution: Check database connection and restart the application
# Tables are created automatically on startup
```

### Windows-Specific Commands

```powershell
# Navigate to project directory
cd "C:\Users\DIGITAL ZONE\Downloads\cup-streaming-main (2) (1)\cup-streaming-main\cup-streaming-main"

# Install dependencies
pip install -r requirements_fastapi.txt

# Run application
py -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Test API
Invoke-WebRequest -Uri http://127.0.0.1:8000/health -UseBasicParsing
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## ⚡ Quick Start - All Commands in Sequence

### Complete Setup & Run (Copy & Paste)
```bash
# 1. Navigate to project
cd "C:\Users\DIGITAL ZONE\Downloads\cup-streaming-main (2) (1)\cup-streaming-main\cup-streaming-main"

# 2. Install dependencies
pip install -r requirements_fastapi.txt

# 3. Start PostgreSQL service
net start postgresql-x64-14

# 4. Create database
psql -U postgres -c "CREATE DATABASE \"cup-entertainment\";"

# 5. Test database connection
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', database='cup-entertainment', user='postgres', password='#Trigonometry1'); print('✅ Database connected!'); conn.close()"

# 6. Run FastAPI application
py -m uvicorn main:app --host 127.0.0.1 --port 8000 --log-level info

# 7. Test application (in new terminal)
Invoke-WebRequest -Uri http://127.0.0.1:8000/health -UseBasicParsing
```

### Alternative Port Commands
```bash
# If port 8000 is busy, use port 8001
py -m uvicorn main:app --host 127.0.0.1 --port 8001 --log-level info

# Test on port 8001
Invoke-WebRequest -Uri http://127.0.0.1:8001/health -UseBasicParsing
```

## 📋 Complete Command Reference

### Setup Commands
```bash
# 1. Navigate to project
cd "C:\Users\DIGITAL ZONE\Downloads\cup-streaming-main (2) (1)\cup-streaming-main\cup-streaming-main"

# 2. Install dependencies
pip install -r requirements_fastapi.txt

# 3. Create database (PostgreSQL)
createdb cup-entertainment
```

### Run Commands
```bash
# Basic run
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Using Python module
py -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# With detailed logging
py -m uvicorn main:app --host 127.0.0.1 --port 8000 --log-level info

# Using startup script
python start_fastapi.py

# Run on different port
uvicorn main:app --reload --host 127.0.0.1 --port 8001

# Run without reload (production)
uvicorn main:app --host 127.0.0.1 --port 8000
```

### Test Commands
```bash
# Test health endpoint
curl http://127.0.0.1:8000/health

# PowerShell test
Invoke-WebRequest -Uri http://127.0.0.1:8000/health -UseBasicParsing

# Test API documentation
# Open browser: http://127.0.0.1:8000/docs
```

### Development Commands
```bash
# Install development dependencies
pip install pytest pytest-asyncio httpx black isort flake8

# Run tests
pytest

# Format code
black app/
isort app/

# Lint code
flake8 app/
```

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For questions and support, please open an issue in the repository.
