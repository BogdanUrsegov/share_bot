import logging
import asyncio
import traceback
from datetime import datetime


class TelegramLogHandler(logging.Handler):
    def __init__(self, bot, channel_id):
        super().__init__()

        self.bot = bot
        self.channel_id = channel_id

    def emit(self, record):
        if record.levelno < logging.WARNING:
            return

        try:
            message = self.format(record)

            if record.exc_info:
                message += "\n\n" + "".join(
                    traceback.format_exception(*record.exc_info)
                )

            text = (
                f"🚨 <b>{record.levelname}</b>\n\n"
                f"📂 <b>Logger:</b> {record.name}\n"
                f"📅 <b>Time:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n"
                f"<code>...\n{message[-3500:]}</code>"
            )

            loop = asyncio.get_running_loop()

            loop.create_task(
                self.bot.send_message(
                    self.channel_id,
                    text,
                    parse_mode="HTML"
                )
            )

        except Exception:
            pass