import json
import logging
from pathlib import Path
import sys
import uuid

from aiohttp import web
from aiogram import Bot
from asgiref.sync import sync_to_async

from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotificationFactory


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.bot.app.keyboards import get_pay_tariff_keyboard
from project.database.models import PaymentRecord, User, Tariffs
from project import config

Configuration.account_id = config.YOOKASSA_SHOP_ID
Configuration.secret_key = config.YOOKASSA_SECRET_KEY


async def create_payment(amount, user, description, metadata):
    payment_id = str(uuid.uuid4())

    payment_data = {
        "amount": {"value": str(amount), "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://t.me/{config.BOT_NAME}",
        },
        "capture": True,
        "description": description,
        "metadata": {**metadata, "payment_id": payment_id},
    }

    payment = Payment.create(payment_data)

   
    await PaymentRecord.objects.acreate(
        user=user,
        payment_id=payment_id,
        amount=amount,
        status="pending",
        metadata=metadata,
    )

    
    return payment.confirmation.confirmation_url



async def payment_tarif_generate(user: User, tariff_id: int):
    tariff = await Tariffs.objects.aget(id=tariff_id)
    payment_url = await create_payment(
        amount=tariff.cost,
        user=user,
        description=f'Покупка пакета {tariff.name}',
        metadata={
            'tariff_id': tariff_id,
            'type': 'tariff',
            'count_generations': tariff.count_generations,
        },
    )
    return payment_url


async def kassa_webhook(request: web.Request, bot: Bot):
    try:
        body = await request.text()
        event_dict = json.loads(body)

        notification = WebhookNotificationFactory().create(event_dict)
        metadata = notification.object.metadata
        payment_id = metadata.get('payment_id')
        payment_type = metadata.get('type')
        
        status = notification.object.status

        payment = await PaymentRecord.objects.select_related('user').aget(payment_id=payment_id)

        if status == "succeeded" and payment.status != 'succeeded':
            payment.status = 'succeeded'
            await payment.asave()
            
            if payment_type == 'tariff':
                count_generations = metadata.get('count_generations')
                user = payment.user
                try:
                    user.generation_count += int(count_generations)
                except Exception as e:
                    print(e)
                    
                
                await bot.send_message(
                    chat_id=payment.user.id,
                    text=f'✅Поздравляю, оплата прошла успешно!\nТеперь у вас {user.generation_count} генераций',
                    reply_markup=await get_pay_tariff_keyboard(user=user)
                )

                await user.asave()
            
            
        elif status == "canceled":
            payment.status = 'canceled' 
            await payment.asave()

        return web.Response(status=200, text="ok")

    except Exception as e:
        print(f"Webhook error: {e}")
        return web.Response(status=500, text="Server error")