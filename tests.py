import pytest
from database import add_new_user, check_user_in_db


@pytest.mark.asyncio
async def test_add_new_user():
    # Параметры для тестирования
    telegram_id = "1234567890"
    telegram_username = "test_user"
    username = "Test User"

    # Выполняем тестирование функции
    await add_new_user(
        telegram_id=telegram_id,
        telegram_username=telegram_username,
        username=username
    )

    # Проверяем, что пользователь был добавлен в базу данных
    user = await check_user_in_db(telegram_id)
    assert user is not None

