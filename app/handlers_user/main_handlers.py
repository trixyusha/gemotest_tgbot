import os
# from math import ceil
# import re
from dotenv import load_dotenv
# from contextlib import suppress

import random
from aiogram import F, Bot, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.methods.delete_message import DeleteMessage
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
# from aiogram.types import FSInputFile as send_file
from aiogram.fsm.state import StatesGroup, State
# from aiogram.fsm.context import FSMContext
# from aiogram.types import LabeledPrice, PreCheckoutQuery
# from aiogram.exceptions import TelegramBadRequest
# from aiogram.types.input_file import InputFile as send_file
from aiogram.types.input_file import BufferedInputFile as send_buffer

from app.keyboards_admin.inline.inline_keyboards import get_button
# import app.keyboards as kb
# import app.database.main_requests as request
# from ..filters.symbol_or_letter import MessageMatch
from hashlib import sha256
# from time import monotonic

# from app.send_sms import SMSC
# from app.send_sms import get_kod as code

from app.keyboards_user.default_keyboard import default_keyboard_builder
from app.keyboards_user.inline.cities_keyboard import cities
from app.database.requests.main_requests import set_user, get_hashid_card, get_QR_code


load_dotenv()
router = Router()

GET_QR_TEXT = '''Это <b>ваш QR-код</b>.\nОн хранит данные о текущем заказе и ваш TelegramID.\n
Отсканируйте его у администратора, чтобы подключить услугу <b>"Отправка результатов исследований в Telegram"</b> без использования мобильного номера телефона.'''
GET_QR_TEXT_CONNECT = 'Это <b>ваш QR-код</b> (карточка клиента).\nУслуга "Отправка результатов исследований в Telegram" подключена.\n\nОтсканируйте его у администратора.'
GET_QR_TEXT_DISCONNECT = '''Вы пока не подключили услугу <b>"Отправка результатов исследований в Telegram"</b>.\n
Для того, чтобы получить QR-код, вам необходимо оформить заказ. В этот чат будет отправлен <b>временный</b> QR-код, который нужно отсканировать у администратора. После проделанных действий, вам придет новый и уже <b>постоянный</b> QR-код, а услуга подключится автоматически.
\nЕсли же вы не хотите подключать данную услуга, то просто не показывайте QR-код администратору.'''

# class Confirm_Number(StatesGroup):
#     p_number = State()
#     confirm_code = State()
#     time = State()
#     resend = State()

class ConfirmPlaceAnOrder(StatesGroup):
    confirm = State()
    not_confirm = State()

def get_hash_data(data):
    return sha256(data.encode("utf-8")).hexdigest()


# пользователь нажал на команду старт
@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot) -> None:
    
    await bot.send_message(chat_id = os.getenv('MAIN_ADMIN_ID'), text = f'''❗<b><i>Зашел пользователь</i></b>❗\nusername: @{message.from_user.username}
id: <code>{message.from_user.id}</code>\nfullname: <code>{message.from_user.full_name}</code>\n''', 
reply_markup = await get_button(message.from_user.id), parse_mode = 'HTML')
    
    
    user, phone = await set_user(message.from_user.id)
    if user:
        if phone:
            await message.answer(f'Рады снова приветствовать вас, {message.from_user.first_name}! Выберите пункт меню.', 
                                    reply_markup = await default_keyboard_builder(
                                        text = ['📝Оформить предварительный заказ','🛒Корзина','🧾Заказы','⚙️Помощь','❌Отключиться от услуги'],
                                        sizes = [1,2,1,1],
                                        input_field_placeholder = 'Выберите пункт меню...',
                                        resize_keyboard = True
                                    )
                                )
        else:
            await message.answer(f'Рады снова приветствовать вас, {message.from_user.first_name}! Выберите пункт меню.', 
                                    reply_markup = await default_keyboard_builder(
                                        text = ['📝Оформить предварительный заказ','🛒Корзина','🧾Заказы','⚙️Помощь','🆕Подключить получение результатов'],
                                        sizes = [1,2,1,1],
                                        input_field_placeholder = 'Выберите пункт меню...',
                                        resize_keyboard = True
                                    )
                                )
    else:
        await message.answer(f'Это бот Гемотест для оформления предварительных заказов и отправки результатов лабораторных исследований. {message.from_user.first_name}, выберите город:', 
                                reply_markup = await cities()
                            )

@router.message(Command('get_qrcode'))
async def get_qrcode(message: Message):
    hashid_card = await get_hashid_card(message.from_user.id)
    if hashid_card:
        qr_code = await get_QR_code(message.from_user.id, hashid_card, dont_need_bool=True)
        await message.answer_photo(send_buffer(qr_code.getvalue(), f'qrcode_{message.from_user.id}.png'), caption=GET_QR_TEXT_CONNECT, protect_content=True, parse_mode='HTML')
    else: await message.answer(GET_QR_TEXT_DISCONNECT, parse_mode='HTML')

# пользователь выбрал город (появляется, если пользователь ранее не запускал бота)
@router.callback_query(F.data.startswith('city_'))
async def enter_city(callback: CallbackQuery) -> None:
    await set_user(callback.from_user.id, callback.from_user.username, callback.data.split('_')[1])
    await callback.answer()
    await callback.message.answer(f'Рады приветствовать вас, {callback.from_user.first_name}! Выберите пункт меню.', 
                                    reply_markup = await default_keyboard_builder(
                                        text = ['📝Оформить предварительный заказ','🛒Корзина','🧾Заказы','⚙️Помощь','🆕Подключить получение результатов'],
                                        sizes = [1,2,1,1],
                                        input_field_placeholder = 'Выберите пункт меню...',
                                        resize_keyboard = True
                                    )
                                )
    try:
        return DeleteMessage(chat_id = callback.message.chat.id, message_id = callback.message.message_id)
    except: pass


# @router.callback_query(F.data.regexp(r'\b[sid]{,3}agree\b'))
# async def activate_the_service_disagree(callback: CallbackQuery, state: FSMContext) -> None:
#     if 'dis' in callback.data:
#         await callback.answer()
#         await callback.message.answer('Согласие на обработку персональных данных отклонено. Подключение услуги невозможно.')
#         try:
#             return DeleteMessage(chat_id = callback.message.chat.id, message_id = callback.message.message_id)
#         except: pass
#     else:
#         await state.set_state(Confirm_Number.p_number)
#         await callback.answer()
#         await callback.message.edit_caption(callback.inline_message_id,'Вы дали свое согласие на обработку персональных данных!',
#                                             reply_markup = None)
#         await callback.message.answer('Отправьте свой номер телефона, чтобы подключить услугу <b>"Отправка результатов исследований в Telegram"</b>.', 
#                                         parse_mode = 'HTML', 
#                                         reply_markup =  await kb.default_keyboard_builder(
#                                             text = '📱Отправить номер телефона',
#                                             sizes = 1,
#                                             request_cont = True,
#                                             resize_keyboard = True,
#                                             input_field_placeholder = 'Отправьте номер телефона...'
#                                         )
#                                     )

