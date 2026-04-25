import logging
import time
from sqlalchemy import update
from bot.database.models import User
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def update_daily_time(telegram_id: int):
    async with AsyncSessionLocal() as session:
        try:
            now = int(time.time())
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(daily_time=now)
            )
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка update_daily_time: {e}")
            raise