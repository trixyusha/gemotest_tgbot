from typing import List
import re

from aiogram.filters import BaseFilter
from aiogram.types import Message

class MessageMatch(BaseFilter):
    
    def __init__(self, texts: List[str]) -> None:
        self.texts=texts
    
    async def __call__(self, message: Message) -> bool:
        if not message.text[1:] in ['cart', 'help']:
            if bool(re.search(r'[a-zA-Z]', message.text)):
                print('Пользователь не переключил раскладку или пишет на английском языке, или что-то другое...')
                return False
        if not any(char.isdigit() for char in message.text):
            if message.text[0].isalpha():
                    return message.text.lower() in self.texts
            if message.text[1].isalpha():
                    return message.text[1:].lower() in self.texts
            if message.text[2].isalpha():
                    return message.text[2:].lower() in self.texts
            return False
        else: 
            print('Некорректный ввод сообщения пользователем!')
            return False