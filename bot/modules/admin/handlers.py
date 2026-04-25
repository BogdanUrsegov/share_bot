import os
from aiogram import Bot, Router, F
from aiogram.types import Message
from .states import AddMedia
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from bot.database.utils.add_media import add_media


router = Router()

import logging

from bot.database.utils import all_info, delete_media_by_file_id


ADMIN_ID = os.getenv("ADMIN_ID")

logger = logging.getLogger(__name__)

router = Router()

@router.message(F.text == "/stats")
async def cmd_pay(message: Message):
    user_id = message.from_user.id
    if str(user_id) != ADMIN_ID:
        await message.answer("❌ You are not authorized to use this command.")
        return
    else:
        stats = await all_info()
        text = (
            "📊 <b>Статистика</b>\n\n"
            f"👥 Пользователей: <code>{stats['total_users']}</code>\n"
            f"📦 Ордеров: <code>{stats['total_orders']}</code>\n"
            f"✅ Оплачено: <code>{stats['paid_orders_count']}</code>\n"
            f"💰 Сумма: <code>{stats['paid_orders_sum']:,.2f} USDT</code>\n\n"
            f"🖼 Фото в базе: <code>{stats['total_photos']}</code>\n"
            f"🎥 Видео в базе: <code>{stats['total_videos']}</code>"
        )
        await message.answer(text)

@router.message(F.text == "/add_media")
async def cmd_add_media(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if str(user_id) != ADMIN_ID:
        await message.answer("❌ You are not authorized to use this command.")
        return
    else:
        await message.answer("Отправьте медиафайлы для добавления в базу данных\n\n/stop_add_media - для завершения")
        await state.set_state(AddMedia.wait)

@router.message(F.text == "/stop_add_media")
async def cmd_stop_add_media(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if str(user_id) != ADMIN_ID:
        await message.answer("❌ You are not authorized to use this command.")
        return
    else:
        await message.answer("Завершение добавления медиафайлов.")
        await state.clear()

@router.message(StateFilter(AddMedia.wait))
async def handle_media_state(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if str(user_id) != ADMIN_ID:
        await message.answer("❌ You are not authorized to use this command.")
        return
    else:
        if message.photo:
            media_type = "photo"
            file_id = message.photo[-1].file_id
        elif message.video:
            media_type = "video"
            file_id = message.video.file_id
        else:
            await message.answer("Пожалуйста, отправьте фото или видео.")
            return
        
        result, err = await add_media(media_type, file_id)
        if result:
            await message.answer(f"<b>Добавлено в {media_type}</b>\n\n<code>{file_id}</code>", reply_to_message_id=message.message_id)
        else:
            await message.answer(f"Ошибка при добавлении медиафайла: {err}")

@router.message(Command("del_file"))
async def cmd_del_file(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    if str(user_id) != ADMIN_ID:
        await message.answer("❌ You are not authorized to use this command.")
        return
    else:
        file_id = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not file_id:
            await message.answer("Пожалуйста, укажите file_id\nПример: /del_file <file_id>", parse_mode=None)
            return
        else:
            try:
                await delete_media_by_file_id(file_id)
                await message.answer("Файл удален")
            except Exception as e:
                await message.answer(f"Произошла ошибка при удалении: {e}")

@router.message(Command("get_file"))
async def cmd_get_file(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    if str(user_id) != ADMIN_ID:
        await message.answer("❌ You are not authorized to use this command.")
        return
    else:
        file_id = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        if not file_id:
            await message.answer("Пожалуйста, укажите file_id\nПример: /get_file <file_id>", parse_mode=None)
            return
        else:
            await message.answer_photo(file_id)
