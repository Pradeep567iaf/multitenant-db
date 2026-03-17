from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None
    role: Optional[str] = None
    is_superadmin: Optional[bool] = None
