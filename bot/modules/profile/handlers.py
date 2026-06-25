import os
import uuid
import logging

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from bot.utils.notify_admin import notify_admin

from sqlalchemy import select, update

from bot.modules.const_callb import (
    DAILY_CALL,
    TOP_UP_BALANCE_CALL,
    PROFILE_CALL,
    EARN_CALL,
)
from bot.services.crypto_bot import CryptoBotAPI
from bot.services.rollypay import RollyPay
from .utils import calculate_price, show_profile
from bot.database.utils import (
    can_claim_daily_bonus,
    increase_balance,
    insert_payment,
    update_daily_time,
)
from bot.database.session import AsyncSessionLocal
from bot.database.models import PaymentRecord
from .states import TopUpBalance
from .keyboards import *

logger = logging.getLogger(__name__)

router = Router()

crypto = CryptoBotAPI(token=os.getenv("CRYPTO_BOT_TOKEN"))

ROLLYPAY_API_KEY = os.getenv("ROLLYPAY_API_KEY")
rollypay = RollyPay(api_key=ROLLYPAY_API_KEY) if ROLLYPAY_API_KEY else None

ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else None


async def _get_payment_record(payment_key: str):
    async with AsyncSessionLocal() as session:
        stmt = select(PaymentRecord).where(PaymentRecord.crypto_invoice_id == str(payment_key))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def _mark_payment_paid_once(payment_key: str) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            stmt = select(PaymentRecord).where(PaymentRecord.crypto_invoice_id == str(payment_key))
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()

            if not record:
                return False

            if record.status == "paid":
                return False

            upd = (
                update(PaymentRecord)
                .where(PaymentRecord.crypto_invoice_id == str(payment_key))
                .values(status="paid")
            )
            await session.execute(upd)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка _mark_payment_paid_once: {e}")
            return False

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
        "<i>Вы можете пополнить счет через:</i>\n\n"
        "🟡 <b>CryptoBot</b> — оплата в USDT\n"
        "🏦 <b>СБП</b> — оплата в рублях\n\n"
        "🚀 <b>Мгновенное зачисление</b>\n"
        "Средства поступают на баланс сразу после подтверждения\n\n"
        "🛡 <b>Безопасно и надежно</b>\n\n"
        "<b>Ниже введите число, на которое хотите пополнить баланс (чем выше сумма - тем меньше курс)</b> 👇"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=back_menu
    )
    await state.set_state(TopUpBalance.choice)


