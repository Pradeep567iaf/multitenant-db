from pydantic import BaseModel, EmailStr, Field, ConfigDict


class SuperAdminBase(BaseModel):
    email: EmailStr


class SuperAdminLogin(BaseModel):
    email: EmailStr
    password: str


class SuperAdminCreate(SuperAdminBase):
    password: str = Field(..., min_length=8)


class SuperAdminResponse(SuperAdminBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
