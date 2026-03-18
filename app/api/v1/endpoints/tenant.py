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
from ....schemas.auth import PlanSelectionWithSubdomain, FeatureUsageWithSubdomain, TenantUserCreateWithSubdomainRequest, ListUsersWithSubdomainRequest, TenantUserUpdateWithSubdomain, TenantUserDeleteWithSubdomain
from ....core.security import get_password_hash
from ....core.authentication import get_current_tenant_user
from ....services.billing_service import BillingService

router = APIRouter()


@router.post("/plan/select-with-subdomain", response_model=dict)
async def select_plan_with_subdomain(
    plan_data: PlanSelectionWithSubdomain,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user)
):
    """Select a plan (Basic or Advanced) for the tenant using subdomain parameter."""
    # Validate tenant exists with the provided subdomain
    tenant = db.query(Tenant).filter(
        Tenant.subdomain == plan_data.subdomain,
        Tenant.id == current_user.tenant_id
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with subdomain '{plan_data.subdomain}' not found or access denied"
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


@router.post("/users-with-subdomain", response_model=TenantUserResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant_user_with_subdomain_request(
    user_data: TenantUserCreateWithSubdomainRequest,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user)
):
    """Create a new tenant user with subdomain parameter."""
    # Validate tenant exists with the provided subdomain and belongs to current user's tenant
    tenant = db.query(Tenant).filter(
        Tenant.subdomain == user_data.subdomain,
        Tenant.id == current_user.tenant_id
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with subdomain '{user_data.subdomain}' not found or access denied"
        )
    
    # Check if email already exists within this tenant
    existing_user = db.query(TenantUser).filter(
        TenantUser.email == user_data.email,
        TenantUser.tenant_id == tenant.id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered for this tenant"
        )
    
    # Create user
    user = TenantUser(
        tenant_id=tenant.id,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/users-with-subdomain", response_model=List[TenantUserResponse])
async def list_tenant_users_with_subdomain(
    subdomain: str,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user)
):
    """List all users for the specified tenant using subdomain parameter."""
    # Validate tenant exists with the provided subdomain and belongs to current user's tenant
    tenant = db.query(Tenant).filter(
        Tenant.subdomain == subdomain,
        Tenant.id == current_user.tenant_id
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with subdomain '{subdomain}' not found or access denied"
        )
    
    users = db.query(TenantUser).filter(TenantUser.tenant_id == tenant.id).all()
    return users


@router.put("/users/{user_id}/update/{subdomain}", response_model=TenantUserResponse)
async def update_tenant_user_with_subdomain_param(
    user_id: int,
    subdomain: str,
    user_data: TenantUserUpdate,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user)
):
    """Update a tenant user with subdomain as path parameter."""
    # Validate tenant exists with the provided subdomain and belongs to current user's tenant
    tenant = db.query(Tenant).filter(
        Tenant.subdomain == subdomain,
        Tenant.id == current_user.tenant_id
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with subdomain '{subdomain}' not found or access denied"
        )
    
    # Find user within this tenant
    user = db.query(TenantUser).filter(
        TenantUser.id == user_id,
        TenantUser.tenant_id == tenant.id
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
            TenantUser.tenant_id == tenant.id,
            TenantUser.id != user.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user.email = user_data.email
    
    if user_data.role is not None:
        user.role = user_data.role
    
    # Handle is_active update
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return user


# @router.delete("/users/{user_id}/delete/{subdomain}")
# async def delete_tenant_user_with_subdomain_param(
#     user_id: int,
#     subdomain: str,
#     db: Session = Depends(get_db),
#     current_user: TenantUser = Depends(get_current_tenant_user)
# ):
#     """Delete a tenant user with subdomain as path parameter."""
#     # Validate tenant exists with the provided subdomain and belongs to current user's tenant
#     tenant = db.query(Tenant).filter(
#         Tenant.subdomain == subdomain,
#         Tenant.id == current_user.tenant_id
#     ).first()
    
#     if not tenant:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Tenant with subdomain '{subdomain}' not found or access denied"
#         )
    
#     # Find user within this tenant
#     user = db.query(TenantUser).filter(
#         TenantUser.id == user_id,
#         TenantUser.tenant_id == tenant.id
#     ).first()
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
    
#     # Prevent deleting admin user
#     if user.role == "admin":
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Cannot delete admin user"
#         )
    
#     db.delete(user)
#     db.commit()
    
#     return {
#         "message": "User deleted successfully",
#         "tenant_subdomain": tenant.subdomain,
#         "deleted_user_id": user.id
#     }


@router.post("/features/use-with-subdomain")
async def use_feature_with_subdomain(
    feature_data: FeatureUsageWithSubdomain,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user)
):
    """Record feature usage and increase billing using subdomain parameter."""
    # Validate tenant exists with the provided subdomain
    tenant = db.query(Tenant).filter(
        Tenant.subdomain == feature_data.subdomain,
        Tenant.id == current_user.tenant_id
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with subdomain '{feature_data.subdomain}' not found or access denied"
        )
    
    try:
        result = BillingService.record_feature_usage(
            db=db,
            tenant_id=tenant.id,
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


@router.get("/billing/current-with-subdomain", response_model=CurrentBillingResponse)
async def get_current_billing_with_subdomain(
    subdomain: str,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user)
):
    """Get current billing details using subdomain parameter."""
    # Validate tenant exists with the provided subdomain
    tenant = db.query(Tenant).filter(
        Tenant.subdomain == subdomain,
        Tenant.id == current_user.tenant_id
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with subdomain '{subdomain}' not found or access denied"
        )
    
    billing_data = BillingService.get_current_billing(db=db, tenant_id=tenant.id)
    return billing_data


@router.get("/billing/history-with-subdomain", response_model=List[BillingResponse])
async def get_billing_history_with_subdomain(
    subdomain: str,
    db: Session = Depends(get_db),
    current_user: TenantUser = Depends(get_current_tenant_user)
):
    """Get billing history using subdomain parameter."""
    # Validate tenant exists with the provided subdomain and belongs to current user's tenant
    tenant = db.query(Tenant).filter(
        Tenant.subdomain == subdomain,
        Tenant.id == current_user.tenant_id
    ).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with subdomain '{subdomain}' not found or access denied"
        )
    
    billings = BillingService.get_billing_history(db=db, tenant_id=tenant.id)
    return billings


# @router.get("/billing/history", response_model=List[BillingResponse])
# async def get_billing_history(
#     db: Session = Depends(get_db),
#     current_user: TenantUser = Depends(get_current_tenant_user),
#     request: Request = None
# ):
#     """Get billing history."""
#     tenant_id = getattr(request.state, 'tenant_id', None)
    
#     if not tenant_id:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid subdomain"
#         )
    
#     billings = BillingService.get_billing_history(db=db, tenant_id=tenant_id)
#     return billings
