# Testing Subdomains Without Hosts File

## ✅ Header-Based Subdomain Routing

The middleware now supports a custom header `X-Tenant-Subdomain` for testing without modifying the hosts file!

---

## Method 1: Using Swagger UI (Recommended)

### Step 1: Go to Swagger UI
```
http://localhost:8000/docs
```

### Step 2: Add Custom Header
1. Click **"Authorize"** button at the top right
2. Under "global" section, add header:
   ```
   Key: X-Tenant-Subdomain
   Value: abc
   ```
3. Click **"Authorize"** then **"Close"**

### Step 3: Use Tenant Endpoints
Now all requests will be routed to tenant `abc`:

**Example - Tenant Login:**
1. Find endpoint: `POST /api/v1/auth/tenant/login`
2. Click "Try it out"
3. Enter body:
```json
{
  "email": "abc@gmail.com",
  "password": "abcuser@123"
}
```
4. Click "Execute"

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "plan_selection_required": true,
  "tenant_name": "ABC Company"
}
```

---

## Method 2: Using cURL

### Login as Tenant
```bash
curl -X POST "http://localhost:8000/api/v1/auth/tenant/login" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Subdomain: abc" \
  -d '{
    "email": "abc@gmail.com",
    "password": "abcuser@123"
  }'
```

### Create Tenant User
```bash
curl -X POST "http://localhost:8000/api/v1/tenant/users" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Subdomain: abc" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "email": "user@abc.com",
    "password": "user123",
    "role": "user"
  }'
```

### Use Feature
```bash
curl -X POST "http://localhost:8000/api/v1/tenant/features/use" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-Subdomain: abc" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "feature_code": "F1"
  }'
```

---

## Method 3: Using Postman

### Setup Collection Variable
1. Open Postman
2. Create a new collection or open existing one
3. Go to "Collection" tab → "Variables"
4. Add variable:
   ```
   Variable: subdomain
   Initial Value: abc
   Current Value: abc
   ```

### Add Header to Requests
For each request, add this header:
```
Key: X-Tenant-Subdomain
Value: {{subdomain}}
```

### Example Request
**Method**: POST  
**URL**: http://localhost:8000/api/v1/auth/tenant/login  
**Headers**:
```
Content-Type: application/json
X-Tenant-Subdomain: abc
```
**Body** (raw JSON):
```json
{
  "email": "abc@gmail.com",
  "password": "abcuser@123"
}
```

---

## Method 4: Using Python Requests

```python
import requests

# Add custom header
headers = {
    "Content-Type": "application/json",
    "X-Tenant-Subdomain": "abc"  # This routes to abc.localhost
}

# Tenant login
response = requests.post(
    "http://localhost:8000/api/v1/auth/tenant/login",
    headers=headers,
    json={
        "email": "abc@gmail.com",
        "password": "abcuser@123"
    }
)

print(response.json())
# Output: {'access_token': '...', 'plan_selection_required': True}

# Use the token for subsequent requests
token = response.json()["access_token"]
headers["Authorization"] = f"Bearer {token}"

# Create user
response = requests.post(
    "http://localhost:8000/api/v1/tenant/users",
    headers=headers,
    json={
        "email": "user@abc.com",
        "password": "user123",
        "role": "user"
    }
)

print(response.json())
```

---

## Method 5: Using JavaScript/Fetch

```javascript
// Tenant login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/tenant/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-Tenant-Subdomain': 'abc'  // Route to abc tenant
    },
    body: JSON.stringify({
        email: 'abc@gmail.com',
        password: 'abcuser@123'
    })
});

const { access_token } = await loginResponse.json();

// Use feature
await fetch('http://localhost:8000/api/v1/tenant/features/use', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${access_token}`,
        'X-Tenant-Subdomain': 'abc'
    },
    body: JSON.stringify({
        feature_code: 'F1'
    })
});
```

---

## Switching Between Tenants

To test with different tenants, just change the header value:

```bash
# Test with tenant 'abc'
X-Tenant-Subdomain: abc

# Test with tenant 'xyz'
X-Tenant-Subdomain: xyz

# Test with tenant 'company1'
X-Tenant-Subdomain: company1
```

---

## Verify Database Setup

Make sure your tenant exists in the database:

```sql
-- Check tenant exists with correct subdomain
SELECT id, name, email, subdomain, is_active 
FROM tenants 
WHERE subdomain IN ('abc', 'xyz', 'company1');

-- Fix subdomain if needed (should be just 'abc', not full URL)
UPDATE tenants 
SET subdomain = 'abc' 
WHERE email = 'abc@gmail.com';
```

---

## Comparison: Header vs Hosts File

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Header (X-Tenant-Subdomain)** | ✅ No system changes<br>✅ Easy to switch tenants<br>✅ Works immediately<br>✅ Developer-friendly | ❌ Not production-ready<br>❌ Manual header addition | **Development & Testing** |
| **Hosts File** | ✅ Realistic subdomain simulation<br>✅ Production-like behavior | ❌ Requires admin rights<br>✅ Browser cache issues<br>❌ Manual editing | **Pre-production testing** |
| **Real Domain** | ✅ Production environment | ❌ Requires DNS setup<br>❌ Cost involved | **Production only** |

---

## Recommended Workflow

### For Development:
1. Use `X-Tenant-Subdomain` header in Swagger UI
2. Add header once in "Authorize" dialog
3. Test all tenant endpoints easily
4. Switch tenants by changing header value

### For Pre-Production Testing:
1. Use hosts file method
2. Test actual subdomain routing
3. Verify SSL/TLS if applicable

### For Production:
1. Use real DNS records
2. Configure wildcard subdomains
3. Set up proper SSL certificates

---

## Troubleshooting

### Issue: "Tenant not found"
**Solution**: Verify tenant exists and subdomain is correct:
```sql
SELECT * FROM tenants WHERE subdomain = 'abc';
```

### Issue: Header not working
**Solution**: 
1. Restart the FastAPI server
2. Clear browser cache
3. Verify header name is exactly: `X-Tenant-Subdomain` (case-sensitive)

### Issue: Still getting superadmin routes
**Solution**: Make sure you're not accessing via `localhost` or `www` - these route to superadmin. Always use the header or proper subdomain.

---

## Summary

✅ **No hosts file needed!**  
✅ **Easy tenant switching** - Just change the header value  
✅ **Works immediately** - No browser restart required  
✅ **Developer-friendly** - Test in Swagger UI directly  

**Header to use:**
```
X-Tenant-Subdomain: abc
```

Replace `abc` with your actual tenant subdomain! 🎉
