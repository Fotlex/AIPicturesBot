from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from ..states import Promo
from ..keyboards import *
from ..texts import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.database.models import Promocode, User


exampl = Router()


@exampl.message(F.text == EXAMPL_BTN_GENERATIONS)
async def get_example(message: Message):
    photo = FSInputFile("docs/exampl.jpg")
    await message.answer_photo(
        photo=photo,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Инструкция', callback_data='first_ok')]
        ])
    )