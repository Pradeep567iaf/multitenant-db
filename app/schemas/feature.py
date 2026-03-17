from pydantic import BaseModel, Field, ConfigDict


class FeatureBase(BaseModel):
    code: str = Field(..., pattern="^F[1-9]$")
    name: str
    cost: float = Field(..., gt=0)


class FeatureCreate(FeatureBase):
    pass


class FeatureResponse(FeatureBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
