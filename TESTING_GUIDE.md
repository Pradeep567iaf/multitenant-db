# Multi-Tenant System - Complete Testing Guide

## Prerequisites Checklist

✅ PostgreSQL database created with all tables  
✅ Python 3.9+ installed  
✅ Redis installed and running  
✅ Environment variables configured in `.env`  

---

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd c:\Multi-tenant-system

# Create virtual environment (if not already done)
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Or on Windows Command Prompt:
.\venv\Scripts\activate.bat

# Install all dependencies
pip install -r requirements.txt
```

---

## Step 2: Verify Environment Configuration

Open `c:\Multi-tenant-system\.env` and verify:

```env
# Update with your PostgreSQL credentials
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/multitenant_db

# JWT keys (already configured)
SECRET_KEY_SUPERADMIN=9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2c1b0a9f8e
SECRET_KEY_TENANT=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration (Update with your SMTP credentials)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=noreply@multitenant.com
```

**For Gmail SMTP:**
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password in `SMTP_PASSWORD`

---

## Step 3: Start Redis Server

```bash
# On Windows, if Redis is installed as a service:
redis-server

# Or check if Redis is already running:
redis-cli ping
# Should return: PONG
```

---

## Step 4: Initialize Database (Optional - if not already done)

If you haven't run the SQL script yet:

```bash
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Run database initialization
python init_db.py
```

This will create:
- 1 Superadmin account
- 4 Features (F1-F4)
- 2 Plans (Basic & Advanced)
- Feature-Plan associations

---

## Step 5: Start Celery Worker (Terminal 1)

Open a **new terminal window**:

```bash
# Navigate to project directory
cd c:\Multi-tenant-system

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start Celery worker
celery -A celery_worker worker --loglevel=info
```

You should see output like:
```
 -------------- celery@YOURPC v5.3.4 (emerald-rush)
--- ***** ----- 
-- ******* ---- Windows-10-10.0.xxxxxx
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         worker:0x...
- ** ---------- .> transport:   redis://localhost:6379//0
- ** ---------- .> results:     redis://localhost:6379//0
```

**Keep this terminal running!**

---

## Step 6: Start FastAPI Server (Terminal 2)

Open another **new terminal window**:

```bash
# Navigate to project directory
cd c:\Multi-tenant-system

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx]
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Step 7: Access API Documentation

Open your browser and go to:

**Swagger UI (Interactive API Documentation):**
```
http://localhost:8000/docs
```

**Alternative - ReDoc:**
```
http://localhost:8000/redoc
```

---

## Step 8: Complete Testing Workflow

### 📋 **TEST SCENARIO 1: Superadmin Operations**

#### 1. Login as Superadmin

