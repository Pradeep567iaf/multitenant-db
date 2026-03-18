import redis
import os
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def is_redis_available():
    """Check if Redis is available and configured."""
    try:
        redis_url = os.getenv('CELERY_BROKER_URL')
        if not redis_url:
            return False
            
        # Test Redis connection
        client = redis.from_url(redis_url, socket_connect_timeout=1)
        client.ping()
        return True
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}")
        return False

def skip_if_no_redis(func):
    """Decorator to skip Celery tasks if Redis is not available."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_redis_available():
            logger.info("Redis not available, skipping Celery task")
            return {"success": False, "message": "Redis/Celery not configured"}
        return func(*args, **kwargs)
    return wrapper