# # пользователь отправил свой номер телефона    
# @router.message(Confirm_Number.p_number, F.contact)
# @router.message(Confirm_Number.p_number, F.text.regexp(r'\d+'))
# async def get_contact(message: Message, state: FSMContext) -> None:
#     smsc = SMSC()
#     ccode = code()
#     sms_text = f'Никому не говорите код {ccode}! Авторизация в боте https://t.me/GemotestLaboratory_Bot.'
#     # написать проверку на номер телефона
#     # cost = smsc.get_sms_cost(message.contact.phone_number[1:], sms_text)
#     # print(re.findall(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', message.contact.phone_number))
#     if message.contact:
#         if '+' in message.contact.phone_number:
#             await state.update_data(p_number = message.contact.phone_number[1:])
#             # smsc.send_sms(message.contact.phone_number[1:], sms_text)
#             start_time = monotonic()
#             print(f'\n\nPHONE NUMBER {message.contact.phone_number[1:]}\n-----------\nTEXT\n{sms_text}\n-----------\n\n')
#             await state.set_state(Confirm_Number.confirm_code)
#             await state.update_data(confirm_code = ccode, time = start_time)
#         else:
#             await state.update_data(p_number = message.contact.phone_number)
#             # smsc.send_sms(message.contact.phone_number, sms_text)
#             start_time = monotonic()
#             print(f'\n\nTIME {start_time}\n-----------\nPHONE NUMBER {message.contact.phone_number}\n-----------\nTEXT\n{sms_text}\n-----------\n\n')
#             await state.set_state(Confirm_Number.confirm_code)
#             await state.update_data(confirm_code = ccode, time = start_time)
#         # Код действителен в течение 15 минут, после чего подключение услуги будет автоматически отменено.
#     elif message.text:
#         if bool(re.match(r'^(\+7|8)\s?\(?9[0-9]{2}\)?\s?((\s|-)?[0-9]){7}', message.text)):
#             await state.update_data(p_number = message.text)
#             # smsc.send_sms(message.contact.phone_number, sms_text)
#             start_time = monotonic()
#             print(f'\n\nTIME {start_time}\n-----------\nPHONE NUMBER {message.text}\n-----------\nTEXT\n{sms_text}\n-----------\n\n')
#             await state.set_state(Confirm_Number.confirm_code)
#             await state.update_data(confirm_code = ccode, time = start_time)
#         else: 
#             await message.answer('Неверный номер телефона, введите снова или нажмите на кнопку <b>"Отправить номер телефона"</b>', parse_mode = 'HTML')
#             await state.get_state(Confirm_Number.p_number)
#     await message.answer('''Для подтверждения номера телефона, вам придет код в SMS-сообщении, который необходимо будет отправить в этот чат.
# Код действителен в течение 15 минут.''', reply_markup = ReplyKeyboardRemove())
#     try:
#         return DeleteMessage(chat_id = message.chat.id, message_id = message.message_id)
#     except: pass

# # пользователь отправляет код подтверждения, который ему был выслан в смс сообщении    
# @router.message(Confirm_Number.confirm_code)
# async def confirmation(message: Message, state: FSMContext) -> None:
#     data = await state.get_data()
#     if monotonic() - data['time'] < float(15*60): # 15*60
#         print(f'\n\nNEW IF TIME {monotonic()-data["time"]}\n\n')
#         if data['confirm_code']  ==  message.text:
#             await message.answer('Услуга <b>"Отправка результатов исследований в Telegram"</b> подключена!', parse_mode = 'HTML', 
#                                     reply_markup = await kb.default_keyboard_builder(
#                                         text = ['📝Оформить предварительный заказ','🛒Корзина','🧾Заказы','⚙️Помощь','❌Отключиться от услуги'],
#                                         sizes = [1,2,1,1],
#                                         input_field_placeholder = 'Выберите пункт меню...',
#                                         resize_keyboard = True
#                                     )
#                                 )
#             await request.set_user(message.from_user.id, phone_number = get_hash_data(data['p_number']))
#             await state.clear()
#         else:
#             await message.answer('Неверный код, повторите попытку ввода.', reply_markup = None)
#     else:
#         await message.answer('''15 минут прошло, код больше не является действительным.
# Отправить повторно?''', reply_markup = await kb.default_keyboard_builder(text = ['Да', 'Нет'], callback_data = ['yes_resend', 'no_resend']))
#         await state.set_state(Confirm_Number.resend)

# # код не действителен
# @router.callback_query(Confirm_Number.resend, F.data.regexp(r'\w{2,3}_resend'))
# async def re_sending_code(callback: CallbackQuery, state: FSMContext):
#     if 'no' in callback.data:
#         await callback.answer()
#         await callback.message.answer('Услуга <b>"Отправка результатов исследований в Telegram"</b> не была подключена.', parse_mode = 'HTML', reply_markup = await kb.default_keyboard_builder(
#                                 text = ['📝Оформить предварительный заказ','🛒Корзина','🧾Заказы','⚙️Помощь','🆕Подключить получение результатов'],
#                                 sizes = [1,2,1,1],
#                                 input_field_placeholder = 'Выберите пункт меню...',
#                                 resize_keyboard = True
#                             ))
#         await state.clear()
#         try:
#             return DeleteMessage(chat_id = callback.message.chat.id, message_id = callback.message.message_id)
#         except: pass
#     elif 'yes' in callback.data:
#         smsc = SMSC()
#         ccode = code()
#         sms_text = f'Никому не говорите код {ccode}! Авторизация в боте https://t.me/GemotestLaboratory_Bot.'
#         data = await state.get_data()
#         await callback.answer()
#         start_time = monotonic()
#         print(f'\n\nPHONE NUMBER {data["p_number"]}\n-----------\nTEXT\n{sms_text}\n-----------\n\n')
#         await state.set_state(Confirm_Number.confirm_code)
#         await state.update_data(confirm_code = ccode, time = start_time)
#         await callback.message.edit_text('Код отправлен повторно. Он также действителен 15 минут.', reply_markup = None)

# # оформление предварительного заказа, пользователь выбирает категорию (обработка нажатий на инлайн кнопки и команды)
# @router.message(Command('researches', 'services'))
# @router.callback_query(F.data.in_({'researches','services','actions', 'notice_actions'}))
# async def categories(m_or_q: Message | CallbackQuery) -> None:
#     if isinstance(m_or_q, Message):
#         if m_or_q.text  ==  '/researches':
#             await m_or_q.answer('💉Иcследования\nВыберите категорию:', reply_markup = await kb.research_categories(m_or_q.from_user.id))
#         elif m_or_q.text  ==  '/services':
#             await m_or_q.answer('🧑‍⚕️Медицинские услуги\nВыберите категорию:', reply_markup = await kb.service_categories(m_or_q.from_user.id))
#     else:    
#         if m_or_q.data[:-2]  ==  'research':
#             await m_or_q.answer()
#             await m_or_q.message.edit_text('💉Иcследования\nВыберите категорию:')
#             await m_or_q.message.edit_reply_markup(reply_markup = await kb.research_categories(m_or_q.from_user.id))
#         elif m_or_q.data[:-1]  ==  'service':
#             await m_or_q.answer()
#             await m_or_q.message.edit_text('🧑‍⚕️Медицинские услуги\nВыберите категорию:')
#             await m_or_q.message.edit_reply_markup(reply_markup = await kb.service_categories(m_or_q.from_user.id))
#         elif m_or_q.data[:-1]  ==  'action':
#             await m_or_q.answer()
#             await m_or_q.message.edit_text('🛍️Акции\nВыберите категорию:')
#             await m_or_q.message.edit_reply_markup(reply_markup = await kb.actions_categories())
#         elif m_or_q.data  ==  'notice_actions':
#             await m_or_q.answer()
#             await m_or_q.message.answer('🛍️Акции\nВыберите категорию:', reply_markup = await kb.actions_categories())

# @router.callback_query(F.data.regexp(r'[resachviton]{6,8}-category_'))
# async def subcategories(callback: CallbackQuery) -> None:
#     await callback.answer()
#     indx = callback.data.find('-')
#     if callback.data[:indx]  ==  'research':
#         cat_name, keyboard = await kb.research_subcategories(int(callback.data.split('_')[1]), False, callback.from_user.id)
#     elif callback.data[:indx]  ==  'service':
#         cat_name, keyboard = await kb.service_subcategories(int(callback.data.split('_')[1]), False, callback.from_user.id)
#     elif callback.data[:indx]  ==  'action':
#         cat_name, keyboard = await kb.actions_subcategories(int(callback.data.split('_')[1]), False)
#     await callback.message.edit_text(f'Категория: <b>{cat_name}</b>\nВыберите подкатегорию:', parse_mode = 'HTML')
#     await callback.message.edit_reply_markup(reply_markup = keyboard)

