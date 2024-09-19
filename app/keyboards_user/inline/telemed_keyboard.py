from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests.telemed_requests import get_telemed_data



async def get_telemed_buttons():
    keyboard = InlineKeyboardBuilder()
    telemed_data = await get_telemed_data()
    for item in telemed_data:
        keyboard.add(InlineKeyboardButton(text = item[1], callback_data = f'telemed-serviceid_{item[0]}', url = item[2]))
    keyboard.add(InlineKeyboardButton(text = '⬅️Назад к категориям', callback_data = f'back_service_categories'))
    keyboard.add(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service'))
    return keyboard.adjust(1).as_markup()
