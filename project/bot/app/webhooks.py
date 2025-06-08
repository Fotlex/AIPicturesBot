from pathlib import Path
import sys
from aiohttp import web
from aiogram import Bot

import logging


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from project import config
from project.bot.app.keyboards import tariffs_inline_keyboards

bot = Bot(token=config.BOT_TOKEN)

async def handle_payment_reminder_webhook(request):
    try:
        data = await request.json()
        user_id = data.get("user_id")

        if not user_id:
            return web.json_response({"error": "Missing user_id"}, status=400)

        message_text = (
            "⚠ Видим, что вы не оплатили пакет генерации.\n\n"
            "💡 Предлагаем вам попробовать один из наших пакетов:"
        )

        await bot.send_message(
            chat_id=user_id,
            text=message_text,
            reply_markup=await tariffs_inline_keyboards()
        )

        return web.json_response({"message": "Payment reminder sent"}, status=200)

    except Exception as e:
        logging.error(f"Ошибка обработки вебхука напоминания об оплате: {e}")
        return web.json_response({"error": str(e)}, status=500)