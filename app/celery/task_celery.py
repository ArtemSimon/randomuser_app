import asyncio
from fastapi import Depends
from redis.asyncio import Redis
from app.celery.celery_app import celery 
from app.core.redis import get_redis
from app.config import logger



# @celery.task(bind=True)
# async def load_users_task(self):
#     try:
#         redis = await get_redis()  # Самостоятельно получаем соединение
        
#         await redis.publish('task_message', 'Load users start')
        
#         await asyncio.sleep(5) # Асинхронное ожидание
        
#         await redis.publish('task_message', 'Load users end')
#         logger.info("Task completed")

#         return {"status": "success"}
#     except Exception as e:
#         logger.error(f'Task failed {e}')

@celery.task(bind=True)
def load_users_task(self):
    async def _async_wrapper():
        try:
            redis = await get_redis()  # Ваша функция получения Redis
            
            # Публикуем сообщения
            await redis.publish('task_message', 'Load users start')
            logger.info("Task started")
            
            # Имитация работы
            for i in range(5):
                self.update_state(state='PROGRESS', meta={'current': i+1})
                await asyncio.sleep(1)
            
            message = 'Load users end'
            await redis.publish('task_message', message)
            logger.info("Task completed")
            
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f'Task failed: {e}')
            raise  # Пробрасываем исключение для retry

    # Запускаем асинхронный код
    return asyncio.get_event_loop().run_until_complete(_async_wrapper())