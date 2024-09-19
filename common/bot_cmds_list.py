from aiogram.types import BotCommand

users_commands = [
    BotCommand(command='start', description='Начать работу бота'),
    BotCommand(command='cart', description='Посмотреть, что в корзине'),
    BotCommand(command='researches', description='Посмотреть доступные исследования'),
    BotCommand(command='services', description='Посмотреть доступные медицинские услуги'),
    BotCommand(command='help', description='Помощь'),
    BotCommand(command='get_qrcode', description='Получить QR-код'),
    # BotCommand(),
]