from typing import List
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext

from pathlib import Path
from aiohttp import ClientSession

from ..keyboards import *
from ..texts import *
from ..states import Email
from ..servise import generate_avatar, json

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.database.models import Tariffs, User, Avatar, UserArchive
from project.bot.app.yookassa import payment_tarif_generate
from project.bot.app.states import Email
from project.database.services import process_and_save_photos
from project import config

pay = Router()


@pay.callback_query(F.data == 'start_buy')
async def start_buy(callback: CallbackQuery):
    doc = FSInputFile("docs/Пользовательское_соглашение_и_Политика_конфиденциальности_v2.docx")
    await callback.message.answer_document(
        document=doc,
        caption=PAY_DOCS_TEXT,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=PAY_DOCS_TEXT_BTN, 
                    callback_data='start_choise_tariff',
                    parse_mode="Markdown",
                )]
            ]
        )
    )
    await callback.answer('')
    await callback.message.delete()


@pay.message(F.text == BUY_BTN_TEXT)
async def start_buy(message: Message):
    doc = FSInputFile("docs/Пользовательское_соглашение_и_Политика_конфиденциальности_v2.docx")
    await message.answer_document(
        document=doc,
        caption=PAY_DOCS_TEXT,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=PAY_DOCS_TEXT_BTN, 
                    callback_data='start_choise_tariff',
                    parse_mode="Markdown",
                )]
            ]
        )
    )
    
    
@pay.callback_query(F.data == 'start_choise_tariff')
async def tariffs_list(callback: CallbackQuery):
    await callback.message.answer(
        text=CHOISE_TARIFF_BTN,
        reply_markup=await tariffs_inline_keyboards()
    )
    
    await callback.answer('')
    await callback.message.delete()


@pay.callback_query(F.data.startswith('payment_'))
async def email_start(callback: CallbackQuery, state: FSMContext):
    tariff_id = int(callback.data.split('_')[1])
    await state.update_data(tariff = tariff_id)
    await state.set_state(Email.wait_email)
    
    await callback.message.edit_text(
        text='Введите свою почту'
    )
    
    await callback.answer('')
    
    
@pay.message(Email.wait_email)
async def get_email(message: Message, state: FSMContext, user: User):
    email = message.text.strip()

    if "@" not in email or "." not in email:
        await message.answer("❌ Некорректный email. Пожалуйста, введите корректный email.")
        return

    user.email = email
    await user.asave()
    await state.update_data(email=email)
    await state.set_state(Email.non)
    
    try:
        data = await state.get_data()
        tariff_id = data.get('tariff')
        pay_url = await payment_tarif_generate(
            user=user,
            tariff_id=int(tariff_id),
        )
        await message.answer(
            text=f'💳Переходите по ссылке для оплаты.',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='💸', url=pay_url)],
                ]
            )
        )
    except Exception as e:
        print(f'Ошибка: {e}')
        


@pay.callback_query(F.data == 'instruction_avatar')
async def namee(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='Придумайте и введите имя вашего аватара:',
    )
    await state.set_state(Email.wait_name)
    await callback.answer('')



@pay.message(F.text, Email.wait_name)
async def instruction_avatar(message: Message, state: FSMContext, user: User):
    new_avatar = await Avatar.objects.acreate(
        user=user,
        name=message.text,
    )
    
    await message.answer(
        text=f"📸 Отправьте мне от 10 до 20 фотографий для создания аватара.\n"\
            f"Фотографии должны быть разными и хорошо освещенными!",
        reply_markup=None
    )
    await state.update_data(photos=[])
    await state.update_data(new_avatar_id=new_avatar.id)
    await state.set_state(Email.wait_photos)
    

@pay.message(Email.wait_photos, F.photo)
async def collect_photos(message: Message, state: FSMContext, bot: Bot, user: User, album: List[Message] = None):
    data = await state.get_data()
    photos = data.get("photos", [])
    avatar_id = data.get('new_avatar_id')

    if album:
        for msg in album:
            if msg.photo:
                photos.append(msg.photo[-1].file_id)
    else:
        photos.append(message.photo[-1].file_id)
    
    await state.update_data(photos=photos)

    if 10 <= len(photos) <= 20:
        photos_to_process = photos[:20]

        await message.answer("Спасибо! Все 10 фото получены. Начинаю обработку...")
        
        avatar = await Avatar.objects.aget(id=avatar_id)
        
        file_relative_url = await process_and_save_photos(bot, message.from_user.id, photos)
        
        full_public_url = config.DEVELOP_URL + file_relative_url
        
        result = await generate_avatar(
            config.LORA_KEY,
            full_public_url,
            avatar.api_name,
            avatar.trigger_phrase,
            '/train_model',
        )
        
        if result and result.get("status") == 'Completed':
            user.current_avatar_id = avatar.id
            user.is_pay_error_avatar = False
            await message.answer(
                text='Мы создали твой аватар, можем приступать к генерации фотографий',
                reply_markup=main_menu_keyboard()
            )
            avatar.is_complete = True
            await state.clear()
            await avatar.asave()
            await user.asave()
            
        else:
            await message.answer(
                text=f"Что-то пошло не так, попробуем снова\n📸 Отправьте мне от 10 до 20 фотографий для создания аватара.\n"\
                    f"Фотографии должны быть разными и хорошо освещенными!",
                reply_markup=None
            )
            from pprint import pprint
            pprint(result)
            await state.update_data(photos=[])
            await state.set_state(Email.wait_photos)
            
        try:
            arch = await UserArchive.objects.aget(telegram_user_id=user.id)
            await arch.adelete()
        except Exception as e:
            print(f'При удалении произошла ошибка - {e}')
        
        
@pay.message(F.photo)
async def error_photo(message: Message):
    await message.answer(text='Следуйте инструкции от бота, прежде чем отправлять фото')
       
            