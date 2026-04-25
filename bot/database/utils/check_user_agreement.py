import logging
from sqlalchemy import select
from bot.database.models import User
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def check_user_agreement(telegram_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            stmt = select(User.agreement).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            agreement = result.scalar_one_or_none()
            
            return agreement if agreement is not None else False
            
        except Exception as e:
            logger.error(f"Ошибка check_user_agreement: {e}")
            return False