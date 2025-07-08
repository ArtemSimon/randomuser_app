import asyncio
from fastapi import Depends
from app.core.redis import get_redis
from redis.asyncio import Redis
from telegram import Bot
from app.config import logger

bot = Bot(token="8019078191:AAE8xuB_xybCZ8R9puza1q0gt8Pkx-0yoDk")
CHAT_ID = 988345361  # Ваш chat_id


# async def listen_events(
        
# ):
#     redis = await get_redis()
#     pubsub = redis.pubsub()
#     await pubsub.subscribe("task_message")  # Канал, куда Celery публикует
#     logger.info("Subscribed to Redis channel")
    
#     print("Ожидание событий...")

#     while True:
#         message = await pubsub.get_message()
#         if message is None:
#             continue
#         # if message["type"] == "message":
#         event = message["data"].decode()
#         await bot.send_message(chat_id=CHAT_ID, text=event)
#         print(f"Уведомление отправлено: {event}")

async def listen_events():
    redis = None
    while True:
        try:
            if redis is None:
                redis = await get_redis()
                pubsub = redis.pubsub()
                await pubsub.subscribe('task_message')
                logger.info("Subscribed to Redis channel")

            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1.0
            )
            
            if not message:
                continue
                
            await _process_message(message)
                
        except (ConnectionError) as e:
            logger.error(f"Redis error: {e}")
            await asyncio.sleep(5)
            redis = None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await asyncio.sleep(1)

async def _process_message(message):
    try:
        text = message['data']
        await bot.send_message(
            chat_id=CHAT_ID,
            text=text,
            parse_mode='HTML'
        )
        logger.info(f"Message sent to Telegram: {text}")
    except Exception as e:
        logger.error(f"Telegram error: {e}")