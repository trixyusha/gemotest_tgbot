from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.requests.main_requests import get_search



black_list = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text = 'Заблокировать', callback_data = 'block_user')],
    [InlineKeyboardButton(text = 'Разблокировать', callback_data = 'unblock_user')],
])

stats = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text = 'Количество пользователей', callback_data = 'users_count')],
    [InlineKeyboardButton(text = 'Количество заказов', callback_data = 'orderds_count')],
    [InlineKeyboardButton(text = 'Топ услуг', callback_data = 'top')],
    # [InlineKeyboardButton(text = '', callback_data = '')],
])

stats_users = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text = 'Новые', callback_data = 'users_new_count')],
    [InlineKeyboardButton(text = 'Все', callback_data = 'users_all_count')],
    [InlineKeyboardButton(text = 'Назад', callback_data = 'back_to_stats')],
])

help_button = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text = 'Поддержка', url = 't.me/m/D2BiL8rWNzZi')] # t.me/m/D2BiL8rWNzZi tg://resolve?domain = lilshanya
])

async def get_button(userid):
    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text = 'Перейти', url = f'tg://user?id = {userid}'))
    return button.as_markup()

async def get_notice_buttons(user_id, actions_list):
    keyboard = InlineKeyboardBuilder()
    for action in actions_list:
        result = await get_search(user_id, action, True)
        keyboard.add(InlineKeyboardButton(text = f'{action}', callback_data = f'notice_button_action#{result[0][0]}'))
    keyboard.add(InlineKeyboardButton(text = '🛍️Все акции', callback_data = 'notice_actions'))
    return keyboard.adjust(1).as_markup()

async def get_period_buttons(stats):
    period = ['Сегодня', 'Неделя', 'Месяц', 'Год']
    keyboard = InlineKeyboardBuilder()
    i = 0
    if stats == 'users':
        for p in period:
            if p != 'Год':
                keyboard.add(InlineKeyboardButton(text = p, callback_data = f'pusers#{i}'))
                i += 1
    if stats == 'orders':
        for p in period:
            keyboard.add(InlineKeyboardButton(text = p, callback_data = f'porders#{i}'))
            i += 1
    return keyboard.adjust(1).as_markup()

async def contin(block):
    keyboard = InlineKeyboardBuilder()
    if block:
        keyboard.add(InlineKeyboardButton(text = 'Продолжить', callback_data = 'continue_b'))
        keyboard.add(InlineKeyboardButton(text = 'Выйти', callback_data = 'exit_b'))
        # keyboard.row(
        #     [InlineKeyboardButton(text = 'Продолжить', callback_data = 'continue_b')],
        #     [InlineKeyboardButton(text = 'Выйти', callback_data = 'exit_b')],
        #     width = 2
        # )
    else:
        keyboard.add(InlineKeyboardButton(text = 'Продолжить', callback_data = 'continue_ub'))
        keyboard.add(InlineKeyboardButton(text = 'Выйти', callback_data = 'exit_ub'))
        # keyboard.row(
        #     [InlineKeyboardButton(text = 'Продолжить', callback_data = 'continue_ub')],
        #     [InlineKeyboardButton(text = 'Выйти', callback_data = 'exit_ub')],
        #     width = 2
        # )
    return keyboard.adjust(2).as_markup()
