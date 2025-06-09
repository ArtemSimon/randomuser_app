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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код,который выполняется при запуске приложения
    logger.info('Starting app')
    await create_tables()
    async with async_session_maker() as session:
        start_app = UserApi(session)
        await start_app.async_load_user(1000)
        logger.info('Loading 1000 users completed')

    # Приложение работает
    yield



app= FastAPI(lifespan=lifespan)

app.include_router(router_randomuser)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse(request, "base.html")
