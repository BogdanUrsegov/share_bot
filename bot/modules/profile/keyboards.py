import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.modules.const_callb import (
    EARN_CALL, LOOK_CALL, MAIN_MENU_CALLBACK, 
    TOP_UP_BALANCE_CALL, PROFILE_CALL,
    DAILY_CALL, EARN_FRIENDS_CALL, EARN_CONTENT_CALL
)

from bot.services.rollypay import RollyPay

rollypay = RollyPay(
    api_key=os.getenv("ROLLYPAY_API_KEY")
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

profile_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Пополнить", callback_data=TOP_UP_BALANCE_CALL)],
        [InlineKeyboardButton(text="💰 Заработать", callback_data=EARN_CALL)],
        [InlineKeyboardButton(text="🎁 Ежедневный бонус", callback_data=DAILY_CALL)],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data=MAIN_MENU_CALLBACK)]
    ])

back_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data=PROFILE_CALL)]
    ])

earn_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👬 Пригласить друга", callback_data=EARN_FRIENDS_CALL)],
        [InlineKeyboardButton(text="📸 Предложить контент", callback_data=EARN_CONTENT_CALL)],
        [InlineKeyboardButton(text="↩️ Назад", callback_data=PROFILE_CALL)]

    ])

main_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data=MAIN_MENU_CALLBACK)]
    ])

def get_payment_kb(
    amount: float,
    url: str,
    payment_id: str,
    count: int,
    payment_type: str
) -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()

    kb.button(
        text=f"💰 Оплатить {amount}",
        url=url
    )

    kb.button(
        text="🔄 Проверить оплату",
        callback_data=f"check_payment:{payment_type}:{payment_id}:{count}"
    )

    kb.adjust(1)

    return kb.as_markup()

def build_payment_choice_kb(count: int, amount: float, order_id: str):
    kb = InlineKeyboardBuilder()

    kb.button(
        text=f"🟡 CryptoBot",
        callback_data=f"create_payment:crypto:{order_id}:{count}",
    )
    kb.button(
        text=f"🏦 СБП",
        callback_data=f"create_payment:sbp:{order_id}:{count}",
    )
    kb.button(
        text="⬅️ Назад",
        callback_data=TOP_UP_BALANCE_CALL,
    )

    kb.adjust(1)
    return kb.as_markup()


def build_payment_kb(amount: float, url: str, payment_id: str, count: int, payment_type: str):
    kb = InlineKeyboardBuilder()
    kb.button(text=f"💰 Оплатить {amount}", url=url)
    kb.button(
        text="🔄 Проверить оплату",
        callback_data=f"check_payment:{payment_type}:{payment_id}:{count}",
    )
    kb.adjust(1)
    return kb.as_markup()