# # пользователь нажал на кнопку "назад" и вернулся к категориям 
# @router.callback_query(F.data.regexp(r'back_[resachviton]{6,8}_categories'))
# async def back_categories(callback: CallbackQuery) -> None:
#     await callback.answer()
#     if callback.data.split('_')[1]  ==  'research':
#         await callback.message.edit_text('💉Иcследования\nВыберите категорию:')
#         await callback.message.edit_reply_markup(reply_markup = await kb.research_categories(callback.from_user.id))
#     elif callback.data.split('_')[1]  ==  'service':
#         await callback.message.edit_text('🧑‍⚕️Медицинские услуги\nВыберите категорию:')
#         await callback.message.edit_reply_markup(reply_markup = await kb.service_categories(callback.from_user.id))
#     elif callback.data.split('_')[1]  ==  'action':
#         await callback.message.edit_text('🛍️Акции\nВыберите категорию:')
#         await callback.message.edit_reply_markup(reply_markup = await kb.actions_categories())
    
# # оформление предварительного заказа, пользователь выбирает 
# # элемент из списка (ПАГИНАЦИЯ)
# @router.callback_query(F.data.regexp(r'[resachviton]{6,8}-subcategory_'))
# async def items(callback: CallbackQuery) -> None:
#     await callback.answer()
#     page = 1
#     indx = callback.data.find('-')
#     cat_name = callback.message.text[11:callback.message.text.find('\n')]
#     if callback.data[:indx]  ==  'research':
#         subcat_name, count, researches_dict = await kb.researches(callback.data.split('_')[1], callback.from_user.id)
#         pages_count = len(researches_dict)
#         some_text = f'Исследований в подкатегории: {count}\n\nВыбрав и нажав на исследование, будет отправлена дополнительная информация о нем.'
#         keyboards = await pagination(researches_dict, int(page), int(pages_count), callback.data[:indx])
#     elif callback.data[:indx]  ==  'service':
#         subcat_name, count, services_dict = await kb.services(callback.data.split('_')[1], callback.from_user.id)
#         pages_count = len(services_dict)
#         some_text = f'Медицинских услуг в подкатегории: {count}\n\nВыбрав и нажав на медицинскую услугу, будет отправлена дополнительная информация о ней.'
#         keyboards = await pagination(services_dict, int(page), int(pages_count), callback.data[:indx])
#     elif callback.data[:indx]  ==  'action':
#         subcat_name, count, actions_dict = await kb.actions(callback.data.split('_')[1])
#         pages_count = len(actions_dict)
#         some_text = f'Акций в подкатегории: {count}\n\nВыбрав и нажав на акцию, будет отправлена дополнительная информация о ней.'
#         keyboards = await pagination(actions_dict, int(page), int(pages_count), callback.data[:indx])
#     await callback.message.edit_text(f'''Категория: <b>{cat_name}</b>\nПодкатегория: <b>{subcat_name}</b>\n{some_text}''',
# parse_mode = 'HTML')
#     await callback.message.edit_reply_markup(reply_markup = keyboards)


# # оформление предварительного заказа, пользователь выбрал конкретное 
# # исследование
# @router.callback_query(F.data.startswith('research-'))
# async def get_research_data(callback: CallbackQuery) -> None:
#     await callback.answer()
#     research_get_id = callback.data.split('#')[0]
#     research_id = research_get_id.split('-')[1]
#     get_page = callback.data.split('#')[1]
#     page_count = get_page.split('_')[0]
#     page = get_page.split('_')[1]
#     tg_id = callback.from_user.id
#     name, description, price, keyboard = await kb.research_data(research_id, tg_id, page_count, page)
#     if '*' in name:
#         name = name.replace('*', '"')
#     res_cost = ''
#     if len(str(price).split('.')[0])  ==  4:
#         temp_cost = str(price).split('.')[0]
#         res_cost = temp_cost[:1]+' '+temp_cost[1:]
#     elif len(str(price).split('.')[0])  ==  5:
#         temp_cost = str(price).split('.')[0]
#         res_cost = temp_cost[:2]+' '+temp_cost[2:]
#     else: res_cost = str(price).split('.')[0]
#     await callback.message.edit_text(f'<b>{name}</b>\n\n<b>Описание:</b> {description}\n\n<b>Стоимость исследования:</b> {res_cost} ₽',parse_mode = 'HTML')
#     await callback.message.edit_reply_markup(reply_markup = keyboard)

# # оформление предварительного заказа, пользователь выбрал конкретную 
# # медицинскую услугу
# @router.callback_query(F.data.startswith('service-'))
# async def get_service_data(callback: CallbackQuery) -> None:
#     await callback.answer()
#     service_get_id = callback.data.split('#')[0]
#     service_id = service_get_id.split('-')[1]
#     get_page = callback.data.split('#')[1]
#     page_count = get_page.split('_')[0]
#     page = get_page.split('_')[1]
#     tg_id = callback.from_user.id
#     name, price, keyboard = await service_data(service_id, tg_id, page_count, page)
#     if '*' in name:
#         name = name.replace('*', '"')
#     res_cost = ''
#     if len(str(price).split('.')[0])  ==  4:
#         temp_cost = str(price).split('.')[0]
#         res_cost = temp_cost[:1]+' '+temp_cost[1:]
#     elif len(str(price).split('.')[0])  ==  5:
#         temp_cost = str(price).split('.')[0]
#         res_cost = temp_cost[:2]+' '+temp_cost[2:]
#     else: res_cost = str(price).split('.')[0]
#     await callback.message.edit_text(f'<b>{name}</b>\n\n<b>Стоимость медицинской услуги:</b> {res_cost} ₽', parse_mode = 'HTML')
#     await callback.message.edit_reply_markup(reply_markup = keyboard)

# # оформление предварительного заказа, пользователь выбрал конкретную 
# # акцию
# @router.callback_query(F.data.startswith('action-'))
# async def get_service_data(callback: CallbackQuery) -> None:
#     await callback.answer()
#     action_get_id = callback.data.split('#')[0]
#     action_id = action_get_id.split('-')[1]
#     get_page = callback.data.split('#')[1]
#     page_count = get_page.split('_')[0]
#     page = get_page.split('_')[1]
#     name, description, price, keyboard = await kb.action_data(action_id, page_count, page)
#     if '*' in name:
#         name = name.replace('*', '"')
#     res_cost = ''
#     if len(str(price).split('.')[0])  ==  4:
#         temp_cost = str(price).split('.')[0]
#         res_cost = temp_cost[:1]+' '+temp_cost[1:]
#     elif len(str(price).split('.')[0])  ==  5:
#         temp_cost = str(price).split('.')[0]
#         res_cost = temp_cost[:2]+' '+temp_cost[2:]
#     else: res_cost = str(price).split('.')[0]
#     await callback.message.edit_text(f'<b>{name}</b>\n\n<b>Описание:</b> {description}\n\n<b>Стоимость акции:</b> {res_cost} ₽', parse_mode = 'HTML')
#     await callback.message.edit_reply_markup(reply_markup = keyboard)

# # обработка нажатия на среднюю кнопку пагинации, которая показывает номера страниц
# # (номер текущей/номер последней) 
# # отправляет алерт "Текущая страница"
# @router.callback_query(F.data.startswith('back_proxy_type'))
# async def edit_page(callback: CallbackQuery) -> None:
#     page = callback.data.split('#')[1]
#     await callback.answer(f'Текущая страница №{page}')

# # обработка нажатий на боковые кнопки пагинации    
# @router.callback_query(F.data.regexp(r'[rsa]page'))
# async def pages(callback: CallbackQuery) -> None:
#     data = callback.data.split('_')[0]
#     ppages = callback.data.split('_')[1]
#     pages_count = ppages.split('#')[0]
#     page = ppages.split('#')[1]
#     if callback.data[0]  ==  'r':
#         researches_dict = await kb.researches(data.split('&')[1], callback.from_user.id, True)
#         keyboards = await pagination(researches_dict, int(page), int(pages_count), 'research')
#     elif callback.data[0]  ==  's':
#         services_dict = await kb.services(data.split('&')[1], callback.from_user.id, True)
#         keyboards = await pagination(services_dict, int(page), int(pages_count), 'service')
#     elif callback.data[0]  ==  'a':
#         actions_dict = await kb.actions(data.split('&')[1], True)
#         keyboards = await pagination(actions_dict, int(page), int(pages_count), 'action')
#     await callback.message.edit_reply_markup(reply_markup = keyboards)

