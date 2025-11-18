# Admin API Access Guide

## Overview

Admin APIs are protected and require:
1. **Authentication**: A valid JWT access token
2. **Authorization**: User must have `is_staff=True` OR `is_superuser=True`

## Step 1: Create an Admin User

You have two options to create an admin user:

### Option A: Using Seed Script (Recommended)

The project includes a fixture file with a pre-configured admin user:

**File**: `fixtures/users/users.json`
```json
{
  "email": "admin@kyakhao.com",
  "password": "AdminPassword123!",
  "is_staff": true,
  "is_superuser": true,
  "role": "admin"
}
```

Run the seed script:
```bash
python seed_database.py
```

This will create the admin user if it doesn't exist, or update it if it does.

### Option B: Manual Database Update

If you already have a user account, you can update it directly in the database:

```sql
UPDATE users 
SET is_staff = true, 
    is_superuser = true,
    role = 'admin',
    profile_status = 'active'
WHERE email = 'your-email@example.com';
```

## Step 2: Login to Get Access Token

### Using Swagger UI (Easiest)

1. Start the API server:
   ```bash
   uvicorn main:app --reload
   ```

2. Open Swagger UI: `http://localhost:8000/docs`

3. Go to the **Authentication** section

4. Use the `/auth/login` endpoint:
   - **Email**: `admin@kyakhao.com`
   - **Password**: `AdminPassword123!`

5. Copy the `access_token` from the response

6. Click the **"Authorize"** button at the top of Swagger UI

7. Enter: `Bearer <your-access-token>`

8. Now you can test admin endpoints!

### Using cURL

```bash
# 1. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -H "X-Device-Id: test-device-123" \
  -H "X-Device-Type: web" \
  -H "X-App-Version: 1.0.0" \
  -d '{
    "email": "admin@kyakhao.com",
    "password": "AdminPassword123!"
  }'

# Response will include:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "refresh_token": "...",
#   "token_type": "bearer"
# }

# 2. Use the access token for admin APIs
curl -X GET "http://localhost:8000/api/v1/admin/dishes" \
  -H "Authorization: Bearer <your-access-token>" \
  -H "X-Device-Id: test-device-123" \
  -H "X-Device-Type: web" \
  -H "X-App-Version: 1.0.0"
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "X-Device-Id": "test-device-123",
    "X-Device-Type": "web",
    "X-App-Version": "1.0.0"
}

# 1. Login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "admin@kyakhao.com",
        "password": "AdminPassword123!"
    },
    headers=HEADERS
)

access_token = login_response.json()["data"]["access_token"]

# 2. Use token for admin APIs
admin_headers = {
    **HEADERS,
    "Authorization": f"Bearer {access_token}"
}

# Example: Get all dishes
dishes_response = requests.get(
    f"{BASE_URL}/admin/dishes",
    headers=admin_headers
)

print(dishes_response.json())
```

## Step 3: Access Admin APIs

Once authenticated, you can access all admin endpoints:

### Admin Endpoints Available:

- **Dishes**: `/api/v1/admin/dishes`
  - `POST /admin/dishes` - Create dish
  - `GET /admin/dishes` - List all dishes
  - `GET /admin/dishes/{id}` - Get dish
  - `PUT /admin/dishes/{id}` - Update dish
  - `DELETE /admin/dishes/{id}` - Delete dish

- **Cuisines**: `/api/v1/admin/cuisines`
  - `POST /admin/cuisines` - Create cuisine
  - `GET /admin/cuisines` - List all cuisines
  - `GET /admin/cuisines/{id}` - Get cuisine
  - `PUT /admin/cuisines/{id}` - Update cuisine
  - `DELETE /admin/cuisines/{id}` - Delete cuisine

- **Moods**: `/api/v1/admin/moods`
  - `POST /admin/moods` - Create mood
  - `GET /admin/moods` - List all moods
  - `GET /admin/moods/{id}` - Get mood
  - `PUT /admin/moods/{id}` - Update mood
  - `DELETE /admin/moods/{id}` - Delete mood

- **Restaurants**: `/api/v1/admin/restaurants`
  - `POST /admin/restaurants` - Create restaurant
  - `GET /admin/restaurants` - List all restaurants
  - `GET /admin/restaurants/{id}` - Get restaurant
  - `PUT /admin/restaurants/{id}` - Update restaurant
  - `DELETE /admin/restaurants/{id}` - Delete restaurant

- **FAQs**: `/api/v1/admin/faqs`
  - `POST /admin/faqs` - Create FAQ
  - `GET /admin/faqs` - List all FAQs
  - `GET /admin/faqs/{id}` - Get FAQ
  - `PUT /admin/faqs/{id}` - Update FAQ
  - `DELETE /admin/faqs/{id}` - Delete FAQ

## Required Headers

All API requests (including admin) require these headers:

- `X-Device-Id`: Device identifier (e.g., "device-123")
- `X-Device-Type`: Device type (e.g., "web", "ios", "android", "desktop")
- `X-App-Version`: App version (e.g., "1.0.0")
- `Authorization`: Bearer token (for authenticated endpoints)

## Permission Levels

### Admin Access (`is_staff=True` OR `is_superuser=True`)
- Can access all admin endpoints
- Can manage dishes, cuisines, moods, restaurants, FAQs

### Super Admin (`is_superuser=True`)
- Has all admin permissions
- Can perform additional super admin operations (if any are implemented)

## Troubleshooting

### Error: "Admin access required" (403)
- **Cause**: User doesn't have `is_staff=True` or `is_superuser=True`
- **Solution**: Update the user in the database or use the seed script

### Error: "Invalid token" (401)
- **Cause**: Token expired or invalid
- **Solution**: Login again to get a new token

### Error: "Missing headers"
- **Cause**: Required headers (`X-Device-Id`, `X-Device-Type`, `X-App-Version`) are missing
- **Solution**: Include all required headers in your request

## Quick Test

Test admin access with this simple command:

```bash
# Login and get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -H "X-Device-Id: test-123" \
  -H "X-Device-Type: web" \
  -H "X-App-Version: 1.0.0" \
  -d '{"email":"admin@kyakhao.com","password":"AdminPassword123!"}' \
  | jq -r '.data.access_token')

# Test admin endpoint
curl -X GET "http://localhost:8000/api/v1/admin/dishes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Device-Id: test-123" \
  -H "X-Device-Type: web" \
  -H "X-App-Version: 1.0.0"
```

## Notes

- Access tokens expire after 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Use the refresh token endpoint to get a new access token without re-logging in
- All admin operations use soft deletes (items are marked as deleted, not removed)

