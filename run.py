import os
from dotenv import load_dotenv

import sys
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeAllPrivateChats

from app.middelwares.check_ban import CheckBan
from app.middelwares.check_admin import CheckAdmin
from app.admin_handlers import admin_router
from app.handlers_user.main_handlers import router
from common.bot_cmds_list import users_commands
from app.database.models import async_main


async def main():
    await async_main()
    load_dotenv()
    bot = Bot(token = os.getenv('TOKEN'))
    dp = Dispatcher()
    
    dp.message.outer_middleware(CheckAdmin())
    dp.message.middleware(CheckBan())
    
    dp.include_routers(router, admin_router)
    
    await bot.delete_webhook(drop_pending_updates = True)
    await bot.set_my_commands(commands = users_commands, scope = BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('EXIT')
