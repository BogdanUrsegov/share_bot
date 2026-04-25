import logging
from sqlalchemy import update
from bot.database.models import User
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def increase_balance(telegram_id: int, count: float):
    async with AsyncSessionLocal() as session:
        try:
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(balance=User.balance + count)
            )
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка increase_balance: {e}")
            raise