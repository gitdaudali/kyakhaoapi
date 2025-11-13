## Kya Khao Platform API

The service now combines authentication with a rich food discovery experience for the Kya Khao platform. Alongside the original auth flows (registration, login, tokens, OTP, Google OAuth), it exposes curated content for dishes, cuisines, moods, restaurants, AI suggestions, and reservations.

### What's Included
- FastAPI application with versioned `/api/v1/auth`, `/api/v1/` (user endpoints), and `/api/v1/admin` routers (RBAC-protected discovery + admin CRUD)
- PostgreSQL + SQLAlchemy models for cuisines, moods, restaurants, dishes, and reservations
- Celery + Redis for background email tasks (with graceful error handling)
- Pagination, filtering, and reusable query utilities
- Faker-powered seed script to populate sample data
- Alembic migrations for both auth and food schemas
- Pytest coverage for pagination utilities and query helpers

### Directory Overview
```
kyakhao_API/
├── alembic/                     # Alembic migrations (auth + food domain)
│   └── versions/
│       ├── de5d1ac06c9d_initil_schema.py
│       └── 20251112_add_food_domain.py
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── admin/           # Admin CRUD routers (dishes, cuisines, moods, restaurants, FAQs) with RBAC
│   │       ├── auth/            # Authentication endpoints (registration, login, OTP, Google OAuth)
│   │       └── endpoints/       # User-facing routers (discovery, AI, reservations, search, FAQs)
│   ├── core/                    # Config, DB, auth helpers, response handling
│   ├── models/                  # Auth + food SQLAlchemy models
│   ├── schemas/                 # Pydantic schemas (auth, food, pagination, search, AI, admin/user bases)
│   ├── tasks/                   # Celery email tasks
│   └── utils/                   # Auth helpers, Google OAuth, pagination, filters, seed data
├── tests/                       # Pytest suite
├── main.py                      # FastAPI entry point
├── requirements.txt             # Python dependencies
└── README.md                    # You’re reading it
```

### Getting Started
1. **Create & activate a virtual environment**
   ```bash
   python -m venv env
   env\Scripts\activate  # Windows
   # source env/bin/activate  # macOS/Linux
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   Create a `.env` with at least:
   ```
   # Database
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=kyakhao
   
   # Security
   SECRET_KEY=super-secret-key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   
   # Celery & Redis (for background email tasks)
   CELERY_BROKER_URL=redis://localhost:6379
   CELERY_RESULT_BACKEND=redis://localhost:6379
   REDIS_URL=redis://localhost:6379
   
   # Email (optional - set to false if not using email)
   EMAILS_ENABLED=false
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FROM_EMAIL=noreply@kyakhao.com
   FROM_NAME=Kya Khao
   
   # Google OAuth (optional)
   GOOGLE_OAUTH_ENABLED=false
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
   ```
4. **Set up Redis (for Celery background tasks)**
   
   **Windows:**
   - Download Redis for Windows from [Memurai](https://www.memurai.com/) or use WSL
   - Or use Docker: `docker run -d -p 6379:6379 redis:latest`
   
   **macOS/Linux:**
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:latest
   
   # Or install via package manager
   # macOS: brew install redis && brew services start redis
   # Ubuntu: sudo apt-get install redis-server && sudo systemctl start redis
   ```
   
   **Note:** The API will work without Redis, but email tasks will fail gracefully (errors logged, registration still succeeds).

5. **Run migrations**
   ```bash
   alembic upgrade head
   ```

6. **(Optional) Seed dummy data**
   ```bash
   # Windows
   python seed_database.py
   
   # macOS/Linux
   python seed_database.py
   ```

7. **Start the API**
   ```bash
   uvicorn main:app --reload
   ```
   Visit `http://localhost:8000/docs` for interactive OpenAPI docs.

