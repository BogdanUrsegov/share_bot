import os
import uuid
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, Message
from bot.modules.const_callb import (
    DAILY_CALL, TOP_UP_BALANCE_CALL, 
    PROFILE_CALL, EARN_CALL
)
from bot.services.crypto_bot import CryptoBotAPI
from .utils import calculate_price, show_profile
from bot.database.utils import can_claim_daily_bonus, increase_balance, insert_payment, update_daily_time, update_payment_status
from .states import TopUpBalance
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from .keyboards import profile_menu, back_menu, get_payment_kb, earn_menu, categories_menu
import logging

crypto = CryptoBotAPI(token=os.getenv("CRYPTO_BOT_TOKEN"))
ADMIN_ID = os.getenv("ADMIN_ID")

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data == PROFILE_CALL)
async def handle_profile(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await callback.answer("👤 Профиль")
    
    text_profile = await show_profile(user_id)
    await callback.message.edit_text(
        text_profile,
        reply_markup=profile_menu
    )
    await state.clear()

@router.callback_query(F.data == TOP_UP_BALANCE_CALL)
async def handle_top_up(callback: CallbackQuery, state: FSMContext):
    await callback.answer("💳 Пополнить")
    text = (
        "<i>Вы можете пополнить счет через <b>CryptoBot</b></i>\n\n"
        "🚀 <b>Мгновенное зачисление</b>\n"
        "Средства поступают на баланс сразу после подтверждения сети.\n\n"
        "💎 <b>Оплата в USDT TRC-20</b>\n\n"
        "🛡 <b>Безопасно и надежно</b>\n"
        "Все транзакции защищены и анонимны.\n\n"
        "<b>Ниже введите число на которое хотите пополнить баланс (чем выше сумма, тем ниже курс)</b> 👇"
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=back_menu
    )
    await state.set_state(TopUpBalance.choice)

@router.message(StateFilter(TopUpBalance.choice))
async def process_topup_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not message.text.isdigit():
        await message.answer("❌ Введите число (например: 10)")
        return

    count = int(message.text)
    
    if count < 1: # Минимальная сумма
        await message.answer("⚠️ Минимальная сумма пополнения: 1")
        return

    if count > 1000000: # Минимальная сумма
        await message.answer("⚠️ Максимальная сумма пополнения: 1000000")
        return
    amount, discount = calculate_price(count)
    order_id = f"{uuid.uuid4().hex[:8].upper()}"
    invoice = await crypto.create_invoice(
            amount=amount,
            asset="USDT",
            description=order_id,
            payload=order_id
        )

    payment_record = {
        "order_id": order_id,
        "user_id": user_id,
        "amount": amount,
        "crypto_invoice_id": invoice["invoice_id"],
        "status": "pending"
    }
    await insert_payment(payment_record)
    discount_percent = int(discount * 100)
    # Если скидки нет, строка будет пустой или можно скрыть её условием
    discount_text = f"(-{discount_percent}%) 🔥" if discount > 0 else ""

    text = (
        "🧾 <b>Счет на оплату</b>\n\n"
        f"💎 <b>К оплате:</b> {amount} USDT {discount_text}\n\n"
        "1. Нажмите <b>«Оплатить»</b>\n"
        "2. Затем <b>«Проверить»</b>\n\n"
        f"<i>После оплаты ваш баланс будет увеличен на <b>{count}</b></i> 💎\n\n"
        "<i>/start - вернуться в меню</i>"
    )
    await message.answer(text, reply_markup=get_payment_kb(amount, invoice["bot_invoice_url"], invoice["invoice_id"], count))
    
    await state.clear()


@router.callback_query(F.data.startswith("check_invoice:"))
async def check_invoice_cb(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    invoice_id = int(callback.data.split(":")[1])
    count = int(callback.data.split(":")[2])

    try:
        status = await crypto.get_invoice_status(invoice_id)
        
        if not status:
            await callback.answer("❌ Invoice not found or expired", show_alert=True)
            return

        if status["status"] == "paid":
            await update_payment_status(invoice_id, "paid")
            await callback.answer("✅ Оплата получена")
            await increase_balance(user_id, count)
            await callback.message.edit_text(
                "✅ <b>Оплата получена!</b>\n\n"
                f"Ваш баланс пополнен на {count}\n\n"
                "❤️ <b>Приятного просмотра!</b>"
            )
            await bot.send_message(ADMIN_ID, f"{user_id} приобрел {count}\n\n/stats - посмотреть статистику")
            await callback.message.answer(
                        "<b>Добро пожаловать!</b>\n\n"
                        "<i>Выбери действие</i> 👇",
                reply_markup=categories_menu
            )
        else:
            # Сообщение с кнопкой остаётся, юзер видит статус во всплывашке
            await callback.answer(f"⏳ Status: {status['status']}. Try again later ⏳", show_alert=False)

    except Exception as e:
        logger.error(f"Error checking invoice: {e}")
        await callback.answer(f"❌ Error")

@router.callback_query(F.data == EARN_CALL)
async def handle_earn(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer("💰 Заработать")
    user_id = callback.from_user.id
    bot_username = (await bot.get_me()).username
    await callback.message.edit_text(
        "<b>Заработай 💎</b>\n\n"
        "Выбери способ:\n\n"
        "🤝 <b>Приглашай друзей</b>\n"
        "<i>Увеличивай баланс за рефералов</i>\n\n"
        "📽 <b>Предлагай контент</b>\n"
        "<i>Получай вознаграждение за новые материалы</i>",
        reply_markup=earn_menu
    )
    await state.clear()

@router.callback_query(F.data == DAILY_CALL)
async def handle_daily(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    if await can_claim_daily_bonus(user_id):
        await update_daily_time(user_id)
        await callback.answer("🎉 Вы получили ежедневный бонус: +5")
        await bot.send_message(ADMIN_ID, f"🎁 {user_id} получил ежедневный бонус")
        await increase_balance(user_id, 5)
        text_profile = await show_profile(user_id)
        await callback.message.edit_text(
            text_profile,
            reply_markup=profile_menu
        )
    else:
        await callback.answer("❌ Ежедневный бонус уже получен")