from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def get_payment_buttons(order_number, anon: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text = 'Онлайн', callback_data = f'online_payment#{order_number}/{anon}'))
    keyboard.add(InlineKeyboardButton(text = 'В отделении', callback_data = f'offline_payment#{order_number}/{anon}'))
    return keyboard.as_markup()
