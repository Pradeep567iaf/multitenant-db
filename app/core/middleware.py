from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable
from ..db.session import SessionLocal
from ..models.tenant import Tenant


class SubdomainMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle subdomain-based routing.
    Extracts subdomain from host header and determines if request is for superadmin or tenant.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        # Get host from request (e.g., "localhost:8000" or "abc.localhost:8000")
        host = request.headers.get("host", "")
        
        # Check for custom subdomain header first (for testing without hosts file)
        custom_subdomain = request.headers.get("X-Tenant-Subdomain")
        if custom_subdomain:
            subdomain = custom_subdomain
        else:
            # Parse subdomain from host
            subdomain = self._extract_subdomain(host)
        
        # Set subdomain info in request state
        request.state.subdomain = subdomain
        request.state.is_superadmin = subdomain in [None, "", "www", "localhost"]
        
        # If it's a tenant request, validate tenant exists
        if not request.state.is_superadmin:
            tenant = self._get_tenant_by_subdomain(subdomain)
            
            if not tenant:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"detail": f"Tenant with subdomain '{subdomain}' not found"}
                )
            
            if not tenant.is_active:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Tenant account is deactivated"}
                )
            
            request.state.tenant_id = tenant.id
            request.state.tenant = tenant
        
        # Continue processing the request
        response = await call_next(request)
        return response
    
    def _extract_subdomain(self, host: str) -> str | None:
        """Extract subdomain from host header."""
        if not host:
            return None
        
        # Remove port if present
        host = host.split(":")[0]
        
        # Check for localhost or IP addresses
        if host in ["localhost", "127.0.0.1", "::1"]:
            return None
        
        # Split by dots
        parts = host.split(".")
        
        # If only one part (no subdomain), return None
        if len(parts) <= 2:
            return None
        
        # Return first part as subdomain
        return parts[0]
    
    def _get_tenant_by_subdomain(self, subdomain: str) -> Tenant | None:
        """Get tenant by subdomain from database."""
        if not subdomain:
            return None
        
        db = SessionLocal()
        try:
            tenant = db.query(Tenant).filter(Tenant.subdomain == subdomain).first()
            return tenant
        finally:
            db.close()
