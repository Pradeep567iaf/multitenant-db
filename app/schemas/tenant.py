from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TenantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    subdomain: str = Field(..., min_length=3, max_length=50, pattern="^[a-z0-9]+$")
    email: EmailStr


class TenantCreate(TenantBase):
    password: str = Field(..., min_length=8)


class TenantResponse(TenantBase):
    id: int
    is_active: bool
    created_at: datetime
    plan_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class TenantListResponse(BaseModel):
    id: int
    name: str
    subdomain: str
    email: str
    is_active: bool
    created_at: datetime
    plan_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)
