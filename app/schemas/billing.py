from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class FeatureUsageCreate(BaseModel):
    feature_code: str = Field(..., pattern="^F[1-9]$")


class BillingResponse(BaseModel):
    id: int
    tenant_id: int
    tenant_subdomain: Optional[str] = None
    feature_code: Optional[str] = None
    usage_count: int
    total_amount: float
    total_cost: Optional[float] = None  # Make it truly optional
    billing_period_start: datetime
    billing_period_end: datetime
    is_sent: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CurrentBillingResponse(BaseModel):
    total_amount: float
    tenant_subdomain: Optional[str] = None  # Added subdomain field
    billing_period_start: datetime
    billing_period_end: datetime
    breakdown: List[dict]


class PlanSelection(BaseModel):
    plan_name: str = Field(..., pattern="^(Basic|Advanced)$")
