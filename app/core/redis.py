from redis.asyncio import Redis
from app.config import settings,logger



async def get_redis() -> Redis:

    redis_client = Redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        socket_timeout = 5,  # Ждём ответа не более 5 сек
        socket_connect_timeout=3,  # Подключение должно установиться за 3 сек
        decode_responses=True, # decode_responses=True для автоматического декодирования в str
        health_check_interval=10,   # Проверка соединения каждые 10 сек
    )
    try:
        await redis_client.ping()
        return redis_client
    except Exception as e:
        await redis_client.close()
        logger.error('Error for connect Redis')
        raise RuntimeError(f'Error for connect at Redis:{e}')