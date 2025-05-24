from fastapi import HTTPException, logger
from app.api.models import User
from app.api.service import fetch_random_users,process_users_batch
# from app.api.service import fetch_random_users,parse_user,process_users_batch,fetch_users
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

class UserApi():

    def __init__(self,session:AsyncSession):
        self.session = session

    """Асинхронная загрузка пользователей из внешнего API с парсингом """
    async def async_load_user(self, total:int, batch_size:int = 5000) -> int:
           
        try:
            added_count = 0

        
            # Рассчитываем количество страниц
            total_pages = (total + batch_size - 1) // batch_size 
            
            for page in range(1, total_pages + 1):
                # Определяем количество пользователей для текущей страницы
                current_batch_size = min(batch_size, total - (page-1)*batch_size)
                
                # Загружаем данные с API
                response = await fetch_random_users(
                    count=current_batch_size,
                    page=page,
                )
                
                users = response['results']
                print(f"Загружено страница {page}: {len(users)} пользователей")
            
                for i in range(0, len(users), 100):  # Внутренний batch по 100 записей
                    small_batch = users[i:i + 100]
                    parsed_users = await process_users_batch(small_batch)
                    
                    for user_data in parsed_users:
                        # # Проверяем, существует ли пользователь с таким email
                        # existing_user = await self.session.execute(
                        #     select(User).where(User.email == user_data.email)
                        # )
                        # if existing_user.scalar_one_or_none() is None:
                        self.session.add(user_data)
                        await self.session.flush()  # Частичное сохранение
                        user_data.profile_url = f'http://homepage/internal_user/{user_data.id}'
                        added_count += 1
                
                
                await self.session.commit() 
            
            print(f"Всего загружено пользователей: {added_count}")
            return added_count
        
        except Exception as e:
            await self.session.rollback()
            print(f"Ошибка при загрузке пользователей: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"User loading failed: {str(e)}"
            )
        finally:
            await self.session.close()

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
        

    async def get_users_from_db(self,limit:int, offset:int = 0):
        try:
            query= select(User)
            users_in_db = await self.session.execute(
                query.order_by(User.id)
                .limit(limit)
                .offset(offset)
            )

            users_final = users_in_db.scalars().all()

            count_query = select(func.count()).select_from(User)


            total_all = (await self.session.execute(count_query)).scalar_one()

            return users_final, total_all
        
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
            status_code=500,
            detail="Database error"
        )