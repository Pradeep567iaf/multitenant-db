from celery import Celery
from app.core.config import settings
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_celery_app():
    """Create Celery app compatible with Render's limitations."""
    try:
        # Check if we're on Render
        is_render = os.getenv('RENDER', False)
        
        if is_render:
            # Use in-memory broker for Render (limited functionality)
            broker_url = "memory://"
            backend_url = "cache+memory://"
            logger.info("🔧 Using memory broker for Render deployment")
        else:
            # Use Redis for local development
            broker_url = settings.CELERY_BROKER_URL
            backend_url = settings.CELERY_RESULT_BACKEND
            logger.info("🔧 Using Redis broker for local development")
        
        # Create Celery instance
        celery_app = Celery(
            "worker",
            broker=broker_url,
            backend=backend_url
        )
        
        # Configure Celery
        celery_app.conf.update(
            task_serializer="json",
            result_serializer="json",
            accept_content=["json"],
            timezone="UTC",
            enable_utc=True,
            # Render-specific configurations
            worker_prefetch_multiplier=1,
            task_acks_late=True,
            worker_max_tasks_per_child=1000,
            # Disable persistent connections for Render
            broker_connection_retry_on_startup=False,
            broker_connection_max_retries=3,
            # Task routing
            task_routes={
                'app.tasks.celery_tasks.send_billing_emails_task': {'queue': 'emails'}
            }
        )
        
        # For Render, disable result backend if using memory
        if is_render:
            celery_app.conf.update(
                result_backend=None,
                task_ignore_result=True
            )
        
        logger.info("✅ Celery app created successfully")
        return celery_app
        
    except Exception as e:
        logger.error(f"❌ Failed to create Celery app: {e}")
        raise

# Create the Celery app
celery_app = create_celery_app()

# Add a health check task
@celery_app.task
def health_check():
    """Simple health check task."""
    return {"status": "healthy", "timestamp": __import__('datetime').datetime.now().isoformat()}

if __name__ == "__main__":
    celery_app.start()