import sys

from pathlib import Path

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           ReplyKeyboardMarkup, KeyboardButton)
from asgiref.sync import sync_to_async

from .texts import *


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.database.models import Tariffs, User, Styles, Categories
from project.bot.app.callbacks import *
from project.bot.app.db_servise import *

def start_menu_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=INSTRUCRION_BTN_TEXT)],
        [KeyboardButton(text=BUY_BTN_TEXT)],
        [KeyboardButton(text=PROMO_BTN_TEXT)],
        [KeyboardButton(text=EXAMPL_BTN_GENERATIONS)],
    ], resize_keyboard=True)
    
    
def btn_descript_step_first():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=DESCRIPTION_FIRST_OK, callback_data='first_ok')]
    ])
    

def btn_descript_step_second():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=DESCRIPTION_SECOND_OK, callback_data='second_ok')]
    ])
    

def btn_descript_cost():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=COST_QUESTION, callback_data='cost_question')]
    ])
    
    
def referral_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=GET_REFERRAL_LINK, callback_data='get_ref_link')],
        [InlineKeyboardButton(text=REFFERAL_BALANCE, callback_data='referral_balance')]
    ])


async def tariffs_inline_keyboards():
    tariffs = await sync_to_async(lambda: list(Tariffs.objects.all()))()
    
    buttons = [
            [InlineKeyboardButton(text=f"📦 {tariff.name} {tariff.count_generations} генераций - {tariff.cost}₽", callback_data=f"payment_{tariff.id}")]
            for tariff in tariffs
        ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

        
def get_pay_tariff_keyboard(user: User):
    if user.current_avatar_id:
        return main_menu_keyboard()
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Инструкция', callback_data='instruction_avatar')]
    ])
    
    
def main_menu_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Стили')],
        [KeyboardButton(text='Аватар')],
        [KeyboardButton(text='Генерации')],
        [KeyboardButton(text='Настройки')],
        [KeyboardButton(text='Поддержка')],
    ])
    
    
PAGE_SIZE = 8  

async def get_main_styles_keyboard(page: int = 1):
    builder = InlineKeyboardBuilder()
    
    items, has_next = await get_paginated_main_menu_items(page, PAGE_SIZE)
    
    for item in items:
        if isinstance(item, Categories):
            builder.button(
                text=f"📁 {item.name}",
                callback_data=CategoryCallback(action='open', category_id=item.id).pack()
            )
        elif isinstance(item, Styles):
            builder.button(
                text=f"🎨 {item.name}",
                callback_data=StyleCallback(action='select', style_id=item.id).pack()
            )
    
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=PaginatorCallback(action='prev', page=page, category_id=None).pack())
        )
    if has_next:
        pagination_buttons.append(
            InlineKeyboardButton(text="Вперед ➡️", callback_data=PaginatorCallback(action='next', page=page, category_id=None).pack())
        )
    
    builder.adjust(2) 
    builder.row(*pagination_buttons)
    
    return builder.as_markup()

async def get_category_styles_keyboard(category_id: int, page: int = 1):
    builder = InlineKeyboardBuilder()
    
    styles, has_next, _ = await get_paginated_styles_in_category(category_id, page, PAGE_SIZE)

    for style in styles:
        builder.button(
            text=f"🎨 {style.name}",
            callback_data=StyleCallback(action='select', style_id=style.id).pack()
        )
        
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=PaginatorCallback(action='prev', page=page, category_id=category_id).pack())
        )
    if has_next:
        pagination_buttons.append(
            InlineKeyboardButton(text="Вперед ➡️", callback_data=PaginatorCallback(action='next', page=page, category_id=category_id).pack())
        )
        
    builder.adjust(2) 
    builder.row(*pagination_buttons)
    builder.row(
        InlineKeyboardButton(text="🔙 К категориям", callback_data=CategoryCallback(action='back_to_main', category_id=0).pack())
    )
    
    return builder.as_markup()

    