import pytest
import httpx
from unittest.mock import AsyncMock

from pytest_httpx import HTTPXMock
from app.api.service import fetch_random_users,parse_user,process_users_batch
from app.api.models import User

@pytest.fixture
def httpx_mock(httpx_mock: HTTPXMock):
    return httpx_mock


@pytest.mark.asyncio
async def test_fetch_random_users_success(httpx_mock):
    # Тестовые данные
    test_user = {
        "login": {"uuid": "123"},
        "name": {"first": "Artem", "last": "Doe"},
        "email": "artem@example.com", 
        "phone": "123-456-7890",
        "location": {
            "street": {"number": 123, "name": "Main St"},
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postcode": "10001"
        },
        "picture": {"thumbnail": "https://example.com/thumb.jpg"}
    }


    mock_response = {"results": [test_user]}
    httpx_mock.add_response(
        url="https://randomuser.me/api/?results=10&page=1",
        json=mock_response  
    )


    # Вызов тестируемой функции
    responce_data = await fetch_random_users(count=10, page=1)

    # Проверки
    assert 'results' in responce_data
    users_data = responce_data['results']
    assert len(users_data) == 1
    assert users_data[0]["name"]["first"] == "Artem"



@pytest.mark.asyncio
async def test_parse_user_valid_data():
    test_data = {
        "login": {"uuid": "123e4567-e89b-12d3-a456-426614174000"},
        "gender": "male",
        "name": {"first": "John", "last": "Doe"},
        "email": "john@example.com",
        "phone": "123-456-7890",
        "location": {
            "street": {"number": 123, "name": "Main St"},
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postcode": "10001"
        },
        "picture": {"thumbnail": "https://example.com/thumb.jpg"}
    }
    
    # Вызов тестируемой функции
    user = await parse_user(test_data)
        
    # Проверки
    assert isinstance(user, User)
    assert user.first_name == "John"
    assert user.profile_url == "http://homepage/internal_user/123e4567-e89b-12d3-a456-426614174000"



@pytest.mark.asyncio
async def test_process_users_batch(mocker):
    # Тестовые данные
    test_batch = [
        {"name": {"first": "Alice"}, "login": {"uuid": "1"}},
        {"name": {"first": "Bob"}, "login": {"uuid": "2"}}
    ]

    # Настройка мока
    mock_parse = mocker.patch("app.api.service.parse_user", AsyncMock())
    mock_parse.side_effect = [
        User(first_name="Alice"),  # Для первого вызова
        User(first_name="Bob")     # Для второго
    ]

    # Вызов тестируемой функции
    result = await process_users_batch(test_batch)
    
    # Проверки
    assert len(result) == 2
    assert result[0].first_name == "Alice"
    assert result[1].first_name == "Bob"
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(test_batch[0])  # Проверяем аргументы


