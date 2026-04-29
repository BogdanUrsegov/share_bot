import os
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from bot.modules.const_callb import EARN_CONTENT_CALL, EARN_FRIENDS_CALL
from bot.modules.earn.states import ContentEarn
from ..keyboards.inline_keyboards import back_menu
from aiogram.fsm.context import FSMContext
import logging


ADMIN_ID = os.getenv("ADMIN_ID")

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == EARN_FRIENDS_CALL)
async def handle_earn(callback: CallbackQuery, bot: Bot):
    await callback.answer("💰 Пригласить друга")
    user_id = callback.from_user.id
    bot_username = (await bot.get_me()).username
    text = (
        "🤝 <b>Приглашай друзей — увеличивай баланс!</b>\n\n"
        "💰 За каждого приглашенного: +2 💎 на баланс\n\n"
        f"<b>Делись своей ссылкой:</b>\n<code>https://t.me/{bot_username}?start={user_id}</code> (нажми, чтобы скопировать)"
        )
    try:
        await callback.message.edit_text(
            text,
            reply_markup=back_menu
        )
    except Exception as e:
        logger.error(e)
        await callback.message.answer(
            text,
            reply_markup=back_menu
        )

@router.callback_query(F.data == EARN_CONTENT_CALL)
async def handle_earn(callback: CallbackQuery, state: FSMContext):
    await callback.answer("💰 Предложить контент")
    user_id = callback.from_user.id
    text = (
        "🎞 <b>Предлагай новый контент!</b>\n\n"
        "Вознаграждение определяем индивидуально. Выплата — после проверки (до 6 часов).\n\n"
        "<b>Отправь фото или видео</b> 👇"
    )
    try:
        await callback.message.edit_text(
            text,
            reply_markup=back_menu
        )
    except Exception as e:
        await callback.message.answer(
            text,
            reply_markup=back_menu
        )
    await state.set_state(ContentEarn.wait)