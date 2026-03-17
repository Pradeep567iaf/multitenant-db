from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from ....db.session import get_db
from ....models.superadmin import SuperAdmin
from ....models.tenant import Tenant
from ....models.user import TenantUser
from ....models.plan import Plan
from ....models.feature import Feature
from ....models.plan_feature import PlanFeature
from ....schemas import (
    TenantCreate,
    TenantResponse,
    TenantListResponse,
    TenantUserResponse,
    PlanCreate,
    PlanResponse,
    FeatureCreate,
    FeatureResponse,
)
from ....core.security import get_password_hash
from ....core.authentication import get_current_superadmin

router = APIRouter()


@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db),
    current_superadmin: SuperAdmin = Depends(get_current_superadmin)
):
    """Create a new tenant."""
    # Check if subdomain already exists
    existing_tenant = db.query(Tenant).filter(Tenant.subdomain == tenant_data.subdomain).first()
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subdomain already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(Tenant).filter(Tenant.email == tenant_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create tenant
    tenant = Tenant(
        name=tenant_data.name,
        subdomain=tenant_data.subdomain,
        email=tenant_data.email,
        hashed_password=get_password_hash(tenant_data.password),
        created_by_superadmin_id=current_superadmin.id,
        plan_id=None  # Will be set on first login
    )
    
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    # Create admin user for this tenant
    admin_user = TenantUser(
        tenant_id=tenant.id,
        email=tenant.email,
        hashed_password=get_password_hash(tenant_data.password),
        role="admin"
    )
    
    db.add(admin_user)
    db.commit()
    
    return tenant


@router.get("/tenants", response_model=List[TenantListResponse])
async def list_tenants(
    db: Session = Depends(get_db),
    current_superadmin: SuperAdmin = Depends(get_current_superadmin)
):
    """List all tenants."""
    tenants = db.query(Tenant).all()
    return tenants


@router.get("/tenants/{tenant_id}/users", response_model=List[TenantUserResponse])
async def list_tenant_users(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_superadmin: SuperAdmin = Depends(get_current_superadmin)
):
    """List all users of a particular tenant."""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    users = db.query(TenantUser).filter(TenantUser.tenant_id == tenant_id).all()
    return users


@router.post("/plans", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
    current_superadmin: SuperAdmin = Depends(get_current_superadmin)
):
    """Create a new plan with features."""
    # Check if plan name already exists
    existing_plan = db.query(Plan).filter(Plan.name == plan_data.name).first()
    if existing_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan name already exists"
        )
    
    # Create plan
    plan = Plan(
        name=plan_data.name,
        description=plan_data.description or "",
        created_at=datetime.utcnow().isoformat()
    )
    
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    # Add features to plan
    if plan_data.feature_ids:
        for feature_id in plan_data.feature_ids:
            feature = db.query(Feature).filter(Feature.id == feature_id).first()
            if not feature:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Feature with id {feature_id} not found"
                )
            
            plan_feature = PlanFeature(plan_id=plan.id, feature_id=feature.id)
            db.add(plan_feature)
        
        db.commit()
        db.refresh(plan)
    
    return plan


@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(
    db: Session = Depends(get_db),
    current_superadmin: SuperAdmin = Depends(get_current_superadmin)
):
    """List all plans."""
    plans = db.query(Plan).all()
    return plans


@router.post("/features", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_feature(
    feature_data: FeatureCreate,
    db: Session = Depends(get_db),
    current_superadmin: SuperAdmin = Depends(get_current_superadmin)
):
    """Create a new feature."""
    # Check if feature code already exists
    existing_feature = db.query(Feature).filter(Feature.code == feature_data.code).first()
    if existing_feature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feature code already exists"
        )
    
    # Create feature
    feature = Feature(
        code=feature_data.code,
        name=feature_data.name,
        cost=feature_data.cost
    )
    
    db.add(feature)
    db.commit()
    db.refresh(feature)
    
    return feature


@router.post("/plans/{plan_id}/features")
async def add_features_to_plan(
    plan_id: int,
    feature_ids: List[int],
    db: Session = Depends(get_db),
    current_superadmin: SuperAdmin = Depends(get_current_superadmin)
):
    """Add features to an existing plan."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Add features to plan
    for feature_id in feature_ids:
        feature = db.query(Feature).filter(Feature.id == feature_id).first()
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature with id {feature_id} not found"
            )
        
        # Check if feature is already in plan
        existing = db.query(PlanFeature).filter(
            PlanFeature.plan_id == plan_id,
            PlanFeature.feature_id == feature_id
        ).first()
        
        if not existing:
            plan_feature = PlanFeature(plan_id=plan_id, feature_id=feature_id)
            db.add(plan_feature)
    
    db.commit()
    
    return {"message": "Features added successfully"}
