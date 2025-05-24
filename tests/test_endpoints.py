
import pytest
import httpx
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from pytest_httpx import HTTPXMock
from app.api.crud import UserApi
from app.api.models import User
from app.main import app


transport = httpx.ASGITransport(app=app)

@pytest.mark.asyncio
async def test_get_user_by_id():
    # 1. Создаем мок с правильной структурой
    mock_user = AsyncMock()
    mock_user.first_name = "John"
    mock_user.last_name = "Doe"
    mock_user.email = "john@example.com"
    mock_user.picture_thumbnail = "https://example.com/avatar.jpg"
    mock_user.phone = "+7 123 456-78-90"
    mock_user.street = "ул. Ленина, 10"
    mock_user.city = "Москва"
    mock_user.country = "Россия"
    mock_user.gender = "male"
    # Добавляем другие необходимые атрибуты

    # 2. Мокаем метод
    with patch(
        "app.api.crud.UserApi.get_user_by_id",
        new_callable=AsyncMock,
        return_value=mock_user
    ) as mock_method:
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 3. Делаем запрос
            response = await client.get("/internal_user/1")
        
        # 4. Проверяем
        assert response.status_code == 200
        assert "Профиль John Doe" in response.text  # Проверяем рендеринг
        mock_method.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_random_user():
    mock_random = AsyncMock()
    mock_random.first_name = "Artem"
    mock_random.last_name = "As"
    mock_random.email = "artem@example.com"
    mock_random.picture_thumbnail = "https://example.com/avatar.jpg"
    mock_random.phone = "+7 568 741-21-75"
    mock_random.street = "ул. Ленина, 10"
    mock_random.city = "Москва"
    mock_random.country = "Россия"
    mock_random.gender = "male"

    
    # 2. Мокаем метод
    with patch(
        "app.api.crud.UserApi.get_random_user",
        new_callable=AsyncMock,
        return_value=mock_random
    ) as mock_method:
      
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 3. Делаем запрос
            response =  await client.get("/random")
        
        # 4. Проверяем
        assert response.status_code == 200
        assert "Профиль Artem As" in response.text  # Проверяем рендеринг
        mock_method.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_users_in_db():
    # Подготавливаем мок-данные
    mock_users = [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            'gender': 'male',
            "email": "john@example.com",
            "phone": "+1234567890",
            "street": "123 Main St",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postcode": "10001",
            "profile_url": "https://example.com/profiles/1",
            "picture_thumbnail": "https://example.com/thumbs/1.jpg"
    }

        
    ]
    mock_meta = {
        "total": 100,
        "page": 1,
        "per_page": 10,
        "total_pages": 10
    }



    # Мокаем метод get_users_from_db
    with patch("app.api.crud.UserApi.get_users_from_db", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = (mock_users, 100)  # Возвращаем пользователей и общее количество

        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/users_in_db?page=1&limit=10")
        
        # Проверяем ответ
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["first_name"] == "John"
        assert data["meta"]["total"] == 100
        mock_method.assert_awaited_once_with(10, offset=0)


@pytest.mark.asyncio
async def test_load_user_random():
    # Мокаем метод async_load_user
    with patch("app.api.crud.UserApi.async_load_user", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = {"message": "10 users loaded"}
        
        # Вызываем эндпоинт
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/load_user?count=10")
        
        # Проверяем ответ
        assert response.status_code == 200
        assert response.json()["message"] == "10 users loaded"
        mock_method.assert_awaited_once_with(10)

# Тест на ошибочную загрузку
@pytest.mark.asyncio
async def test_load_user_random_failure():
    # Мокаем неудачную загрузку
    with patch("app.api.crud.UserApi.async_load_user", new_callable=AsyncMock) as mock_method:
        mock_method.return_value = None
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/load_user?count=10")
        
        assert response.status_code == 200
        assert response.text == "null"  
        mock_method.assert_awaited_once_with(10)