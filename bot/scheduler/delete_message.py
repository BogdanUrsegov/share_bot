async def delete_telegram_msg(chat_id: int, message_id: int):
    from bot.create_bot import bot

    await bot.delete_message(chat_id=chat_id, message_id=message_id)