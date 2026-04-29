from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.modules.const_callb import EARN_CALL, GIVE_LITTLE_CALL, GIVE_LOT_CALL, SKIP_GIVE_CALL


back_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data=EARN_CALL)]
    ])

async def award_menu(user_id: int):
    user_id_str = str(user_id)
    return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Выдать мало (4-6)", callback_data=GIVE_LITTLE_CALL+user_id_str)],
            [InlineKeyboardButton(text="Выдать МНОГО (8-10)", callback_data=GIVE_LOT_CALL+user_id_str)],
            [InlineKeyboardButton(text="Пропустить", callback_data=SKIP_GIVE_CALL+user_id_str)]
        ])