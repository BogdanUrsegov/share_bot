from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def get_payment_kb(amount: float, url: str, invoice_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f"💰 Pay {amount} USDT", url=url)
    kb.button(text="🔄 Check Payment", callback_data=f"check_invoice:{invoice_id}")
    return kb.as_markup()