from fastapi import APIRouter, HTTPException
from app.services.email_service import EmailService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/test-email")
async def test_email_sending():
    """Test email sending functionality."""
    try:
        # Test with a sample email
        result = EmailService.send_billing_email(
            tenant_email="test@example.com",
            tenant_name="Test Tenant",
            total_amount=10.50,
            billing_period_start="2026-03-01",
            billing_period_end="2026-04-01",
            breakdown=[
                {"feature_code": "F1", "usage_count": 5, "total_cost": 5.0},
                {"feature_code": "F2", "usage_count": 3, "total_cost": 5.5}
            ]
        )
        
        if result["success"]:
            return {"message": "Email sent successfully!", "details": result}
        else:
            return {"message": "Email failed to send", "error": result["error"]}
            
    except Exception as e:
        logger.error(f"Email test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email test failed: {str(e)}")