@router.message(StateFilter(TopUpBalance.choice))
async def process_topup_amount(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❌ Введите число (например: 10)")
        return

    user_id = message.from_user.id
    count = int(message.text)

    if count < 1:
        await message.answer("⚠️ Минимальная сумма пополнения: 1")
        return

    if count > 1000000:
        await message.answer("⚠️ Максимальная сумма пополнения: 1000000")
        return

    amount, discount = calculate_price(count)
    order_id = uuid.uuid4().hex[:8].upper()

    await state.update_data(
        count=count,
        amount=float(amount),
        discount=float(discount),
        order_id=order_id,
    )

    discount_percent = int(discount * 100)
    discount_text = f"(-{discount_percent}%) 🔥" if discount > 0 else ""

    text = (
        "🧾 <b>Выбор способа оплаты</b>\n\n"
        f"<b>Ты получишь:</b> {count} 💎\n"
        f"💰 <b>К оплате:</b> {amount} {discount_text}\n\n"
        "Выберите удобный способ оплаты ниже 👇"
    )

    await message.answer(
        text,
        reply_markup=build_payment_choice_kb(count=count, amount=amount, order_id=order_id)
    )


@router.callback_query(F.data.startswith("create_payment:"))
async def create_payment_cb(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    try:
        _, payment_type, order_id, count_str = callback.data.split(":", 3)
        count = int(count_str)
    except Exception:
        await callback.answer("❌ Ошибка данных оплаты", show_alert=True)
        return

    data = await state.get_data()
    amount = data.get("amount")
    discount = data.get("discount")
    saved_order_id = data.get("order_id")

    if amount is None or saved_order_id != order_id:
        await callback.answer("⏳ Сессия оплаты устарела. Начните заново.", show_alert=True)
        await state.clear()
        return

    payment_id = None
    pay_url = None
    currency_label = ""

    try:
        if payment_type == "crypto":
            invoice = await crypto.create_invoice(
                amount=amount,
                asset="USDT",
                description=order_id,
                payload=order_id
            )

            payment_id = str(invoice["invoice_id"])
            pay_url = invoice["bot_invoice_url"]
            currency_label = "USDT"

        elif payment_type == "sbp":
            if rollypay is None:
                await callback.answer(
                    "⚠️ СБП временно недоступно",
                    show_alert=True
                )
                return

            payment = rollypay.create_payment(
                amount=amount,
                order_id=order_id,
                description=f"Пополнение на {count} 💎"
            )

            payment_id = str(
                payment.get("payment_id")
                or payment.get("id")
                or payment.get("invoice_id")
                or order_id
            )
            pay_url = (
                payment.get("pay_url")
                or payment.get("payment_url")
                or payment.get("url")
            )
            currency_label = "RUB"

            if not pay_url:
                await callback.answer("❌ Не удалось получить ссылку на оплату", show_alert=True)
                return

        else:
            await callback.answer("❌ Неизвестный способ оплаты", show_alert=True)
            return

        payment_record = {
            "order_id": order_id,
            "user_id": user_id,
            "amount": amount,
            "crypto_invoice_id": payment_id,
            "status": "pending",
        }
        await insert_payment(payment_record)

        discount_percent = int(discount * 100)
        discount_text = f"(-{discount_percent}%) 🔥" if discount > 0 else ""

        if payment_type == "crypto":
            text = (
                "🧾 <b>Счет на оплату</b>\n\n"
                f"💎 <b>К оплате:</b> {amount} RUB {discount_text}\n\n"
                "1. Нажмите <b>«Оплатить»</b>\n"
                "2. Затем <b>«Проверить оплату»</b>\n\n"
                f"<i>После оплаты ваш баланс будет увеличен на <b>{count}</b></i> 💎\n\n"
                "<i>/start - вернуться в меню</i>"
            )
        else:
            text = (
                "🧾 <b>Счет на оплату</b>\n\n"
                f"💎 <b>К оплате:</b> {amount} {currency_label} {discount_text}\n\n"
                "1. Нажмите <b>«Оплатить»</b>\n"
                "2. Затем <b>«Проверить оплату»</b>\n\n"
                f"<i>После оплаты ваш баланс будет увеличен на <b>{count}</b></i> 💎\n\n"
                "<i>/start - вернуться в меню</i>"
            )

        await callback.message.edit_text(
            text=text,
            reply_markup=build_payment_kb(
                amount=amount,
                url=pay_url,
                payment_id=payment_id,
                count=count,
                payment_type=payment_type,
            )
        )

        await callback.answer("✅ Счет создан")
        await state.clear()

    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        await callback.answer("❌ Ошибка создания счета", show_alert=True)


@router.callback_query(F.data.startswith("check_payment:"))
async def check_payment_cb(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    try:
        _, payment_type, payment_id, count_str = callback.data.split(":", 3)
        count = int(count_str)
    except Exception:
        await callback.answer("❌ Ошибка данных проверки", show_alert=True)
        return

    try:
        payment_record = await _get_payment_record(payment_id)
        if not payment_record:
            await callback.answer("❌ Платеж не найден", show_alert=True)
            return

        if payment_record.user_id != user_id:
            await callback.answer("❌ Это не ваш платёж", show_alert=True)
            return

        if payment_record.status == "paid":
            await callback.answer("✅ Оплата уже была учтена", show_alert=True)
            return

        paid = False

        if payment_type == "crypto":
            invoice = await crypto.get_invoice_status(int(payment_id))
            if invoice and invoice.get("status") == "paid":
                paid = True

        elif payment_type == "sbp":
            if rollypay is None:
                await callback.answer("⚠️ СБП временно недоступно", show_alert=True)
                return
            paid = rollypay.is_paid(payment_id)

        else:
            await callback.answer("❌ Неизвестный тип платежа", show_alert=True)
            return

        if paid:
            marked = await _mark_payment_paid_once(payment_id)
            if not marked:
                await callback.answer("✅ Оплата уже была учтена", show_alert=True)
                return

            await callback.answer("✅ Оплата получена")

            await increase_balance(user_id, count)

            await callback.message.edit_text(
                "✅ <b>Оплата получена!</b>\n\n"
                f"Ваш баланс пополнен на <b>{count}</b> 💎\n\n"
                "❤️ <b>Приятного просмотра!</b>"
            )

            await notify_admin(
                bot,
                f"{user_id} приобрел {count}\n\n/stats - посмотреть статистику"
            )

            await callback.message.answer(
                "<b>Добро пожаловать!</b>\n\n"
                "<i>Выбери действие</i> 👇",
                reply_markup=categories_menu
            )
        else:
            await callback.answer("⏳ Платёж ещё не поступил. Попробуйте позже...", show_alert=False)

    except Exception as e:
        logger.error(f"Error checking payment: {e}")
        await callback.answer("❌ Error", show_alert=True)


@router.callback_query(F.data == EARN_CALL)
async def handle_earn(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer("💰 Заработать")

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
        await notify_admin(bot, f"🎁 {user_id} получил ежедневный бонус")
        await increase_balance(user_id, 5)

        text_profile = await show_profile(user_id)
        await callback.message.edit_text(
            text_profile,
            reply_markup=profile_menu
        )
    else:
        await callback.answer("❌ Ежедневный бонус уже получен")