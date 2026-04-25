from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.modules.const_callb import PHOTO_CALL, PROFILE_CALL, VIDEO_CALL, MAIN_MENU_CALLBACK
import os


LINK_PREVIEW = os.getenv("LINK_PREVIEW")


categories_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📷 Фото", callback_data=PHOTO_CALL),
            InlineKeyboardButton(text="🎥 Видео", callback_data=VIDEO_CALL)

        ],
        [
            InlineKeyboardButton(text="🗒 Резервный канал", url=LINK_PREVIEW)
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data=MAIN_MENU_CALLBACK)
        ]
    ]
)

short_categories_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📷 Фото", callback_data=PHOTO_CALL),
            InlineKeyboardButton(text="🎥 Видео", callback_data=VIDEO_CALL)

        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data=MAIN_MENU_CALLBACK)
        ]
    ]
)

profile_n_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data=PROFILE_CALL)
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data=MAIN_MENU_CALLBACK)
        ]
    ]
)