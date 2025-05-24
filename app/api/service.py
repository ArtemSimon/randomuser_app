import asyncio
import json
import math

from fastapi import Depends, HTTPException
from app.api.models import User
from app.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from typing import AsyncGenerator, List
import uuid
from app.config import logger

"""Асинхронный генератор, который загружает пользователей порциями"""
async def fetch_random_users(count: int, page: int = 1) -> AsyncGenerator[List[dict], None]:

    try:
        logger.debug(f"Starting to fetch {count} random users, page {page}")

        async with httpx.AsyncClient() as client:
            params = {
            "results": count,
            "page": page
        }
            
        async with httpx.AsyncClient() as client:
            logger.debug(f"Making request to randomuser.me with params: {params}")
            response = await client.get("https://randomuser.me/api/", params=params)
            response.raise_for_status()

            logger.info(f"Successfully fetched {count} users from API, page {page}")
            logger.debug(f"Response status: {response.status_code}")

            return response.json()
        
    except httpx.HTTPStatusError as e:
        logger.error(
            f"API returned error status: {e.response.status_code} "
            f"when fetching {count} users, page {page}. Error: {str(e)}"
        )
        raise HTTPException(
            status_code=502,
            detail="Bad response from randomuser API"
        )
    
    except httpx.RequestError as e:
        logger.error(
            f"Network error while fetching users: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=503,
            detail="Failed to connect to randomuser API"
        )
    
    except json.JSONDecodeError as e:
        logger.error(
            f"Failed to parse API response for {count} users, page {page}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Invalid response format from API"
        )

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

