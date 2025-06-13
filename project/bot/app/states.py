from aiogram.fsm.state import State, StatesGroup


class Promo(StatesGroup):
    wait_promo = State()
    

class Email(StatesGroup):
    tariff = State()
    wait_email = State()
    non = State()
    wait_photos = State()
    wait_name = State()
    
    

