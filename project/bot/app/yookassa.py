import json
import logging
from pathlib import Path
import sys
import uuid
import time

from aiohttp import web
from aiogram import Bot
from asgiref.sync import sync_to_async
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotificationFactory



BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))


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