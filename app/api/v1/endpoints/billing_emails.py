from fastapi import APIRouter, HTTPException, Header
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
                    billing_data=billing_info
                )
                
                if result:
                    success_count += 1
                else:
                    failed_count += 1
                    logger.warning(f"Failed to send email to {billing_info['tenant_email']}")
                    
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

@router.post("/cron/bulk-billing-emails")
async def cron_bulk_billing_emails(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Cron job endpoint for sending bulk monthly billing emails.
    Requires authorization header for security.
    """
    # Authorization check
    CRON_SECRET = "your-cron-secret-key-here"  # Set this in Render environment variables
    
    if not authorization or authorization != f"Bearer {CRON_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        logger.info("📅 Bulk cron job triggered: Sending monthly billing emails")
        
        # Get all tenants' billing data
        all_billing_data = BillingService.get_all_tenants_billing(db)
        
        if not all_billing_data:
            logger.info("No billing data found for this period")
            return {
                "message": "No billing data found", 
                "processed": 0,
                "status": "completed"
            }
        
        # Send bulk emails with detailed logging
        logger.info(f"📧 Processing {len(all_billing_data)} tenants for billing emails")
        
        results = EmailService.send_bulk_billing_emails(all_billing_data)
        
        success_count = results["success"]
        failed_count = results["failed"]
        
        # Log detailed results
        for detail in results["details"]:
            if detail["success"]:
                logger.info(f"✅ Email sent successfully to {detail['tenant_email']}")
            else:
                logger.error(f"❌ Failed to send email to {detail['tenant_email']}")
        
        logger.info(f"📊 Bulk email job completed: {success_count} successful, {failed_count} failed")
        
        return {
            "message": "Bulk monthly billing emails processed",
            "total_tenants": len(all_billing_data),
            "successful": success_count,
            "failed": failed_count,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Bulk cron job failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk cron job failed: {str(e)}")

@router.post("/cron/billing-emails")
async def cron_billing_emails(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Cron job endpoint for sending monthly billing emails.
    Requires authorization header for security.
    """
    # Simple authorization check (use a strong secret in production)
    CRON_SECRET = "your-cron-secret-key"  # Set this in Render environment variables
    
    if not authorization or authorization != f"Bearer {CRON_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        logger.info("📅 Cron job triggered: Sending monthly billing emails")
        
        # Get all tenants' billing data
        all_billing_data = BillingService.get_all_tenants_billing(db)
        
        if not all_billing_data:
            logger.info("No billing data found for this period")
            return {"message": "No billing data found", "processed": 0}
        
        # Send emails
        success_count = 0
        failed_count = 0
        
        for billing_info in all_billing_data:
            try:
                result = EmailService.send_billing_email(
                    tenant_email=billing_info["tenant_email"],
                    tenant_name=billing_info["tenant_name"],
                    billing_data=billing_info
                )
                
                if result:
                    success_count += 1
                    logger.info(f"✅ Email sent to {billing_info['tenant_email']}")
                else:
                    failed_count += 1
                    logger.warning(f"❌ Failed to send email to {billing_info['tenant_email']}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending email to {billing_info['tenant_email']}: {str(e)}")
        
        logger.info(f"📊 Cron job completed: {success_count} successful, {failed_count} failed")
        
        return {
            "message": "Monthly billing emails processed",
            "total_processed": len(all_billing_data),
            "successful": success_count,
            "failed": failed_count,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cron job failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cron job failed: {str(e)}")

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
                        billing_data=billing_info
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