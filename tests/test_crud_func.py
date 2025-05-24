import pytest
import httpx

from app.main import app
from app.api.crud import UserApi
from app.api.models import User
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from pytest_httpx import HTTPXMock
from unittest.mock import AsyncMock, MagicMock, patch



@pytest.mark.asyncio
async def test_async_load_user():
    mock_session = AsyncMock()
     # Мокаем add и commit как async
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()


    mock_fetch = AsyncMock(return_value={"results": [{"id": 1}, {"id": 2}]})
    mock_process = AsyncMock(return_value=[User(id=1), User(id=2)])

    with patch("app.api.service.fetch_random_users", mock_fetch), \
        patch("app.api.service.process_users_batch", mock_process):
        
        user_api = UserApi(mock_session)
        result = await user_api.async_load_user(total=2, batch_size=1)
        
        assert result == 2
        mock_session.add.assert_called()
        mock_session.commit.assert_awaited()

@pytest.mark.asyncio
async def test_get_user_by_id():
    mock_session = AsyncMock()
    
    # Создаём mock-объект пользователя
    mock_user = User(id=1, first_name="John", last_name="Doe")
    
    # Создаём mock для data_user.scalar_one_or_none()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    
    # Создаём mock для session.execute (чтобы вернуть mock_result при await)
    mock_session.execute = AsyncMock(return_value=mock_result)

    user_api = UserApi(mock_session)
    result = await user_api.get_user_by_id(1)

    assert result is not None
    assert result.id == 1


@pytest.mark.asyncio
async def test_get_random_user():
    mock_session = AsyncMock()

    # Создаем mock-пользователя
    mock_user = User(id=1, first_name="Artem", last_name="As")

    # Мокируем результат execute и scalar_one_or_none
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user

    mock_session.execute = AsyncMock(return_value=mock_result)

    user_api = UserApi(mock_session)
    result = await user_api.get_random_user()

    assert result is not None
    assert result.id == 1




@pytest.mark.asyncio
async def test_get_users_from_db():
    mock_session = AsyncMock()

    # Создаем мок пользователей
    mock_users = [
        User(id=1, first_name="Thomas", last_name="Doe"),
        User(id=2, first_name="Jane", last_name="Smith")
    ]

    # Мокируем результат для основного запроса
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_users

    # Мокируем count
    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 2

    mock_session.execute = AsyncMock(
        side_effect=[mock_result, mock_count_result]
    )

    user_api = UserApi(mock_session)
    users, total = await user_api.get_users_from_db(limit=2, offset=0)

    assert len(users) == 2
    assert total == 2
    assert users[0].id == 1
    assert users[1].id == 2



@pytest.mark.asyncio
async def test_get_users_from_db_empty_result():
    mock_session = AsyncMock()

    # Пользователей нет 
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_session.execute = AsyncMock(return_value=mock_result)

    # Count = 0
    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 0
    mock_session.execute.return_value = mock_count_result

    user_api = UserApi(mock_session)
    users, total = await user_api.get_users_from_db(limit=2, offset=100)

    assert len(users) == 0
    assert total == 0

