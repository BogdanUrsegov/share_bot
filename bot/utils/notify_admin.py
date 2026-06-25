import os
from aiogram import Bot
import logging


logger = logging.getLogger(__name__)

ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else None


async def notify_admin(bot: Bot, text: str):
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, text)
        except Exception as e:
            logger.error(f"Ошибка отправки админу: {e}")