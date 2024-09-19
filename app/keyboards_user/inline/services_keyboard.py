from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests.city_requests import get_city_id
from app.database.requests.service_requests import get_service_categories, get_service_subcategories, get_services, get_service_data, get_service_price



async def service_categories(tg_id):
    city_id = await get_city_id(tg_id)
    print(f'[SERVICE CATEGORY] CITY ID {city_id}')
    all_service_categories = await get_service_categories(city_id)
    telemed = None
    keyboard = InlineKeyboardBuilder()
    buf = -1
    for service_category in all_service_categories:
        if service_category.Name !=  'Телемедицина':
            if buf  ==  0:
                buf = service_category.ID
            elif buf  ==  service_category.ID:
                continue
            elif buf !=  service_category.ID:
                keyboard.add(InlineKeyboardButton(text = service_category.Name, callback_data = f'service-category_{service_category.ID}'))
                buf = 0
        else:
            telemed = service_category
    keyboard.add(InlineKeyboardButton(text = telemed.Name, callback_data = f'telemed-category_{telemed.ID}'))
    keyboard.add(InlineKeyboardButton(text = '⬅️Назад в меню', callback_data = 'exit_to_research_or_service'))
    return keyboard.adjust(1).as_markup()

async def service_subcategories(service_category_id, only_cat_name, tg_id):
    service_category_id = int(service_category_id)
    city_id = await get_city_id(tg_id)
    cat = await get_service_categories(None, service_category_id)
    if not only_cat_name:
        all_service_subcategories = await get_service_subcategories(service_category_id, city_id)
        keyboard = InlineKeyboardBuilder()
        buf = -1
        for service_subcategory in all_service_subcategories:
            if buf  ==  0:
                buf = service_subcategory.ID
            elif buf  ==  service_subcategory.ID:
                continue
            elif buf !=  service_subcategory.ID:
                keyboard.add(InlineKeyboardButton(text = service_subcategory.Name, callback_data = f'service-subcategory_{service_category_id}#{service_subcategory.ID}'))
                buf = 0
        keyboard.add(InlineKeyboardButton(text = '⬅️Назад к категориям', callback_data = 'back_service_categories'))
        keyboard.add(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service'))
        return cat.Name, keyboard.adjust(1).as_markup()
    else: return cat.Name

async def service_data(service_id, tg_id, page_count, page):
    service_id = int(service_id)
    city_id, city_name = await get_city_id(tg_id, True)
    data = await get_service_data(service_id)
    price = await get_service_price(service_id, city_id)
    services_count = len([i for i in await get_services(data.ServiceCategoryID, data.ServiceSubcategoryID, city_id)])
    keyboard = InlineKeyboardBuilder()
    if price is not None:
        keyboard.add(InlineKeyboardButton(text = '🛒В корзину', callback_data = f'to_cart_service#{data.ID}&{data.ServiceCategoryID}#{data.ServiceSubcategoryID}/{services_count}_{page_count}#{page}'))
    keyboard.add(InlineKeyboardButton(text = '⬅️Назад', callback_data = f'sback-to-pagination&{data.ServiceCategoryID}#{data.ServiceSubcategoryID}/{services_count}_{page_count}#{page}'))
    print(f'\nSERVICE GET DATA\nPAGE COUNT {page_count}\nPAGE {page}\nCITY NAME {city_name}')
    if price is not None:
        return data.Name, price.Cost, city_name, keyboard.adjust(1).as_markup()
    else:
        return data.Name, price, city_name, keyboard.adjust(1).as_markup()
