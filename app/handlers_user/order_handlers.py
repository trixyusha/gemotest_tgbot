import random
from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
# from aiogram.types import FSInputFile as send_file
from app.functions import researches, services, actions
from aiogram.types.input_file import InputFile as send_file
from app.database.requests.order_requests import get_order_number
from app.keyboards_user.default_keyboard import default_keyboard_builder
from app.keyboards_user.inline.payment_keyboard import get_payment_buttons
from app.keyboards_user.inline.order_cart_keyboard import get_cart_buttons
from app.keyboards_user.inline.buttons_pagination_keyboard import pagination
from app.keyboards_user.inline.actions_keyboard import actions_categories, actions_subcategories, action_data
from app.keyboards_user.inline.services_keyboard import service_categories, service_subcategories, service_data
from app.keyboards_user.inline.researches_keyboard import research_categories, research_subcategories, research_data

from app.handlers_user.main_handlers import router

# оформление предварительного заказа, пользователь выбирает категорию (обработка нажатий на инлайн кнопки и команды)
@router.message(Command('researches', 'services'))
@router.callback_query(F.data.in_({'researches','services','actions', 'notice_actions'}))
async def categories(m_or_q: Message | CallbackQuery) -> None:
    if isinstance(m_or_q, Message):
        if m_or_q.text  ==  '/researches':
            await m_or_q.answer('💉Иcследования\nВыберите категорию:', reply_markup = await research_categories(m_or_q.from_user.id))
        elif m_or_q.text  ==  '/services':
            await m_or_q.answer('🧑‍⚕️Медицинские услуги\nВыберите категорию:', reply_markup = await service_categories(m_or_q.from_user.id))
    else:    
        if m_or_q.data[:-2]  ==  'research':
            await m_or_q.answer()
            await m_or_q.message.edit_text('💉Иcследования\nВыберите категорию:')
            await m_or_q.message.edit_reply_markup(reply_markup = await research_categories(m_or_q.from_user.id))
        elif m_or_q.data[:-1]  ==  'service':
            await m_or_q.answer()
            await m_or_q.message.edit_text('🧑‍⚕️Медицинские услуги\nВыберите категорию:')
            await m_or_q.message.edit_reply_markup(reply_markup = await service_categories(m_or_q.from_user.id))
        elif m_or_q.data[:-1]  ==  'action':
            await m_or_q.answer()
            await m_or_q.message.edit_text('🛍️Акции\nВыберите категорию:')
            await m_or_q.message.edit_reply_markup(reply_markup = await actions_categories())
        elif m_or_q.data  ==  'notice_actions':
            await m_or_q.answer()
            await m_or_q.message.answer('🛍️Акции\nВыберите категорию:', reply_markup = await actions_categories())

@router.callback_query(F.data.regexp(r'[resachviton]{6,8}-category_'))
async def subcategories(callback: CallbackQuery) -> None:
    await callback.answer()
    indx = callback.data.find('-')
    if callback.data[:indx]  ==  'research':
        cat_name, keyboard = await research_subcategories(int(callback.data.split('_')[1]), False, callback.from_user.id)
    elif callback.data[:indx]  ==  'service':
        cat_name, keyboard = await service_subcategories(int(callback.data.split('_')[1]), False, callback.from_user.id)
    elif callback.data[:indx]  ==  'action':
        cat_name, keyboard = await actions_subcategories(int(callback.data.split('_')[1]), False)
    await callback.message.edit_text(f'Категория: <b>{cat_name}</b>\nВыберите подкатегорию:', parse_mode = 'HTML')
    await callback.message.edit_reply_markup(reply_markup = keyboard)

