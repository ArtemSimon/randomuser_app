


from sqlalchemy import delete, select, text
from app.api.schemas import SUserResponse, SUserFind,SUserListResponce
from app.api.crud import UserApi
from app.api.models import User
from app.database import get_async_session
from app.config import logger
from fastapi import APIRouter,Depends, HTTPException, Query,status,Request
from fastapi.templating import Jinja2Templates
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()


templates = Jinja2Templates(directory="app/templates")

@router.get("/health")  # для проверки работоспособности сервера 
async def health_check():
    return {"status": "ok"}

@router.get('/users_in_db',response_model=SUserListResponce)
async def get_users(
    page: int,
    limit: int,
    session: AsyncSession = Depends(get_async_session)
): 
    try:
        
        logger.debug(f"Request params - page: {page}, limit: {limit}")

        user = UserApi(session)
        users_get,count = await user.get_users_from_db(limit,offset=(page-1)*limit)

        logger.info(f"Successfully returned {len(users_get)} users (page {page})")
       
        
        return {
            "data": users_get,
            "meta": {
                "total": count,
                "page": page,
                "per_page": limit,
                "total_pages": (count + limit - 1) // limit
            }
        }
    except Exception as e:
        logger.error(
            f"Unexpected error in /users_in_db endpoint: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get('/load_user')
async def load_user_random(
    count: int,
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    
    try:
        logger.info(f"User load request from {request.client.host} for {count} users")
        logger.debug(f"Request parameters - count: {count}")
        
        users_api = UserApi(session)
        users_count = await users_api.async_load_user(count)

        logger.info(f"Successfully loaded {users_count} users")
        logger.debug(f"Load operation completed for {count} requested users")
        
        return users_count
    
    except HTTPException as http_exc:
        # Уже обработанные HTTP ошибки
        logger.warning(f"HTTP error in load_user: {http_exc.detail}")
        raise

    except SQLAlchemyError as db_exc:
        logger.error(
            f"Database error while loading users: {str(db_exc)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Database operation failed"
        )


@router.delete("/reset/", summary="Удалить всех пользователей и сбросить ID")
async def reset_users (
    session: AsyncSession = Depends(get_async_session),
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
    try:
        logger.info(f"User profile request for ID: {user_id} from {request.client.host}")
        logger.debug(f"Request details: {request.method} {request.url}")

        user = UserApi(session)
        data_user = await user.get_user_by_id(user_id)

        logger.info(f"Successfully retrieved user ID: {user_id}")
        logger.debug(f"User data: {data_user.first_name} {data_user.last_name}")

        return templates.TemplateResponse(
            request,"user_profile.html",
            {
                "user": data_user,
                "title": f"Профиль {data_user.first_name} {data_user.last_name}"
            }
    )

    except HTTPException as http_exc:
        # Уже обработанные HTTP ошибки
        logger.warning(f"HTTP error in user profile: {http_exc.detail}")
        raise
        
    except SQLAlchemyError as db_exc:
        logger.error(
            f"Database error while fetching user {user_id}: {str(db_exc)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Database operation failed"
        )

@router.get('/random',response_model=SUserResponse,summary="Получение случайного пользователя")
async def get_random_user(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        logger.info(f"Random user profile request from {request.client.host}")
        logger.debug(f"Request details: {request.method} {request.url}")

        user_random = UserApi(session)
        data_user_random = await user_random.get_random_user()

        logger.info("Successfully retrieved random user")
        logger.debug(f"Random user ID: {data_user_random.id}, Name: {data_user_random.first_name} {data_user_random.last_name}")
        return templates.TemplateResponse(
            request, "user_profile.html",
            {
                "user": data_user_random,
                "title": f"Профиль {data_user_random.first_name} {data_user_random.last_name}"
            }
        )
    
    except HTTPException as http_exc:
        # Уже обработанные HTTP ошибки
        logger.warning(f"HTTP error in random user endpoint: {http_exc.detail}")
        raise
        
    except SQLAlchemyError as db_exc:
        logger.error(
            "Database error while fetching random user",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve random user due to database error"
        )
