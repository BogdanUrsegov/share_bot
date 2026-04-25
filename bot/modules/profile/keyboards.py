from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.modules.const_callb import (
    EARN_CALL, MAIN_MENU_CALLBACK, 
    TOP_UP_BALANCE_CALL, PROFILE_CALL,
    DAILY_CALL
)

profile_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Пополнить", callback_data=TOP_UP_BALANCE_CALL)],
        [InlineKeyboardButton(text="💰 Заработать", callback_data=EARN_CALL)],
        [InlineKeyboardButton(text="🎁 Ежедневный бонус", callback_data=DAILY_CALL)],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data=MAIN_MENU_CALLBACK)]
    ])

back_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data=PROFILE_CALL)]
    ])

main_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data=MAIN_MENU_CALLBACK)]
    ])

def get_payment_kb(amount: float, url: str, invoice_id: int, count: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f"💰 Оплатить {amount} USDT", url=url)
    kb.button(text="🔄 Проверить оплату", callback_data=f"check_invoice:{invoice_id}:{count}")
    
    kb.adjust(1)
    
    return kb.as_markup()