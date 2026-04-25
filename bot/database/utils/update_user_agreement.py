import logging
from sqlalchemy import select
from bot.database.models import User
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def update_user_agreement(telegram_id: int):
    async with AsyncSessionLocal() as session:
        try:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                user.agreement = True
                await session.commit()
            else:
                logger.warning(f"Пользователь {telegram_id} не найден для обновления agreement")
                
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка update_user_agreement: {e}")
            raise