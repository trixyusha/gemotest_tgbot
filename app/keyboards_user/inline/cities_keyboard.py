from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests.city_requests import get_cities



async def cities():
    all_cities = await get_cities()
    keyboard = InlineKeyboardBuilder()
    for city in all_cities:
        keyboard.add(InlineKeyboardButton(text = city.Name, callback_data = f'city_{city.ID}'))
    return keyboard.adjust(2).as_markup()    