# оформление предварительного заказа, пользователь выбирает 
# элемент из списка (ПАГИНАЦИЯ)
@router.callback_query(F.data.regexp(r'[resachviton]{6,8}-subcategory_'))
async def items(callback: CallbackQuery) -> None:
    await callback.answer()
    page = 1
    indx = callback.data.find('-')
    cat_name = callback.message.text[11:callback.message.text.find('\n')]
    if callback.data[:indx]  ==  'research':
        subcat_name, count, researches_dict = await researches(callback.data.split('_')[1], callback.from_user.id)
        pages_count = len(researches_dict)
        some_text = f'Исследований в подкатегории: {count}\n\nВыбрав и нажав на исследование, будет отправлена дополнительная информация о нем.'
        keyboards = await pagination(researches_dict, int(page), int(pages_count), callback.data[:indx])
    elif callback.data[:indx]  ==  'service':
        subcat_name, count, services_dict = await services(callback.data.split('_')[1], callback.from_user.id)
        pages_count = len(services_dict)
        some_text = f'Медицинских услуг в подкатегории: {count}\n\nВыбрав и нажав на медицинскую услугу, будет отправлена дополнительная информация о ней.'
        keyboards = await pagination(services_dict, int(page), int(pages_count), callback.data[:indx])
    elif callback.data[:indx]  ==  'action':
        subcat_name, count, actions_dict = await actions(callback.data.split('_')[1])
        pages_count = len(actions_dict)
        some_text = f'Акций в подкатегории: {count}\n\nВыбрав и нажав на акцию, будет отправлена дополнительная информация о ней.'
        keyboards = await pagination(actions_dict, int(page), int(pages_count), callback.data[:indx])
    await callback.message.edit_text(f'''Категория: <b>{cat_name}</b>\nПодкатегория: <b>{subcat_name}</b>\n{some_text}''',
parse_mode = 'HTML')
    await callback.message.edit_reply_markup(reply_markup = keyboards)

# оформление предварительного заказа, пользователь выбрал конкретный элемент 
@router.callback_query(F.data.startswith(('research-', 'service-', 'action-')))
async def get_research_data(callback: CallbackQuery) -> None:
    await callback.answer()
    item_get_id = callback.data.split('#')[0]
    item_id = item_get_id.split('-')[1]
    get_page = callback.data.split('#')[1]
    page_count = get_page.split('_')[0]
    page = get_page.split('_')[1]
    tg_id = callback.from_user.id
    if 'research' in callback.data:
        name, description, price, keyboard = await research_data(item_id, tg_id, page_count, page)
    elif 'service' in callback.data:
        name, price, keyboard = await service_data(item_id, tg_id, page_count, page)
    else:
        name, description, price, keyboard = await action_data(item_id, page_count, page)
    if '*' in name:
        name = name.replace('*', '"')
    res_cost = ''
    if len(str(price).split('.')[0])  ==  4:
        temp_cost = str(price).split('.')[0]
        res_cost = temp_cost[:1]+' '+temp_cost[1:]
    elif len(str(price).split('.')[0])  ==  5:
        temp_cost = str(price).split('.')[0]
        res_cost = temp_cost[:2]+' '+temp_cost[2:]
    else: res_cost = str(price).split('.')[0]
    if 'research' in callback.data:
        await callback.message.edit_text(f'<b>{name}</b>\n\n<b>Описание:</b> {description}\n\n<b>Стоимость исследования:</b> {res_cost} ₽',parse_mode = 'HTML')
    elif 'service' in callback.data:
        await callback.message.edit_text(f'<b>{name}</b>\n\n<b>Стоимость медицинской услуги:</b> {res_cost} ₽', parse_mode = 'HTML')
    else:
        await callback.message.edit_text(f'<b>{name}</b>\n\n<b>Описание:</b> {description}\n\n<b>Стоимость акции:</b> {res_cost} ₽', parse_mode = 'HTML')
    
    await callback.message.edit_reply_markup(reply_markup = keyboard)

