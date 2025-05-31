from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from ..keyboards import *
from ..texts import *
from ..states import Email

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.database.models import Tariffs, User


pay = Router()


@pay.callback_query(F.data == 'start_buy')
async def start_buy(callback: CallbackQuery):
    await callback.message.edit_text(
        text=PAY_DOCS_TEXT,
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


@pay.message(F.text == BUY_BTN_TEXT)
async def start_buy(message: Message):
    await message.answer(
        text=PAY_DOCS_TEXT,
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
    await callback.message.edit_text(
        text=CHOISE_TARIFF_BTN,
        reply_markup=await tariffs_inline_keyboards()
    )
    
    await callback.answer('')


@pay.callback_query(F.data.startwiths('payment_'))
async def email_start(callback: CallbackQuery, state: FSMContext):
    tariff_id = int(callback.data.split('_')[1])
    await state.update_data(tariff = tariff_id)
    await state.set_state(Email.wait_email)
    
    await callback.message.edit_text(
        text='Введите свою почту'
    )
    
    await callback.answer('')
    
    
@pay.message(Email.wait_email)
async def get_email(message: Message, state: FSMContext):
    email = message.text.strip()

    if "@" not in email or "." not in email:
        await message.answer("❌ Некорректный email. Пожалуйста, введите корректный email.")
        return

    await state.update_data(email=email)
    await state.set_state(Email.non)
    
    