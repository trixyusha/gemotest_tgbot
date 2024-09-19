from aiogram.types import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class Pagination(CallbackData, prefix = 'pag'):
    action: str
    query: str
    page: int
    all_pages: int
    many: int
    
    
def paginator(query: str, all_pages: int, page: int = 1, item_id: int = 0, what_is: str = 'none', many: bool = False):
    builder = InlineKeyboardBuilder()
    if not many:
        builder.add(InlineKeyboardButton(text = '🛒В корзину', callback_data = f'search-item_id/{what_is}#{item_id}'))
    if page == 1:
        prev_page = '⛔️'
        prev_cb_data = 'stop_stop'
        next_page = '➡️'
        next_cb_data = Pagination(query = query, action = 'next', page = page, all_pages = all_pages, many = int(many)).pack()
    elif page == all_pages:
        next_page = '⛔️'
        next_cb_data = 'stop_stop'
        prev_page = '⬅️'
        prev_cb_data = Pagination(query = query, action = 'prev', page = page, all_pages = all_pages, many = int(many)).pack()
    else: 
        prev_page = '⬅️'
        prev_cb_data = Pagination(query = query, action = 'prev', page = page, all_pages = all_pages, many = int(many)).pack()
        next_page = '➡️'
        next_cb_data = Pagination(query = query, action = 'next', page = page, all_pages = all_pages, many = int(many)).pack()
    if all_pages > 1:
        builder.row(
            InlineKeyboardButton(text = prev_page, callback_data = prev_cb_data),
            InlineKeyboardButton(text = f'{page}/{all_pages}', callback_data = Pagination(query = query, action = 'now', page = page, all_pages = all_pages, many = int(many)).pack()),
            InlineKeyboardButton(text = next_page, callback_data = next_cb_data)
        )
    builder.add(InlineKeyboardButton(text = '⏪Выйти', callback_data = 'pag_exit'))
    if not many: builder.adjust(1,3,1)
    else: builder.adjust(3,1)
    return builder.as_markup()
