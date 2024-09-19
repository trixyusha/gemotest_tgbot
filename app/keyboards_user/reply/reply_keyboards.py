from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



cart = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = '🛒Корзина')]],
                            resize_keyboard = True
                        )

contin = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = 'Продолжить')]],
                            resize_keyboard = True,
                            input_field_placeholder = 'Прочтите инструкцию!'
                        )


