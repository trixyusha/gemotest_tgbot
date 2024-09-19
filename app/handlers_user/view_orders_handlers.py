from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from app.handlers_user.main_handlers import router
from app.functions import orders
from app.keyboards_user.inline.order_cart_keyboard import order_data


# кнопка "ЗАКАЗЫ"
@router.callback_query(F.data.startswith('orders_page'))
async def orders_pages(callback: CallbackQuery) -> None:
    ppages = callback.data.split('&')[1]
    pages_count = ppages.split('#')[0]
    page = ppages.split('#')[1]
    orders_dict = await orders(callback.from_user.id, True)
    keyboards = await orders_pagination(orders_dict, int(page), int(pages_count))
    await callback.message.edit_reply_markup(reply_markup = keyboards)
    
async def orders_pagination(data, page, page_count):
    buttons = []
    for data_page in data[page]:
        name_button = [
            InlineKeyboardButton(text = f'№{data_page[1]} ({data_page[2].date().strftime("%d.%m.%Y")})', callback_data = f'order-{data_page[0]}#{page_count}_{page}') # #{item.ResearchCategoryID}#{item.ResearchSubcategoryID}
        ]
        buttons.append(name_button)
    
    bottom_buttons = []
    if page !=  1:
        bottom_buttons.append(InlineKeyboardButton(text = f'⬅️', callback_data = f'orders_page&{page_count}#{page-1}'))
    else:
        bottom_buttons.append(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'orders_stop_back'))
        
    bottom_buttons.append(InlineKeyboardButton(text = f'{page}/{page_count}', callback_data = f'back_proxy_type#{page}'))
    
    if page  ==  page_count:
        bottom_buttons.append(InlineKeyboardButton(text = f'⛔️', callback_data = f'stop_stop'))
    else:
        bottom_buttons.append(InlineKeyboardButton(text = f'➡️', callback_data = f'orders_page&{page_count}#{page+1}'))
        
    buttons.append(bottom_buttons)
    if page > 1:
        buttons.append([
            InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'orders_stop_back')
        ])
    
    keyboard = InlineKeyboardMarkup(row_width = 1, inline_keyboard = buttons)
    return keyboard

@router.callback_query(F.data.startswith('order-'))
async def order(callback: CallbackQuery):
    await callback.answer()
    data = callback.data.split('#')
    order_id = data[0].split('-')[1]
    ppages = data[1].split('_')
    pages_count = ppages[0]
    page = ppages[1]
    text, keyboards = await order_data(callback.from_user.id, order_id, pages_count, page)
    await callback.message.edit_text(f'{text}', parse_mode = 'HTML')
    await callback.message.edit_reply_markup(reply_markup = keyboards)
    
@router.callback_query(F.data.startswith('order_back_to_pagination'))
async def order_back_to_pagination(callback: CallbackQuery):
    await callback.answer()
    data = callback.data.split('&')
    ppages = data[1].split('#')
    pages_count = ppages[0]
    page = ppages[1]
    count, orders_dict = await orders(callback.from_user.id)
    keyboards = await orders_pagination(orders_dict, int(page), int(pages_count))
    if count  ==  1: t = 'Ваш заказ'
    else: t = 'Ваши заказы'
    await callback.message.edit_text(f'{t} ({count}):')
    await callback.message.edit_reply_markup(reply_markup = keyboards)
