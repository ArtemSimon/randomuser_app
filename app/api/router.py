
from app.api.schemas import SUserResponse, SUserFind
from app.api.crud import UserApi
from app.database import get_async_session
from fastapi import APIRouter,Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.service import fetch_random_users,parse_user

router = APIRouter()



@router.get("/health")  # для проверки работоспособности сервера 
async def health_check():
    return {"status": "ok"}

@router.get('/load_user')
async def load_user_random(
    count: int,
    session: AsyncSession = Depends(get_async_session),
):
    users_api = UserApi(session)
    if not users_api:
        return {'message':f'Пользователи не загрузились'}
    return await users_api.async_load_user(count)

@router.get('/internal_user/{user_id}',response_model=SUserResponse,summary="Получение пользователя по id")
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    user = UserApi(session)
    data_user = await user.get_user_by_id(user_id)
    if data_user is None:
        return {'message':f'Записи с таким  нету'}  # сделать нормальное логирование
    return data_user

@router.get('/random',response_model=SUserResponse,summary="Получение случайного пользователя")
async def get_random_user(
    session: AsyncSession = Depends(get_async_session)
):
    user_random = UserApi(session)
    data_user_random = await user_random.get_random_user()
    if data_user_random is None:
        return {'message':f'Записи с таким {data_user_random.id} нету'}
    return data_user_random