from typing import Callable, Awaitable, Dict, Any

from aiogram.types import Message
from aiogram import BaseMiddleware

from app.keyboards_admin.inline.inline_keyboards import help_button
from app.database.admin_requests.admin_requests import get_all_users_ids

class CheckBan(BaseMiddleware):
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any] 
    ) -> Any:
        user_id = message.from_user.id

        if user_id in [u_id for u_id in await get_all_users_ids(True)]:
            print('>>> INFO CHECK_BAN -> в ЧС')
            await message.answer('Вы в черном списке, обратитесь в поддержку.', reply_markup=help_button)
        # elif user_id not in [u_id for u_id in await get_all_users_ids(None)]:
        #     print(f'>>> INFO CHECK_IS_USER -> это не пользователь бота (info: tg_id: {message.from_user.id}, name: {message.from_user.first_name})')
        #     await message.answer('Чтобы подключиться к боту, обратитесь в поддержку.', reply_markup=help_button)
        else:
            print('>>> INFO CHECK_BAN -> не в ЧС')
            return await handler(message, data)
