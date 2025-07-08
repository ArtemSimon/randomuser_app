from celery import Celery
from app.config import settings

celery = Celery('tasks',
        broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_always_eager=False,
        broker_connection_retry_on_startup=True)


