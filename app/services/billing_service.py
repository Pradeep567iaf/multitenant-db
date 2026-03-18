from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.tenant import Tenant
from ..models.plan import Plan
from ..models.feature import Feature
from ..models.plan_feature import PlanFeature
from ..models.billing import Billing, FeatureUsage
from datetime import datetime, timedelta


class BillingService:
    """Service for handling billing-related operations."""
    
    @staticmethod
    def record_feature_usage(db: Session, tenant_id: int, feature_code: str) -> dict:
        """Record a feature usage and update billing."""
        
        # Get feature details
        feature = db.query(Feature).filter(Feature.code == feature_code).first()
        if not feature:
            raise ValueError(f"Feature {feature_code} not found")
        
        # Get tenant's plan
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise ValueError("Tenant not found")
        
        if not tenant.plan_id:
            raise ValueError("Tenant has not selected a plan yet")
        
        # Check if feature is in tenant's plan
        plan_features = db.query(Feature).join(PlanFeature).filter(
            PlanFeature.plan_id == tenant.plan_id,
            Feature.code == feature_code
        ).first()
        
        if not plan_features:
            raise ValueError(f"Feature {feature_code} is not included in tenant's plan")
        
        # Record feature usage
        usage = FeatureUsage(
            tenant_id=tenant_id,
            feature_code=feature_code,
            usage_count=1,
            total_cost=feature.cost
        )
        db.add(usage)
        
        # Update or create billing record for current period
        current_period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = current_period_start + timedelta(days=32)
        current_period_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get existing billing for this tenant and period
        billing = db.query(Billing).filter(
            Billing.tenant_id == tenant_id,
            Billing.billing_period_start == current_period_start.date(),
            Billing.billing_period_end == current_period_end.date()
        ).first()
        
        if billing:
            # Update existing billing
            billing.total_amount = billing.total_amount + feature.cost
            billing.usage_count += 1
        else:
            # Create new billing
            billing = Billing(
                tenant_id=tenant_id,
                feature_code=feature_code,  # Include feature code
                usage_count=1,
                total_amount=feature.cost,
                billing_period_start=current_period_start.date(),
                billing_period_end=current_period_end.date()
            )
            db.add(billing)
            db.flush()  # Get the billing ID
        
        # Link usage to billing
        usage.billing_id = billing.id
        db.commit()
        db.refresh(billing)
        
        # Calculate total usage for this feature in current period
        total_usage = db.query(FeatureUsage).filter(
            FeatureUsage.tenant_id == tenant_id,
            FeatureUsage.feature_code == feature_code,
            FeatureUsage.created_at >= current_period_start,
            FeatureUsage.created_at < current_period_end
        ).count()
        
        return {
            "feature_code": feature_code,
            "cost": feature.cost,
            "total_usage_count": total_usage,
            "total_cost": float(billing.total_amount)
        }
    
    @staticmethod
    def get_current_billing(db: Session, tenant_id: int) -> dict:
        """Get current billing information for a tenant."""
        current_period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = current_period_start + timedelta(days=32)
        current_period_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get tenant info for subdomain
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return {
                "total_amount": 0.0,
                "billing_period_start": current_period_start,
                "billing_period_end": current_period_end,
                "breakdown": []
            }
        
        # Get billing for current period
        billing = db.query(Billing).filter(
            Billing.tenant_id == tenant_id,
            Billing.billing_period_start == current_period_start.date(),
            Billing.billing_period_end == current_period_end.date()
        ).first()
        
        if not billing:
            return {
                "total_amount": 0.0,
                "tenant_subdomain": tenant.subdomain,  # Include subdomain
                "billing_period_start": current_period_start,
                "billing_period_end": current_period_end,
                "breakdown": []
            }
        
        # Get feature usages for breakdown
        usages = db.query(FeatureUsage).filter(
            FeatureUsage.billing_id == billing.id
        ).all()
        
        breakdown = []
        feature_totals = {}
        
        # Aggregate by feature
        for usage in usages:
            if usage.feature_code not in feature_totals:
                feature_totals[usage.feature_code] = {
                    "feature_code": usage.feature_code,
                    "usage_count": 0,
                    "total_cost": 0.0
                }
            feature_totals[usage.feature_code]["usage_count"] += usage.usage_count
            feature_totals[usage.feature_code]["total_cost"] += float(usage.total_cost)
        
        breakdown = list(feature_totals.values())
        
        return {
            "total_amount": float(billing.total_amount),
            "tenant_subdomain": tenant.subdomain,  # Include subdomain
            "billing_period_start": current_period_start,
            "billing_period_end": current_period_end,
            "breakdown": breakdown
        }
    
    @staticmethod
    def get_billing_history(db: Session, tenant_id: int) -> List[Billing]:
        """Get billing history for a tenant."""
        billings = db.query(Billing).filter(
            Billing.tenant_id == tenant_id
        ).order_by(Billing.billing_period_start.desc()).all()
        
        # Add tenant subdomain to each billing record and ensure proper values
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if tenant:
            for billing in billings:
                # Add subdomain as an attribute (will be picked up by Pydantic)
                billing.tenant_subdomain = tenant.subdomain
                # Ensure total_cost is not None (use total_amount if needed)
                if billing.total_cost is None and billing.total_amount is not None:
                    billing.total_cost = float(billing.total_amount)
        
        return billings
    
    @staticmethod
    def get_all_tenants_billing(db: Session) -> List[dict]:
        """Get billing information for all tenants (for email sending)."""
        current_period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = current_period_start + timedelta(days=32)
        current_period_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
        
        all_billing = []
        for tenant in tenants:
            # Get billing for current period
            billing = db.query(Billing).filter(
                Billing.tenant_id == tenant.id,
                Billing.billing_period_start == current_period_start.date(),
                Billing.billing_period_end == current_period_end.date()
            ).first()
            
            if not billing:
                total_amount = 0.0
                breakdown = []
            else:
                total_amount = float(billing.total_amount)
                
                # Get feature usages for breakdown
                usages = db.query(FeatureUsage).filter(
                    FeatureUsage.billing_id == billing.id
                ).all()
                
                feature_totals = {}
                for usage in usages:
                    if usage.feature_code not in feature_totals:
                        feature_totals[usage.feature_code] = {
                            "feature_code": usage.feature_code,
                            "usage_count": 0,
                            "total_cost": 0.0
                        }
                    feature_totals[usage.feature_code]["usage_count"] += usage.usage_count
                    feature_totals[usage.feature_code]["total_cost"] += float(usage.total_cost)
                
                breakdown = list(feature_totals.values())
            
            all_billing.append({
                "tenant_id": tenant.id,
                "tenant_name": tenant.name,
                "tenant_email": tenant.email,
                "total_amount": total_amount,
                "billing_period_start": current_period_start,
                "billing_period_end": current_period_end,
                "breakdown": breakdown
            })
        
        return all_billing
