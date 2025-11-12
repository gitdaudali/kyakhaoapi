## Kya Khao Platform API

The service now combines authentication with a rich food discovery experience for the Kya Khao platform. Alongside the original auth flows (registration, login, tokens, OTP, Google OAuth), it exposes curated content for dishes, cuisines, moods, restaurants, AI suggestions, and reservations.

### What’s Included
- FastAPI application with `/api/v1/auth` plus new food-domain routers (dishes, cuisines, moods, restaurants, reservations, search, featured, AI suggestions)
- PostgreSQL + SQLAlchemy models for cuisines, moods, restaurants, dishes, and reservations
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
│   ├── api/v1/
│   │   ├── api.py               # Aggregates all v1 routers
│   │   └── endpoints/           # auth, dishes, restaurants, cuisines, moods, reservations, search, featured, AI
│   ├── core/                    # Config, DB, auth helpers, response handling
│   ├── models/                  # Auth + food SQLAlchemy models
│   ├── schemas/                 # Pydantic schemas (auth, food, pagination, search, AI)
│   ├── tasks/                   # Celery email tasks
│   └── utils/                   # Auth utils, Google OAuth, pagination, filters, seed data
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
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=kyakhao
   SECRET_KEY=super-secret-key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   EMAILS_ENABLED=false
   GOOGLE_OAUTH_ENABLED=false
   ```
4. **Run migrations**
   ```bash
   alembic upgrade head
   ```
5. **(Optional) Seed dummy data**
   ```bash
   env\Scripts\python -m app.utils.data_seed
   ```
6. **Start the API**
   ```bash
   uvicorn main:app --reload
   ```
   Visit `http://localhost:8000/docs` for interactive OpenAPI docs.

### API Surface
| Category        | Endpoint (prefix `/api/v1`) | Highlights |
|----------------|-----------------------------|------------|
| Auth           | `/auth/*`                    | Registration, login, refresh, logout, OTP, Google OAuth |
| Cuisines       | `/cuisines`                  | CRUD + pagination |
| Moods          | `/moods`                     | CRUD + pagination |
| Restaurants    | `/restaurants`               | CRUD, top rated, nearby lookup |
| Dishes         | `/dishes`                    | CRUD, filtering, featured, top-rated, by cuisine/mood |
| Reservations   | `/reservations`              | Create & list reservations |
| AI Suggestions | `/ai/suggestions`            | Random or top-rated dish recommendations |
| Featured       | `/featured`                  | Dish of the week feed |
| Search         | `/search`                    | Unified search across dishes, restaurants, cuisines |

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
- Email delivery remains disabled by default; enable SMTP settings when ready.
- Delete operations use soft-deletes (`is_deleted`) to preserve historical data.
- Nearby restaurant search uses a Haversine distance expression (requires latitude/longitude).
- Faker seed data is intended for development/demo usage only.
