import logging
from sqlalchemy import delete
from bot.database.models import Media
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def delete_media_by_file_id(file_id: str):
    async with AsyncSessionLocal() as session:
        try:
            stmt = delete(Media).where(Media.file_id == file_id)
            result = await session.execute(stmt)
            await session.commit()
            
            if result.rowcount == 0:
                logger.warning(f"Файл с ID {file_id} не найден для удаления")
            else:
                logger.info(f"Файл {file_id} успешно удален из БД")
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка delete_media_by_file_id: {e}")
            raise