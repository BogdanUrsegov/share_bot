import os
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from bot.database.utils import add_user_media, decrease_balance
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
    await callback.answer()

    file_id = await get_random_file_id(callback.from_user.id, media_type)
    
    if not file_id:
        await callback.message.answer(
            "❌ <b>Нет доступных файлов в этой категории</b>\n\n"
            "<i>Попробуйте позже...</i>"
            )
        return

    if media_type == "photo":
        res = await decrease_balance(telegram_id, 1)
        if res:
            try:
                await callback.message.answer_photo(file_id, reply_markup=short_categories_menu)
            except:
                res = False
        else:
            await callback.message.answer(
                "⚙️ <b>Недостаточно средств</b>\n\n"
                "<i>Увеличить баланс можно в <b>профиле</b></i> ⬇️",
                reply_markup=profile_n_main_menu
                )
    else:
        res = await decrease_balance(telegram_id, 2)
        if res:
            try:
                await callback.message.answer_video(file_id, reply_markup=short_categories_menu)
            except:
                res = False
        else:
            await callback.message.answer(
                "⚙️ <b>Недостаточно средств</b>\n\n"
                "<i>Увеличить баланс можно в <b>профиле</b></i> ⬇️",
                reply_markup=profile_n_main_menu
                )
    if res:
        await add_user_media(callback.from_user.id, media_type, file_id)
        await bot.send_message(ADMIN_ID, f"🌅 {telegram_id} получил {media_type}: {file_id}")
        logger.info(f"User {callback.from_user.id} got {media_type}: {file_id}")