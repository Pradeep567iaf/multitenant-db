from fastapi import APIRouter
from .endpoints import auth, superadmin, tenant, billing, billing_celery, email_test

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Superadmin routes
api_router.include_router(superadmin.router, prefix="/superadmin", tags=["Superadmin"])

# Tenant routes
api_router.include_router(tenant.router, prefix="/tenant", tags=["Tenant"])

# Billing routes
api_router.include_router(billing.router, tags=["Billing"])

# Celery-based Billing routes
api_router.include_router(billing_celery.router, tags=["Billing - Celery"])

# Email test route
api_router.include_router(email_test.router, prefix="/email", tags=["Email Testing"])