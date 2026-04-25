import logging
from bot.database.models import User
from bot.database.session import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def add_user(telegram_id: int):
    async with AsyncSessionLocal() as session:
        try:
            new_user = User(telegram_id=telegram_id)
            session.add(new_user)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка add_user: {e}")
            raise