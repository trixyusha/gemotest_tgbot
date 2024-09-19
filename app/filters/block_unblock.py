import re

from aiogram.types import Message
from aiogram.filters import BaseFilter

from app.keyboards_admin.inline.inline_keyboards import contin
from app.database.admin_requests.admin_requests import block_or_unblock_user

class BlockUnblock(BaseFilter):
    
    def __init__(self, block: bool) -> None:
        self.block=block
    
    async def __call__(self, message: Message) -> bool:
        if self.block:
            txts='заблокированы'
            txt='заблокирован'
        else:
            txts='разблокированы'
            txt='разблокирован'
        if bool(re.findall(r'\W|\s|_', message.text)):
            ids=re.findall(r'\d+', message.text)
            i=0
            tg_ids=[]
            other_tg_ids=[]
            for tg_id in ids:
                if await block_or_unblock_user(int(tg_id), self.block):
                    tg_ids.append(tg_id)
                else:
                    other_tg_ids.append(tg_id)
                    # await message.answer(f'Пользователь с идентификатором {tg_id} не пользуется @GemotestLaboratory_Bot.')
            if len(tg_ids)>1:
                str_ids=', '.join(tg_ids)
                await message.answer(f'Пользователи с идентификаторами: <code>{str_ids}</code> успешно {txts}.', parse_mode='HTML', reply_markup=await contin(self.block))
            elif len(tg_ids)==1: 
                str_ids=str(tg_ids[0])
                await message.answer(f'Пользователь с идентификатором <code>{str_ids}</code> успешно {txt}.', parse_mode='HTML', reply_markup=await contin(self.block))
            if len(other_tg_ids)>1:
                str_ids=', '.join(other_tg_ids)
                await message.answer(f'Пользователи с идентификаторами: <code>{str_ids}</code> не пользуются @GemotestLaboratory_Bot.', parse_mode='HTML', reply_markup=await contin(self.block))
            elif len(other_tg_ids)==1: 
                str_ids=str(other_tg_ids[0])
                await message.answer(f'Пользователь с идентификатором <code>{str_ids}</code> не пользуется @GemotestLaboratory_Bot.', parse_mode='HTML', reply_markup=await contin(self.block))
        elif bool(re.findall(r'\d+', message.text)):
            tg_id=re.findall(r'\d+', message.text)
            if await block_or_unblock_user(int(tg_id[0]), self.block):
                await message.answer(f'Пользователь с идентификатором <code>{message.text}</code> успешно {txt}.', parse_mode='HTML', reply_markup=await contin(self.block))
            else:
                await message.answer(f'Пользователь с идентификатором <code>{message.text}</code> не пользуется @GemotestLaboratory_Bot.', parse_mode='HTML', reply_markup=await contin(self.block))
