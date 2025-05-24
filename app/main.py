from app.api.router import router as router_randomuser
from app.database import create_tables
from app.api.crud import UserApi
from app.database import get_async_session,async_session_maker
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI,Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

app= FastAPI()
app.include_router(router_randomuser)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "title": "Главная страница",
            "message": "Добро пожаловать!"
        }
    )


@app.on_event("startup")
async def on_startup():
    await create_tables()
    async with async_session_maker() as session:
        start_app = UserApi(session)
        await start_app.async_load_user(1000)