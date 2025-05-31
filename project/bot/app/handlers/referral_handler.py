from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import Router, F

from ..keyboards import *
from ..texts import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.database.models import User


referral = Router()


@referral.message(F.text == REFFERAL_BTN_TEXT)
async def add_friend_message(message: Message):
    await message.answer(
        text=ADD_FRIEND_TEXT,
        reply_markup=referral_keyboard()
    )
    
    
@referral.callback_query(F.data == 'get_ref_link')
async def get_link(callback: CallbackQuery, user: User):
    await callback.message.edit_text(
        text=f'Ваша оеферальная ссылка:\n{user.refferal_link}',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=REFFERAL_BALANCE, callback_data='referral_balance')]
            ]
        )
    )
    
    
@referral.callback_query(F.data == 'referral_balance')
async def ref_balance_info(callback: CallbackQuery):
    await callback.message.edit_text(
        text=REF_BALLANCE_INFO_TEXT,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text=BUY_BY_BALANCE_TEXT, callback_data='start_pay')
            ]]
        )
    )