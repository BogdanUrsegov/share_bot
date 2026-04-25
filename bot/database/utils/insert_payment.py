from bot.database.session import AsyncSessionLocal
from bot.database.models import PaymentRecord
import logging
from sqlalchemy import insert


logger = logging.getLogger(__name__)

async def insert_payment(data: dict) -> int:
    async with AsyncSessionLocal() as session:
        try:
            stmt = insert(PaymentRecord).values(**data)
            result = await session.execute(stmt)
            await session.commit()
            return result.inserted_primary_key[0]
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка insert_payment: {e}")
            return 0