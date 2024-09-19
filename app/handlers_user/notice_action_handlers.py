from aiogram import F
from main_handlers import router
from aiogram.types import CallbackQuery
from app.database.requests.city_requests import get_city_id
from app.keyboards_user.inline.text_pagination_keyboard import paginator
from app.keyboards_user.inline.order_cart_keyboard import get_formating_cost
from app.database.requests.research_requests import get_research_data, get_research_price



@router.callback_query(F.data.startswith('notice_button_action'))
async def notice_actions(callback: CallbackQuery):
    await callback.answer()
    notice_action_id = callback.data.split('#')[1].split('/')[0]
    city_id = await get_city_id(callback.from_user.id)
    action = await get_research_data(int(notice_action_id))
    if len(action.Name)>20: res_text = action.Name[:20]
    else: res_text = action.Name
    price = await get_research_price(action.ID, city_id)
    cost = get_formating_cost(price.Cost)
    await callback.message.answer(f'<b>Наименование:</b> {action.Name}.\n\n<b>Цена:</b> {cost} ₽', 
                                parse_mode = 'HTML', reply_markup = paginator(res_text, 1, item_id = action.ID, what_is = 'research'))