# # ПАГИНАЦИЯ
# async def pagination(data, page, page_count, what_is):
#     if what_is  ==  'research':
#         buttons = []
#         cat_id = data[page][0][2]
#         subcat_id = data[page][0][3]
#         for data_page in data[page]:
#             if '*' in data_page[1]:
#                 data_page[1] = data_page[1].replace('*', '"')
#             name_button = [
#                 InlineKeyboardButton(text = f'{data_page[1]}', callback_data = f'research-{data_page[0]}#{page_count}_{page}') # #{item.ResearchCategoryID}#{item.ResearchSubcategoryID}
#             ]
#             buttons.append(name_button)
        
        
#         if page_count > 1:
#             bottom_buttons = []
#             if page !=  1:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'⬅️', callback_data = f'rpage&{cat_id}#{subcat_id}_{page_count}#{page-1}'))
#             else:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'rstop_back#{cat_id}'))
                
#             bottom_buttons.append(InlineKeyboardButton(text = f'{page}/{page_count}', callback_data = f'back_proxy_type#{page}'))
            
#             if page  ==  page_count:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'⛔️', callback_data = f'stop_stop'))
#             else:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'➡️', callback_data = f'rpage&{cat_id}#{subcat_id}_{page_count}#{page+1}'))
                
#             buttons.append(bottom_buttons)
#             if page > 1:
#                 buttons.append([
#                     InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'rstop_back#{cat_id}')
#                 ])
#         else:
#             buttons.append([
#                 InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'rstop_back#{cat_id}')
#             ])
#         buttons.append([
#             InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service')
#         ])
        
#         keyboard = InlineKeyboardMarkup(row_width = 1, inline_keyboard = buttons)
#         return keyboard
    
#     elif what_is  ==  'service':
#         buttons = []
#         cat_id = data[page][0][2]
#         subcat_id = data[page][0][3]
#         for data_page in data[page]:
#             if '*' in data_page[1]:
#                 data_page[1] = data_page[1].replace('*', '"')
#             name_button = [
#                 InlineKeyboardButton(text = f'{data_page[1]}', callback_data = f'service-{data_page[0]}#{page_count}_{page}') # #{item.ResearchCategoryID}#{item.ResearchSubcategoryID}
#             ]
#             buttons.append(name_button)
        
#         if page_count > 1:
#             bottom_buttons = []
#             if page !=  1:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'⬅️', callback_data = f'spage&{cat_id}#{subcat_id}_{page_count}#{page-1}'))
#             else:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'sstop_back#{cat_id}'))
                
#             bottom_buttons.append(InlineKeyboardButton(text = f'{page}/{page_count}', callback_data = f'back_proxy_type#{page}'))
            
#             if page  ==  page_count:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'⛔️', callback_data = f'stop_stop'))
#             else:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'➡️', callback_data = f'spage&{cat_id}#{subcat_id}_{page_count}#{page+1}'))
                
#             buttons.append(bottom_buttons)
#             if page > 1:
#                 buttons.append([
#                     InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'sstop_back#{cat_id}')
#                 ])
        
#         else:
#             buttons.append([
#                 InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'sstop_back#{cat_id}')
#             ])
#         buttons.append([
#             InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service')
#         ])
        
#         keyboard = InlineKeyboardMarkup(row_width = 1, inline_keyboard = buttons)
#         return keyboard
    
#     elif what_is  ==  'action':
#         buttons = []
#         cat_id = data[page][0][3]
#         subcat_id = data[page][0][4]
#         for data_page in data[page]:
#             if '*' in data_page[1]:
#                 data_page[1] = data_page[1].replace('*', '"')
#             name_button = [
#                 InlineKeyboardButton(text = f'{data_page[1]}', callback_data = f'action-{data_page[0]}#{page_count}_{page}') # #{item.ResearchCategoryID}#{item.ResearchSubcategoryID}
#             ]
#             buttons.append(name_button)
        
#         if page_count > 1:
#             bottom_buttons = []
#             if page !=  1:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'⬅️', callback_data = f'apage&{cat_id}#{subcat_id}_{page_count}#{page-1}'))
#             else:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'astop_back#{cat_id}'))
                
#             bottom_buttons.append(InlineKeyboardButton(text = f'{page}/{page_count}', callback_data = f'back_proxy_type#{page}'))
            
#             if page  ==  page_count:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'⛔️', callback_data = f'stop_stop'))
#             else:
#                 bottom_buttons.append(InlineKeyboardButton(text = f'➡️', callback_data = f'apage&{cat_id}#{subcat_id}_{page_count}#{page+1}'))
                
#             buttons.append(bottom_buttons)
#             if page > 1:
#                     buttons.append([
#                         InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'astop_back#{cat_id}')
#                     ])
        
#         else:
#             buttons.append([
#                 InlineKeyboardButton(text = f'⬅️Назад', callback_data = f'astop_back#{cat_id}')
#             ])
#         buttons.append([
#             InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service')
#         ])
        
#         keyboard = InlineKeyboardMarkup(row_width = 1, inline_keyboard = buttons)
#         return keyboard

# # обработка нажатия на кнопку стоп на последней странице пагинации
# @router.callback_query(F.data  ==  'stop_stop')
# async def stop_pagination(callback: CallbackQuery):
#     await callback.answer('Список закончился')
    
# # обработка нажатия на боковую кнопку первой страницы (возвращает к списку подкатегорий) 
# @router.callback_query(F.data.regexp(r'[rsa]stop_back'))
# async def back_stop_pagination(callback: CallbackQuery):
#     await callback.answer()
#     cat_id = int(callback.data.split('#')[1])
#     if callback.data[0]  ==  'r':
#         cat_name, keyboard = await kb.research_subcategories(cat_id, False, callback.from_user.id)
#     elif callback.data[0]  ==  's':
#         cat_name, keyboard = await kb.service_subcategories(cat_id, False, callback.from_user.id)
#     elif callback.data[0]  ==  'a':
#         cat_name, keyboard = await kb.actions_subcategories(cat_id, False)
#     await callback.message.edit_text(f'Категория: <b>{cat_name}</b>\nВыберите подкатегорию:', parse_mode = 'HTML')
#     await callback.message.edit_reply_markup(reply_markup = keyboard)

# # вернуться к пагинации 
# @router.callback_query(F.data.regexp(r'[rsa]back-to-pagination'))
# async def back_to_pagination(callback: CallbackQuery):
#     # rback-to-pagination&{cat.Name}#{subcat_name}/{researches_count}_{page_count}#{page}
#     count = callback.data.split('_')[0].split('/')[1]
#     ids = callback.data.split('_')[0].split('/')[0].split('&')[1].split('#')
#     cat_id = ids[0]
#     subcat_id = ids[1]
#     ppages = callback.data.split('_')[1]
#     pages_count = ppages.split('#')[0]
#     page = ppages.split('#')[1]
#     if callback.data[0]  ==  'r':
#         await callback.answer()
#         researches_dict = await kb.researches(callback.data.split('_')[0].split('/')[0].split('&')[1], callback.from_user.id, True)
#         cat_name, subcat_name = await kb.get_cat_subcat_names(cat_id, subcat_id, 'research')
#         keyboards = await pagination(researches_dict, int(page), int(pages_count), 'research')
#         some_text = f'Исследований в подкатегории: {count}\n\nВыбрав и нажав на исследование, будет отправлена дополнительная информация о нем.'
#     elif callback.data[0]  ==  's':
#         await callback.answer()
#         services_dict = await kb.services(callback.data.split('_')[0].split('/')[0].split('&')[1], callback.from_user.id, True)
#         cat_name, subcat_name = await kb.get_cat_subcat_names(cat_id, subcat_id, 'service')
#         keyboards = await pagination(services_dict, int(page), int(pages_count), 'service')
#         some_text = f'Медицинских услуг в подкатегории: {count}\n\nВыбрав и нажав на медицинскую услугу, будет отправлена дополнительная информация о ней.'
#     elif callback.data[0]  ==  'a':
#         await callback.answer()
#         actions_dict = await kb.actions(callback.data.split('_')[0].split('/')[0].split('&')[1], True)
#         cat_name, subcat_name = await kb.get_cat_subcat_names(cat_id, subcat_id, 'action')
#         keyboards = await pagination(actions_dict, int(page), int(pages_count), 'action')
#         some_text = f'Акций в подкатегории: {count}\n\nВыбрав и нажав на акцию, будет отправлена дополнительная информация о ней.'
#     await callback.message.edit_text(f'''Категория: <b>{cat_name}</b>\nПодкатегория: <b>{subcat_name}</b>\n{some_text}''', parse_mode = 'HTML')
#     await callback.message.edit_reply_markup(reply_markup = keyboards)

