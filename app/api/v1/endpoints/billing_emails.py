from fastapi import APIRouter, HTTPException
from app.services.email_service import EmailService
from app.services.billing_service import BillingService
from sqlalchemy.orm import Session
from app.db.session import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/send-billing-emails-sync")
async def send_billing_emails_synchronously(db: Session = Depends(get_db)):
    """Send billing emails synchronously (no Celery required)."""
    try:
        # Get all tenants' billing data
        all_billing_data = BillingService.get_all_tenants_billing(db)
        
        if not all_billing_data:
            return {"message": "No billing data found", "sent_count": 0}
        
        # Send emails synchronously
        success_count = 0
        failed_count = 0
        
        for billing_info in all_billing_data:
            try:
                result = EmailService.send_billing_email(
                    tenant_email=billing_info["tenant_email"],
                    tenant_name=billing_info["tenant_name"],
                    total_amount=billing_info["total_amount"],
                    billing_period_start=billing_info["billing_period_start"],
                    billing_period_end=billing_info["billing_period_end"],
                    breakdown=billing_info["breakdown"]
                )
                
                if result["success"]:
                    success_count += 1
                else:
                    failed_count += 1
                    logger.warning(f"Failed to send email to {billing_info['tenant_email']}: {result['error']}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending email to {billing_info['tenant_email']}: {str(e)}")
        
        return {
            "message": "Billing emails sent",
            "total_processed": len(all_billing_data),
            "successful": success_count,
            "failed": failed_count
        }
        
    except Exception as e:
        logger.error(f"Billing email sending failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Billing email sending failed: {str(e)}")

@router.post("/send-billing-emails-async-emulation")
async def send_billing_emails_async_emulation(db: Session = Depends(get_db)):
    """Emulate async behavior using background tasks (FastAPI built-in)."""
    from fastapi import BackgroundTasks
    
    async def background_email_sender():
        """Background task to send emails."""
        try:
            all_billing_data = BillingService.get_all_tenants_billing(db)
            
            for billing_info in all_billing_data:
                try:
                    EmailService.send_billing_email(
                        tenant_email=billing_info["tenant_email"],
                        tenant_name=billing_info["tenant_name"],
                        total_amount=billing_info["total_amount"],
                        billing_period_start=billing_info["billing_period_start"],
                        billing_period_end=billing_info["billing_period_end"],
                        breakdown=billing_info["breakdown"]
                    )
                except Exception as e:
                    logger.error(f"Background email failed for {billing_info['tenant_email']}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Background task failed: {str(e)}")
    
    # Start background task
    BackgroundTasks().add_task(background_email_sender)
    
    return {"message": "Billing emails queued for sending", "status": "processing"}

# Add to your main router
# api_router.include_router(router, prefix="/billing", tags=["Billing Emails"])