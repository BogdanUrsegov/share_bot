import logging
import random
from sqlalchemy import select
from bot.database.models import Media, UserMedia
from bot.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def get_random_file_id(user_id: int, media_type: str) -> str | None:
    async with AsyncSessionLocal() as session:
        try:
            # 1. Получаем все file_id этого типа
            all_res = await session.execute(
                select(Media.file_id).where(Media.type == media_type)
            )
            all_ids = [row[0] for row in all_res.fetchall()]
            if not all_ids:
                return None

            # 2. Получаем просмотренные этим юзером
            viewed_res = await session.execute(
                select(UserMedia.file_id).where(
                    UserMedia.user_id == user_id,
                    UserMedia.type_media == media_type
                )
            )
            viewed_ids = {row[0] for row in viewed_res.fetchall()}

            # 3. Ищем новые (непросмотренные)
            new_ids = [fid for fid in all_ids if fid not in viewed_ids]
            
            # Если есть новые - берем новый, иначе - любой старый
            target_list = new_ids if new_ids else all_ids
            
            return random.choice(target_list)
        except Exception as e:
            logger.error(f"Ошибка get_random_file_id: {e}")
            return None