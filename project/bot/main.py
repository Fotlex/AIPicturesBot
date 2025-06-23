import django
import asyncio
import sys
import os
import logging

from functools import partial
from aiohttp import web
from pathlib import Path

from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.configuration.settings')
django.setup()


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from project import config
from project.bot.app.middlewares import UserMiddleware, MediaGroupMiddleware
from project.bot.app.handlers.start_handler import start
from project.bot.app.handlers.referral_handler import referral
from project.bot.app.handlers.promo_handler import promo
from project.bot.app.handlers.pay_handler import pay
from project.bot.app.handlers.styles_handler import style
from project.bot.app.handlers.generation_handlers import generate
from project.bot.app.handlers.avatar_handler import avatar_router
from project.bot.app.handlers.exampl_handler import exampl
from project.bot.app.yookassa import kassa_webhook
from project.bot.app.webhooks import handle_payment_reminder_webhook


async def start_webhook(bot: Bot):
    app = web.Application()
    app.router.add_post('/yookassa/webhook/', partial(kassa_webhook, bot=bot))
    app.router.add_post('/payment-reminder/', handle_payment_reminder_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080) 
    await site.start()
    print("Webhook server started")    
    

async def main():
    print(config.YOOKASSA_SECRET_KEY)
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),   
    )
    
    
    dp = Dispatcher()
    
    main_menu_commands = [
        BotCommand(command='/start', description='🚀 Запустить/перезапустить бота'),
        BotCommand(command='/first_menu', description='Меню для новика'),
        BotCommand(command='/main_menu', description='Основное меню'),
    ]
    await bot.set_my_commands(main_menu_commands)
    
    dp.include_routers(
        start,
        referral,
        promo,
        pay,
        style,
        generate,
        avatar_router,
        exampl,
    )
    
    await start_webhook(bot=bot)
    
    dp.message.middleware(MediaGroupMiddleware())
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except KeyboardInterrupt:
        pass