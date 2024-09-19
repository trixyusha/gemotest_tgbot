from aiogram import F
from aiogram.types import CallbackQuery
from main_handlers import router
from app.keyboards_user.inline.telemed_keyboard import get_telemed_buttons



@router.callback_query(F.data.startswith('telemed-category'))
async def get_telemed(callback: CallbackQuery):
    await callback.answer()
    cat_name = 'Телемедицина'
    await callback.message.answer(f'''Категория: <b>{cat_name}</b>
Доступные специалисты (чтобы узнать более подробную информацию, нажмите на интересующую специальность врача, вас перенаправит на сайт):''',
reply_markup = await get_telemed_buttons(),
parse_mode = 'HTML')
