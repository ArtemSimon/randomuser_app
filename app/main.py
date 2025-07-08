import asyncio
from contextlib import asynccontextmanager
from app.api.router import router as router_randomuser
from app.database import create_tables
from app.api.crud import UserApi
from app.database import get_async_session,async_session_maker
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI,Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import logger
from app.core.redis import get_redis
from app.core.subscriber import listen_events

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код,который  выполняется при запуске приложения
    logger.info('Starting app')
    await create_tables()
    redis = await get_redis()
    async with async_session_maker() as session:
        start_app = UserApi(session)
        await start_app.async_load_user(1000)
        logger.info('Loading 1000 users completed')
    
    
    listener_task = asyncio.create_task(listen_events())
    logger.info('Redis listener started in background')

    try:
        # 4. Передаем управление приложению
        yield {'redis': redis}
    finally:
        # 5. Очистка ресурсов при завершении
        logger.info('Stopping application...')
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            logger.info('Redis listener stopped gracefully')
        await redis.close()

        
    # # Приложение работает
    # yield {'redis':redis}
    
    # await redis.close()



app= FastAPI(lifespan=lifespan)

app.include_router(router_randomuser)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse(request, "base.html")
