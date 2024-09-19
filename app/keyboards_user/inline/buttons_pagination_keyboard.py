from aiogram import F
from app.handlers_user.main_handlers import router
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .researches_keyboard import research_subcategories
from .services_keyboard import service_subcategories
from .actions_keyboard import actions_subcategories 
from app.functions import get_cat_subcat_names, researches, services, actions

async def pagination(data, page, page_count, what_is):
    if what_is  ==  'research':
        buttons = []
        cat_id = data[page][0][2]
        subcat_id = data[page][0][3]
        for data_page in data[page]:
            if '*' in data_page[1]:
                data_page[1] = data_page[1].replace('*', '"')
            name_button = [
                InlineKeyboardButton(text = f'{data_page[1]}', callback_data = f'research-{data_page[0]}#{page_count}_{page}') # #{item.ResearchCategoryID}#{item.ResearchSubcategoryID}
            ]
            buttons.append(name_button)
        
        
        if page_count > 1:
            bottom_buttons = []
            if page !=  1:
                bottom_buttons.append(InlineKeyboardButton(text = f'⬅️', callback_data = f'rpage&{cat_id}#{subcat_id}_{page_count}#{page-1}'))
            else:
                bottom_buttons.append(InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'rstop_back#{cat_id}'))
                
            bottom_buttons.append(InlineKeyboardButton(text = f'{page}/{page_count}', callback_data = f'back_proxy_type#{page}'))
            
            if page  ==  page_count:
                bottom_buttons.append(InlineKeyboardButton(text = f'⛔️', callback_data = f'stop_stop'))
            else:
                bottom_buttons.append(InlineKeyboardButton(text = f'➡️', callback_data = f'rpage&{cat_id}#{subcat_id}_{page_count}#{page+1}'))
                
            buttons.append(bottom_buttons)
            if page > 1:
                buttons.append([
                    InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'rstop_back#{cat_id}')
                ])
        else:
            buttons.append([
                InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'rstop_back#{cat_id}')
            ])
        buttons.append([
            InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service')
        ])
        
        keyboard = InlineKeyboardMarkup(row_width = 1, inline_keyboard = buttons)
        return keyboard
    
    elif what_is  ==  'service':
        buttons = []
        cat_id = data[page][0][2]
        subcat_id = data[page][0][3]
        for data_page in data[page]:
            if '*' in data_page[1]:
                data_page[1] = data_page[1].replace('*', '"')
            name_button = [
                InlineKeyboardButton(text = f'{data_page[1]}', callback_data = f'service-{data_page[0]}#{page_count}_{page}') # #{item.ResearchCategoryID}#{item.ResearchSubcategoryID}
            ]
            buttons.append(name_button)
        
        if page_count > 1:
            bottom_buttons = []
            if page !=  1:
                bottom_buttons.append(InlineKeyboardButton(text = f'⬅️', callback_data = f'spage&{cat_id}#{subcat_id}_{page_count}#{page-1}'))
            else:
                bottom_buttons.append(InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'sstop_back#{cat_id}'))
                
            bottom_buttons.append(InlineKeyboardButton(text = f'{page}/{page_count}', callback_data = f'back_proxy_type#{page}'))
            
            if page  ==  page_count:
                bottom_buttons.append(InlineKeyboardButton(text = f'⛔️', callback_data = f'stop_stop'))
            else:
                bottom_buttons.append(InlineKeyboardButton(text = f'➡️', callback_data = f'spage&{cat_id}#{subcat_id}_{page_count}#{page+1}'))
                
            buttons.append(bottom_buttons)
            if page > 1:
                buttons.append([
                    InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'sstop_back#{cat_id}')
                ])
        
        else:
            buttons.append([
                InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'sstop_back#{cat_id}')
            ])
        buttons.append([
            InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service')
        ])
        
        keyboard = InlineKeyboardMarkup(row_width = 1, inline_keyboard = buttons)
        return keyboard
    
    elif what_is  ==  'action':
        buttons = []
        cat_id = data[page][0][3]
        subcat_id = data[page][0][4]
        for data_page in data[page]:
            if '*' in data_page[1]:
                data_page[1] = data_page[1].replace('*', '"')
            name_button = [
                InlineKeyboardButton(text = f'{data_page[1]}', callback_data = f'action-{data_page[0]}#{page_count}_{page}') # #{item.ResearchCategoryID}#{item.ResearchSubcategoryID}
            ]
            buttons.append(name_button)
        
        if page_count > 1:
            bottom_buttons = []
            if page !=  1:
                bottom_buttons.append(InlineKeyboardButton(text = f'⬅️', callback_data = f'apage&{cat_id}#{subcat_id}_{page_count}#{page-1}'))
            else:
                bottom_buttons.append(InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'astop_back#{cat_id}'))
                
            bottom_buttons.append(InlineKeyboardButton(text = f'{page}/{page_count}', callback_data = f'back_proxy_type#{page}'))
            
            if page  ==  page_count:
                bottom_buttons.append(InlineKeyboardButton(text = f'⛔️', callback_data = f'stop_stop'))
            else:
                bottom_buttons.append(InlineKeyboardButton(text = f'➡️', callback_data = f'apage&{cat_id}#{subcat_id}_{page_count}#{page+1}'))
                
            buttons.append(bottom_buttons)
            if page > 1:
                    buttons.append([
                        InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'astop_back#{cat_id}')
                    ])
        
        else:
            buttons.append([
                InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'astop_back#{cat_id}')
            ])
        buttons.append([
            InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service')
        ])
        
        keyboard = InlineKeyboardMarkup(row_width = 1, inline_keyboard = buttons)
        return keyboard

