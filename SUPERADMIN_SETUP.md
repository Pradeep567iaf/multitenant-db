# Superadmin Creation API

## Endpoint Details

### Create Superadmin (Initial Setup)

**Endpoint**: `POST /api/v1/auth/superadmin/create`

**Description**: Creates the first superadmin account for initial system setup.

**Request URL**: http://localhost:8000/api/v1/auth/superadmin/create

**Method**: POST

**Authentication**: Not required (for initial setup only)

---

## Request Format

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "email": "admin@multitenant.com",
  "password": "admin123"
}
```

### Validation Rules
- **Email**: Must be a valid email format, unique in the system
- **Password**: Minimum 8 characters

---

## Response

### Success Response (201 Created)
```json
{
  "id": 1,
  "email": "admin@multitenant.com"
}
```

### Error Responses

#### 400 Bad Request - Email Already Exists
```json
{
  "detail": "Superadmin with this email already exists"
}
```

#### 422 Unprocessable Entity - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Usage Examples

### Using Swagger UI

1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/auth/superadmin/create`
3. Click "Try it out"
4. Enter request body:
```json
{
  "email": "admin@multitenant.com",
  "password": "admin123"
}
```
5. Click "Execute"
6. You should receive a response with the superadmin ID and email

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/auth/superadmin/create" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@multitenant.com",
    "password": "admin123"
  }'
```

### Using Python Requests

```python
import requests

url = "http://localhost:8000/api/v1/auth/superadmin/create"
data = {
    "email": "admin@multitenant.com",
    "password": "admin123"
}

response = requests.post(url, json=data)
print(response.json())
```

### Using Postman

1. Create a new POST request
2. URL: `http://localhost:8000/api/v1/auth/superadmin/create`
3. Go to Body tab → Select "raw" → Select "JSON"
4. Enter JSON:
```json
{
  "email": "admin@multitenant.com",
  "password": "admin123"
}
```
5. Click "Send"

---

## Complete Setup Workflow

### Step 1: Create Superadmin
```bash
POST /api/v1/auth/superadmin/create
{
  "email": "admin@multitenant.com",
  "password": "admin123"
}
```

### Step 2: Login as Superadmin
```bash
POST /api/v1/auth/superadmin/login
{
  "email": "admin@multitenant.com",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Step 3: Use Token for Protected Endpoints

Copy the `access_token` from the login response and use it in subsequent requests:

```bash
GET /api/v1/superadmin/tenants
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

## Security Considerations

### ⚠️ IMPORTANT: Production Deployment

The `/superadmin/create` endpoint is designed for **initial setup only**. In production:

1. **Disable after first use**: Add a check to prevent multiple superadmins
2. **Or protect with setup token**: Require a special environment variable
3. **Or remove entirely**: Create superadmin directly in database

### Example: Disable After First Superadmin

The current implementation already prevents creating multiple superadmins with the same email.

### Example: Protect with Setup Token (Optional Enhancement)

You can modify the endpoint to require a setup token:

```python
@router.post("/superadmin/create")
async def create_superadmin(
    superadmin_data: SuperAdminCreate,
    db: Session = Depends(get_db),
    setup_token: str = Header(...)
):
    # Verify setup token matches environment variable
    if setup_token != os.getenv("SETUP_TOKEN"):
        raise HTTPException(status_code=403, detail="Invalid setup token")
    # ... rest of code
```

---

## Testing the Endpoint

### Test 1: Create First Superadmin (Should Succeed)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/superadmin/create" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "SecurePass123!"}'
```

Expected: 201 Created with superadmin details

### Test 2: Try Creating Duplicate Superadmin (Should Fail)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/superadmin/create" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "AnotherPass456!"}'
```

Expected: 400 Bad Request - "Superadmin with this email already exists"

### Test 3: Login with Created Superadmin

```bash
curl -X POST "http://localhost:8000/api/v1/auth/superadmin/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "SecurePass123!"}'
```

Expected: 200 OK with access token

---

## Troubleshooting

### Issue: "Superadmin already exists"

**Solution**: If you want to create a new superadmin, either:
1. Use a different email address
2. Delete the existing superadmin from the database:
```sql
DELETE FROM super_admins WHERE email = 'admin@multitenant.com';
```

### Issue: Database connection error

**Solution**: Ensure PostgreSQL is running and `.env` file has correct credentials:
```
DATABASE_URL=postgresql://postgres:root@localhost:5432/multitenant
```

### Issue: bcrypt/passlib error

**Solution**: Run the fix script:
```bash
fix_bcrypt.bat
```

---

## Alternative: Direct Database Insert

If you prefer to create the superadmin directly in the database instead of using the API:

```sql
INSERT INTO super_admins (email, hashed_password, created_at)
VALUES (
    'admin@multitenant.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    NOW()
);
```

This creates a superadmin with password: `admin123`

---

## Summary

✅ **Endpoint**: `POST /api/v1/auth/superadmin/create`  
✅ **Purpose**: Initial superadmin setup  
✅ **Authentication**: None required  
✅ **Validation**: Email uniqueness, password length (min 8 chars)  
✅ **Security**: Prevents duplicate emails  
⚠️ **Production**: Consider disabling or protecting after initial setup  
