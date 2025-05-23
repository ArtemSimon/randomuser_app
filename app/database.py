import asyncio


from app.api.models import Base
from app.config import get_db_url
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from typing import AsyncGenerator

DATA_BASE_URL = get_db_url()

engine = create_async_engine(DATA_BASE_URL)

async_session_maker = async_sessionmaker(engine,expire_on_commit=False)


# Создаем  ассинхронную сессию через ассинхронный генератор 

async def get_async_session() -> AsyncGenerator[AsyncSession,None]:
    async with async_session_maker() as session:
        yield session
        

async def create_tables():
    engine = create_async_engine(DATA_BASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)