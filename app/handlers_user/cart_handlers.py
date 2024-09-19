from aiogram import F
from app.handlers_user.main_handlers import router
from aiogram.types import CallbackQuery

from app.database.requests import cart_requests
from app.keyboards_user.inline.buttons_pagination_keyboard import pagination
from app.functions import get_cat_subcat_names, researches, services, actions
from app.keyboards_user.inline.order_cart_keyboard import get_cart_buttons


# добавление в корзину 
@router.callback_query(F.data.startswith('to_cart'))
async def to_cart(callback: CallbackQuery):
    data = callback.data.split('/')
    all_page_data = data[1].split('_')
    count = all_page_data[0]
    page_data = all_page_data[1].split('#')
    pages_count = page_data[0]
    page = page_data[1]
    ids = data[0].split('&')
    ide = ids[0].split('#')[1]
    what_is = ids[0].split('#')[0][8:]
    print(f'\nДобавление в корзину {what_is}')
    cat_id = ids[1].split('#')[0]
    subcat_id = ids[1].split('#')[1]
    cat_name, subcat_name = await get_cat_subcat_names(cat_id, subcat_id, what_is)
    if what_is  ==  'research':
        researches_dict = await researches(ids[1], callback.from_user.id, True)
        added = await cart_requests.add_to_cart(callback.from_user.id, Rid = int(ide))
        keyboards = await pagination(researches_dict, int(page), int(pages_count), what_is)
        some_text = f'Исследований в подкатегории: {count}\n\nВыбрав и нажав на исследование, будет отправлена дополнительная информация о нем.'
    elif what_is  ==  'service':
        services_dict = await services(ids[1], callback.from_user.id, True)
        added = await cart_requests.add_to_cart(callback.from_user.id, Sid = int(ide))
        keyboards = await pagination(services_dict, int(page), int(pages_count), what_is)
        some_text = f'Медицинских услуг в подкатегории: {count}\n\nВыбрав и нажав на медицинскую услугу, будет отправлена дополнительная информация о ней.'
    elif what_is  ==  'action':
        actions_dict = await actions(ids[1], True)
        added = await cart_requests.add_to_cart(callback.from_user.id, Aid = int(ide))
        keyboards = await pagination(actions_dict, int(page), int(pages_count), what_is)
        some_text = f'Акций в подкатегории: {count}\n\nВыбрав и нажав на акцию, будет отправлена дополнительная информация о ней.'
    # print(added)
    if added:
        await callback.answer('Добавлено в корзину')
    else: await callback.answer('Уже в корзине')
    await callback.message.edit_text(f'''Категория: <b>{cat_name}</b>\nПодкатегория: <b>{subcat_name}</b>\n{some_text}''', parse_mode = 'HTML')
    await callback.message.edit_reply_markup(reply_markup = keyboards)

# удалить элемент
@router.callback_query(F.data.startswith('delete-'))
async def delete_item(callback: CallbackQuery):
    await callback.answer('Удалено')
    if 'research' in callback.data:
        research_id = callback.data.split('&')[1]
        await cart_requests.edit_cart(callback.from_user.id, research_id, 'research')
        # out_text, keyboard = await kb.get_cart_buttons(callback.from_user.id)
    elif 'service' in callback.data:
        service_id = callback.data.split('&')[1]
        await cart_requests.edit_cart(callback.from_user.id, service_id, 'service')
        # out_text, keyboard = await kb.get_cart_buttons(callback.from_user.id)
    elif 'action' in callback.data:
        action_id = callback.data.split('&')[1]
        await cart_requests.edit_cart(callback.from_user.id, action_id, 'action')
    out_text, keyboard = await get_cart_buttons(callback.from_user.id)
    if keyboard:
        await callback.message.edit_text(f'<b>Ваш заказ:</b>\n{out_text}', parse_mode = 'HTML')
        await callback.message.edit_reply_markup(reply_markup = keyboard)
    else:
        await callback.message.edit_reply_markup(reply_markup = None)
        await callback.message.edit_text('<i><b>Корзина пуста.</b></i>\n\nЧтобы добавить исследование или медицинскую услугу в корзину, нажмите кнопку в меню <b>"Оформить предварительный заказ"</b>.',
                                            parse_mode = 'HTML'
                                        )

# удалить весь заказ из корзины
@router.callback_query(F.data  ==  'delete_all')
async def delete_all(callback: CallbackQuery):
    await callback.answer()
    await cart_requests.del_cart(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup = None)
    await callback.message.edit_text('<i><b>Корзина пуста.</b></i>\n\nЧтобы добавить исследование или медицинскую услугу в корзину, нажмите кнопку в меню <b>"Оформить предварительный заказ"</b>.',
                                        parse_mode = 'HTML'
                                    )

@router.callback_query(F.data  ==  'cart_del_instruction')
async def cart_del_item(callback: CallbackQuery):
    await callback.answer('Выберите номер для удаления из корзины')