# # возврат в меню выбора (исследования или медицинские услуги)
# @router.callback_query(F.data  ==  'exit_to_research_or_service')
# async def exit_to_research_or_service(callback: CallbackQuery):
#     await callback.answer()
#     await callback.message.edit_text('Исследования или медицинские услуги?\nДля поиска необходимо отправить примерное наименование исследования/услуги.')
#     await callback.message.edit_reply_markup(reply_markup = await kb.default_keyboard_builder(
#                                                     text = ['💉Исследования', '🧑‍⚕️Медицинские услуги', '🛍️Акции', '⏪Покинуть меню'], 
#                                                     callback_data = ['researches', 'services', 'actions', 'exit_or_exit'], 
#                                                     sizes = 1
#                                                 )
#                                             )

# # выход из меню выбора (исследования илм иедицинские услуги)
# @router.callback_query(F.data.in_(['exit_or_exit', 'cart_exit', 'pag_exit', 'orders_stop_back']))
# async def exit_or_exit(callback: CallbackQuery) -> None:
#     await callback.answer()
#     await callback.message.edit_reply_markup(reply_markup = None)
#     await callback.message.edit_text('Выберите пункт нижнего меню.')
    # await callback.message.edit_reply_markup(reply_markup = None)

# # добавление в корзину 
# @router.callback_query(F.data.startswith('to_cart'))
# async def to_cart(callback: CallbackQuery):
#     data = callback.data.split('/')
#     all_page_data = data[1].split('_')
#     count = all_page_data[0]
#     page_data = all_page_data[1].split('#')
#     pages_count = page_data[0]
#     page = page_data[1]
#     ids = data[0].split('&')
#     ide = ids[0].split('#')[1]
#     what_is = ids[0].split('#')[0][8:]
#     print(f'\nДобавление в корзину {what_is}')
#     cat_id = ids[1].split('#')[0]
#     subcat_id = ids[1].split('#')[1]
#     cat_name, subcat_name = await kb.get_cat_subcat_names(cat_id, subcat_id, what_is)
#     if what_is  ==  'research':
#         researches_dict = await kb.researches(ids[1], callback.from_user.id, True)
#         added = await request.add_to_cart(callback.from_user.id, Rid = int(ide))
#         keyboards = await pagination(researches_dict, int(page), int(pages_count), what_is)
#         some_text = f'Исследований в подкатегории: {count}\n\nВыбрав и нажав на исследование, будет отправлена дополнительная информация о нем.'
#     elif what_is  ==  'service':
#         services_dict = await kb.services(ids[1], callback.from_user.id, True)
#         added = await request.add_to_cart(callback.from_user.id, Sid = int(ide))
#         keyboards = await pagination(services_dict, int(page), int(pages_count), what_is)
#         some_text = f'Медицинских услуг в подкатегории: {count}\n\nВыбрав и нажав на медицинскую услугу, будет отправлена дополнительная информация о ней.'
#     elif what_is  ==  'action':
#         actions_dict = await kb.actions(ids[1], True)
#         added = await request.add_to_cart(callback.from_user.id, Aid = int(ide))
#         keyboards = await pagination(actions_dict, int(page), int(pages_count), what_is)
#         some_text = f'Акций в подкатегории: {count}\n\nВыбрав и нажав на акцию, будет отправлена дополнительная информация о ней.'
#     # print(added)
#     if added:
#         await callback.answer('Добавлено в корзину')
#     else: await callback.answer('Уже в корзине')
#     await callback.message.edit_text(f'''Категория: <b>{cat_name}</b>\nПодкатегория: <b>{subcat_name}</b>\n{some_text}''', parse_mode = 'HTML')
#     await callback.message.edit_reply_markup(reply_markup = keyboards)

# @router.callback_query(F.data.startswith('search-item_id'))
# async def from_search_to_cart(callback: CallbackQuery):
#     data = callback.data.split('#')
#     item_id = int(data[1])
#     what_is = data[0].split('/')[1]
#     if what_is  ==  'research':
#         added = await request.add_to_cart(callback.from_user.id, Rid = item_id)
#     elif what_is  ==  'service':
#         added = await request.add_to_cart(callback.from_user.id, Sid = item_id)
#     if added:
#         await callback.answer('Добавлено в корзину')
#     else: await callback.answer('Уже в корзине')
    # await callback.message.edit_reply_markup(reply_markup = None)
    # await callback.message.edit_text(f'Чтобы оформить заказ, перейдите в корзину, нажав на кнопку <b>"Корзина"</b>.', parse_mode = 'HTML')
    
# телемедицина        
# @router.callback_query(F.data.startswith('telemed-category'))
# async def get_telemed(callback: CallbackQuery):
#     await callback.answer()
#     cat_name = 'Телемедицина'
#     await callback.message.answer(f'''Категория: <b>{cat_name}</b>
# Доступные специалисты (чтобы узнать более подробную информацию, нажмите на интересующую специальность врача, вас перенаправит на сайт):''',
# reply_markup = await kb.get_telemed_buttons(),
# parse_mode = 'HTML')

# # удалить элемент
# @router.callback_query(F.data.startswith('delete-'))
# async def delete_item(callback: CallbackQuery):
#     await callback.answer('Удалено')
#     if 'research' in callback.data:
#         research_id = callback.data.split('&')[1]
#         await request.edit_cart(callback.from_user.id, research_id, 'research')
#         # out_text, keyboard = await kb.get_cart_buttons(callback.from_user.id)
#     elif 'service' in callback.data:
#         service_id = callback.data.split('&')[1]
#         await request.edit_cart(callback.from_user.id, service_id, 'service')
#         # out_text, keyboard = await kb.get_cart_buttons(callback.from_user.id)
#     elif 'action' in callback.data:
#         action_id = callback.data.split('&')[1]
#         await request.edit_cart(callback.from_user.id, action_id, 'action')
#     out_text, keyboard = await kb.get_cart_buttons(callback.from_user.id)
#     if keyboard:
#         await callback.message.edit_text(f'<b>Ваш заказ:</b>\n{out_text}', parse_mode = 'HTML')
#         await callback.message.edit_reply_markup(reply_markup = keyboard)
#     else:
#         await callback.message.edit_reply_markup(reply_markup = None)
#         await callback.message.edit_text('<i><b>Корзина пуста.</b></i>\n\nЧтобы добавить исследование или медицинскую услугу в корзину, нажмите кнопку в меню <b>"Оформить предварительный заказ"</b>.',
#                                             parse_mode = 'HTML'
#                                         )

# # удалить весь заказ из корзины
# @router.callback_query(F.data  ==  'delete_all')
# async def delete_all(callback: CallbackQuery):
#     await callback.answer()
#     await request.del_cart(callback.from_user.id)
#     await callback.message.edit_reply_markup(reply_markup = None)
#     await callback.message.edit_text('<i><b>Корзина пуста.</b></i>\n\nЧтобы добавить исследование или медицинскую услугу в корзину, нажмите кнопку в меню <b>"Оформить предварительный заказ"</b>.',
#                                         parse_mode = 'HTML'
#                                     )

