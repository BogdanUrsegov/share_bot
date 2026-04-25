import time
from sqlalchemy import select
from bot.database.models import User
from bot.database.session import AsyncSessionLocal

async def can_claim_daily_bonus(telegram_id: int) -> bool:
    now = int(time.time())
    day_in_seconds = 86400

    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(User.daily_time).where(User.telegram_id == telegram_id)
        )
        last_time = res.scalar_one_or_none()

        # Если никогда не получал или прошло больше 24 часов
        if last_time is None or (now - last_time) >= day_in_seconds:
            return True
        return False