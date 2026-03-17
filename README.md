# Multi-Tenant System

A simplified multi-tenant system built with FastAPI, PostgreSQL, and Celery that supports subdomain-based tenant isolation.

## Features

- **Superadmin Portal** (localhost:8000)
  - Create and manage tenants
  - View all tenants and their users
  - Create plans (Basic/Advanced) with features
  - Trigger billing emails to all tenants

- **Tenant Portal** (abc.localhost:8000, xyz.localhost:8000)
  - Subdomain-based access
  - Plan selection on first login
  - Create and manage tenant users
  - Track feature usage and billing
  - Receive monthly billing statements via email

## Technology Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **Task Queue**: Celery with Redis
- **Email**: SMTP service

## Project Structure

```
multi-tenant-system/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   ├── superadmin.py
│   │       │   ├── tenant.py
│   │       │   └── billing.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── middleware.py
│   │   └── authentication.py
│   ├── db/
│   │   ├── session.py
│   │   └── base.py
│   ├── models/
│   │   ├── superadmin.py
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── plan.py
│   │   ├── feature.py
│   │   ├── billing.py
│   │   └── plan_feature.py
│   ├── schemas/
│   │   ├── tenant.py
│   │   ├── superadmin.py
│   │   ├── auth.py
│   │   ├── plan.py
│   │   ├── feature.py
│   │   ├── user.py
│   │   └── billing.py
│   ├── services/
│   │   ├── billing_service.py
│   │   └── email_service.py
│   ├── tasks/
│   │   └── celery_tasks.py
│   └── main.py
├── celery_worker.py
├── requirements.txt
├── .env
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file with your credentials:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/multitenant_db

# JWT
SECRET_KEY_SUPERADMIN=your_superadmin_secret_key
SECRET_KEY_TENANT=your_tenant_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=noreply@multitenant.com
```

### 3. Create Database

```bash
createdb multitenant_db
```

Or using psql:
```sql
CREATE DATABASE multitenant_db;
```

### 4. Initialize Database

The database tables will be created automatically when you start the application.

### 5. Start Redis

```bash
redis-server
```

### 6. Start Celery Worker

```bash
celery -A celery_worker worker --loglevel=info
```

### 7. Start FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- Superadmin: http://localhost:8000
- Tenant 1: http://abc.localhost:8000
- Tenant 2: http://xyz.localhost:8000

## API Endpoints

### For Superadmin (http://localhost:8000/)

#### Authentication
- `POST /api/v1/auth/superadmin/login` - Login as Superadmin

#### Tenant Management
- `POST /api/v1/superadmin/tenants` - Create Tenant
- `GET /api/v1/superadmin/tenants` - List all Tenants
- `GET /api/v1/superadmin/tenants/{tenant_id}/users` - List tenant users

#### Plan Management
- `POST /api/v1/superadmin/plans` - Create plan
- `GET /api/v1/superadmin/plans` - List all plans
- `POST /api/v1/superadmin/features` - Create feature
- `POST /api/v1/superadmin/plans/{plan_id}/features` - Add features to plan

#### Billing
- `POST /api/v1/billing/send-emails` - Trigger billing emails
- `GET /api/v1/billing/status` - Get billing status

### For Tenant (http://abc.localhost:8000/)

#### Authentication
- `POST /api/v1/auth/tenant/login` - Login as Tenant user

#### Plan Selection
- `POST /api/v1/tenant/plan/select` - Select plan (first login only)

#### User Management
- `POST /api/v1/tenant/users` - Create tenant user
- `GET /api/v1/tenant/users` - List tenant users
- `PUT /api/v1/tenant/users/{user_id}` - Update user
- `DELETE /api/v1/tenant/users/{user_id}` - Delete user

#### Feature Usage & Billing
- `POST /api/v1/tenant/features/use` - Record feature usage
- `GET /api/v1/tenant/billing/current` - Get current billing
- `GET /api/v1/tenant/billing/history` - Get billing history

## Usage Flow

### 1. Create Initial Superadmin

You'll need to manually insert a superadmin into the database or create an endpoint for initial setup. Here's a SQL script:

```sql
INSERT INTO super_admins (email, hashed_password, created_at)
VALUES (
    'admin@example.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- password: "admin123"
    NOW()
);
```

### 2. Create Plans and Features