# # оформление заказа (из корзины)        
# @router.callback_query(F.data  ==  'place_an_order')
# async def place_an_order_qconfirm(callback: CallbackQuery):
#     await callback.answer()
#     await callback.message.delete()
#     # await callback.message.edit_text()
#     await callback.message.answer_document(send_file('files\\personal_data_agreement.pdf'), 
#                                             reply_markup = await kb.default_keyboard_builder(
#                                                 text = ['✅Соглашаюсь','❌Не соглашаюсь'], 
#                                                 callback_data = ['agree_place_an_order', 'disagree_place_an_order']), 
#                                             caption = 'Вы согласны на обработку персональных данных?', protect_content = True
#                                         )
    
    
# @router.callback_query(F.data.regexp(r'\b[sid]{,3}agree_\w{14}'))
# async def place_an_order_confirm(callback: CallbackQuery):
#     await callback.answer()
#     if 'dis' in callback.data:
#         await callback.message.edit_caption(inline_message_id = callback.inline_message_id, 
#                                                 caption = 'Согласие на обработку персональных данных отклонено.\nОформление заказа возможно, но он будет выполнен анонимно, такие результаты исследований врачи не принимают.', 
#                                                 reply_markup = await kb.default_keyboard_builder(
#                                                     text = ['Продолжить','Отмена'], 
#                                                     callback_data = ['continue_place_an_order','cancle_place_an_order_comfirm']
#                                                 )   
#                                             )        
#     else:
#         while True:
#             digits = random.sample('1234567890', 9)
#             order_num = await request.get_order_number(''.join(digits))
#             if order_num: break
#         text = await kb.get_cart_buttons(callback.from_user.id, get_text = True)
#         # await callback.message.edit_reply_markup(reply_markup = None)
#         await callback.message.edit_caption(inline_message_id = callback.inline_message_id, caption = 'Вы дали свое согласие на обработку персональных данных.',
#                                             reply_markup = None)
#         await callback.message.answer(f'Ваш заказ <b>№{"".join(digits)}</b>:\n{text}', parse_mode = 'HTML')
#         await callback.message.answer('Каким способом хотите произвести оплату?', reply_markup = await kb.get_payment_buttons(''.join(digits), 0))
    
# @router.callback_query(F.data.startswith(('continue_place','cancle_place')))   
# async def place_an_order_continue(callback: CallbackQuery):
#     await callback.answer()
#     if 'continue' in callback.data:
#         while True:
#             digits = random.sample('1234567890', 9)
#             order_num = await request.get_order_number(''.join(digits))
#             if order_num: break
#         await callback.message.edit_reply_markup(reply_markup = None)
#         await callback.message.answer('Каким способом хотите произвести оплату?', reply_markup = await kb.get_payment_buttons(''.join(digits), 1))
#     else:
#         await callback.message.edit_reply_markup(reply_markup = None)
#         await callback.message.answer(f'Оформление заказа отменено (заказ <b>не удален</b>), чтобы повторно попробовать оформить заказ, вам необходимо <i>перейти в корзину</i>.', parse_mode = 'HTML')

# # пользователь выбрал оплату в лабораторном отделении
# @router.callback_query(F.data.startswith('offline_payment'))
# async def offline_payment(callback: CallbackQuery):
#     await callback.answer()
#     await callback.message.edit_text('Вы выбрали оплату в лабораторном отделении.', reply_markup = None)
#     data = callback.data.split('#')[1]
#     order_num = data.split('/')[0]
#     anon = data.split('/')[1]
#     # print('>>> ANON? -> ', anon)
#     qr_buffer = await request.place_order(callback.from_user.id, order_num, False, anon)
#     if qr_buffer:
#         await callback.message.answer_photo(photo = send_buffer(qr_buffer.getvalue(), f'qrcode_{callback.from_user.id}.png'), 
#                                                 caption = GET_QR_TEXT, 
#                                                 protect_content = True, parse_mode = 'HTML'
#                                             )
#     else:
#         # сделать проверку на подключение мед. карты клиента, иначе отправить новый QR
#         await callback.message.edit_text('Воспользуйтесь своим QR-кодом, который уже был отправлен в этот чат, чтобы отсканировать в терминале самообслуживания или у администратора.', 
#                                             reply_markup = await kb.default_keyboard_builder(
#                                             text = 'Запросить QR-код',
#                                             callback_data = f'resend_qrcode',
#                                             sizes = 1
#                                         ))

# @router.callback_query(F.data.startswith('resend_qrcode'))
# async def resend_qrcode(callback: CallbackQuery):
#     await callback.answer()
#     qr_buffer = await request.place_order(callback.from_user.id)
#     await callback.message.edit_text('Вы запросили повторную отправку QR-кода.', reply_markup = None)
#     await callback.message.answer_photo(photo = send_buffer(qr_buffer.getvalue(), f'qrcode_{callback.from_user.id}.png'), 
#                                             caption = GET_QR_TEXT_CONNECT, 
#                                             protect_content = True, parse_mode = 'HTML'
#                                         )

# # выбрана онлайн оплата
# @router.callback_query(F.data.startswith('online_payment'))
# async def online_payment(callback: CallbackQuery):
#     await callback.answer()
#     await callback.message.edit_text('Вы выбрали онлайн оплату.', reply_markup = None)
#     # добавить в бд заказ (перенести из корзины в заказы)
#     data = callback.data.split('#')[1]
#     order_num = data.split('/')[0]
#     anon = data.split('/')[1]
#     cost = await kb.get_cart_buttons(callback.from_user.id, True)
#     price = LabeledPrice(label = f'Заказ №{order_num}', amount = cost*100)
#     await callback.message.answer_invoice(
#         title = f'Заказ №{order_num}',
#         description = f'Оплата предварительного заказа №{order_num}. В течение 30 дней, с момента оформления заказа, вам необходимо посетить любое лабораторное отделение.',
#         provider_token = os.getenv('PAYMENTS_TOKEN'),
#         payload = f'place_an_order#{order_num}/{anon}',
#         currency = 'rub',
#         prices = [price],
#         start_parameter = 'GemotestBot',
#         provider_data = None,
#         need_name = False,
#         need_phone_number = False,
#         need_email = False, # точно нужна почта?
#         need_shipping_address = False,
#         is_flexible = False,
#         disable_notification = False,
#         protect_content = True,
#         reply_to_message_id = None,
#         reply_markup = None
#     )
    # await callback.message.edit_reply_markup(reply_markup = None)

# @router.pre_checkout_query(lambda query: True)
# async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
#     await pre_checkout_query.answer(ok = True)
#     print(pre_checkout_query)

# @router.message(F.successful_payment)
# async def success_payment(message: Message):
#     print('GET ADD ORDER AND DEL CART')
#     data = message.successful_payment.invoice_payload.split('#')[1]
#     order_num = data.split('/')[0]
#     anon = data.split('/')[1]
#     print(f'\nORDER ID - {order_num}')
#     qr_buffer = await request.place_order(message.from_user.id, order_num, True, anon)
#     if qr_buffer:
#         await message.answer_photo(photo = send_buffer(qr_buffer.getvalue(), f'qrcode_{message.from_user.id}.png'), 
#                                         caption = 'Это ваш QR-код (карточка клиента).\nОтсканируйте его в терминале самообслуживания или у администратора.', 
#                                         protect_content = True
#                                     )
#     else:
#         await message.answer('Воспользуйтесь своим QR-кодом, который уже был отправлен в этот чат, чтобы отсканировать в терминале самообслуживания или у администратора.',
#                                 reply_markup = await kb.default_keyboard_builder(
#                                     text = 'Запросить QR-код',
#                                     callback_data = f'resend_qrcode#{order_num}',
#                                     sizes = 1
#                                 )
#                             )

# @router.callback_query(F.data  ==  'cart_del_instruction')
# async def cart_del_item(callback: CallbackQuery):
#     await callback.answer('Выберите номер для удаления из корзины')
    
    

