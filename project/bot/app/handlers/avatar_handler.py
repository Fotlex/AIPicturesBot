import math
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile

from ..keyboards import *
from ..texts import *
from ..servise import generate_photo, decode_base64_to_image, convert_pil_to_bytes
from ..callbacks import *

avatar_router = Router()

from project import config
from project.database.models import Avatar
from project.bot.app.yookassa import payment_avatar_generate


AVATARS_PER_PAGE = 5

@avatar_router.message(F.text == 'Аватар')
async def avatar(message: Message):
    await message.answer(
        text='Здесь ты можешь выбрать человека, с лицом которого генерируются фотографии',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Выбрать аватар', callback_data='choise_avat')],
            [InlineKeyboardButton(text='Добавить аватар', callback_data='add_avat')],
        ])
    )
    
    
class AvatarPaginator(CallbackData, prefix="av_pag"):
    action: str  
    page: int

class SelectAvatar(CallbackData, prefix="sel_av"):
    avatar_id: str



def create_avatar_pagination_keyboard(
    avatars_on_page: list, page: int, total_pages: int
) -> InlineKeyboardBuilder.as_markup:
    builder = InlineKeyboardBuilder()

    for avatar in avatars_on_page:
        builder.button(
            text=f"Аватар: {avatar.name}",
            callback_data=SelectAvatar(avatar_id=str(avatar.id))
        )
    builder.adjust(1)

    navigation_row = []
    if page > 0:
        navigation_row.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=AvatarPaginator(action="prev", page=page - 1).pack())
        )
    
    if total_pages > 1: 
        navigation_row.append(
            InlineKeyboardButton(text=f"{page + 1} / {total_pages}", callback_data="ignore_page_count")
        )

    if page < total_pages - 1:
        navigation_row.append(
            InlineKeyboardButton(text="Вперед ➡️", callback_data=AvatarPaginator(action="next", page=page + 1).pack())
        )
    
    if navigation_row:
        builder.row(*navigation_row)
    
    return builder.as_markup()


@sync_to_async
def get_user_avatars(user_id: int) -> list[Avatar]:
    try:
        user = User.objects.get(id=user_id)
        return list(user.avatars.all().order_by('-created_at'))
    except User.DoesNotExist:
        return []


@avatar_router.callback_query(F.data == 'choise_avat')
async def show_my_avatars(callback: CallbackQuery, user: User):
    user_avatars = await get_user_avatars(user.id)

    if not user_avatars:
        await callback.answer("У вас пока нет созданных аватаров.")
        return

    total_pages = math.ceil(len(user_avatars) / AVATARS_PER_PAGE)
    current_page_avatars = user_avatars[:AVATARS_PER_PAGE]

    keyboard = create_avatar_pagination_keyboard(current_page_avatars, 0, total_pages)

    await callback.message.edit_text("Выберите аватар:", reply_markup=keyboard)
    await callback.answer('')


@avatar_router.callback_query(AvatarPaginator.filter(F.action.in_(["prev", "next"])))
async def paginate_avatars(query: CallbackQuery, callback_data: AvatarPaginator):
    page = callback_data.page
    
    user_avatars = await get_user_avatars(query.from_user.id)
    
    if not user_avatars:
        await query.message.edit_text("У вас нет аватаров.")
        await query.answer('')
        return

    total_pages = math.ceil(len(user_avatars) / AVATARS_PER_PAGE)
    start_index = page * AVATARS_PER_PAGE
    end_index = start_index + AVATARS_PER_PAGE
    current_page_avatars = user_avatars[start_index:end_index]

    keyboard = create_avatar_pagination_keyboard(current_page_avatars, page, total_pages)

    await query.message.edit_reply_markup(reply_markup=keyboard)
    await query.answer('') 


@avatar_router.callback_query(SelectAvatar.filter())
async def process_avatar_selection(query: CallbackQuery, callback_data: SelectAvatar, user: User):
    avatar_id = callback_data.avatar_id
    current_avatar = await Avatar.objects.aget(id=avatar_id)
    await query.answer(f"Вы выбрали аватар - {current_avatar.name}", show_alert=True)
    user.current_avatar_id = avatar_id
    await user.asave()

@avatar_router.callback_query(F.data == "ignore_page_count")
async def ignore_callback(query: CallbackQuery):
    await query.answer('')
    
    
@avatar_router.callback_query(F.data == 'add_avat')
async def add_avat(callback: CallbackQuery):
    await callback.message.edit_text(
        text='Ты можешь иметь сразу несколько аватаров и выбирать для генерации любой из них.\nСтоимость добавления аватара 111р',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Купить', callback_data='buy_avatar')],
            [InlineKeyboardButton(text='Поддержка', url=config.SUPPORT_URL)],
        ])
    )
    await callback.answer('')
    
    
@avatar_router.callback_query(F.data == 'buy_avatar')
async def pay_url_avatar(callback: CallbackQuery, user: User):
    if not user.is_pay_error_avatar: 
        url = await payment_avatar_generate(user=user)
        await callback.message.answer(
            text='Жми для оплаты',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Оплатить', url=url)]
            ])
        )
    else:
        await callback.message.answer(
            text=f'✅Продолжите создание своего аватара!',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Создать аватар', callback_data='instruction_avatar')]
            ])
        )
    await callback.answer('')