# обработка нажатия на среднюю кнопку пагинации, которая показывает номера страниц
# (номер текущей/номер последней) 
# отправляет алерт "Текущая страница"
@router.callback_query(F.data.startswith('back_proxy_type'))
async def edit_page(callback: CallbackQuery) -> None:
    page = callback.data.split('#')[1]
    await callback.answer(f'Текущая страница №{page}')

# обработка нажатий на боковые кнопки пагинации    
@router.callback_query(F.data.regexp(r'[rsa]page'))
async def pages(callback: CallbackQuery) -> None:
    data = callback.data.split('_')[0]
    ppages = callback.data.split('_')[1]
    pages_count = ppages.split('#')[0]
    page = ppages.split('#')[1]
    if callback.data[0]  ==  'r':
        researches_dict = await researches(data.split('&')[1], callback.from_user.id, True)
        keyboards = await pagination(researches_dict, int(page), int(pages_count), 'research')
    elif callback.data[0]  ==  's':
        services_dict = await services(data.split('&')[1], callback.from_user.id, True)
        keyboards = await pagination(services_dict, int(page), int(pages_count), 'service')
    elif callback.data[0]  ==  'a':
        actions_dict = await actions(data.split('&')[1], True)
        keyboards = await pagination(actions_dict, int(page), int(pages_count), 'action')
    await callback.message.edit_reply_markup(reply_markup = keyboards)

# обработка нажатия на кнопку стоп на последней странице пагинации
@router.callback_query(F.data  ==  'stop_stop')
async def stop_pagination(callback: CallbackQuery):
    await callback.answer('Список закончился')
    
# обработка нажатия на боковую кнопку первой страницы (возвращает к списку подкатегорий) 
@router.callback_query(F.data.regexp(r'[rsa]stop_back'))
async def back_stop_pagination(callback: CallbackQuery):
    await callback.answer()
    cat_id = int(callback.data.split('#')[1])
    if callback.data[0]  ==  'r':
        cat_name, keyboard = await research_subcategories(cat_id, False, callback.from_user.id)
    elif callback.data[0]  ==  's':
        cat_name, keyboard = await service_subcategories(cat_id, False, callback.from_user.id)
    elif callback.data[0]  ==  'a':
        cat_name, keyboard = await actions_subcategories(cat_id, False)
    await callback.message.edit_text(f'Категория: <b>{cat_name}</b>\nВыберите подкатегорию:', parse_mode = 'HTML')
    await callback.message.edit_reply_markup(reply_markup = keyboard)

# вернуться к пагинации 
@router.callback_query(F.data.regexp(r'[rsa]back-to-pagination'))
async def back_to_pagination(callback: CallbackQuery):
    # rback-to-pagination&{cat.Name}#{subcat_name}/{researches_count}_{page_count}#{page}
    count = callback.data.split('_')[0].split('/')[1]
    ids = callback.data.split('_')[0].split('/')[0].split('&')[1].split('#')
    cat_id = ids[0]
    subcat_id = ids[1]
    ppages = callback.data.split('_')[1]
    pages_count = ppages.split('#')[0]
    page = ppages.split('#')[1]
    if callback.data[0]  ==  'r':
        await callback.answer()
        researches_dict = await researches(callback.data.split('_')[0].split('/')[0].split('&')[1], callback.from_user.id, True)
        cat_name, subcat_name = await get_cat_subcat_names(cat_id, subcat_id, 'research')
        keyboards = await pagination(researches_dict, int(page), int(pages_count), 'research')
        some_text = f'Исследований в подкатегории: {count}\n\nВыбрав и нажав на исследование, будет отправлена дополнительная информация о нем.'
    elif callback.data[0]  ==  's':
        await callback.answer()
        services_dict = await services(callback.data.split('_')[0].split('/')[0].split('&')[1], callback.from_user.id, True)
        cat_name, subcat_name = await get_cat_subcat_names(cat_id, subcat_id, 'service')
        keyboards = await pagination(services_dict, int(page), int(pages_count), 'service')
        some_text = f'Медицинских услуг в подкатегории: {count}\n\nВыбрав и нажав на медицинскую услугу, будет отправлена дополнительная информация о ней.'
    elif callback.data[0]  ==  'a':
        await callback.answer()
        actions_dict = await actions(callback.data.split('_')[0].split('/')[0].split('&')[1], True)
        cat_name, subcat_name = await get_cat_subcat_names(cat_id, subcat_id, 'action')
        keyboards = await pagination(actions_dict, int(page), int(pages_count), 'action')
        some_text = f'Акций в подкатегории: {count}\n\nВыбрав и нажав на акцию, будет отправлена дополнительная информация о ней.'
    await callback.message.edit_text(f'''Категория: <b>{cat_name}</b>\nПодкатегория: <b>{subcat_name}</b>\n{some_text}''', parse_mode = 'HTML')
    await callback.message.edit_reply_markup(reply_markup = keyboards)
