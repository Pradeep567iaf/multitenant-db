from pydantic import BaseModel, Field
from typing import Optional
from pydantic.networks import EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None
    role: Optional[str] = None
    is_superadmin: Optional[bool] = None


class TenantLoginRequest(BaseModel):
    email: str
    password: str
    subdomain: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "abc@gmail.com",
                "password": "abcuser@123",
                "subdomain": "abc"
            }
        }


class TenantUserCreateWithSubdomain(BaseModel):
    email: str
    password: str
    role: str = "user"
    subdomain: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@abc.com",
                "password": "user123",
                "role": "user",
                "subdomain": "abc"
            }
        }


class PlanSelectionWithSubdomain(BaseModel):
    plan_name: str
    subdomain: str

    class Config:
        json_schema_extra = {
            "example": {
                "plan_name": "Basic",
                "subdomain": "abc"
            }
        }


class FeatureUsageWithSubdomain(BaseModel):
    feature_code: str
    subdomain: str

    class Config:
        json_schema_extra = {
            "example": {
                "feature_code": "F1",
                "subdomain": "abc"
            }
        }


class TenantUserCreateWithSubdomainRequest(BaseModel):
    email: str
    password: str
    role: str = "user"
    subdomain: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@abc.com",
                "password": "user123",
                "role": "user",
                "subdomain": "abc"
            }
        }


class ListUsersWithSubdomainRequest(BaseModel):
    subdomain: str

    class Config:
        json_schema_extra = {
            "example": {
                "subdomain": "abc"
            }
        }


class TenantUserUpdateWithSubdomain(BaseModel):
    user_id: int
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|user)$")
    is_active: Optional[bool] = None
    subdomain: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "email": "updated@abc.com",
                "role": "user",
                "is_active": True,
                "subdomain": "abc"
            }
        }


class TenantUserDeleteWithSubdomain(BaseModel):
    subdomain: str
    user_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "subdomain": "abc",
                "user_id": 1
            }
        }
