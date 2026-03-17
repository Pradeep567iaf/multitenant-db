from celery import Celery

# Use memory-based broker for testing (no Redis required)
# WARNING: Not for production use - data lost on restart

celery_app = Celery(
    "worker",
    broker="memory://localhost",
    backend="cache+memory://localhost"
)

# Configure Celery
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.timezone = "UTC"
celery_app.conf.broker_transport_options = {'visibility_timeout': 3600}
