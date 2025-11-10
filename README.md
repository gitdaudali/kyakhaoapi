## Cup Streaming Auth API

This repository is a focused authentication service extracted from the larger Cup Streaming platform.  
It keeps every auth-related capability—registration, login, token management, OTP verification, password resets, and Google OAuth—while removing all streaming, subscription, and content features.

### What’s Included
- FastAPI application exposing only `/api/v1/auth` routes
- Complete JWT access/refresh token lifecycle with device tracking
- Email + OTP workflows for registration and password reset
- Google OAuth sign-up/sign-in & account linking
- Token revocation, blacklist, and multi-device support
- Shared response handling, security headers, and error formatting from the original project

### Directory Overview
```
Cup_Streaming_Auth/
├── alembic/              # Alembic migrations (users, tokens, verification)
├── app/
│   ├── api/v1/
│   │   ├── api.py        # Router that exposes only /auth
│   │   └── endpoints/
│   │       └── auth.py   # Authentication endpoints
│   ├── core/             # Core config, auth helpers, DB, messaging, responses
│   ├── models/           # User, token, verification models + SQLModel base
│   ├── schemas/          # Auth, user, and Google OAuth schemas
│   ├── tasks/            # Email-related Celery tasks
│   └── utils/            # Auth utilities, Google OAuth helpers, email templates
├── app/templates/        # Email templates (verification, password reset, OTP)
├── main.py               # FastAPI entry point
├── requirements.txt      # Python dependencies
└── README.md             # You're reading it
```

### Getting Started
1. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**  
   Copy `.env.example` if present, or create `.env` with at least:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=cup_streaming_auth
   SECRET_KEY=super-secret-key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   EMAILS_ENABLED=false
   ```
   Configure SMTP and Google OAuth settings if you intend to use them.

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the API**
   ```bash
   uvicorn main:app --reload
   ```
   Visit `http://localhost:8000/docs` for interactive documentation.

### Available Endpoints ( `/api/v1/auth` )
- `POST /register` — Email/Password registration with OTP email
- `POST /login` — Authenticates and returns access + refresh tokens
- `POST /refresh` — Rotates refresh token; issues new token pair
- `POST /logout` — Revokes a refresh token or all active sessions
- `POST /password/reset` — Sends password reset OTP
- `POST /password/reset/confirm` — Confirms reset via OTP
- `POST /change-password` — Changes password (requires auth)
- `POST /verify-otp` — Verifies email with OTP
- `GET  /me` — Returns current user (requires auth)
- `GET  /token-info` — Returns token metadata
- `POST /social/google` — Google OAuth sign-in/sign-up

### Useful Commands
```bash
# Run formatters & checks
make format
make lint
pytest

# Run celery worker for emails (optional)
celery -A app.tasks.email_tasks worker --loglevel=info
```

### Notes
- Non-auth models, endpoints, and utilities from the original project have been removed to keep dependencies light.
- Email delivery is disabled by default; enable via `.env` when ready.
- Token storage and blacklist tables remain untouched to ensure logout and multi-device logic keep working exactly as before.
