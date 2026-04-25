from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable
import logging

from bot.database.utils import user_checker


logger = logging.getLogger(__name__)

class CheckUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        text = ""

        if isinstance(event, Update):
            if event.message:
                user, text = event.message.from_user, event.message.text or ""
            elif event.callback_query:
                user = event.callback_query.from_user
        elif isinstance(event, Message):
            user, text = event.from_user, event.text or ""
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        # Регистронезависимый пропуск /start
        if text.lower().startswith("/start"):
            return await handler(event, data)

        try:
            if user and await user_checker(user.id):
                return await handler(event, data)
        except Exception as e:
            logger.error(f"[Middleware] check_user_suitable failed for {user.id}: {e}")
            return None  # или raise, если нужно прерывать бота

        return None