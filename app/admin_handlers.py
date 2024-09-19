from datetime import datetime
import matplotlib.pyplot as plt 

from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile as send_file
from aiogram.types.input_file import BufferedInputFile as send_buffer

from app.handlers_user.main_handlers import router
from app.keyboards_user.default_keyboard import default_keyboard_builder
from app.database.requests.main_requests import get_QR_code
from app.filters.block_unblock import BlockUnblock
from .database.admin_requests import admin_requests

import app.keyboards_admin.reply.reply_keyboards as admin_reply
import app.keyboards_admin.inline.inline_keyboards as admin_inline

admin_router = Router()

async def get_user_filter():
    user_ids = [i for i in await admin_requests.get_nonadmin_ids()]
    # router.message.filter(F.from_user.id.in_(user_ids))
    admin_router.message.filter(F.from_user.id.not_in(user_ids))
    print('>>> ТГ идентификаторы пользователей: ', user_ids)

async def get_admin_filter():
    admin_ids = [i for i in await admin_requests.get_admin_ids()]
    # admin_router.message.filter(F.from_user.id.in_(admin_ids))
    router.message.filter(F.from_user.id.not_in(admin_ids))
    print('>>> ТГ идентификаторы админов: ', admin_ids)


class BlockOrUnblock(StatesGroup):
    block = State()
    unblock = State()
    continue_ub = State()
    exit_ub = State()
    continue_b = State()
    exit_b = State()
    

class GetButtonToUser(StatesGroup):
    userid = State()


@admin_router.message(Command('get_qrcode'))
async def get_qrcode(message: Message):
    boooool, buuuff = await get_QR_code(message.from_user.id)
    await message.answer_photo(photo = send_buffer(buuuff.getvalue(), f'qrcode_{message.from_user.id}.png'))


# @admin_router.message(F.sticker)
# async def get_id_sticker(message: Message):
#     await message.answer(message.sticker.file_id)

@admin_router.message(CommandStart())
async def admin_start(message: Message):
    await message.answer_sticker('CAACAgIAAxkBAAIT3mYf01XVD-RfXekmBvVc5DePbNV7AALZLQACsuHZSX9zLhCmtLzqNAQ')
    await message.answer('Админ панель в твоем распоряжении!', reply_markup = admin_reply.main)


# ЧЕРНЫЙ СПИСОК
@admin_router.message(F.text == 'Черный список')
async def black_list(message: Message):
    await message.answer('Манипуляции с черным списком', reply_markup = admin_inline.black_list)

@admin_router.callback_query(F.data == 'black_list')
async def get_black_list(call: CallbackQuery):
    users_tg_ids = await admin_requests.get_all_users_ids(True)
    text = ''
    i = 0
    for user_tg_id in users_tg_ids:
        if i == 0:
            text = text+f'\n<code>{user_tg_id}</code>'
            i = 1
        else: text = text+f', <code>{user_tg_id}</code>'
    await call.message.edit_reply_markup(reply_markup = None)
    await call.message.edit_text(f'Список идентификаторов пользователей <b>в блоке</b>: {text}', parse_mode = 'HTML')

@admin_router.callback_query(F.data.in_(['block_user', 'continue_b']))
async def block_user(call: CallbackQuery, state: FSMContext):
    # выводить список идентификаторов всех пользователей
    users_tg_ids = await admin_requests.get_all_users_ids(False)
    text = ''
    i = 0
    for user_tg_id in users_tg_ids:
        if i == 0:
            text = text+f'\n<code>{user_tg_id}</code>'
            i = 1
        else: text = text+f', <code>{user_tg_id}</code>'
    await state.set_state(BlockOrUnblock.block)
    await call.message.edit_reply_markup(reply_markup = None)
    await call.message.edit_text(f'''Чтобы <b>заблокировать</b> пользователя, нажми на идентификатор и отправь в этот чат⬇️.
Список идентификаторов пользователей <b>не в блоке</b>: {text}''', parse_mode = 'HTML')

