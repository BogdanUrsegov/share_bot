from sqlalchemy import update
import logging
from bot.database.models import PaymentRecord
from bot.database.session import AsyncSessionLocal


logger = logging.getLogger(__name__)

async def update_payment_status(crypto_invoice_id: str, status: str) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            stmt = (
                update(PaymentRecord)
                .where(PaymentRecord.crypto_invoice_id == crypto_invoice_id)
                .values(status=status)
            )
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка update_payment_status: {e}")
            return False