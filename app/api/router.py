
import logging

from sqlalchemy import delete, select, text
from app.api.schemas import SUserResponse, SUserFind
from app.api.crud import UserApi
from app.api.models import User
from app.database import get_async_session
from fastapi import APIRouter,Depends, HTTPException, Query, logger,status,Request
from fastapi.templating import Jinja2Templates
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")

@router.get("/health")  # для проверки работоспособности сервера 
async def health_check():
    return {"status": "ok"}

@router.get('/users_in_db')
async def get_users(
    page: int,
    limit: int,
    session: AsyncSession = Depends(get_async_session)
):
    user = UserApi(session)
    users_get,count = await user.get_users_from_db(limit,offset=(page-1)*limit)
    return {
        "data": users_get,
        "meta": {
            "total": count,
            "page": page,
            "per_page": limit,
            "total_pages": (count + limit - 1) // limit
        }
    }


@router.get('/load_user')
async def load_user_random(
    count: int,
    session: AsyncSession = Depends(get_async_session),
):
    users_api = UserApi(session)
    users_count = await users_api.async_load_user(count)
    if not users_api:
        return {'message':f'Пользователи не загрузились'}
    return users_count


@router.delete("/reset/", summary="Удалить всех пользователей и сбросить ID")
async def reset_users (
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Удаляем всех пользователей
        await session.execute(delete(User))
        
        # Сбрасываем SEQUENCE
        await session.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1;"))
        await session.commit()
        
        return {"message": "Все пользователи удалены, ID сброшен."}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/internal_user/{user_id}',response_model=SUserResponse,summary="Получение пользователя по id")
async def get_user(
    user_id: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    user = UserApi(session)
    data_user = await user.get_user_by_id(user_id)
    return templates.TemplateResponse(
        "user_profile.html",
        {
            "request": request,
            "user": data_user,
            "title": f"Профиль {data_user.first_name} {data_user.last_name}"
        }
    )

@router.get('/random',response_model=SUserResponse,summary="Получение случайного пользователя")
async def get_random_user(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    user_random = UserApi(session)
    data_user_random = await user_random.get_random_user()
    return templates.TemplateResponse(
        "user_profile.html",
        {
            "request": request,
            "user": data_user_random,
            "title": f"Профиль {data_user_random.first_name} {data_user_random.last_name}"
        }
    )
