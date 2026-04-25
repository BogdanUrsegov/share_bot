import logging
from sqlalchemy import select
from bot.database.models import User
from bot.database.session import AsyncSessionLocal


logger = logging.getLogger(__name__)


async def user_checker(telegram_id: int):
    async with AsyncSessionLocal() as session:
        try:
            query = select(User.telegram_id).where(User.telegram_id == telegram_id).limit(1)
            result = await session.execute(query)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Ошибка user_checker: {e}")
            await session.rollback()
            raise