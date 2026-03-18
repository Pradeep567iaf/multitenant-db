from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TenantUserBase(BaseModel):
    email: EmailStr
    role: str = Field(..., pattern="^(admin|user)$")


class TenantUserCreate(TenantUserBase):
    password: str = Field(..., min_length=8)


class TenantUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|user)$")
    is_active: Optional[bool] = Field(None, description="Set user active status")

    model_config = ConfigDict(from_attributes=True)


class TenantUserResponse(TenantUserBase):
    id: int
    tenant_id: int
    tenant_subdomain: Optional[str] = None  # Added subdomain field
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
