from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import Router, F

from ..keyboards import *
from ..texts import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.database.models import Tariffs


start = Router()


@start.message(CommandStart())
async def start_message(message: Message):
    await message.answer(text=START_TEXT, reply_markup=start_menu_keyboard())
    
    
@start.message(F.text == INSTRUCRION_BTN_TEXT)
async def description_bot(message: Message):
    await message.answer(text=DESCRIPTION_BOT, reply_markup=btn_descript_step_first())
    
    
@start.callback_query(F.data == 'first_ok')
async def adout_photo(callback: CallbackQuery):
    await callback.message.edit_text(
        text=DESCRIPTION_ABOUT_PHOTO,
        reply_markup=btn_descript_step_second()
    )
    
    
@start.callback_query(F.data == 'second_ok')
async def about_styles(callback: CallbackQuery):
    await callback.message.edit_text(
        text=ABOUT_STYLES_AVATAR_TEXT,
        reply_markup=btn_descript_cost()
    )
    
    
@start.callback_query(F.data == 'cost_question')
async def about_styles(callback: CallbackQuery):
    tariffs = await sync_to_async(lambda: list(Tariffs.objects.all()))()
   
    text_about_tarifs = "\n".join(
            [f"📦 **{tariff.name}** - {tariff.cost}₽ ({tariff.count_generations} генераций)" for tariff in tariffs]
        )
    
    await callback.message.edit_text(
            f"💰 **Стоимость пакетов**\n\n{text_about_tarifs}\n\n✅",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=BUY_BTN_TEXT, callback_data="start_buy")]]
            ),
            parse_mode="Markdown"
        )
