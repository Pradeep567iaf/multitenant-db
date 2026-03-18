from celery import Celery
from app.core.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_celery_app():
    """Create and configure Celery app with error handling."""
    try:
        # Create Celery instance
        celery_app = Celery(
            "worker",
            broker=settings.CELERY_BROKER_URL,
            backend=settings.CELERY_RESULT_BACKEND
        )
        
        # Configure Celery
        celery_app.conf.update(
            task_serializer="json",
            result_serializer="json",
            accept_content=["json"],
            timezone="UTC",
            enable_utc=True,
            broker_connection_retry_on_startup=True,
            broker_connection_max_retries=10,
            task_routes={
                'app.tasks.celery_tasks.send_billing_emails_task': {'queue': 'emails'}
            }
        )
        
        logger.info("✅ Celery app created successfully")
        return celery_app
        
    except Exception as e:
        logger.error(f"❌ Failed to create Celery app: {e}")
        raise

# Create the Celery app
celery_app = create_celery_app()

if __name__ == "__main__":
    celery_app.start()