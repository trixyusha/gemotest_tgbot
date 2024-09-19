from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests.action_requests import get_action_categories, get_action_subcategories, get_actions, get_action_subcategory_name, get_action_data, get_action_price



async def actions_categories():
    all_action_categories = await get_action_categories()
    keyboard = InlineKeyboardBuilder()
    buf = -1
    for action_category in all_action_categories:
            if buf  ==  0:
                buf = action_category.ID
            elif buf  ==  action_category.ID:
                continue
            elif buf !=  action_category.ID:
                keyboard.add(InlineKeyboardButton(text = action_category.Name, callback_data = f'action-category_{action_category.ID}'))
                buf = 0
    keyboard.add(InlineKeyboardButton(text = '⬅️Назад в меню', callback_data = 'exit_to_research_or_service'))
    return keyboard.adjust(1).as_markup()

async def actions_subcategories(action_category_id, only_cat_name):
    action_category_id = int(action_category_id)
    cat = await get_action_categories(action_category_id)
    if not only_cat_name:
        all_action_subcategories = await get_action_subcategories(action_category_id)
        keyboard = InlineKeyboardBuilder()
        buf = -1
        for action_subcategory in all_action_subcategories:
            # print(f'\nRESEARCH {research_subcategory.ID} - {research_subcategory.Name}')
            if buf  ==  0:
                buf = action_subcategory.ID
            elif buf  ==  action_subcategory.ID:
                continue
            elif buf !=  action_subcategory.ID:
                keyboard.add(InlineKeyboardButton(text = action_subcategory.Name, callback_data = f'action-subcategory_{action_category_id}#{action_subcategory.ID}'))
                buf = 0
        keyboard.add(InlineKeyboardButton(text = '⬅️Назад к категориям', callback_data = 'back_action_categories'))
        keyboard.add(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service'))
        return cat.Name, keyboard.adjust(1).as_markup()
    else: return cat.Name

async def action_data(action_id, page_count, page):
    action_id = int(action_id)
    data = await get_action_data(action_id)
    price = await get_action_price(action_id)
    actions_count = len([i for i in await get_actions(data.ActionCategoryID, data.ActionSubcategoryID)])
    keyboard = InlineKeyboardBuilder()
    if price is not None:
        keyboard.add(InlineKeyboardButton(text = '🛒В корзину', callback_data = f'to_cart_action#{data.ID}&{data.ActionCategoryID}#{data.ActionSubcategoryID}/{actions_count}_{page_count}#{page}'))
    keyboard.add(InlineKeyboardButton(text = '⬅️Назад', callback_data = f'aback-to-pagination&{data.ActionCategoryID}#{data.ActionSubcategoryID}/{actions_count}_{page_count}#{page}'))
    if price is not None:
        return data.Name, data.Description, price.Cost, keyboard.adjust(1).as_markup()
    else:
        return data.Name, data.Description, price, keyboard.adjust(1).as_markup()