# # обработка ввода с клавиатуры пользователя и нажатие кнопок
# @router.message(MessageMatch(['подключить получение результатов', 'подключить услугу', 'получение результатов']))
# async def activate_the_service(message: Message) -> None:
#     user, phone = await request.set_user(message.from_user.id)
#     if not phone:
#         await message.answer_document(send_file('files\\personal_data_agreement.pdf'), 
#                                         reply_markup = await kb.default_keyboard_builder(
#                                             text = ['✅Соглашаюсь','❌Не соглашаюсь'], 
#                                             callback_data = ['agree', 'disagree']
#                                         ), 
#                                         caption = 'Для начала рекомендуется установить двухэтапную аутентификацию (<b>облачный пароль</b>) в настройках.\n\nВы согласны на обработку персональных данных?', 
#                                         protect_content = True, parse_mode = 'HTML'
#                                     )
#     else: await message.answer('Вы уже подключили услугу.')
# # обработка ввода с клавиатуры пользователя и нажатие кнопок
# @router.message(MessageMatch(['оформить предварительный заказ', 'оформить заказ', 'оформить заявку', 'оформить предварительную заявку']))
# async def researches_or_services(message: Message) -> None:
#     await message.answer('Исследования или медицинские услуги?\nДля поиска необходимо отправить примерное наименование исследования/услуги.', 
#                             reply_markup = await kb.default_keyboard_builder(
#                                     text = ['💉Исследования', '🧑‍⚕️Медицинские услуги', '🛍️Акции', '⏪Покинуть меню'], 
#                                     callback_data = ['researches', 'services', 'actions', 'exit_or_exit'], sizes = 1
#                             )
#                         )
# # обработка ввода с клавиатуры пользователя
# @router.message(MessageMatch(['исследования', 'сдать анализы', 'исследование', 'сдать анализ', 'пройти исследование']))
# async def researches_categories(message: Message) -> None:
#     await message.answer('💉Иcследования\nВыберите категорию:', 
#                             reply_markup = await kb.research_categories(message.from_user.id)
#                         )
# # обработка ввода с клавиатуры пользователя
# @router.message(MessageMatch(['медицинские услуги', 'услуги', 'медуслуги', 'мед услуги', 'мед. услуги', 'медицинская услуга', 'услуга', 'медуслуга', 'мед. услуга', 'мед услуга']))
# async def services_categories(message: Message) -> None:
#     await message.answer('Выберите категорию:', 
#                             reply_markup = await kb.service_categories(message.from_user.id)
#                         )
# # обработка ввода с клавиатуры пользователя и нажатие кнопок
# @router.message(MessageMatch(['помощь', 'help', 'помоги', 'помогите']))
# async def cmd_help(message: Message) -> None:
#     user, phone = await request.set_user(message.from_user.id)
#     if phone  ==  True:
#     # доставать данные, если пациент подключен, т.е. ему приходят результаты анализов в телеграм, то отправлять одно сообщение, такое как сейчас
#         await message.answer('''*_Вы авторизованы и подключены к боту\._*\nКогда результаты анализов будут готовы, вы получите их в этом чате\.
# Если анализов несколько, результаты будут доставлены по мере их готовности\.\n
# Для повторного запроса результата исследований нажмите *"История заказов"*\.\n
# Если вы больше не хотите получать результаты исследований в Telegram, нажмите *"Отключиться от услуги"*\.''', 
# parse_mode = 'MarkdownV2', reply_markup = help_button)
#     else:
#         await message.answer('''*_Вы не авторизованы\._*\n
# Если вы хотите получать результаты исследований в Telegram, нажмите *"Подключить получение результатов"*\.''', 
# parse_mode = 'MarkdownV2', reply_markup = help_button)
# # обработка ввода с клавиатуры пользователя и нажатие кнопок
# @router.message(MessageMatch(['отключиться от услуги', 'отключить услугу', 'отключиться', 'отключить']))
# async def exit_button(message: Message) -> None:
#     disconnect = await request.disconnect_user(message.from_user.id)
#     if disconnect:
#         await message.answer('Вы отключились от услуги.', 
#                                 reply_markup = await kb.default_keyboard_builder(
#                                     text = ['📝Оформить предварительный заказ','🛒Корзина','🧾Заказы','⚙️Помощь','🆕Подключить получение результатов'],
#                                     sizes = [1,2,1,1],
#                                     input_field_placeholder = 'Выберите пункт меню...',
#                                     resize_keyboard = True
#                                 )
#                             )
#     else: await message.answer('Ошибка! Вы не были подключены к услуге.', 
#                                 reply_markup = await kb.default_keyboard_builder(
#                                     text = ['📝Оформить предварительный заказ','🛒Корзина','🧾Заказы','⚙️Помощь','🆕Подключить получение результатов'],
#                                     sizes = [1,2,1,1],
#                                     input_field_placeholder = 'Выберите пункт меню...',
#                                     resize_keyboard = True
#                                 )
#                             )
# # обработка ввода с клавиатуры пользователя и нажатие кнопок
# @router.message(MessageMatch(['корзина', 'корзинка', 'cart']))
# async def cart(message: Message) -> None:
#     # cart = await request.get_cart(message.from_user.id)
#     out_text, keyboard = await kb.get_cart_buttons(message.from_user.id, message_cart = True)
#     if keyboard:
#         await message.answer(f'<b>Ваш заказ:</b>\n{out_text}', parse_mode = 'HTML', reply_markup = keyboard)
#     else:
#         await message.answer('<i><b>Корзина пуста.</b></i>\n\nЧтобы добавить исследование или медицинскую услугу в корзину, нажмите кнопку в меню <b>"Оформить предварительный заказ"</b>.',
#                                 parse_mode = 'HTML'
#                             )

# # обработка ввода с клавиатуры пользователя и нажатие кнопок (выводит список заказов)
# @router.message(MessageMatch(['посмотреть заказ','мой заказ','заказы','мои заказы', 'история заказов']))
# async def orders(message: MessageMatch) -> None:
#     page = 1
#     count, orders_dict = await kb.orders(message.from_user.id)
#     if orders_dict:
#         pages_count = len(orders_dict)
#         keyboards = await orders_pagination(orders_dict, int(page), int(pages_count))
#         if count  ==  1: t = 'Ваш заказ'
#         else: t = 'Ваши заказы'
#         await message.answer(f'{t} ({count}):', reply_markup = keyboards)
#     else: await message.answer(f'''Вы пока не оформляли заказы.\n
# Чтобы оформить заказ, вам необходимо нажать на кнопку <b>"Оформить предварительный заказ"</b>, либо <b>"Корзина"</b>.''', 
# parse_mode = 'HTML')

# @router.callback_query(F.data.startswith('orders_page'))
# async def orders_pages(callback: CallbackQuery) -> None:
#     ppages = callback.data.split('&')[1]
#     pages_count = ppages.split('#')[0]
#     page = ppages.split('#')[1]
#     orders_dict = await kb.orders(callback.from_user.id, True)
#     keyboards = await orders_pagination(orders_dict, int(page), int(pages_count))
#     await callback.message.edit_reply_markup(reply_markup = keyboards)
    
# async def orders_pagination(data, page, page_count):
#     buttons = []
#     # cat_id = data[page][1][2]
#     # subcat_id = data[page][1][3]
#     for data_page in data[page]:
#         name_button = [
#             InlineKeyboardButton(text = f'№{data_page[1]} ({data_page[2].date().strftime("%d.%m.%Y")})', callback_data = f'order-{data_page[0]}#{page_count}_{page}') # #{item.ResearchCategoryID}#{item.ResearchSubcategoryID}
#         ]
#         buttons.append(name_button)
    
#     bottom_buttons = []
#     if page !=  1:
#         bottom_buttons.append(InlineKeyboardButton(text = f'⬅️', callback_data = f'orders_page&{page_count}#{page-1}'))
#     else:
#         bottom_buttons.append(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'orders_stop_back'))
        
#     bottom_buttons.append(InlineKeyboardButton(text = f'{page}/{page_count}', callback_data = f'back_proxy_type#{page}'))
    
#     if page  ==  page_count:
#         bottom_buttons.append(InlineKeyboardButton(text = f'⛔️', callback_data = f'stop_stop'))
#     else:
#         bottom_buttons.append(InlineKeyboardButton(text = f'➡️', callback_data = f'orders_page&{page_count}#{page+1}'))
        
#     buttons.append(bottom_buttons)
#     if page > 1:
#         buttons.append([
#             InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'orders_stop_back')
#         ])
    
#     keyboard = InlineKeyboardMarkup(row_width = 1, inline_keyboard = buttons)
#     return keyboard