**Via Swagger UI (http://localhost:8000/docs):**
1. Find endpoint: `POST /api/v1/auth/superadmin/login`
2. Click "Try it out"
3. Enter request body:
```json
{
  "email": "admin@multitenant.com",
  "password": "admin123"
}
```
4. Click "Execute"
5. Copy the `access_token` from response

**Or via cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/superadmin/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"admin@multitenant.com\", \"password\": \"admin123\"}"
```

---

#### 2. Create First Tenant

**Request:**
```json
POST /api/v1/superadmin/tenants
Authorization: Bearer YOUR_SUPERADMIN_TOKEN

{
  "name": "ABC Company",
  "subdomain": "abc",
  "email": "contact@abc.com",
  "password": "abc12345"
}
```

**Expected Response:**
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

---

#### 3. Create Second Tenant

```json
POST /api/v1/superadmin/tenants
Authorization: Bearer YOUR_SUPERADMIN_TOKEN

{
  "name": "XYZ Corporation",
  "subdomain": "xyz",
  "email": "contact@xyz.com",
  "password": "xyz12345"
}
```

---

#### 4. List All Tenants

```bash
GET /api/v1/superadmin/tenants
Authorization: Bearer YOUR_SUPERADMIN_TOKEN
```

---

#### 5. View Plans (Already created by init_db.py)

```bash
GET /api/v1/superadmin/plans
Authorization: Bearer YOUR_SUPERADMIN_TOKEN
```

Should show:
- Basic Plan (F1, F2)
- Advanced Plan (F1, F2, F3, F4)

---

### 📋 **TEST SCENARIO 2: Tenant Operations (ABC Company)**

**Important:** For tenant operations, you need to access via subdomain.

#### Option A: Using Hosts File (Recommended)

Add to `C:\Windows\System32\drivers\etc\hosts`:
```
127.0.0.1    abc.localhost
127.0.0.1    xyz.localhost
```

Then access:
- ABC Company: http://abc.localhost:8000/docs
- XYZ Corporation: http://xyz.localhost:8000/docs

#### Option B: Using Host Header

In Swagger UI, click "Authorize" at top, then add header:
```
Host: abc.localhost
```

---

#### 1. Login as Tenant User (ABC Company)

Go to: http://abc.localhost:8000/docs

```json
POST /api/v1/auth/tenant/login

{
  "email": "contact@abc.com",
  "password": "abc12345"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "plan_selection_required": true,
  "tenant_name": "ABC Company"
}
```

Note: `plan_selection_required: true` means plan selection is needed.

---

#### 2. Select Plan (First Login Requirement)

```json
POST /api/v1/tenant/plan/select
Authorization: Bearer YOUR_TENANT_TOKEN

{
  "plan_name": "Basic"
}
```

**Response:**
```json
{
  "message": "Plan 'Basic' selected successfully",
  "plan_name": "Basic",
  "features_count": 2
}
```

Now tenant can use features F1 and F2 only.

---

#### 3. Create Tenant User

```json
POST /api/v1/tenant/users
Authorization: Bearer YOUR_TENANT_TOKEN

{
  "email": "user@abc.com",
  "password": "user12345",
  "role": "user"
}
```

---

#### 4. List Tenant Users

```bash
GET /api/v1/tenant/users
Authorization: Bearer YOUR_TENANT_TOKEN
```

---

#### 5. Use Feature F1 (Costs $1)

```json
POST /api/v1/tenant/features/use
Authorization: Bearer YOUR_TENANT_TOKEN

{
  "feature_code": "F1"
}
```

**Response:**
```json
{
  "message": "Feature usage recorded",
  "feature_code": "F1",
  "cost": 1.0,
  "total_usage_count": 1,
  "total_cost": 1.0
}
```

---

#### 6. Use Feature F2 (Costs $2)

```json
POST /api/v1/tenant/features/use
Authorization: Bearer YOUR_TENANT_TOKEN

{
  "feature_code": "F2"
}
```

---

#### 7. Try Using Feature F3 (Should Fail - Not in Basic Plan)

```json
POST /api/v1/tenant/features/use
Authorization: Bearer YOUR_TENANT_TOKEN

{
  "feature_code": "F3"
}
```

**Expected Error:**
```json
{
  "detail": "Feature F3 is not included in tenant's plan"
}
```

---

#### 8. Check Current Billing

```bash
GET /api/v1/tenant/billing/current
Authorization: Bearer YOUR_TENANT_TOKEN
```

**Response:**
```json
{
  "total_amount": 3.0,
  "billing_period_start": "2024-01-01T00:00:00",
  "billing_period_end": "2024-02-01T00:00:00",
  "breakdown": [
    {
      "feature_code": "F1",
      "usage_count": 1,
      "total_cost": 1.0
    },
    {
      "feature_code": "F2",
      "usage_count": 1,
      "total_cost": 2.0
    }
  ]
}
```

---

#### 9. Check Billing History

```bash
GET /api/v1/tenant/billing/history
Authorization: Bearer YOUR_TENANT_TOKEN
```

---

### 📋 **TEST SCENARIO 3: Second Tenant (XYZ Corporation)**

Repeat similar steps for XYZ:

1. Go to: http://xyz.localhost:8000/docs
2. Login with:
   - Email: contact@xyz.com
   - Password: xyz12345
3. Select "Advanced" plan
4. Use features F1, F2, F3, F4
5. Check billing

---

### 📋 **TEST SCENARIO 4: Superadmin - View Tenant Users**

Back to superadmin (http://localhost:8000/docs):

```bash
GET /api/v1/superadmin/tenants/1/users
Authorization: Bearer YOUR_SUPERADMIN_TOKEN
```

Shows all users of ABC Company (tenant ID 1).

---

### 📋 **TEST SCENARIO 5: Send Billing Emails**

#### 1. Trigger Bulk Email

```bash
POST /api/v1/billing/send-emails
Authorization: Bearer YOUR_SUPERADMIN_TOKEN
```

**Response:**
```json
{
  "message": "Billing email task initiated",
  "task_id": "abc123-def456-...",
  "total_tenants": 2
}
```

Check Celery worker terminal - you should see task execution logs.

#### 2. Check Billing Status

```bash
GET /api/v1/billing/status
Authorization: Bearer YOUR_SUPERADMIN_TOKEN
```

**Response:**
```json
{
  "total_tenants": 2,
  "total_revenue": 15.0,
  "tenants": [
    {
      "name": "ABC Company",
      "email": "contact@abc.com",
      "total_amount": 3.0
    },
    {
      "name": "XYZ Corporation",
      "email": "contact@xyz.com",
      "total_amount": 12.0
    }
  ]
}
```

---

## Step 9: Verify in Database

Run these queries in PostgreSQL:

```sql
-- Check tenants
SELECT * FROM tenants;

-- Check users
SELECT * FROM tenant_users;

-- Check feature usages
SELECT * FROM feature_usages;

-- Check billings
SELECT * FROM billings;

-- Check billing summary view
SELECT * FROM tenant_billing_summary;

-- Check feature usage stats
SELECT * FROM feature_usage_stats;
```

---

## Common Issues & Solutions

### ❌ Issue: "Connection refused" when starting Celery

**Solution:** Make sure Redis is running:
```bash
redis-server
# or
redis-cli ping
```

---

### ❌ Issue: Database connection error

**Solution:** 
1. Check PostgreSQL is running
2. Verify `DATABASE_URL` in `.env`
3. Confirm database exists: `psql -U postgres -l | findstr multitenant`

---

### ❌ Issue: Module not found errors

**Solution:**
```bash
# Make sure you're in virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

---

### ❌ Issue: Subdomain not working

**Solution:**
1. Add entries to hosts file: `C:\Windows\System32\drivers\etc\hosts`
```
127.0.0.1    abc.localhost
127.0.0.1    xyz.localhost
```
2. Restart browser after editing hosts file

---

### ❌ Issue: Email not sending

**Solution:**
1. Verify SMTP credentials in `.env`
2. For Gmail, ensure App Password is used (not regular password)
3. Check firewall isn't blocking port 587

---

## Testing Checklist

- [ ] Superadmin login successful
- [ ] Created tenant "ABC Company"
- [ ] Created tenant "XYZ Corporation"
- [ ] Listed all tenants
- [ ] Tenant login (ABC) successful
- [ ] Selected Basic plan for ABC
- [ ] Created tenant user
- [ ] Used feature F1 (success)
- [ ] Used feature F2 (success)
- [ ] Tried F3 with Basic plan (error expected)
- [ ] Checked current billing
- [ ] Checked billing history
- [ ] Second tenant (XYZ) login and Advanced plan selection
- [ ] XYZ used F1, F2, F3, F4
- [ ] Superadmin viewed tenant users
- [ ] Triggered billing emails
- [ ] Checked billing status
- [ ] Verified data in PostgreSQL

---

## Next Steps

After successful testing:

1. **Create more tenants** to test scalability
2. **Test edge cases**:
   - Duplicate subdomain (should fail)
   - Invalid email format (should fail)
   - Weak password (should fail)
   - Inactive tenant accessing system
3. **Monitor Celery worker** for task processing
4. **Check email inbox** for billing statements
5. **Review database views** for analytics

---

## Quick Reference

**Superadmin Credentials:**
- Email: admin@multitenant.com
- Password: admin123

**Tenant URLs:**
- ABC Company: http://abc.localhost:8000
- XYZ Corporation: http://xyz.localhost:8000

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Health Check:**
```bash
GET http://localhost:8000/health
```

---

🎉 **Congratulations!** Your multi-tenant system is up and running!
