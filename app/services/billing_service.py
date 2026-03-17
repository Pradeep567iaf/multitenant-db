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
            cost=feature.cost
        )
        db.add(usage)
        
        # Update or create billing record for current period
        current_period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = current_period_start + timedelta(days=32)
        current_period_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        billing = db.query(Billing).filter(
            Billing.tenant_id == tenant_id,
            Billing.feature_code == feature_code,
            Billing.billing_period_start >= current_period_start,
            Billing.billing_period_start < current_period_end
        ).first()
        
        if billing:
            billing.usage_count += 1
            billing.total_cost += feature.cost
        else:
            billing = Billing(
                tenant_id=tenant_id,
                feature_code=feature_code,
                usage_count=1,
                total_cost=feature.cost,
                billing_period_start=current_period_start,
                billing_period_end=current_period_end
            )
            db.add(billing)
        
        db.commit()
        db.refresh(billing)
        
        return {
            "feature_code": feature_code,
            "cost": feature.cost,
            "total_usage_count": billing.usage_count,
            "total_cost": billing.total_cost
        }
    
    @staticmethod
    def get_current_billing(db: Session, tenant_id: int) -> dict:
        """Get current billing information for a tenant."""
        current_period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = current_period_start + timedelta(days=32)
        current_period_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        billings = db.query(Billing).filter(
            Billing.tenant_id == tenant_id,
            Billing.billing_period_start >= current_period_start,
            Billing.billing_period_start < current_period_end
        ).all()
        
        total_amount = sum(b.total_cost for b in billings)
        
        breakdown = [
            {
                "feature_code": b.feature_code,
                "usage_count": b.usage_count,
                "total_cost": b.total_cost
            }
            for b in billings
        ]
        
        return {
            "total_amount": total_amount,
            "billing_period_start": current_period_start,
            "billing_period_end": current_period_end,
            "breakdown": breakdown
        }
    
    @staticmethod
    def get_billing_history(db: Session, tenant_id: int) -> List[Billing]:
        """Get billing history for a tenant."""
        return db.query(Billing).filter(
            Billing.tenant_id == tenant_id
        ).order_by(Billing.billing_period_start.desc()).all()
    
    @staticmethod
    def get_all_tenants_billing(db: Session) -> List[dict]:
        """Get billing information for all tenants (for email sending)."""
        current_period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = current_period_start + timedelta(days=32)
        current_period_end = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
        
        all_billing = []
        for tenant in tenants:
            billings = db.query(Billing).filter(
                Billing.tenant_id == tenant.id,
                Billing.billing_period_start >= current_period_start,
                Billing.billing_period_start < current_period_end
            ).all()
            
            total_amount = sum(b.total_cost for b in billings)
            
            breakdown = [
                {
                    "feature_code": b.feature_code,
                    "usage_count": b.usage_count,
                    "total_cost": b.total_cost
                }
                for b in billings
            ]
            
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
