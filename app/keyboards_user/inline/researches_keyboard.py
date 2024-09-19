from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests.research_requests import get_research_categories, get_research_subcategories, get_researches, get_research_data, get_research_price
from app.database.requests.city_requests import get_city_id



async def research_categories(tg_id):
    city_id = await get_city_id(tg_id)
    all_research_categories = await get_research_categories(city_id)
    keyboard = InlineKeyboardBuilder()
    buf = -1
    for research_category in all_research_categories:
            if buf  ==  0:
                buf = research_category.ID
            elif buf  ==  research_category.ID:
                continue
            elif buf !=  research_category.ID:
                keyboard.add(InlineKeyboardButton(text = research_category.Name, callback_data = f'research-category_{research_category.ID}'))
                buf = 0
    keyboard.add(InlineKeyboardButton(text = '⬅️Назад в меню', callback_data = 'exit_to_research_or_service'))
    return keyboard.adjust(1).as_markup()

async def research_subcategories(research_category_id, only_cat_name, tg_id):
    research_category_id = int(research_category_id)
    city_id = await get_city_id(tg_id)
    cat = await get_research_categories(None, research_category_id)
    if not only_cat_name:
        all_research_subcategories = await get_research_subcategories(research_category_id, city_id)
        keyboard = InlineKeyboardBuilder()
        buf = -1
        for research_subcategory in all_research_subcategories:
            # print(f'\nRESEARCH {research_subcategory.ID} - {research_subcategory.Name}')
            if buf  ==  0:
                buf = research_subcategory.ID
            elif buf  ==  research_subcategory.ID:
                continue
            elif buf !=  research_subcategory.ID:
                keyboard.add(InlineKeyboardButton(text = research_subcategory.Name, callback_data = f'research-subcategory_{research_category_id}#{research_subcategory.ID}'))
                buf = 0
        keyboard.add(InlineKeyboardButton(text = '⬅️Назад к категориям', callback_data = 'back_research_categories'))
        keyboard.add(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service'))
        return cat.Name, keyboard.adjust(1).as_markup()
    else: return cat.Name

async def research_data(research_id, tg_id, page_count, page):
    research_id = int(research_id)
    city_id = await get_city_id(tg_id)
    data = await get_research_data(research_id)
    price = await get_research_price(research_id, city_id)
    researches_count = len([i for i in await get_researches(data.ResearchCategoryID, data.ResearchSubcategoryID, city_id)])
    keyboard = InlineKeyboardBuilder()
    if price is not None:
        keyboard.add(InlineKeyboardButton(text = '🛒В корзину', callback_data = f'to_cart_research#{data.ID}&{data.ResearchCategoryID}#{data.ResearchSubcategoryID}/{researches_count}_{page_count}#{page}'))
    keyboard.add(InlineKeyboardButton(text = '⬅️Назад', callback_data = f'rback-to-pagination&{data.ResearchCategoryID}#{data.ResearchSubcategoryID}/{researches_count}_{page_count}#{page}'))
    keyboard.add(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service'))
    # print(f'\nRESEARCH GET DATA\nPAGE COUNT {page_count}\nPAGE {page}\n')
    if price is not None:
        return data.Name, data.Description, price.Cost, keyboard.adjust(1).as_markup()
    else:
        return data.Name, data.Description, price, keyboard.adjust(1).as_markup()
