import logging
from sqlalchemy import select, update
from bot.database.models import User
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def decrease_balance(telegram_id: int, amount: float) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            # 1. Проверяем текущий баланс
            res = await session.execute(
                select(User.balance).where(User.telegram_id == telegram_id)
            )
            current_balance = res.scalar_one_or_none()

            if current_balance is None or current_balance < amount:
                return False

            # 2. Вычитаем сумму
            stmt = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(balance=User.balance - amount)
            )
            await session.execute(stmt)
            await session.commit()
            return True
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка decrease_balance: {e}")
            return False