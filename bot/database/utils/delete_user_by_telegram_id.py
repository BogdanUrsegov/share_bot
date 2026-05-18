import logging
from sqlalchemy import delete
from bot.database.models import User, UserMedia, PaymentRecord
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def delete_user_by_telegram_id(telegram_id: int):
    async with AsyncSessionLocal() as session:
        try:
            # Удаляем связанные записи
            await session.execute(delete(UserMedia).where(UserMedia.user_id == telegram_id))
            await session.execute(delete(PaymentRecord).where(PaymentRecord.user_id == telegram_id))
            
            # Удаляем пользователя
            result = await session.execute(delete(User).where(User.telegram_id == telegram_id))
            
            await session.commit()
            
            if result.rowcount == 0:
                return False, "Пользователь не найден"
            
            return True, None
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка delete_user_by_telegram_id: {e}")
            return False, str(e)