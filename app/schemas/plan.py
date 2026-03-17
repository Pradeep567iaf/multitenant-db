from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from .feature import FeatureResponse


class PlanBase(BaseModel):
    name: str = Field(..., pattern="^(Basic|Advanced)$")
    description: Optional[str] = None


class PlanCreate(PlanBase):
    feature_ids: list[int] = []


class PlanResponse(PlanBase):
    id: int
    created_at: str
    features: List[FeatureResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