8. **(Optional) Start Celery worker (for email processing)**
   ```bash
   # Windows
   celery -A app.core.celery_app worker --loglevel=info
   
   # macOS/Linux
   celery -A app.core.celery_app worker --loglevel=info
   ```
   
   **Note:** Celery worker is only needed if `EMAILS_ENABLED=true`. Without it, email tasks will be queued but not processed.

### API Surface

**Authentication APIs (`/api/v1/auth`)**

| Endpoint                     | Method | Description |
|------------------------------|--------|-------------|
| `/auth/register`             | POST   | Register new user with email OTP |
| `/auth/login`                | POST   | Login and get access/refresh tokens |
| `/auth/refresh`              | POST   | Refresh access token |
| `/auth/logout`               | POST   | Logout and revoke tokens |
| `/auth/verify-otp`           | POST   | Verify email OTP |
| `/auth/resend-otp`           | POST   | Resend email verification OTP |
| `/auth/password-reset`       | POST   | Request password reset OTP |
| `/auth/password-reset/confirm` | POST | Confirm password reset with OTP |
| `/auth/google`               | POST   | Google OAuth login/registration |

**User APIs (`/api/v1/`)**

| Category        | Endpoint                     | Highlights |
|----------------|------------------------------|------------|
| FAQs           | `/faqs`                      | View published FAQs (public) |
| Dishes         | `/dishes`                    | Filtering, pagination, featured, top-rated, by cuisine/mood |
| Cuisines       | `/cuisines`                  | Paginated catalogue lookup |
| Moods          | `/moods`                     | Paginated mood listing |
| Restaurants    | `/restaurants`               | Listing, detail, top-rated, nearby lookup |
| Reservations   | `/reservations`              | Create & list reservations |
| AI Suggestions | `/ai/suggestions`            | Random or top-rated dish recommendations |
| Featured       | `/featured`                  | Dish of the week feed |
| Search         | `/search`                    | Unified search across dishes, restaurants, cuisines |

**Admin APIs (`/api/v1/admin`)**

| Category     | Endpoint       | Highlights |
|--------------|----------------|------------|
| Dishes       | `/dishes`      | Create, update, soft-delete dishes |
| Cuisines     | `/cuisines`    | Manage cuisine catalogue |
| Moods        | `/moods`       | Manage mood catalogue |
| Restaurants  | `/restaurants` | Create, update, soft-delete restaurants |
| FAQs         | `/faqs`        | Create, update, delete FAQs |

All collection endpoints support pagination (`limit`, `offset`) and filtering where applicable.

### Testing & Tooling
```bash
# Run tests
pytest

# Optional format + lint
make format
make lint
```

### Notes
- **Email & Celery:** Email delivery is disabled by default (`EMAILS_ENABLED=false`). The API gracefully handles Celery/Redis unavailability - registration will succeed even if email tasks fail (errors are logged).
- **Redis:** Required only if using email features. The API works without Redis, but email tasks won't be processed.
- **Soft Deletes:** Delete operations use soft-deletes (`is_deleted`) to preserve historical data.
- **Geolocation:** Nearby restaurant search uses a Haversine distance expression (requires latitude/longitude).
- **Seed Data:** Faker seed data is intended for development/demo usage only.

### Troubleshooting

**Registration returns 500 error:**
- Check if Redis is running (if `EMAILS_ENABLED=true`)
- Check application logs for Celery connection errors
- The API now handles Redis unavailability gracefully - registration should succeed even without Redis

**Emails not being sent:**
- Verify `EMAILS_ENABLED=true` in `.env`
- Check SMTP credentials are correct
- Ensure Celery worker is running: `celery -A app.core.celery_app worker --loglevel=info`
- Check Redis is accessible: `redis-cli ping` (should return `PONG`)

**Windows-specific:**
- Use `env\Scripts\activate` instead of `source env/bin/activate`
- Redis on Windows: Use Docker or Memurai (Redis for Windows)
- Path separators: Use backslashes in Windows paths
