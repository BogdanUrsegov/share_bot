from datetime import datetime, timedelta
import os
from aiogram import Bot, Router, types
from aiogram.filters import Command
from bot.database.utils import increase_balance, user_checker, add_user
from bot.database.utils import check_user_agreement
from bot.scheduler.scheduler import scheduler
from bot.scheduler.delete_message import delete_telegram_msg
from ..keyboards.inline_keyboards import agree_menu, categories_menu


ADMIN_ID = os.getenv("ADMIN_ID")
param_start = os.getenv("START_PARAM")
router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, bot: Bot):
    telegram_id = message.from_user.id

    # Проверяем, существует ли пользователь
    is_user = await user_checker(telegram_id)

    if not is_user:
        parts = message.text.split()
        start_param = parts[1] if len(parts) > 1 else None
        
        is_allowed = False
        ref_id = None

        # 1. Проверка параметров
        if start_param == param_start:
            is_allowed = True
        elif start_param and start_param.isdigit():
            potential_ref_id = int(start_param)
            
            # Защита: нельзя пригласить самого себя
            if potential_ref_id != telegram_id and await user_checker(potential_ref_id):
                ref_id = potential_ref_id
                is_allowed = True

        # 2. Если все ок, регистрируем и начисляем бонус
        if is_allowed:
            await add_user(telegram_id)
            await bot.send_message(ADMIN_ID, f"👤 Новый пользователь {telegram_id}")
            
            # Начисление бонуса рефереру (если он есть)
            if ref_id:
                await increase_balance(ref_id, 2)
                try:
                    await bot.send_message(
                        ref_id, 
                        "🎁 <b>Вы получили бонус за приглашенного пользователя!</b>",
                        reply_markup=categories_menu
                    )
                except Exception:
                    pass # Игнорируем ошибки отправки (например, если бот заблокирован)

            await message.answer(
                "👇 <i>Нажмите кнопку ниже, чтобы принять <a href=\"https://telegra.ph/Policy-04-11-12\">условия</a> и продолжить.</i>",
                reply_markup=agree_menu,
                disable_web_page_preview=True,
                parse_mode="HTML"
            )
    else:
        if await check_user_agreement(telegram_id):
            
            mess = await message.answer(
                "<b>Добро пожаловать!</b>\n\n"
                "<i>Выбери действие</i> 👇",
                reply_markup=categories_menu)
            chat_id = mess.chat.id
            mess_id = mess.message_id
        else:
            await message.answer(
                "👇 <i>Please agree to the <a href=\"https://telegra.ph/Policy-04-11-12\">terms</a> to continue.</i>",
                reply_markup=agree_menu,
                disable_web_page_preview=True
            )