# @router.callback_query(F.data.startswith('order-'))
# async def order(callback: CallbackQuery):
#     await callback.answer()
#     data = callback.data.split('#')
#     order_id = data[0].split('-')[1]
#     ppages = data[1].split('_')
#     pages_count = ppages[0]
#     page = ppages[1]
#     text, keyboards = await kb.order_data(callback.from_user.id, order_id, pages_count, page)
#     await callback.message.edit_text(f'{text}', parse_mode = 'HTML')
#     await callback.message.edit_reply_markup(reply_markup = keyboards)
    
# @router.callback_query(F.data.startswith('order_back_to_pagination'))
# async def order_back_to_pagination(callback: CallbackQuery):
#     await callback.answer()
#     data = callback.data.split('&')
#     ppages = data[1].split('#')
#     pages_count = ppages[0]
#     page = ppages[1]
#     count, orders_dict = await kb.orders(callback.from_user.id)
#     keyboards = await orders_pagination(orders_dict, int(page), int(pages_count))
#     if count  ==  1: t = 'Ваш заказ'
#     else: t = 'Ваши заказы'
#     await callback.message.edit_text(f'{t} ({count}):')
#     await callback.message.edit_reply_markup(reply_markup = keyboards)


# ПОИСК
# @router.callback_query(kb.Pagination.filter(F.action.in_(['prev', 'next'])))
# async def paginator_handler(callback: CallbackQuery, callback_data: kb.Pagination):
#     lresearches, lservices = await request.get_search(callback.from_user.id, callback_data.query)
#     if not bool(callback_data.many):
#         search_list = []
#         if lresearches and lservices:
#             all_list = lresearches + lservices
#             search_list = all_list
#         elif not lresearches and lservices:
#             search_list = lservices
#         elif not lservices and lresearches:
#             search_list = lresearches
#     else:
#         search_list, all_pages = get_ress(lresearches, lservices)
    
#     page_num = int(callback_data.page)
#     page = page_num - 1 if page_num > 1 else 1
#     if callback_data.action  ==  'next':
#         page = page_num + 1 if page_num < int(callback_data.all_pages) else page_num
    
#     with suppress(TelegramBadRequest):
#         if not bool(callback_data.many):
#             if '*' in search_list[page-1][1]:
#                 name = search_list[page-1][1].replace('*', '"')
#             else: name = search_list[page-1][1]
#             cost = kb.get_formating_cost(search_list[page-1][2])
#             await callback.message.edit_text(
#                 f'<b>Наименование:</b> {name}.\n\n<b>Цена:</b> {cost} ₽',
#                 reply_markup = kb.paginator(callback_data.query, callback_data.all_pages, page = page, item_id = search_list[page-1][0], what_is = search_list[page-1][3]),
#                 parse_mode = 'HTML'
#             )
#         else:
#             s = '\n\n'.join(search_list[page-1])
#             await callback.message.edit_text(f'{s}', parse_mode = 'HTML', reply_markup = kb.paginator(callback_data.query, all_pages, page = page, many = True))
#         await callback.answer()

# @router.message(F.text.regexp(r'^\D+([а-яА-я]+\s*\d*){,15}'))
# async def search(message: Message):
#     await message.answer('Поиск...')
#     if '"' in message.text: search_text = message.text.replace('"','*')
#     else: search_text = message.text
#     # await message.answer_sticker('CAACAgEAAxkBAAIT4GYf05AoknhZGHsUaQgdKNvAIz7bAAIDCgACv4yQBJGkR4JOgqlxNAQ')
#     lresearches, lservices = await request.get_search(message.from_user.id, search_text)
#     res_count = len(lresearches)+len(lservices)
#     if res_count <=  8:
#         if res_count  ==  1: await message.answer(f'Найден {res_count} результат по запросу:\n<i>{message.text}</i>.', parse_mode = 'HTML')
#         elif res_count < 5: await message.answer(f'Найдено {res_count} результата по запросу:\n<i>{message.text}</i>.', parse_mode = 'HTML')
#         else: await message.answer(f'Найдено {res_count} результатов по запросу:\n<i>{message.text}</i>.', parse_mode = 'HTML')
#         if len(message.text)>20: res_text = message.text[:20]
#         else: res_text = message.text
#         print(f'>>> Сликом большой текст - {message.text} -------> {res_text}')
#         if lresearches and lservices:
#             all_list = lresearches + lservices
#             if '*' in all_list[0][1]:
#                 name = all_list[0][1].replace('*', '"')
#             else: name = all_list[0][1]
#             cost = kb.get_formating_cost(all_list[0][2])
#             await message.answer(f'<b>Наименование:</b> {name}.\n\n<b>Цена:</b> {cost} ₽', 
#                                 parse_mode = 'HTML', reply_markup = kb.paginator(res_text, res_count, item_id = all_list[0][0], what_is = all_list[0][3]))
#         elif not lresearches and lservices:
#             if '*' in lservices[0][1]:
#                 name = lservices[0][1].replace('*', '"')
#             else: name = lservices[0][1]
#             cost = kb.get_formating_cost(lservices[0][2])
#             await message.answer(f'<b>Наименование:</b> {name}.\n\n<b>Цена:</b> {cost} ₽', 
#                                 parse_mode = 'HTML', reply_markup = kb.paginator(res_text, res_count, item_id = lservices[0][0], what_is = lservices[0][3]))
#         elif not lservices and lresearches:
#             if '*' in lresearches[0][1]:
#                 name = lresearches[0][1].replace('*', '"')
#             else: name = lresearches[0][1]
#             cost = kb.get_formating_cost(lresearches[0][2])
#             await message.answer(f'<b>Наименование:</b> {name}.\n\n<b>Цена:</b> {cost} ₽', 
#                                 parse_mode = 'HTML', reply_markup = kb.paginator(res_text, res_count, item_id = lresearches[0][0], what_is = lresearches[0][3]))
#     else:
#         ress, all_pages = get_ress(lresearches, lservices)
#         s = '\n\n'.join(ress[0])
#         await message.answer(f'Найдено cлишком много результатов ({res_count}) по запросу:\n<i>{message.text}</i>.\n\n<b>Нажмите</b> на наименование и отправьте в этот чат.', parse_mode = 'HTML')
#         if all_pages > 1:
#             await message.answer(f'{s}', parse_mode = 'HTML', reply_markup = kb.paginator(message.text, all_pages, many = True))
#         else: await message.answer(f'{s}', parse_mode = 'HTML')
# # если результатов больше 8
# def get_ress(lresearches, lservices, need_pages = False):
#     text = []
#     if lresearches and lservices:
#         all_list = lresearches + lservices
#         for item in all_list:
#             if '*' in item[1]: item[1] = item[1].replace('*','"')
#             text.append(f'🔎 <code>{item[1]}</code>')
#     elif not lresearches and lservices:
#         for item in lservices:
#             if '*' in item[1]: item[1] = item[1].replace('*','"')
#             text.append(f'🔎 <code>{item[1]}</code>')
#     elif not lservices and lresearches:
#         for item in lresearches:
#             if '*' in item[1]: item[1] = item[1].replace('*','"')
#             text.append(f'🔎 <code>{item[1]}</code>')
#     all_pages = ceil(len(text)/12)
#     print('>>> Количество страниц ', all_pages)
#     split = lambda lst, n: [lst[i::n] for i in range(n)]
#     ress = split(text, all_pages)
#     return ress, all_pages

# @router.callback_query(F.data.startswith('notice_button_action'))
# async def notice_actions(callback: CallbackQuery):
#     await callback.answer()
#     notice_action_id = callback.data.split('#')[1].split('/')[0]
#     city_id = await request.get_city_id(callback.from_user.id)
#     action = await request.get_research_data(int(notice_action_id))
#     if len(action.Name)>20: res_text = action.Name[:20]
#     else: res_text = action.Name
#     price = await request.get_research_price(action.ID, city_id)
#     cost = kb.get_formating_cost(price.Cost)
#     await callback.message.answer(f'<b>Наименование:</b> {action.Name}.\n\n<b>Цена:</b> {cost} ₽', 
#                                 parse_mode = 'HTML', reply_markup = kb.paginator(res_text, 1, item_id = action.ID, what_is = 'research'))
    
    
