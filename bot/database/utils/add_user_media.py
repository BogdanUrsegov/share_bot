import logging
from bot.database.models import UserMedia
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def add_user_media(user_id: int, media_type: str, file_id: str):
    async with AsyncSessionLocal() as session:
        try:
            new_record = UserMedia(user_id=user_id, type_media=media_type, file_id=file_id)
            session.add(new_record)
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка add_user_media: {e}")
            raise