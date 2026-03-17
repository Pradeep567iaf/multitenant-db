from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class FeatureUsageCreate(BaseModel):
    feature_code: str = Field(..., pattern="^F[1-9]$")


class BillingResponse(BaseModel):
    id: int
    tenant_id: int
    feature_code: str
    usage_count: int
    total_cost: float
    billing_period_start: datetime
    billing_period_end: Optional[datetime] = None
    is_sent: bool
    
    model_config = ConfigDict(from_attributes=True)


class CurrentBillingResponse(BaseModel):
    total_amount: float
    billing_period_start: datetime
    billing_period_end: datetime
    breakdown: List[dict]


class PlanSelection(BaseModel):
    plan_name: str = Field(..., pattern="^(Basic|Advanced)$")