# оформление заказа (из корзины)        
@router.callback_query(F.data  ==  'place_an_order')
async def place_an_order_qconfirm(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    # await callback.message.edit_text()
    await callback.message.answer_document(send_file('files\\personal_data_agreement.pdf'), 
                                            reply_markup = await default_keyboard_builder(
                                                text = ['✅Соглашаюсь','❌Не соглашаюсь'], 
                                                callback_data = ['agree_place_an_order', 'disagree_place_an_order']), 
                                            caption = 'Вы согласны на обработку персональных данных?', protect_content = True
                                        )
    
    
@router.callback_query(F.data.regexp(r'\b[sid]{,3}agree_\w{14}'))
async def place_an_order_confirm(callback: CallbackQuery):
    await callback.answer()
    if 'dis' in callback.data:
        await callback.message.edit_caption(inline_message_id = callback.inline_message_id, 
                                                caption = 'Согласие на обработку персональных данных отклонено.\nОформление заказа возможно, но он будет выполнен анонимно, такие результаты исследований врачи не принимают.', 
                                                reply_markup = await default_keyboard_builder(
                                                    text = ['Продолжить','Отмена'], 
                                                    callback_data = ['continue_place_an_order','cancle_place_an_order_comfirm']
                                                )   
                                            )        
    else:
        while True:
            digits = random.sample('1234567890', 9)
            order_num = await get_order_number(''.join(digits))
            if order_num: break
        text = await get_cart_buttons(callback.from_user.id, get_text = True)
        # await callback.message.edit_reply_markup(reply_markup = None)
        await callback.message.edit_caption(inline_message_id = callback.inline_message_id, caption = 'Вы дали свое согласие на обработку персональных данных.',
                                            reply_markup = None)
        await callback.message.answer(f'Ваш заказ <b>№{"".join(digits)}</b>:\n{text}', parse_mode = 'HTML')
        await callback.message.answer('Каким способом хотите произвести оплату?', reply_markup = await get_payment_buttons(''.join(digits), 0))

@router.callback_query(F.data.startswith(('continue_place','cancle_place')))   
async def place_an_order_continue(callback: CallbackQuery):
    await callback.answer()
    if 'continue' in callback.data:
        while True:
            digits = random.sample('1234567890', 9)
            order_num = await get_order_number(''.join(digits))
            if order_num: break
        await callback.message.edit_reply_markup(reply_markup = None)
        await callback.message.answer('Каким способом хотите произвести оплату?', reply_markup = await get_payment_buttons(''.join(digits), 1))
    else:
        await callback.message.edit_reply_markup(reply_markup = None)
        await callback.message.answer(f'Оформление заказа отменено (заказ <b>не удален</b>), чтобы повторно попробовать оформить заказ, вам необходимо <i>перейти в корзину</i>.', parse_mode = 'HTML')
        
# пользователь нажал на кнопку "назад" и вернулся к категориям 
@router.callback_query(F.data.regexp(r'back_[resachviton]{6,8}_categories'))
async def back_categories(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.data.split('_')[1]  ==  'research':
        await callback.message.edit_text('💉Иcследования\nВыберите категорию:')
        await callback.message.edit_reply_markup(reply_markup = await research_categories(callback.from_user.id))
    elif callback.data.split('_')[1]  ==  'service':
        await callback.message.edit_text('🧑‍⚕️Медицинские услуги\nВыберите категорию:')
        await callback.message.edit_reply_markup(reply_markup = await service_categories(callback.from_user.id))
    elif callback.data.split('_')[1]  ==  'action':
        await callback.message.edit_text('🛍️Акции\nВыберите категорию:')
        await callback.message.edit_reply_markup(reply_markup = await actions_categories())
        
# возврат в меню выбора (исследования или медицинские услуги)
@router.callback_query(F.data  ==  'exit_to_research_or_service')
async def exit_to_research_or_service(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Исследования или медицинские услуги?\nДля поиска необходимо отправить примерное наименование исследования/услуги.')
    await callback.message.edit_reply_markup(reply_markup = await default_keyboard_builder(
                                                    text = ['💉Исследования', '🧑‍⚕️Медицинские услуги', '🛍️Акции', '⏪Покинуть меню'], 
                                                    callback_data = ['researches', 'services', 'actions', 'exit_or_exit'], 
                                                    sizes = 1
                                                )
                                            )

# выход из меню выбора (исследования илм иедицинские услуги)
@router.callback_query(F.data.in_(['exit_or_exit', 'cart_exit', 'pag_exit', 'orders_stop_back']))
async def exit_or_exit(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup = None)
    await callback.message.edit_text('Выберите пункт нижнего меню.')

