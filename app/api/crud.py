from fastapi import HTTPException
from app.api.models import User
from app.api.service import fetch_random_users,process_users_batch
from uuid import UUID
from typing import Tuple, List
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError,NoResultFound,MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import logger
class UserApi():

    def __init__(self,session:AsyncSession):
        self.session = session

    """Асинхронная загрузка пользователей из внешнего API с парсингом """
    async def async_load_user(self, total:int, batch_size:int = 5000) -> int:
           
        try:
            added_count = 0
            logger.info(f"Starting user loading process. Total: {total}, batch size: {batch_size}")
        
            # Рассчитываем количество страниц
            total_pages = (total + batch_size - 1) // batch_size 
            logger.debug(f"Total pages to process: {total_pages}")
            
            for page in range(1, total_pages + 1):
                
                try:
                    # Определяем количество пользователей для текущей страницы
                    current_batch_size = min(batch_size, total - (page-1)*batch_size)
                    logger.debug(f"Processing page {page}/{total_pages} with batch size {current_batch_size}")

                    # Загружаем данные с API
                    response = await fetch_random_users(
                        count=current_batch_size,
                        page=page,
                    )
                    
                    users = response['results']
                    logger.info(f"Successfully fetched page {page}: {len(users)} users")
                
                    for i in range(0, len(users), 100):  # Внутренний batch по 100 записей
                        small_batch = users[i:i + 100]
                        parsed_users = await process_users_batch(small_batch)
                        
                        for user_data in parsed_users:
                            self.session.add(user_data)
                            await self.session.flush()  # Частичное сохранение
                            user_data.profile_url = f'http://homepage/internal_user/{user_data.id}'
                            added_count += 1
                    
                    
                    await self.session.commit() 
                    last_successful_page = page
                    logger.debug(f"Successfully committed page {page}")
                
                except Exception as page_error:
                    logger.error(f"Error processing page {page}: {str(page_error)}")
                    await self.session.rollback()
                    continue
            
            logger.info(f"User loading completed. Total added: {added_count}")    
            return added_count
        
        except Exception as global_error:
            logger.critical(f"Critical error in user loading process: {str(global_error)}")
            await self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail={"message": "User loading process failed",
                "last_successful_page": last_successful_page,
                "users_added": added_count,
                "error": str(global_error)}
            )
        finally:
                try:
                    await self.session.close()
                    logger.debug("Database session closed")
                except Exception as close_error:
                    logger.error(f"Error closing session: {str(close_error)}")

    """ Получение конкретного пользователя по id """
    async def get_user_by_id(self,user_id:int) -> User:
        try:
            logger.debug(f"Trying to get user from ID: {user_id}")
            query = select(User).filter(User.id==user_id)
            logger.debug(f"Executing query: {query}")

            data_user = await self.session.execute(query)
            all_record = data_user.scalar_one_or_none()

            logger.debug(f"User successfully received: {user_id}")
            return all_record
        
        except NoResultFound:
            logger.warning(f"User with ID {user_id} not found (NoResultFound)")
            return None
        except MultipleResultsFound:
            logger.error(f"Found several users with ID {user_id}!")
            raise HTTPException(
                status_code=500,
                detail=f"Database Error: Multiple users found with ID {user_id}"
            )
        except SQLAlchemyError as e:
            logger.error(
            f"Database error while querying user {user_id}: {str(e)}",
            exc_info=True
        )
            raise HTTPException(
                status_code=500,
                detail="Internal server error while retrieving user"
            )


    """ Получение случайного пользователя """
    async def get_random_user(self) -> User:
        try:

            logger.debug("Attempting to fetch random user from database")
            query = select(User).order_by(func.random()).limit(1) # SELECT * FROM users ORDER BY RAND() LIMIT 1 
            logger.debug(f"Executing query: {query}")
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()
        
            if not user:
                logger.warning("No users found in database when fetching random user")
                raise HTTPException(
                    status_code=404,
                    detail="В базе данных нет пользователей"
                )      
            
            logger.info(f"Successfully fetched random user ID: {user.id}")
            logger.debug(f"User details - Email: {user.email} | Name: {user.first_name} {user.last_name}")
            return user
            
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while fetching random user: {str(e)}",
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve random user due to database error"
            )
        
    """Получаем пользователей из базы данных """
    async def get_users_from_db(self,limit:int, offset:int = 0) -> Tuple[List[User],int]:
        try:

            logger.debug(f"Fetching users from DB with limit={limit}, offset={offset}")

            query= select(User)
            logger.debug(f"Executing users query: {query}")
            users_in_db = await self.session.execute(
                query.order_by(User.id)
                .limit(limit)
                .offset(offset)
            )

            users_final = users_in_db.scalars().all()

            count_query = select(func.count()).select_from(User)
            logger.debug(f"Executing count query: {count_query}")

            total_all = (await self.session.execute(count_query)).scalar_one()

            logger.info(f"Successfully fetched {len(users_final)}/{total_all} users")
            logger.debug(f"First user ID: {users_final[0].id if users_final else 'None'}")

            return users_final, total_all
        
        except NoResultFound:
            logger.error("No users found in database during paginated query")
            return [], 0
        
        
        except SQLAlchemyError as e:
            logger.error(
                f"Database error while fetching users (limit={limit}, offset={offset}): {str(e)}",
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve users from database"
            )