from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ....db.session import get_db
from ....models.superadmin import SuperAdmin
from ....core.authentication import get_current_superadmin
from ....services.billing_service import BillingService
from ....tasks.celery_tasks import send_billing_emails_task

router = APIRouter()


@router.post("/billing/send-emails-celery")
async def trigger_billing_emails_celery(
    db: Session = Depends(get_db),
    current_superadmin: SuperAdmin = Depends(get_current_superadmin)
):
    """Trigger bulk email sending for all tenants' billing using Celery."""
    # Get all tenants' billing data
    billing_data = BillingService.get_all_tenants_billing(db)
    
    if not billing_data:
        return {
            "message": "No billing data found",
            "total_tenants": 0
        }
    
    # Trigger Celery task to send emails
    task = send_billing_emails_task.delay(billing_data)
    
    return {
        "message": "Billing email task initiated via Celery",
        "task_id": task.id,
        "total_tenants": len(billing_data)
    }


# @router.get("/billing/task-status/{task_id}")
# async def get_task_status(
#     task_id: str,
#     current_superadmin: SuperAdmin = Depends(get_current_superadmin)
# ):
#     """Get status of a Celery task."""
#     from celery.result import AsyncResult
#     from ....tasks.celery_tasks import celery_app
    
#     task_result = AsyncResult(task_id, app=celery_app)
    
#     return {
#         "task_id": task_id,
#         "status": task_result.status,
#         "result": task_result.result if task_result.ready() else None
#     }