@admin_router.callback_query(F.data.in_(['unblock_user', 'continue_ub']))
async def unblock_user(call: CallbackQuery, state: FSMContext):
    all_users_tg_ids = await admin_requests.get_all_users_ids(True)
    text = ''
    i = 0
    for user_tg_id in all_users_tg_ids:
        if i == 0:
            text = text+f'\n<code>{user_tg_id}</code>'
            i = 1
        else: text = text+f', <code>{user_tg_id}</code>'
    await state.set_state(BlockOrUnblock.unblock)
    await call.message.edit_reply_markup(reply_markup = None)
    await call.message.edit_text(f'''Чтобы <b>разблокировать</b> пользователя, нажми на идентификатор и отправь в этот чат⬇️.
Список идентификаторов пользователей <b>в блоке</b>: {text}''', parse_mode = 'HTML')

@admin_router.message(BlockOrUnblock.block, BlockUnblock(True))
async def get_block_user(state: FSMContext):
    await state.clear()
@admin_router.message(BlockOrUnblock.unblock, BlockUnblock(False))
async def get_unblock_user(state: FSMContext):
    await state.clear()

@admin_router.callback_query(F.data.startswith('exit'))
async def exit_block(call: CallbackQuery):
    await call.answer()
    await call.message.edit_reply_markup(reply_markup = None)


    
# СТАТИСТИКА
@admin_router.message(F.text == 'Статистика')
async def stats(message: Message):
    await message.answer('Что тебя интересует?', reply_markup = admin_inline.stats)
# какие отчеты необходимы (количество пользвоателей, количество оформленных заказов (и сумма), количество новых пользователей) 
# фильтрация по городам
# какие исследования заказывают чаще??? 
# средний чек???

@admin_router.callback_query(F.data == 'users_count')
async def users_count(call: CallbackQuery):
    await call.answer('Статистика/Пользователи')
    await call.message.edit_text('Какие пользователи?')
    await call.message.edit_reply_markup(reply_markup = admin_inline.stats_users)
    
@admin_router.callback_query(F.data.startswith('users_'))
async def users_(call: CallbackQuery):
    await call.answer('Статистика/Пользователи')
    if 'all' in call.data:
        result = await admin_requests.count_of_users(False)
        await call.message.edit_reply_markup(reply_markup = None)
        await call.message.edit_text(result)
    else:
        await call.message.edit_text('Количество новых пользователей за период:')
        await call.message.edit_reply_markup(reply_markup = await admin_inline.get_period_buttons('users'))
        
@admin_router.callback_query(F.data.startswith('pusers'))
async def users_period(call: CallbackQuery):
    await call.answer('Статистика/Новые пользователи')
    if call.data.split('#')[1] == '0':
        result = await admin_requests.count_of_users(True, 0)
    elif call.data.split('#')[1] == '1':
        result = await admin_requests.count_of_users(True, 1)
    else:
        result = await admin_requests.count_of_users(True, 2)
    await call.message.edit_reply_markup(reply_markup = None)
    await call.message.edit_text(result)

@admin_router.callback_query(F.data == 'orderds_count')
async def orderds_count(call: CallbackQuery):
    await call.answer('Статистика/Заказы')
    await call.message.edit_text('Количество заказов за период:')
    await call.message.edit_reply_markup(reply_markup = await admin_inline.get_period_buttons('orders'))
    
@admin_router.callback_query(F.data.startswith('porders'))
async def orders_period(call: CallbackQuery):
    await call.answer('Статистика/Заказы')
    if call.data.split('#')[1] == '0':
        keyboard = await default_keyboard_builder(
            text = ['Неделя','Месяц','Год','Выйти'],
            callback_data = ['porders#1','porders#2','porders#3','exit'],
            sizes = 1
        )
        result, path = await get_count_of_orders(0)
        print(len(path))
    elif call.data.split('#')[1] == '1':
        keyboard = await default_keyboard_builder(
            text = ['Сегодня','Месяц','Год','Выйти'],
            callback_data = ['porders#0','porders#2','porders#3','exit'],
            sizes = 1
        )
        result, path = await get_count_of_orders(1)
    elif call.data.split('#')[1] == '2':
        keyboard = await default_keyboard_builder(
            text = ['Сегодня','Неделя','Год','Выйти'],
            callback_data = ['porders#0','porders#1','porders#3','exit'],
            sizes = 1
        )
        result, path = await get_count_of_orders(2)
    else:
        keyboard = await default_keyboard_builder(
            text = ['Сегодня','Неделя','Месяц','Выйти'],
            callback_data = ['porders#0','porders#1','porders#2','exit'],
            sizes = 1
        )
        result, path = await get_count_of_orders(3)
    if len(path) > 0:
        await call.message.delete()
        await call.message.answer_photo(photo = send_file(path), caption = result, reply_markup = keyboard)
    else:
        # await call.message.edit_reply_markup(reply_markup = None)
        await call.message.delete()
        await call.message.answer(result, reply_markup = keyboard)

