import sys

from pathlib import Path

from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           ReplyKeyboardMarkup, KeyboardButton)
from asgiref.sync import sync_to_async

from .texts import *


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.database.models import Tariffs


def start_menu_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=INSTRUCRION_BTN_TEXT)],
        [KeyboardButton(text=BUY_BTN_TEXT)],
        [KeyboardButton(text=REFFERAL_BTN_TEXT)],
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
    
    

