import os
from aiogram import Bot, Router, types
from aiogram.filters import Command
from bot.database.utils import increase_balance, user_checker, add_user, check_user_agreement, delete_user_by_telegram_id
from aiogram.fsm.context import FSMContext

from bot.modules.start.states import AgreeTerms
from ..keyboards.inline_keyboards import agree_menu, categories_menu


ADMIN_ID = os.getenv("ADMIN_ID")
param_start = os.getenv("START_PARAM")
router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, bot: Bot, state: FSMContext):
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
            await state.set_state(AgreeTerms.agree)
            await add_user(telegram_id)
            await bot.send_message(ADMIN_ID, f"👤 Новый пользователь {telegram_id}")
            
            # Начисление бонуса рефереру (если он есть)
            if ref_id:
                await state.update_data(ref_id=ref_id)
            await message.answer(
                "👇 <i>Нажмите кнопку ниже, чтобы принять <a href=\"https://telegra.ph/Politika-konfidencialnosti-04-01-26\">политику кофиденциальности</a> и <a href=\"https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19\">пользовательское соглашение</a></i>",
                reply_markup=agree_menu,
                disable_web_page_preview=True,
                parse_mode="HTML"
            )
    else:
        if await check_user_agreement(telegram_id):
            
            await message.answer(
                "<b>Добро пожаловать!</b>\n\n"
                "<i>Выбери действие</i> 👇",
                reply_markup=categories_menu)
            await state.clear()
        else:
            await message.answer(
                "👇 <i>Нажмите кнопку ниже, чтобы принять <a href=\"https://telegra.ph/Politika-konfidencialnosti-04-01-26\">политику кофиденциальности</a> и <a href=\"https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19\">пользовательское соглашение</a></i>",
                reply_markup=agree_menu,
                disable_web_page_preview=True,
                parse_mode="HTML"
            )

@router.message(Command("delete_me"))
async def cmd_delete_me(message: types.Message, bot: Bot, state: FSMContext):
    telegram_id = message.from_user.id

    res = await delete_user_by_telegram_id(telegram_id)
    if res[0]:
        await message.answer("✅ Ваш аккаунт и все связанные данные были удалены.")
    else:
        await message.answer("❌ Произошла ошибка при удалении вашего аккаунта. Пожалуйста, попробуйте позже.")

@router.message(Command("policy"))
async def cmd_policy(message: types.Message, bot: Bot, state: FSMContext):
    await message.answer("<a href=\"https://telegra.ph/Politika-konfidencialnosti-04-01-26\">Политика кофиденциальности</a> и <a href=\"https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19\">пользовательское соглашение</a>")

@router.message(Command("support"))
async def cmd_support(message: types.Message, bot: Bot, state: FSMContext):
    await message.answer("Если у вас возникли вопросы или проблемы, пожалуйста, свяжитесь с нашей поддержкой: @HE_CEBEPHO")