from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.database.utils import user_checker, update_user_agreement
from bot.modules.const_callb import MAIN_MENU_CALLBACK
from ..keyboards.inline_keyboards import categories_menu
from ..keyboards.inline_keyboards import AGREE_TERMS_CALLBACK


router = Router()

@router.callback_query(F.data == AGREE_TERMS_CALLBACK)
async def agree_terms_cb(callback: CallbackQuery):
    telegram_id = callback.from_user.id

    # Проверяем, существует ли пользователь
    is_user = await user_checker(telegram_id)

    if is_user:
        # Обновляем статус согласия в БД
        await update_user_agreement(telegram_id)
        await callback.answer("✅ Вы согласились с условиями!")
        await callback.message.edit_text(text="✅ Вы согласились с <a href=\"https://telegra.ph/Politika-konfidencialnosti-04-01-26\">политикой кофиденциальности</a> и <a href=\"https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19\">пользовательским соглашением</a>", reply_markup=None)  # Удаляем клавиатуру
        mess = await callback.message.answer(
                "<b>Добро пожаловать!</b>\n\n"
                "<i>Выбери действие</i> 👇",
            reply_markup=categories_menu)
        chat_id = mess.chat.id
        mess_id = mess.message_id
        # scheduler.add_job(
        #     func=delete_telegram_msg,
        #     trigger='date',
        #     run_date=datetime.now() + timedelta(minutes=30),
        #     id=f'dltmsg_{chat_id}_{mess_id}',
        #     kwargs={'chat_id': chat_id, 'message_id': mess_id}
        # )
    else:
        await callback.answer("❌ User not found. Please start the bot with /start.", show_alert=True)

@router.callback_query(F.data == MAIN_MENU_CALLBACK)
async def handle_main_menu(callback: CallbackQuery):
    await callback.answer("🏠 Главное меню")
    try:
        await callback.message.edit_text(
                        "<b>Добро пожаловать!</b>\n\n"
                        "<i>Выбери действие</i> 👇",
                        reply_markup=categories_menu
                    )
    except Exception as e:
        # await callback.message.edit_reply_markup(None)
        await callback.message.answer(
                        "<b>Добро пожаловать!</b>\n\n"
                        "<i>Выбери действие</i> 👇",
                        reply_markup=categories_menu
                    )