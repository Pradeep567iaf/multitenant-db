# API Documentation

Complete API documentation for the Multi-Tenant System.

## Base URL

- **Superadmin**: http://localhost:8000
- **Tenant 1**: http://abc.localhost:8000
- **Tenant 2**: http://xyz.localhost:8000

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your_token>
```

---

## SUPERADMIN ENDPOINTS

### 1. Superadmin Login

**Endpoint**: `POST /api/v1/auth/superadmin/login`

**Description**: Authenticate as superadmin and receive JWT token.

**Request Body**:
```json
{
  "email": "admin@multitenant.com",
  "password": "admin123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### 2. Create Tenant

**Endpoint**: `POST /api/v1/superadmin/tenants`

**Authentication**: Required (Superadmin)

**Request Body**:
```json
{
  "name": "ABC Company",
  "subdomain": "abc",
  "email": "contact@abc.com",
  "password": "tenant123"
}
```

**Response**:
```json
{
  "id": 1,
  "name": "ABC Company",
  "subdomain": "abc",
  "email": "contact@abc.com",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "plan_id": null
}
```

**Validation**:
- `name`: 1-100 characters
- `subdomain`: 3-50 characters, alphanumeric only
- `email`: Valid email format
- `password`: Minimum 8 characters

---

### 3. List All Tenants

**Endpoint**: `GET /api/v1/superadmin/tenants`

**Authentication**: Required (Superadmin)

**Response**:
```json
[
  {
    "id": 1,
    "name": "ABC Company",
    "subdomain": "abc",
    "email": "contact@abc.com",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "plan_id": 1
  },
  {
    "id": 2,
    "name": "XYZ Corp",
    "subdomain": "xyz",
    "email": "contact@xyz.com",
    "is_active": true,
    "created_at": "2024-01-02T00:00:00",
    "plan_id": 2
  }
]
```

---

### 4. List Tenant Users

**Endpoint**: `GET /api/v1/superadmin/tenants/{tenant_id}/users`

**Authentication**: Required (Superadmin)

**Path Parameters**:
- `tenant_id`: Integer

**Response**:
```json
[
  {
    "id": 1,
    "tenant_id": 1,
    "email": "admin@abc.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  },
  {
    "id": 2,
    "tenant_id": 1,
    "email": "user@abc.com",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

---

### 5. Create Feature

**Endpoint**: `POST /api/v1/superadmin/features`

**Authentication**: Required (Superadmin)

**Request Body**:
```json
{
  "code": "F1",
  "name": "Feature One",
  "cost": 1.0
}
```

**Response**:
```json
{
  "id": 1,
  "code": "F1",
  "name": "Feature One",
  "cost": 1.0
}
```

**Validation**:
- `code`: Must match pattern `^F[1-9]$`
- `cost`: Must be greater than 0

---

### 6. Create Plan

**Endpoint**: `POST /api/v1/superadmin/plans`

**Authentication**: Required (Superadmin)

**Request Body**:
```json
{
  "name": "Basic",
  "description": "Basic plan with F1 and F2",
  "feature_ids": [1, 2]
}
```

**Response**:
```json
{
  "id": 1,
  "name": "Basic",
  "description": "Basic plan with F1 and F2",
  "created_at": "2024-01-01T00:00:00",
  "features": [
    {
      "id": 1,
      "code": "F1",
      "name": "Feature One",
      "cost": 1.0
    },
    {
      "id": 2,
      "code": "F2",
      "name": "Feature Two",
      "cost": 2.0
    }
  ]
}
```

**Validation**:
- `name`: Must be "Basic" or "Advanced"

---

### 7. List All Plans

**Endpoint**: `GET /api/v1/superadmin/plans`

**Authentication**: Required (Superadmin)

**Response**:
```json
[
  {
    "id": 1,
    "name": "Basic",
    "description": "Basic plan with F1 and F2",
    "created_at": "2024-01-01T00:00:00",
    "features": [...]
  },
  {
    "id": 2,
    "name": "Advanced",
    "description": "Advanced plan with all features",
    "created_at": "2024-01-01T00:00:00",
    "features": [...]
  }
]
```

---

### 8. Add Features to Plan

**Endpoint**: `POST /api/v1/superadmin/plans/{plan_id}/features`

**Authentication**: Required (Superadmin)

**Path Parameters**:
- `plan_id`: Integer

**Query Parameters**:
- `feature_ids`: Array of integers

**Example**: `POST /api/v1/superadmin/plans/1/features?feature_ids=1&feature_ids=2`

**Response**:
```json
{
  "message": "Features added successfully"
}
```

---

### 9. Trigger Billing Emails

**Endpoint**: `POST /api/v1/billing/send-emails`

**Authentication**: Required (Superadmin)

**Response**:
```json
{
  "message": "Billing email task initiated",
  "task_id": "abc123...",
  "total_tenants": 5
}
```

---

### 10. Get Billing Status

**Endpoint**: `GET /api/v1/billing/status`

**Authentication**: Required (Superadmin)

**Response**:
```json
{
  "total_tenants": 5,
  "total_revenue": 150.0,
  "tenants": [
    {
      "name": "ABC Company",
      "email": "contact@abc.com",
      "total_amount": 30.0
    },
    {
      "name": "XYZ Corp",
      "email": "contact@xyz.com",
      "total_amount": 50.0
    }
  ]
}
```

---

## TENANT ENDPOINTS

### 1. Tenant Login

**Endpoint**: `POST /api/v1/auth/tenant/login`

**Description**: Authenticate as tenant user. Must access via tenant subdomain.

**Request Body**:
```json
{
  "email": "admin@abc.com",
  "password": "tenant123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "plan_selection_required": true,
  "tenant_name": "ABC Company"
}
```

**Note**: Access this endpoint via tenant subdomain (e.g., abc.localhost:8000)

---

### 2. Select Plan

**Endpoint**: `POST /api/v1/tenant/plan/select`

**Authentication**: Required (Tenant User)

**Description**: Select plan on first login (Basic or Advanced).

**Request Body**:
```json
{
  "plan_name": "Basic"
}
```

**Response**:
```json
{
  "message": "Plan 'Basic' selected successfully",
  "plan_name": "Basic",
  "features_count": 2
}
```

**Validation**:
- `plan_name`: Must be "Basic" or "Advanced"
- Can only be done once per tenant

---

### 3. Create Tenant User

**Endpoint**: `POST /api/v1/tenant/users`

**Authentication**: Required (Tenant User)

**Request Body**:
```json
{
  "email": "newuser@abc.com",
  "password": "user123",
  "role": "user"
}
```

**Response**:
```json
{
  "id": 3,
  "tenant_id": 1,
  "email": "newuser@abc.com",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

**Validation**:
- `email`: Must be unique within tenant
- `password`: Minimum 8 characters
- `role`: Must be "admin" or "user"

---

### 4. List Tenant Users

**Endpoint**: `GET /api/v1/tenant/users`

**Authentication**: Required (Tenant User)

**Response**:
```json
[
  {
    "id": 1,
    "tenant_id": 1,
    "email": "admin@abc.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  },
  {
    "id": 2,
    "tenant_id": 1,
    "email": "user@abc.com",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

---

### 5. Update Tenant User

**Endpoint**: `PUT /api/v1/tenant/users/{user_id}`

**Authentication**: Required (Tenant User)

**Path Parameters**:
- `user_id`: Integer

**Request Body** (all fields optional):
```json
{
  "email": "updated@abc.com",
  "role": "admin",
  "is_active": false
}
```

**Response**:
```json
{
  "id": 2,
  "tenant_id": 1,
  "email": "updated@abc.com",
  "role": "admin",
  "is_active": false,
  "created_at": "2024-01-01T00:00:00"
}
```

---

### 6. Delete Tenant User

**Endpoint**: `DELETE /api/v1/tenant/users/{user_id}`

**Authentication**: Required (Tenant User)

**Path Parameters**:
- `user_id`: Integer

**Response**:
```json
{
  "message": "User deleted successfully"
}
```

**Note**: Cannot delete admin users

---

### 7. Use Feature

**Endpoint**: `POST /api/v1/tenant/features/use`

**Authentication**: Required (Tenant User)

**Description**: Record feature usage and increase billing.

**Request Body**:
```json
{
  "feature_code": "F1"
}
```

**Response**:
```json
{
  "message": "Feature usage recorded",
  "feature_code": "F1",
  "cost": 1.0,
  "total_usage_count": 5,
  "total_cost": 5.0
}
```

**Validation**:
- `feature_code`: Must be available in tenant's selected plan
- Tenant must have selected a plan

---

### 8. Get Current Billing

**Endpoint**: `GET /api/v1/tenant/billing/current`

**Authentication**: Required (Tenant User)

**Response**:
```json
{
  "total_amount": 15.0,
  "billing_period_start": "2024-01-01T00:00:00",
  "billing_period_end": "2024-02-01T00:00:00",
  "breakdown": [
    {
      "feature_code": "F1",
      "usage_count": 5,
      "total_cost": 5.0
    },
    {
      "feature_code": "F2",
      "usage_count": 5,
      "total_cost": 10.0
    }
  ]
}
```

---

### 9. Get Billing History

**Endpoint**: `GET /api/v1/tenant/billing/history`

**Authentication**: Required (Tenant User)

**Response**:
```json
[
  {
    "id": 1,
    "tenant_id": 1,
    "feature_code": "F1",
    "usage_count": 10,
    "total_cost": 10.0,
    "billing_period_start": "2024-01-01T00:00:00",
    "billing_period_end": "2024-02-01T00:00:00",
    "is_sent": true
  },
  {
    "id": 2,
    "tenant_id": 1,
    "feature_code": "F2",
    "usage_count": 5,
    "total_cost": 10.0,
    "billing_period_start": "2024-01-01T00:00:00",
    "billing_period_end": "2024-02-01T00:00:00",
    "is_sent": true
  }
]
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Testing with cURL

### Example 1: Superadmin Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/superadmin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@multitenant.com",
    "password": "admin123"
  }'
```

### Example 2: Create Tenant

```bash
curl -X POST http://localhost:8000/api/v1/superadmin/tenants \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Test Company",
    "subdomain": "test",
    "email": "test@test.com",
    "password": "test123"
  }'
```

### Example 3: Tenant Login (via subdomain)

```bash
curl -X POST http://test.localhost:8000/api/v1/auth/tenant/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "test123"
  }'
```

### Example 4: Use Feature

```bash
curl -X POST http://test.localhost:8000/api/v1/tenant/features/use \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TENANT_TOKEN" \
  -d '{
    "feature_code": "F1"
  }'
```

---

## Interactive Documentation

Once the server is running, you can access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive interfaces to test all endpoints directly from your browser.
