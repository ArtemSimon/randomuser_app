from redis.asyncio import Redis
from app.config import settings,logger



async def get_redis() -> Redis:

    redis_client = Redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        decode_responses=True # decode_responses=True,
        # для автоматического декодирования в str
    )
    try:
        await redis_client.ping()
        return redis_client
    except Exception as e:
        await redis_client.close()
        logger.error('Error for connect Redis')
        raise RuntimeError(f'Error for connect at Redis:{e}')