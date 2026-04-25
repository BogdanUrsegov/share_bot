from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.modules.const_callb import AGREE_TERMS_CALLBACK, LOOK_CALL, PROFILE_CALL

agree_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Agree ✅", callback_data=AGREE_TERMS_CALLBACK)],
    ]
)

categories_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👀 Смотреть", callback_data=LOOK_CALL)
        ],
        [
            InlineKeyboardButton(text="👤 Профиль", callback_data=PROFILE_CALL)
        ]
    ]
)
