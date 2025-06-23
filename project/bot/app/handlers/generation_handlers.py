from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from ..keyboards import *
from ..texts import *
from ..servise import generate_photo, decode_base64_to_image, convert_pil_to_bytes
from ..callbacks import *

generate = Router()

from project import config
from project.database.models import Avatar


@generate.message(F.text == 'Генерации')
async def start_gener(message: Message, user: User):
    await message.answer(
        text=f'Количество ваших генераций: {user.generation_count}',
        reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='Купить', callback_data='start_choise_tariff')]
                ]
            )
    )
    
    
@generate.message(F.text == 'Настройки')
async def settings(message: Message):
    await message.answer(
        text='Выберите настройки',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Формат фото', callback_data='photo_format')]
        ])
    )
    
    
@generate.callback_query(F.data == 'photo_format')
async def choise_format(callback: CallbackQuery, user: User):
    await callback.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='1:1', callback_data='form-square_hd')],
            [InlineKeyboardButton(text='3:4', callback_data='form-portrait_4_3')],
            [InlineKeyboardButton(text='4:3', callback_data='form-landscape_4_3')],
            [InlineKeyboardButton(text='9:16', callback_data='form-portrait_16_9')],
            [InlineKeyboardButton(text='16:9', callback_data='form-landscape_16_9')],
        ])
    )
    
    await callback.answer('')
    
    
@generate.callback_query(F.data.startswith('form-'))
async def db_format_change(callback: CallbackQuery, user: User):
    format = callback.data.split('-')[1]
    user.photo_format = format
    await user.asave()
    await callback.answer(text=f'Принято, следующие фото будут в формате {format}', show_alert=True)
    await callback.message.delete()
    
    
@generate.message(F.text == 'Поддержка')
async def sup(message: Message):
    await message.answer(
        text='Жми на кнопку, чтобы связаться с поддержкой',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Поддержка', url=config.SUPPORT_URL)],
        ])
    )