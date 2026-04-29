import logging
import os
from aiogram import Router, types, Bot
from ..states import ContentEarn
from ..keyboards.inline_keyboards import back_menu, award_menu

from aiogram.filters import StateFilter


ADMIN_ID = os.getenv("ADMIN_ID")

logger = logging.getLogger(__name__)

router = Router()

@router.message(StateFilter(ContentEarn.wait))
async def handle_content_earn_wait(message: types.Message, bot: Bot):
    telegram_id = message.from_user.id
    username = message.from_user.username
    username = f"@{username}" if username else None

    if message.photo:
        media_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        media_type = "video"
        file_id = message.video.file_id
    else:
        await message.answer("⚙️ <b>Пожалуйста, отправьте фото или видео</b>", reply_markup=back_menu)
        return
    
    send_method = bot.send_video if media_type == "video" else bot.send_photo

    await send_method(ADMIN_ID, file_id, caption=f"{username} ({telegram_id}) отправил {media_type}", reply_markup=await award_menu(telegram_id))

    await message.answer(
        "🔥 <b>На проверке! Дождитесь проверки модерации и получите вознаграждение</b>\n\n"
        "<i>Вы можете отправить ещё или вернуться назад...</i>", reply_markup=back_menu
    )