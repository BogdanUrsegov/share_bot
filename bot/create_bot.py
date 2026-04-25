import os
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from bot.middlewares.check_user import CheckUserMiddleware
from .routers import router

# Читаем переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

if not all([BOT_TOKEN, ADMIN_ID]):
    raise ValueError("Missing required env vars: BOT_TOKEN, ADMIN_ID")

# Создаём компоненты
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)
dp.message.middleware(CheckUserMiddleware())
dp.callback_query.middleware(CheckUserMiddleware())


# Экспортируем
__all__ = ["bot", "dp", "ADMIN_ID"]