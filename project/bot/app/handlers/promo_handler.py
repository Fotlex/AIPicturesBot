from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from ..states import Promo
from ..keyboards import *
from ..texts import *

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

from project.database.models import Promocode, User, UserPromocode


promo = Router()


@promo.message(F.text == PROMO_BTN_TEXT)
async def promo_start(message: Message, state: FSMContext):
    await message.answer('Отправьте ваш промокод!')
    await state.set_state(Promo.wait_promo)
    

@sync_to_async
def has_used_promocode(user, promo):
    return UserPromocode.objects.filter(user=user, used_promocode=promo).exists()


@promo.message(Promo.wait_promo)
async def take_promo(message: Message, state: FSMContext, user: User):
    try:
        promo = await Promocode.objects.aget(code__iexact=message.text.strip())

        if await has_used_promocode(user, promo):
            await message.answer(text='Вы уже использовали этот промокод')
            await state.clear()
            
            return
        
        user.generation_count += promo.count_generations
        promo.count_usage -= 1
        
        await UserPromocode.objects.acreate(
            user=user,
            used_promocode=promo,
        )
        
        if promo.count_usage <= 0:
            await promo.adelete()
        else:
            await promo.asave()
            
        await user.asave()
        
        if not user.current_avatar_id:
            await message.answer(
                text=f'Отлично, теперь вам доступны {user.generation_count} генераций\nНачните создание своего аватара!',
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(
                            text=GO_GENERATE_TEXT, 
                            callback_data='instruction_avatar'
                        )
                    ]]
                )
            )
        else:
            await message.answer(
                text='Отлтчно, приступайте к генерации!',
                reply_markup=main_menu_keyboard()
            )
        
    except Promocode.DoesNotExist:
        await message.answer(text=WITHOUT_PROMOCODE_TEXT, reply_markup=start_menu_keyboard())
        
    except Exception as e:
        print(f"Ошибка при обработке промокода: {e}")
        await message.answer("Произошла ошибка при обработке промокода")
        
    finally:
        await state.clear()
        
        