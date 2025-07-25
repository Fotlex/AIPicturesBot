from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F

from ..keyboards import *
from ..texts import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.database.models import Tariffs, User
from project import config

start = Router()


@start.message(CommandStart())
async def start_message(message: Message, user: User):
    args = message.text.split()
    referrer_id = None

    if len(args) > 1 and args[1].startswith("ref"):
        try:
            referrer_id = int(args[1][3:])
        except ValueError:
            referrer_id = None

    telegram_id = message.from_user.id


    if referrer_id and user.referrer_by is None and referrer_id != telegram_id:
        try:
            referrer = await sync_to_async(User.objects.get)(telegram_id=referrer_id)
            user.referrer_by = referrer
            #Даю награду рефефереру
            await sync_to_async(user.save)()
        except User.DoesNotExist:
            pass  

    
    await message.answer(text=START_TEXT, reply_markup=start_menu_keyboard(), parse_mode="Markdown",)
    
    
@start.message(Command('first_menu'))
async def f_menu(message: Message):
    await message.answer(
        text='Первоначальное меню', reply_markup=start_menu_keyboard()
    )
    
    
@start.message(Command('main_menu'))
async def f_menu(message: Message, user: User):
    if not user.current_avatar_id:
        await message.answer(
        text='Для открытия основного меню, пройдите инструкцию', reply_markup=start_menu_keyboard()
        )
        return
    await message.answer(
        text='Основное меню', reply_markup=main_menu_keyboard()
    )
    
    
@start.message(F.text == INSTRUCRION_BTN_TEXT)
async def description_bot(message: Message):
    await message.answer(
        text=DESCRIPTION_BOT,
        reply_markup=btn_descript_step_first(),
        parse_mode="Markdown",
    )
    
    
@start.callback_query(F.data == 'first_ok')
async def adout_photo(callback: CallbackQuery):
    await callback.message.answer(
        text=DESCRIPTION_ABOUT_PHOTO,
        reply_markup=btn_descript_step_second(),
        parse_mode="Markdown",
    )
    await callback.answer('')
    await callback.message.delete()
    
    
@start.callback_query(F.data == 'second_ok')
async def about_styles(callback: CallbackQuery):
    await callback.message.edit_text(
        text=ABOUT_STYLES_AVATAR_TEXT,
        reply_markup=btn_descript_cost(),
        parse_mode="Markdown",
    )
    await callback.answer('')
    
    
@start.callback_query(F.data == 'cost_question')
async def about_styles(callback: CallbackQuery):
    tariffs = await sync_to_async(lambda: list(Tariffs.objects.all()))()
   
    text_about_tarifs = "\n".join(
            [f"📦 **{tariff.name}** - {tariff.cost}₽ ({tariff.count_generations} генераций)" for tariff in tariffs]
        )
    
    await callback.message.edit_text(
            f"💰 **Стоимость пакетов**\n\n{text_about_tarifs}\n\n✅",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=BUY_BTN_TEXT, callback_data="start_buy")],
                    [InlineKeyboardButton(text='Поддержка', url=config.SUPPORT_URL)]
                ],
                
            ),
            parse_mode="Markdown"
        )
    await callback.answer('')
