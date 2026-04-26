from aiogram.types import InputMediaPhoto, InputMediaVideo


async def send_media(
    bot, 
    chat_id: int, 
    media_type: str, # 'photo' или 'video'
    file_id: str, 
    caption: str = None
):
    if media_type == "photo":
        method = bot.send_photo
        media = InputMediaPhoto(media=file_id, caption=caption)
    elif media_type == "video":
        method = bot.send_video
        media = InputMediaVideo(media=file_id, caption=caption)
    else:
        raise ValueError(f"Unsupported media type: {media_type}")

    return await method(chat_id=chat_id, media=media)