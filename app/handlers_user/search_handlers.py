from aiogram import F
from math import ceil
from contextlib import suppress

from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.handlers_user.main_handlers import router
from app.database.requests import research_requests, city_requests, cart_requests, main_requests
from app.keyboards_user.inline.text_pagination_keyboard import Pagination, paginator
from app.keyboards_user.inline.order_cart_keyboard import get_formating_cost
from app.database.requests.main_requests import get_search


# ПОИСК
@router.callback_query(Pagination.filter(F.action.in_(['prev', 'next'])))
async def paginator_handler(callback: CallbackQuery, callback_data: Pagination):
    lresearches, lservices = await main_requests.get_search(callback.from_user.id, callback_data.query)
    if not bool(callback_data.many):
        search_list = []
        if lresearches and lservices:
            all_list = lresearches + lservices
            search_list = all_list
        elif not lresearches and lservices:
            search_list = lservices
        elif not lservices and lresearches:
            search_list = lresearches
    else:
        search_list, all_pages = await get_ress(lresearches, lservices)
    
    page_num = int(callback_data.page)
    page = page_num - 1 if page_num > 1 else 1
    if callback_data.action  ==  'next':
        page = page_num + 1 if page_num < int(callback_data.all_pages) else page_num
    
    with suppress(TelegramBadRequest):
        if not bool(callback_data.many):
            if '*' in search_list[page-1][1]:
                name = search_list[page-1][1].replace('*', '"')
            else: name = search_list[page-1][1]
            cost = get_formating_cost(search_list[page-1][2])
            await callback.message.edit_text(
                f'<b>Наименование:</b> {name}.\n\n<b>Цена:</b> {cost} ₽',
                reply_markup = paginator(callback_data.query, callback_data.all_pages, page = page, item_id = search_list[page-1][0], what_is = search_list[page-1][3]),
                parse_mode = 'HTML'
            )
        else:
            s = '\n\n'.join(search_list[page-1])
            await callback.message.edit_text(f'{s}', parse_mode = 'HTML', reply_markup = paginator(callback_data.query, all_pages, page = page, many = True))
        await callback.answer()

@router.message(F.text.regexp(r'^\D+([а-яА-я]+\s*\d*){,15}'))
async def search(message: Message):
    await message.answer('Поиск...')
    if '"' in message.text: search_text = message.text.replace('"','*')
    else: search_text = message.text
    # await message.answer_sticker('CAACAgEAAxkBAAIT4GYf05AoknhZGHsUaQgdKNvAIz7bAAIDCgACv4yQBJGkR4JOgqlxNAQ')
    lresearches, lservices = await get_search(message.from_user.id, search_text)
    res_count = len(lresearches)+len(lservices)
    if res_count <=  8:
        if res_count  ==  1: await message.answer(f'Найден {res_count} результат по запросу:\n<i>{message.text}</i>.', parse_mode = 'HTML')
        elif res_count < 5: await message.answer(f'Найдено {res_count} результата по запросу:\n<i>{message.text}</i>.', parse_mode = 'HTML')
        else: await message.answer(f'Найдено {res_count} результатов по запросу:\n<i>{message.text}</i>.', parse_mode = 'HTML')
        if len(message.text)>20: res_text = message.text[:20]
        else: res_text = message.text
        print(f'>>> Сликом большой текст - {message.text} -------> {res_text}')
        if lresearches and lservices:
            all_list = lresearches + lservices
            if '*' in all_list[0][1]:
                name = all_list[0][1].replace('*', '"')
            else: name = all_list[0][1]
            cost = get_formating_cost(all_list[0][2])
            await message.answer(f'<b>Наименование:</b> {name}.\n\n<b>Цена:</b> {cost} ₽', 
                                parse_mode = 'HTML', reply_markup = paginator(res_text, res_count, item_id = all_list[0][0], what_is = all_list[0][3]))
        elif not lresearches and lservices:
            if '*' in lservices[0][1]:
                name = lservices[0][1].replace('*', '"')
            else: name = lservices[0][1]
            cost = get_formating_cost(lservices[0][2])
            await message.answer(f'<b>Наименование:</b> {name}.\n\n<b>Цена:</b> {cost} ₽', 
                                parse_mode = 'HTML', reply_markup = paginator(res_text, res_count, item_id = lservices[0][0], what_is = lservices[0][3]))
        elif not lservices and lresearches:
            if '*' in lresearches[0][1]:
                name = lresearches[0][1].replace('*', '"')
            else: name = lresearches[0][1]
            cost = get_formating_cost(lresearches[0][2])
            await message.answer(f'<b>Наименование:</b> {name}.\n\n<b>Цена:</b> {cost} ₽', 
                                parse_mode = 'HTML', reply_markup = paginator(res_text, res_count, item_id = lresearches[0][0], what_is = lresearches[0][3]))
    else:
        ress, all_pages = await get_ress(lresearches, lservices)
        s = '\n\n'.join(ress[0])
        await message.answer(f'Найдено cлишком много результатов ({res_count}) по запросу:\n<i>{message.text}</i>.\n\n<b>Нажмите</b> на наименование и отправьте в этот чат.', parse_mode = 'HTML')
        if all_pages > 1:
            await message.answer(f'{s}', parse_mode = 'HTML', reply_markup = paginator(message.text, all_pages, many = True))
        else: await message.answer(f'{s}', parse_mode = 'HTML')
# если результатов больше 8
async def get_ress(lresearches, lservices, need_pages = False):
    text = []
    if lresearches and lservices:
        all_list = lresearches + lservices
        for item in all_list:
            if '*' in item[1]: item[1] = item[1].replace('*','"')
            text.append(f'🔎 <code>{item[1]}</code>')
    elif not lresearches and lservices:
        for item in lservices:
            if '*' in item[1]: item[1] = item[1].replace('*','"')
            text.append(f'🔎 <code>{item[1]}</code>')
    elif not lservices and lresearches:
        for item in lresearches:
            if '*' in item[1]: item[1] = item[1].replace('*','"')
            text.append(f'🔎 <code>{item[1]}</code>')
    all_pages = ceil(len(text)/12)
    print('>>> Количество страниц ', all_pages)
    split = lambda lst, n: [lst[i::n] for i in range(n)]
    ress = split(text, all_pages)
    return ress, all_pages

@router.callback_query(F.data.startswith('notice_button_action'))
async def notice_actions(callback: CallbackQuery):
    await callback.answer()
    notice_action_id = callback.data.split('#')[1].split('/')[0]
    city_id = await city_requests.get_city_id(callback.from_user.id)
    action = await research_requests.get_research_data(int(notice_action_id))
    if len(action.Name)>20: res_text = action.Name[:20]
    else: res_text = action.Name
    price = await research_requests.get_research_price(action.ID, city_id)
    cost = get_formating_cost(price.Cost)
    await callback.message.answer(f'<b>Наименование:</b> {action.Name}.\n\n<b>Цена:</b> {cost} ₽', 
                                parse_mode = 'HTML', reply_markup = paginator(res_text, 1, item_id = action.ID, what_is = 'research'))

@router.callback_query(F.data.startswith('search-item_id'))
async def from_search_to_cart(callback: CallbackQuery):
    data = callback.data.split('#')
    item_id = int(data[1])
    what_is = data[0].split('/')[1]
    if what_is  ==  'research':
        added = await cart_requests.add_to_cart(callback.from_user.id, Rid = item_id)
    elif what_is  ==  'service':
        added = await cart_requests.add_to_cart(callback.from_user.id, Sid = item_id)
    if added:
        await callback.answer('Добавлено в корзину')
    else: await callback.answer('Уже в корзине')
