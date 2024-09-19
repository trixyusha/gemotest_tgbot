from typing import Callable, Awaitable, Dict, Any

from aiogram.types import Message
from aiogram import BaseMiddleware

from app.database.admin_requests.admin_requests import get_admin_ids
from app.admin_handlers import get_admin_filter, get_user_filter


class CheckAdmin(BaseMiddleware):
        
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any], 
    ) -> Any:
        admin_id = message.from_user.id
        await get_admin_filter()
        await get_user_filter()
        if admin_id in [a_id for a_id in await get_admin_ids()]:
            print(f'>>> INFO CHECK_ADMIN -> 🟢')
            return await handler(message, data)
        else: 
            print(f'>>> INFO CHECK_ADMIN -> 🔴\n>>> Пользователь ({message.from_user.full_name}) - {message.from_user.id}')
            return await handler(message, data)
