from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



main = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text = 'Статистика')],
    [KeyboardButton(text = 'Черный список'), KeyboardButton(text = 'Перейти к пользователю')],
    [KeyboardButton(text = 'Напомнить об акциях')],
], resize_keyboard = True, input_field_placeholder = 'Выбери пункт меню...')
