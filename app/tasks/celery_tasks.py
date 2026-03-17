from celery_worker import celery_app
from app.db.session import SessionLocal
from app.services.email_service import EmailService
from app.models.billing import Billing
from datetime import datetime


@celery_app.task(bind=True, max_retries=3)
def send_billing_emails_task(self, billing_data: list):
    """Celery task to send billing emails to all tenants."""
    try:
        results = EmailService.send_bulk_billing_emails(billing_data)
        
        # Update billing records to mark emails as sent
        db = SessionLocal()
        try:
            current_period_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            for billing_info in billing_data:
                tenant_id = billing_info["tenant_id"]
                
                # Mark billings as sent
                db.query(Billing).filter(
                    Billing.tenant_id == tenant_id,
                    Billing.billing_period_start >= current_period_start
                ).update({"is_sent": True})
            
            db.commit()
        finally:
            db.close()
        
        return {
            "status": "completed",
            "total": results["total"],
            "success": results["success"],
            "failed": results["failed"]
        }
    
    except Exception as exc:
        # Retry logic
        try:
            raise self.retry(exc=exc, countdown=60)  # Retry after 60 seconds
        except self.MaxRetriesExceededError:
            # Max retries exceeded
            return {
                "status": "failed",
                "error": str(exc)
            }
