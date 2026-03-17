from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from ..db.session import get_db
from ..models.superadmin import SuperAdmin
from ..models.tenant import Tenant
from ..models.user import TenantUser
from ..core.security import decode_access_token
from ..schemas import TokenData

security = HTTPBearer()


async def get_current_superadmin(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> SuperAdmin:
    """Get current authenticated superadmin."""
    token = credentials.credentials
    
    # Decode token with superadmin secret
    payload = decode_access_token(token, is_superadmin=True)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    superadmin = db.query(SuperAdmin).filter(SuperAdmin.email == email).first()
    if superadmin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Superadmin not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return superadmin


async def get_current_tenant_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> TenantUser:
    """Get current authenticated tenant user."""
    token = credentials.credentials
    
    # Decode token with tenant secret
    payload = decode_access_token(token, is_superadmin=False)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(TenantUser).filter(TenantUser.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    
    return user


async def get_optional_tenant_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[TenantUser]:
    """Get current authenticated tenant user or None if not authenticated."""
    try:
        user = await get_current_tenant_user(request, credentials, db)
        return user
    except HTTPException:
        return None
