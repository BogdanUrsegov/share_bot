import os
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from bot.database.utils import add_user_media, decrease_balance, increase_balance
from bot.database.utils import get_random_file_id
from bot.modules.const_callb import LOOK_CALL
# from bot.modules.utils import log_to_channel
from ..keyboards.inline_keyboards import categories_menu, PHOTO_CALL, VIDEO_CALL, short_categories_menu, profile_n_main_menu
import logging


logger = logging.getLogger(__name__)
ADMIN_ID = os.getenv("ADMIN_ID")
router = Router()

@router.callback_query(F.data == LOOK_CALL)
async def handle_look(callback: CallbackQuery):
    await callback.answer("👀 Смотреть")
    await callback.message.edit_text(
        "<b>Выберите категорию</b>", 
        reply_markup=categories_menu)

@router.callback_query(F.data.in_({PHOTO_CALL, VIDEO_CALL}))
async def handle_media(callback: CallbackQuery, bot: Bot):
    telegram_id = callback.from_user.id
    media_type = "photo" if callback.data == PHOTO_CALL else "video"
    price = 1 if media_type == "photo" else 2
    
    await callback.answer()

    # 1. Получаем файл
    file_id = await get_random_file_id(telegram_id, media_type)
    if not file_id:
        await callback.message.answer(
            "❌ <b>Нет доступных файлов в этой категории</b>\n\n<i>Попробуйте позже...</i>",
            parse_mode="HTML"
        )
        return

    # 2. Проверяем баланс
    if not await decrease_balance(telegram_id, price):
        await callback.message.answer(
            "⚙️ <b>Недостаточно средств</b>\n\n<i>Увеличить баланс можно в <b>профиле</b></i> ⬇️",
            reply_markup=profile_n_main_menu,
            parse_mode="HTML"
        )
        return

    # 3. Отправляем медиа
    try:
        send_method = callback.message.answer_photo if media_type == "photo" else callback.message.answer_video
        await send_method(file_id, reply_markup=short_categories_menu)
        
        # 4. Успех: логируем и сохраняем историю
        await add_user_media(telegram_id, media_type, file_id)
        await bot.send_message(ADMIN_ID, f"🌅 {telegram_id} получил {media_type}: <code>{file_id}</code>")
        logger.info(f"User {telegram_id} got {media_type}: {file_id}")
        
    except Exception as e:
        # 5. Ошибка отправки: возвращаем средства (опционально) и сообщаем юзеру
        await increase_balance(telegram_id, price) # Возврат средств при ошибке
        await callback.message.answer("⚠️ <b>Ошибка загрузки файла</b>\nПопробуйте еще раз.", parse_mode="HTML")
        logger.error(f"Failed to send {media_type} to {telegram_id}: {e}")
        await bot.send_message(ADMIN_ID, f"Ошибка загрузки файла {media_type} для {telegram_id}: {e}")