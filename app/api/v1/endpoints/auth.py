from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ....db.session import get_db
from ....models.superadmin import SuperAdmin
from ....models.tenant import Tenant
from ....models.user import TenantUser
from ....schemas import (
    SuperAdminCreate,
    SuperAdminLogin,
    Token,
    PlanSelection,
    TenantUserCreate,
    TenantUserResponse,
    SuperAdminResponse
)
from ....schemas.auth import TenantLoginRequest,TenantUserCreateWithSubdomain
from ....core.security import get_password_hash, create_access_token, verify_password
from ....core.authentication import get_current_superadmin, get_current_tenant_user
from ....core.middleware import SubdomainMiddleware
from ....services.billing_service import BillingService
router = APIRouter()


@router.post("/superadmin/create", response_model=SuperAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_superadmin(
    superadmin_data: SuperAdminCreate,
    db: Session = Depends(get_db)
):
    """Create a new superadmin account.
    
    This endpoint is used for initial setup. In production, this should be disabled
    or protected with a special setup token.
    """
    # Check if superadmin already exists
    existing_superadmin = db.query(SuperAdmin).filter(
        SuperAdmin.email == superadmin_data.email
    ).first()
    
    if existing_superadmin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Superadmin with this email already exists"
        )
    
    # Create superadmin
    superadmin = SuperAdmin(
        email=superadmin_data.email,
        hashed_password=get_password_hash(superadmin_data.password),
        created_at=datetime.utcnow().isoformat()
    )
    
    db.add(superadmin)
    db.commit()
    db.refresh(superadmin)
    
    return superadmin


@router.post("/superadmin/login", response_model=Token)
async def superadmin_login(
    login_data: SuperAdminLogin,
    db: Session = Depends(get_db)
):
    """Login as Superadmin."""
    # Find superadmin by email
    superadmin = db.query(SuperAdmin).filter(SuperAdmin.email == login_data.email).first()
    
    if not superadmin or not verify_password(login_data.password, superadmin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": superadmin.email, "user_id": superadmin.id, "is_superadmin": True},
        expires_delta=access_token_expires,
        is_superadmin=True
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/tenant/login")
async def tenant_login(
    login_data: TenantLoginRequest,
    db: Session = Depends(get_db)
):
    """Login as Tenant user with subdomain parameter."""
    # Validate tenant exists with the provided subdomain
    tenant = db.query(Tenant).filter(
        Tenant.subdomain == login_data.subdomain,
        Tenant.email == login_data.email
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with subdomain '{login_data.subdomain}' and email '{login_data.email}' not found"
        )
    
    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant account is deactivated"
        )
    
    # Find tenant user
    user = db.query(TenantUser).filter(
        TenantUser.email == login_data.email,
        TenantUser.tenant_id == tenant.id
    ).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    # Check if tenant has selected a plan
    plan_selection_required = tenant.plan_id is None
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "tenant_id": tenant.id,
            "role": user.role,
            "is_superadmin": False
        },
        expires_delta=access_token_expires,
        is_superadmin=False
    )
    
    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "plan_selection_required": plan_selection_required,
        "tenant_name": tenant.name
    }
    
    # If plan is already selected, include current billing info
    if not plan_selection_required:
        current_billing = BillingService.get_current_billing(db, tenant.id)
        if current_billing:
            response_data["current_billing_total"] = current_billing.get("total_cost")
    
    return response_data


@router.post("/tenant/users", response_model=TenantUserResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant_user_with_subdomain(
    user_data: TenantUserCreateWithSubdomain,
    db: Session = Depends(get_db)
):
    """Create a new tenant user with subdomain parameter."""
    # Validate tenant exists with the provided subdomain
    tenant = db.query(Tenant).filter(
        Tenant.subdomain == user_data.subdomain
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with subdomain '{user_data.subdomain}' not found"
        )
    
    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant account is deactivated"
        )
    
    # Check if user already exists
    existing_user = db.query(TenantUser).filter(
        TenantUser.email == user_data.email,
        TenantUser.tenant_id == tenant.id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists in this tenant"
        )
    
    # Create new user
    user = TenantUser(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        tenant_id=tenant.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user
