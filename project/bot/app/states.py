from aiogram.fsm.state import State, StatesGroup


class Promo(StatesGroup):
    wait_promo = State()
    