@admin_router.callback_query(F.data == 'top')
async def top(call: CallbackQuery):
    await call.answer()
    text = await admin_requests.get_top()
    await call.message.edit_reply_markup(reply_markup = None)
    await call.message.edit_text(f'Топ услуг:\n{text}')


@admin_router.message(F.text.lower()  ==  'перейти к пользователю')
async def get_to_user(msg: Message, state: FSMContext):
    await state.set_state(GetButtonToUser.userid)
    user_ids  = ['<code>'+str(user_id)+'</code>' for user_id in  await admin_requests.get_nonadmin_ids()]
    await msg.answer(f'Отправь идентификатор пользователя👇\n\n{", ".join(user_ids)}', parse_mode = 'HTML')
    
@admin_router.message(GetButtonToUser.userid, F.text.regexp(r'\d+'))
async def send_id(msg: Message, state: FSMContext):
    await state.update_data(userid = int(msg.text))
    user_id = await state.get_data()
    await msg.answer(f'Нажми на кнопку, чтобы перейти к аккаунту пользователя', 
                        reply_markup = await admin_inline.get_button(user_id['userid'])
                    )
    await state.clear()
    
@admin_router.message(F.text.lower()  ==  'напомнить об акциях')
async def notice_actions(msg: Message, bot: Bot):
    user_ids = await admin_requests.get_nonadmin_ids()
    # user_ids = [6072250641]
    list_of_ids = []
    actions = ['Витамин D (витамин солнца)','Биохимия 8 показателей','Комплексное исследование на клещевые инфекции: боррелиоз, клещевой энцефалит, эрлихиоз, анаплазмоз (ПЦР, один клещ, кач.)']
    for user_id in user_ids:
        list_of_ids.append(f'<code>{user_id}</code>')
        await bot.send_photo(chat_id = user_id, photo = 'https://www.rbgmedia.ru/news/store/postphoto/post-20200402-153113.jpg', 
caption = '<b>Лучшие предложения апреля</b>\n\nВ апреле природа освобождается ото льда и снега: появляется первая зелень, оттаивают жучки-бабочки, а тёплый весенний ветер навевает мысли о великих подвигах и свершениях. Убедитесь, что исполнению ваших планов ничто не помешает, — проверьте здоровье!',
reply_markup = await admin_inline.get_notice_buttons(user_id, actions), parse_mode = 'HTML')
    await msg.answer(f'<b>Успех.</b>\nСледующие пользователи получили напоминание: {", ".join(list_of_ids)}', parse_mode = 'HTML')
    
    
    
    
async def get_count_of_orders(period):
    text = ''
    
    if period == 0:
        path, count = await get_graph(period, '')
        text = f'Заказов за сегодня: {count}'
    elif period == 1:
        path, count = await get_graph(period, 'Количество заказов за неделю')
        text = f'Общее число заказов за неделю: {count}'
    elif period == 2:
        path, count = await get_graph(period, 'Количество заказов за месяц')
        text = f'Общее число заказов за месяц: {count}'
    else:
        path, count = await get_graph(period, 'Количество заказов за год')
        text = f'Общее число заказов за год: {count}'
    return text, path

async def get_graph(period, title):
    path = ''
    count, regdates = await admin_requests.count_of_orders(period)
    if period > 0:
        dates = [date.date() for date in regdates]
        alldata = list(set([(date, dates.count(date)) for date in dates]))
        dated = [date[0] for date in alldata]
        datec = [date[1] for date in alldata]
        if period  !=  1:
            plt.figure(figsize = (12,8))
        else: plt.figure(figsize = (8,6))
        plt.minorticks_on()
        plt.grid(which = 'major')
        plt.grid(which = 'minor', linestyle = ':')
        plt.bar(dated, datec)
        plt.title(title)
        plt.xlabel('Дата')
        plt.ylabel('Количество')
        plt.tight_layout()
        path = f'graphs/{datetime.today().date()}.png'
        plt.savefig(path)
    return path, count
