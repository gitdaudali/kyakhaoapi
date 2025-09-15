# Cup Streaming API - Docker Setup

Simple Docker setup for development and production environments.

## 📁 Files

- `docker-compose.yml` - Production environment (external database)
- `docker-compose-dev.yml` - Development environment (local database)
- `Makefile.docker` - Docker management commands
- `.env` - Environment variables (create from template)

## 🚀 Quick Start

### Development
```bash
# Start development with hot reload
make -f Makefile.docker dev

# Build development images
make -f Makefile.docker dev-build

# View logs
make -f Makefile.docker dev-logs

# Access shell
make -f Makefile.docker dev-shell

# Stop development
make -f Makefile.docker dev-down
```

### Production
```bash
# Build production images
make -f Makefile.docker build

# Start production
make -f Makefile.docker up

# View logs
make -f Makefile.docker logs

# Access shell
make -f Makefile.docker shell

# Stop production
make -f Makefile.docker down
```

## 🔧 Environment Variables

Create a `.env` file with these variables:

```bash
# Database
DB_NAME=cup_streaming
DB_USER=cup_streaming
DB_PASSWORD=your_password
DB_HOST=localhost  # For production, use external DB host
DB_PORT=5432

# Security
SECRET_KEY=your-secret-key

# Server
DEBUG=false  # Set to true for development
HOST=0.0.0.0
PORT=8000

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME=Cup Streaming
EMAILS_ENABLED=false

# Token Expiration (in hours)
PASSWORD_RESET_TOKEN_EXPIRE_HOURS=24
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS=24
```

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check service status
make -f Makefile.docker status
# Check logs
make -f Makefile.docker logs
```

### Entrypoint Issues
If you see `pg_isready: command not found` errors:
- The entrypoint script is properly configured
- For production: Uses direct commands (no database waiting)
- For development: Waits for PostgreSQL container to be ready

### Clean Everything
```bash
# Remove all containers and volumes
make -f Makefile.docker clean
```

## 🌐 Access Points

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `dev` | Start development environment |
| `dev-build` | Build development images |
| `dev-logs` | Show development logs |
| `dev-shell` | Access development backend shell |
| `dev-down` | Stop development environment |
| `build` | Build production images |
| `up` | Start production environment |
| `down` | Stop production environment |
| `logs` | Show production logs |
| `shell` | Access production backend shell |
| `restart` | Restart production environment |
| `clean` | Remove all containers and volumes |
| `status` | Show service status |
| `migrate` | Run database migrations |
| `seed` | Seed database with sample data |

## 🔄 Environment Differences

### Development (`docker-compose-dev.yml`)
- ✅ PostgreSQL in Docker container
- ✅ Hot reload enabled
- ✅ Live code mounting
- ✅ Debug mode

### Production (`docker-compose.yml`)
- ✅ External database connection
- ✅ Optimized performance
- ✅ No hot reload
- ✅ Production settings

## 🗄️ Database Setup

### Development
- Uses local PostgreSQL container
- Database: `cup_streaming`
- User: `cup_streaming`
- Password: From `.env` file

### Production
- Requires external database (AWS RDS, Google Cloud SQL, etc.)
- Configure `DB_HOST` in `.env` file
- Ensure database is accessible from Docker containers

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Database Connection Issues
```bash
# Check service status
make -f Makefile.docker status
# Check logs
make -f Makefile.docker logs
```

### Clean Everything
```bash
# Remove all containers and volumes
make -f Makefile.docker clean
```
