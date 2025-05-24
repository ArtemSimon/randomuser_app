import asyncio
import math

from fastapi import Depends
from app.api.models import User
from app.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from typing import AsyncGenerator, List
import uuid

"""Асинхронный генератор, который загружает пользователей порциями"""
async def fetch_random_users(count: int, page: int = 1) -> AsyncGenerator[List[dict], None]:
    async with httpx.AsyncClient() as client:
        params = {
        "results": count,
        "page": page
    }
        
    async with httpx.AsyncClient() as client:
        response = await client.get("https://randomuser.me/api/", params=params)
        return response.json()

"""Парсинг данных API -> User модель"""
async def parse_user(user_data: dict) -> User:
    return User(
        external_id=uuid.UUID(user_data["login"]["uuid"]),
        gender=user_data["gender"],
        first_name=user_data["name"]["first"],
        last_name=user_data["name"]["last"],
        email=user_data["email"],
        phone=format_phone(user_data["phone"]),
        street=f"{user_data['location']['street']['number']} {user_data['location']['street']['name']}",
        city=user_data["location"]["city"],
        state=user_data["location"]["state"],
        country=user_data["location"]["country"],
        postcode=str(user_data["location"]["postcode"]),
        picture_thumbnail=user_data["picture"]["thumbnail"],
        profile_url = f"http://homepage/internal_user/{user_data['login']['uuid']}"
    )

"""Обработка пакета пользователей"""
async def process_users_batch(batch: List[dict]) -> List[User]:
    return await asyncio.gather(*[parse_user(user) for user in batch])


"""Форматирование телефонного номера"""
def format_phone(phone: str) -> str:
    return "+" + "".join(filter(str.isdigit, phone))

