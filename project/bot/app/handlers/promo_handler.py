from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from ..states import Promo
from ..keyboards import *
from ..texts import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.database.models import Promocode, User


promo = Router()


@promo.message(F.text == PROMO_BTN_TEXT)
async def promo_start(message: Message, state: FSMContext):
    await message.answer('Отправьте ваш промокод!')
    await state.set_state(Promo.wait_promo)
    
    
@promo.message(Promo.wait_promo)
async def take_promo(message: Message, state: FSMContext, user: User):
    try:
        # Пытаемся найти промокод (регистронезависимый поиск)
        promo = await Promocode.objects.aget(code__iexact=message.text.strip())
        
        # Обновляем данные пользователя
        user.generation_count += promo.count_generations
        promo.count_usage -= 1
        
        # Удаляем промокод если он исчерпан
        if promo.count_usage <= 0:
            await promo.adelete()
        else:
            await promo.asave()
            
        # Сохраняем пользователя
        await user.asave()
        
        await message.answer(
            text=f'Отлично, теперь вам доступны {user.generation_count} генераций',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(
                        text=GO_GENERATE_TEXT, 
                        callback_data='go_generate'
                    )
                ]]
            )
        )
        
    except Promocode.DoesNotExist:
        # Промокод не найден
        await message.answer(text=WITHOUT_PROMOCODE_TEXT, reply_markup=start_menu_keyboard())
        
    except Exception as e:
        # Обработка других ошибок
        print(f"Ошибка при обработке промокода: {e}")
        await message.answer("Произошла ошибка при обработке промокода")
        
    finally:
        # Всегда очищаем состояние
        await state.clear()