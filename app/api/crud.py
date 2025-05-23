from fastapi import HTTPException, logger
from app.api.models import User
from app.api.service import fetch_random_users,parse_user
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

class UserApi():

    def __init__(self,session:AsyncSession):
        self.session = session

    """Асинхронная загрузка пользователей из внешнего API с парсингом """
    async def async_load_user(self,count:int) -> int:

        try:
            users_data = await fetch_random_users(count)
            users_dict = [parse_user(user_data) for user_data in users_data]
            self.session.add_all()
            await self.session.commit()
            return len(users_dict)
        
        except Exception as e:
            await self.session.rollback()
            return {'message':f'Ошибка при загрузке пользователей'}
            raise HTTPException(
            status_code=500,
            detail=f"User loading failed: {str(e)}"
        )

    """ Получение конкретного пользователя по id """
    async def get_user_by_id(self,user_id:int) -> User:
        try:
            query = select(User).filter(User.id==user_id)
            data_user = await self.session.execute(query)
            all_record = data_user.scalar_one_or_none()
            return all_record
        except SQLAlchemyError as e:
            pass # тут будет логирование 


    """ Получение случайного пользователя """
    async def get_random_user(self) -> User:
        try:
            query = select(User).order_by(func.random()).limit(1) # SELECT * FROM users ORDER BY RAND() LIMIT 1 
            print(query)
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()
        
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="В базе данных нет пользователей"
                )      
            return user
            
        except SQLAlchemyError as e:
            logger.error(f"Random user fetch failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Не удалось получить случайного пользователя."
            )