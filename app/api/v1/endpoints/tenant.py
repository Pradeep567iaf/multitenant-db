from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from ....db.session import get_db
from ....models.tenant import Tenant
from ....models.user import TenantUser
from ....models.plan import Plan
from ....schemas import (
    TenantUserCreate,
    TenantUserResponse,
    TenantUserUpdate,
    PlanSelection,
    PlanResponse,
    FeatureUsageCreate,
    BillingResponse,
    CurrentBillingResponse,
)
from ....core.security import get_password_hash
from ....core.authentication import get_current_tenant_user
from ....services.billing_service import BillingService

router = APIRouter()


@router.post("/plan/select", response_model=dict)
async def select_plan(
    plan_data: PlanSelection,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user),
    request: Request = None
):
    """Select a plan (Basic or Advanced) for the tenant."""
    tenant_id = getattr(request.state, 'tenant_id', None)
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subdomain"
        )
    
    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Check if plan already selected
    if tenant.plan_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan already selected. Contact superadmin to change."
        )
    
    # Find plan by name
    plan = db.query(Plan).filter(Plan.name == plan_data.plan_name).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan '{plan_data.plan_name}' not found"
        )
    
    # Update tenant's plan
    tenant.plan_id = plan.id
    db.commit()
    
    return {
        "message": f"Plan '{plan_data.plan_name}' selected successfully",
        "plan_name": plan.name,
        "features_count": len(plan.features)
    }


@router.post("/users", response_model=TenantUserResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant_user(
    user_data: TenantUserCreate,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user),
    request: Request = None
):
    """Create a new tenant user."""
    tenant_id = getattr(request.state, 'tenant_id', None)
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subdomain"
        )
    
    # Check if email already exists within this tenant
    existing_user = db.query(TenantUser).filter(
        TenantUser.email == user_data.email,
        TenantUser.tenant_id == tenant_id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered for this tenant"
        )
    
    # Create user
    user = TenantUser(
        tenant_id=tenant_id,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/users", response_model=List[TenantUserResponse])
async def list_tenant_users(
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user),
    request: Request = None
):
    """List all users for this tenant."""
    tenant_id = getattr(request.state, 'tenant_id', None)
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subdomain"
        )
    
    users = db.query(TenantUser).filter(TenantUser.tenant_id == tenant_id).all()
    return users


@router.put("/users/{user_id}", response_model=TenantUserResponse)
async def update_tenant_user(
    user_id: int,
    user_data: TenantUserUpdate,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user),
    request: Request = None
):
    """Update a tenant user."""
    tenant_id = getattr(request.state, 'tenant_id', None)
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subdomain"
        )
    
    # Find user
    user = db.query(TenantUser).filter(
        TenantUser.id == user_id,
        TenantUser.tenant_id == tenant_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_data.email is not None:
        # Check if email is already taken
        existing = db.query(TenantUser).filter(
            TenantUser.email == user_data.email,
            TenantUser.tenant_id == tenant_id,
            TenantUser.id != user_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user.email = user_data.email
    
    if user_data.role is not None:
        user.role = user_data.role
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/users/{user_id}")
async def delete_tenant_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user),
    request: Request = None
):
    """Delete a tenant user."""
    tenant_id = getattr(request.state, 'tenant_id', None)
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subdomain"
        )
    
    # Find user
    user = db.query(TenantUser).filter(
        TenantUser.id == user_id,
        TenantUser.tenant_id == tenant_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting admin user
    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin user"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.post("/features/use")
async def use_feature(
    feature_data: FeatureUsageCreate,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user),
    request: Request = None
):
    """Record feature usage and increase billing."""
    tenant_id = getattr(request.state, 'tenant_id', None)
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subdomain"
        )
    
    try:
        result = BillingService.record_feature_usage(
            db=db,
            tenant_id=tenant_id,
            feature_code=feature_data.feature_code
        )
        
        return {
            "message": "Feature usage recorded",
            **result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/billing/current", response_model=CurrentBillingResponse)
async def get_current_billing(
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user),
    request: Request = None
):
    """Get current billing details."""
    tenant_id = getattr(request.state, 'tenant_id', None)
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subdomain"
        )
    
    billing_data = BillingService.get_current_billing(db=db, tenant_id=tenant_id)
    return billing_data


@router.get("/billing/history", response_model=List[BillingResponse])
async def get_billing_history(
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user),
    request: Request = None
):
    """Get billing history."""
    tenant_id = getattr(request.state, 'tenant_id', None)
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subdomain"
        )
    
    billings = BillingService.get_billing_history(db=db, tenant_id=tenant_id)
    return billings
