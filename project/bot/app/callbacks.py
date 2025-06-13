from aiogram.filters.callback_data import CallbackData

class PaginatorCallback(CallbackData, prefix="pag"):
    action: str
    page: int
    category_id: int | None = None

class StyleCallback(CallbackData, prefix="style"):
    action: str 
    style_id: int

class CategoryCallback(CallbackData, prefix="cat"):
    action: str 
    category_id: int