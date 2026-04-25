import logging
from sqlalchemy import select, func
from bot.database.models import User, UserMedia
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def get_user_stats(telegram_id: int) -> dict:
    async with AsyncSessionLocal() as session:
        try:
            # Получаем баланс
            user_res = await session.execute(
                select(User.balance).where(User.telegram_id == telegram_id)
            )
            balance = user_res.scalar_one_or_none()
            
            if balance is None:
                return {"balance": 0, "photo_count": 0, "video_count": 0}

            # Считаем фото
            photo_res = await session.execute(
                select(func.count()).where(
                    UserMedia.user_id == telegram_id,
                    UserMedia.type_media == "photo"
                )
            )
            photo_count = photo_res.scalar_one()

            # Считаем видео
            video_res = await session.execute(
                select(func.count()).where(
                    UserMedia.user_id == telegram_id,
                    UserMedia.type_media == "video"
                )
            )
            video_count = video_res.scalar_one()

            return {
                "balance": balance,
                "photo_count": photo_count,
                "video_count": video_count
            }
        except Exception as e:
            logger.error(f"Ошибка get_user_stats: {e}")
            return {"balance": 0, "photo_count": 0, "video_count": 0}