from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ....db.session import get_db
from ....models.superadmin import SuperAdmin
from ....core.authentication import get_current_superadmin
from ....services.billing_service import BillingService
from ....services.email_service import EmailService
from ....tasks.celery_tasks import send_billing_emails_task

router = APIRouter()


@router.post("/billing/send-emails")
async def trigger_billing_emails(
    db: Session = Depends(get_db),
    current_superadmin: SuperAdmin = Depends(get_current_superadmin)
):
    """Trigger bulk email sending for all tenants' billing (direct API, no Celery)."""
    # Get all tenants' billing data
    billing_data = BillingService.get_all_tenants_billing(db)
    
    if not billing_data:
        return {
            "message": "No billing data found",
            "total_tenants": 0
        }
    
    # Send emails directly via API (no Celery)
    sent_count = 0
    failed_count = 0
    results = []
    
    for billing in billing_data:
        print(billing)
        try:
            # Send email directly
            EmailService.send_billing_email(
                tenant_email=billing["tenant_email"],
                tenant_name=billing["tenant_name"],
                billing_data=billing
            )
            sent_count += 1
            results.append({
                "tenant": billing["tenant_name"],
                "email": billing["tenant_email"],
                "status": "sent"
            })
        except Exception as e:
            failed_count += 1
            results.append({
                "tenant": billing["tenant_name"],
                "email": billing["tenant_email"],
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "message": f"Billing emails processed",
        "total_tenants": len(billing_data),
        "sent": sent_count,
        "failed": failed_count,
        "results": results
    }


@router.get("/billing/status")
async def get_email_status(
    db: Session = Depends(get_db),
    current_superadmin: SuperAdmin = Depends(get_current_superadmin)
):
    """Get current billing summary for all tenants."""
    billing_data = BillingService.get_all_tenants_billing(db)
    
    total_revenue = sum(b["total_amount"] for b in billing_data)
    
    return {
        "total_tenants": len(billing_data),
        "total_revenue": total_revenue,
        "tenants": [
            {
                "name": b["tenant_name"],
                "email": b["tenant_email"],
                "total_amount": b["total_amount"]
            }
            for b in billing_data
        ]
    }
