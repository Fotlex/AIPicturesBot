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
from project.bot.app.yookassa import payment_tarif_generate
from project.bot.app.states import Email

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
                    [InlineKeyboardButton(text='💸', url=pay_url)]
                ]
            )
        )
    except Exception as e:
        print(f'Ошибка: {e}')
        
        
@pay.callback_query(F.data == 'instruction_avatar')
async def instruction_avatar(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.edit_text(
        text=f"📸 Отправьте мне 10 фотографий для создания аватара.\n"\
            f"Фотографии должны быть разными и хорошо освещенными!",
        reply_markup=None
    )
    await state.set_state(Email.wait_photos)
    
    