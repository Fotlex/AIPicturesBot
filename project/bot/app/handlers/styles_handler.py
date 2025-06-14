from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from ..keyboards import *
from ..texts import *
from ..servise import generate_photo, decode_base64_to_image, convert_pil_to_bytes
from ..callbacks import *

style = Router()

from project import config
from project.database.models import Avatar


@style.message(F.text == "Стили") 
async def show_styles_menu(message: Message):
    await message.answer(
        "Выберите категорию или стиль:",
        reply_markup=await get_main_styles_keyboard()
    )

@style.callback_query(PaginatorCallback.filter())
async def handle_pagination(call: CallbackQuery, callback_data: PaginatorCallback):
    page = callback_data.page
    action = callback_data.action
    category_id = callback_data.category_id
    
    current_page = page + 1 if action == 'next' else page - 1
    
    if category_id is not None:
        _, _, category_name = await get_paginated_styles_in_category(category_id, current_page, 1)
        text = f"Категория: {category_name}"
        keyboard = await get_category_styles_keyboard(category_id, current_page)
    else:
        text = "Выберите категорию или стиль:"
        keyboard = await get_main_styles_keyboard(current_page)

    await call.message.edit_text(text, reply_markup=keyboard)
    await call.answer()

@style.callback_query(CategoryCallback.filter(F.action == 'open'))
async def open_category(call: CallbackQuery, callback_data: CategoryCallback):
    _, _, category_name = await get_paginated_styles_in_category(callback_data.category_id, 1, 1)
    await call.message.edit_text(
        f"Категория: {category_name}",
        reply_markup=await get_category_styles_keyboard(callback_data.category_id, page=1)
    )
    await call.answer()
    
@style.callback_query(CategoryCallback.filter(F.action == 'back_to_main'))
async def back_to_main_menu(call: CallbackQuery):
    await call.message.edit_text(
        "Выберите категорию или стиль:",
        reply_markup=await get_main_styles_keyboard(page=1)
    )
    await call.answer()


@style.callback_query(StyleCallback.filter(F.action == 'select'))
async def select_style(call: CallbackQuery, callback_data: StyleCallback, user: User, bot: Bot):
    style_id = callback_data.style_id
    style = await Styles.objects.aget(id=style_id)
    avatar = await Avatar.objects.aget(id=user.current_avatar_id)
    if user.generation_count <= 0:
        await call.message.answer(
            text='К сожалению, у вас закончились генерации',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='Купить', callback_data='start_choise_tariff')]
                ]
            )
        )
        return
    await call.message.answer(
        text='Начинаю генерацию твоих фото...'
    )
    
    decode_photo_first = await generate_photo(
        config.LORA_KEY,
        avatar.api_name,
        f'{avatar.trigger_phrase} {style.capture_for_lora}',
        #size=user.photo_format
    )
    
    try:
        pil_image = decode_base64_to_image(decode_photo_first)
        image_bytes = convert_pil_to_bytes(pil_image)
        input_file = BufferedInputFile(file=image_bytes, filename="avatar.png")
        
        await bot.send_photo(
            chat_id=user.id,
            photo=input_file,
            caption="Первое фото, генерирую второе..."
        )
        user.generation_count -= 1
        await user.asave()
        if user.generation_count <= 0:
            await call.message.answer(
                text='К сожалению, у вас закончились генерации',
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text='Купить', callback_data='start_choise_tariff')]
                    ]
                )
            )
            return
    except Exception as e:
        await call.message.answer(text=f"Не удалось обработать изображение, попробуйте позже")
        print(e)
        
    decode_photo_second = await generate_photo(
        config.LORA_KEY,
        avatar.api_name,
        f'{avatar.trigger_phrase} {style.capture_for_lora}',
        #size=user.photo_format
    )
    
    try:
        pil_image = decode_base64_to_image(decode_photo_second)
        image_bytes = convert_pil_to_bytes(pil_image)
        input_file = BufferedInputFile(file=image_bytes, filename="avatar.png")
        
        await bot.send_photo(
            chat_id=user.id,
            photo=input_file,
            caption="Готово",
            reply_markup=main_menu_keyboard()
        )
        user.generation_count -= 1
        await user.asave()
        if user.generation_count <= 0:
            await call.message.answer(
                text='К сожалению, у вас закончились генерации',
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text='Купить', callback_data='start_choise_tariff')]
                    ]
                )
            )
            return
    except Exception as e:
        await call.message.answer(text=f"Не удалось обработать изображение, попробуйте позже")
        print(e)
        
    

    
    