Login as superadmin and create:
- Features: F1 ($1), F2 ($2), F3 ($3), F4 ($4)
- Plans: Basic (F1, F2), Advanced (F1, F2, F3, F4)

### 3. Create Tenants

Create tenants with unique subdomains (e.g., "abc", "xyz").

### 4. Tenant Login

Tenants can login using their subdomain:
- abc.localhost:8000 → Login with tenant credentials
- Select plan on first login

### 5. Use Features

Tenants can record feature usage, which increments billing.

### 6. Send Billing Emails

Superadmin can trigger bulk billing emails to all tenants.

## Testing with Subdomains (Windows)

For local testing, add entries to your hosts file (`C:\Windows\System32\drivers\etc\hosts`):

```
127.0.0.1    localhost
127.0.0.1    abc.localhost
127.0.0.1    xyz.localhost
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing with Postman

### Tenant Endpoint Testing

When testing tenant endpoints in Postman, you must include the `X-Tenant-Subdomain` header to route requests to the correct tenant.

#### Required Headers:
```
X-Tenant-Subdomain: abc
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Example Setup:

**1. Tenant Login Request:**
- **Method**: POST
- **URL**: `http://localhost:8000/api/v1/auth/tenant/login`
- **Headers**:
  ```
  X-Tenant-Subdomain: abc
  Content-Type: application/json
  ```
- **Body** (raw JSON):
  ```json
  {
    "email": "abc@gmail.com",
    "password": "abcuser@123"
  }
  ```

**2. After Login - Authenticated Requests:**
- **Method**: POST/GET (depending on endpoint)
- **URL**: `http://localhost:8000/api/v1/tenant/...`
- **Headers**:
  ```
  X-Tenant-Subdomain: abc
  Content-Type: application/json
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```

#### Common Tenant Endpoints to Test:

**Select Plan (First Login Only):**
```
POST /api/v1/tenant/plan/select
Body: {"plan_name": "Basic"}
```

**Create Tenant User:**
```
POST /api/v1/tenant/users
Body: {"email": "user@abc.com", "password": "user123", "role": "user"}
```

**List Tenant Users:**
```
GET /api/v1/tenant/users
```

**Use Feature:**
```
POST /api/v1/tenant/features/use
Body: {"feature_code": "F1"}
```

**Check Current Billing:**
```
GET /api/v1/tenant/billing/current
```

#### Switching Between Tenants:
To test different tenants, simply change the `X-Tenant-Subdomain` header value:
- For tenant "abc": `X-Tenant-Subdomain: abc`
- For tenant "xyz": `X-Tenant-Subdomain: xyz`

#### Superadmin Testing:
For superadmin endpoints, **do NOT include** the `X-Tenant-Subdomain` header:
```
Content-Type: application/json
Authorization: Bearer YOUR_SUPERADMIN_TOKEN
```

### Postman Collection Tips:

1. **Create Environment Variables:**
   - `base_url`: `http://localhost:8000`
   - `tenant_subdomain`: `abc`
   - `auth_token`: `YOUR_JWT_TOKEN`

2. **Use Variables in Requests:**
   - URL: `{{base_url}}/api/v1/tenant/users`
   - Header: `X-Tenant-Subdomain: {{tenant_subdomain}}`
   - Header: `Authorization: Bearer {{auth_token}}`

3. **Auto-save Tokens:**
   In the login request Tests tab:
   ```javascript
   const response = pm.response.json();
   if (response.access_token) {
       pm.environment.set("auth_token", response.access_token);
   }
   ```

## Testing with Subdomains (Windows)
## Important Notes

1. **Subdomain Routing**: The middleware automatically routes requests based on subdomain:
   - `localhost:8000` → Superadmin endpoints
   - `abc.localhost:8000` → Tenant endpoints for tenant "abc"

2. **Plan Selection**: Tenants must select a plan (Basic/Advanced) on first login before accessing other features.

3. **Feature Costs**:
   - F1: $1 per use
   - F2: $2 per use
   - F3: $3 per use
   - F4: $4 per use

4. **Billing Cycle**: Monthly billing cycle starting from the 1st of each month.

## Troubleshooting

### Redis Connection Error
Ensure Redis is running:
```bash
redis-server
```

### Database Connection Error
Check PostgreSQL is running and credentials in `.env` are correct.

### Email Sending Error
Verify SMTP credentials in `.env`. For Gmail, you need an app-specific password.

## License

MIT License
