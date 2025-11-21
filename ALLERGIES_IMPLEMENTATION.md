# Allergies Onboarding Feature - Implementation Summary

## Overview
This document describes the implementation of the allergies onboarding feature in the FastAPI codebase.

## Files Created/Modified

### Models
- **`app/models/food.py`**: 
  - Added `Allergy` model (string ID, not UUID)
  - Added `UserAllergyAssociation` table for many-to-many relationship

- **`app/models/user.py`**: 
  - Added `allergies` relationship to User model

- **`app/models/__init__.py`**: 
  - Exported `Allergy` model

### Schemas
- **`app/schemas/allergy.py`**: 
  - `AllergyResponse`: Response schema for allergy
  - `AllergyCreate`: Schema for creating allergies (admin)
  - `UserAllergyUpdate`: Schema for updating user allergies
  - `UserAllergyResponse`: Response schema for user allergies update

### API Endpoints

#### Public Endpoints
- **`app/api/v1/endpoints/allergies.py`**:
  - `GET /api/v1/allergies` - Get list of all available allergies (public)

#### User Endpoints
- **`app/api/v1/endpoints/user_allergies.py`**:
  - `PUT /api/v1/users/{user_id}/allergies` - Update user's selected allergies (auth required, owner or admin)

#### Admin Endpoints
- **`app/api/v1/admin/endpoints/allergies.py`**:
  - `POST /api/v1/admin/allergies` - Create new allergy (admin only)
  - `DELETE /api/v1/admin/allergies/{allergy_id}` - Delete allergy (admin only)

### Database Migration
- **`alembic/versions/20251119160000_add_allergies_tables.py`**:
  - Creates `allergies` table
  - Creates `user_allergies` association table
  - Includes proper indexes and foreign keys

### Seed Script
- **`scripts/seed_allergies.py`**:
  - Seeds default allergies: wheat, peanut, milk, eggs, soy, nuts

## API Endpoints Details

### 1. GET /api/v1/allergies
**Public endpoint** - No authentication required

**Response:**
```json
[
  {"id": "wheat", "name": "Wheat"},
  {"id": "peanut", "name": "Peanut"},
  {"id": "milk", "name": "Milk"},
  {"id": "eggs", "name": "Eggs"},
  {"id": "soy", "name": "Soy"},
  {"id": "nuts", "name": "Nuts"}
]
```

### 2. PUT /api/v1/users/{user_id}/allergies
**Auth required** - User can only update their own allergies, admins can update any user's allergies

**Request:**
```json
{
  "allergies": ["wheat", "milk", "nuts"]
}
```

**Response:**
```json
{
  "userId": "123",
  "allergies": ["wheat", "milk", "nuts"],
  "updatedAt": "2025-11-19T12:00:00Z"
}
```

**Validation:**
- All allergy IDs must exist in the allergies table
- Returns 400 if invalid allergy IDs are provided

### 3. POST /api/v1/admin/allergies
**Admin only**

**Request:**
```json
{
  "id": "shellfish",
  "name": "Shellfish",
  "type": "food"
}
```

**Response:**
```json
{
  "id": "shellfish",
  "name": "Shellfish",
  "type": "food"
}
```

### 4. DELETE /api/v1/admin/allergies/{allergy_id}
**Admin only**

**Response:**
```json
{
  "message": "Allergy 'shellfish' deleted successfully"
}
```

## Setup Instructions

### 1. Run Migration
```bash
cd kyakhao_API
alembic upgrade head
```

### 2. Seed Default Allergies
```bash
python scripts/seed_allergies.py
```

### 3. Start Server
```bash
python main.py
```

## Testing with cURL

### Get Allergies (Public)
```bash
curl -X GET http://localhost:8000/api/v1/allergies
```

### Update User Allergies
```bash
curl -X PUT http://localhost:8000/api/v1/users/{user_id}/allergies \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"allergies": ["wheat", "milk", "nuts"]}'
```

### Create Allergy (Admin)
```bash
curl -X POST http://localhost:8000/api/v1/admin/allergies \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "shellfish", "name": "Shellfish", "type": "food"}'
```

### Delete Allergy (Admin)
```bash
curl -X DELETE http://localhost:8000/api/v1/admin/allergies/shellfish \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## Notes

- The `Allergy` model uses string IDs (not UUIDs) for simplicity
- User allergies are stored in a many-to-many relationship via `user_allergies` table
- When updating user allergies, existing associations are deleted and new ones are created (transactional)
- All endpoints return appropriate HTTP status codes and error messages
- Admin endpoints require admin authentication via `get_current_admin` dependency

