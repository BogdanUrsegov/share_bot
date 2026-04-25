import logging
from bot.database.models import Media
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def add_media(media_type: str, file_id: str):
    async with AsyncSessionLocal() as session:
        try:
            new_media = Media(type=media_type, file_id=file_id)
            session.add(new_media)
            await session.commit()
            return True, None
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка add_media: {e}")
            return False, str(e)