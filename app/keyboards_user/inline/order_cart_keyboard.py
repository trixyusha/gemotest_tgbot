from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests.cart_requests import del_cart, get_cart
from app.database.requests.order_requests import get_orders, get_order_data 



async def get_cart_buttons(tg_id, order = False, message_cart = False, get_text = False):
    researches, additional_services, services, actions, total_cost = await get_cart(tg_id)
    if total_cost:
        emoji_list = ['0️⃣','1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text = '🚚Оформить заказ', callback_data = 'place_an_order'))
        i = 0
        cart_text = ''
        additional_services_text = ''
        lenght = 0
        if researches:
            lenght +=  len(researches)
        if services:
            lenght +=  len(services)
        if actions:
            lenght +=  len(actions)
        if lenght > 1:
            keyboard.add(InlineKeyboardButton(text = 'Удалить:', callback_data = 'cart_del_instruction'))
        if researches:
            for research_id, research_data in researches.items():
                name = research_data[0]
                cost = research_data[1]
                res_cost = await get_formating_cost(cost)
                if '*' in research_data[0]:
                    name = research_data[0].replace('*', '"')
                if i <=  10:
                    if i  ==  0:
                        if lenght > 1:
                            keyboard.add(InlineKeyboardButton(text = f'{emoji_list[1]}', callback_data = f'delete-research&{research_id}'))
                        cart_text = f'1. {name} - {res_cost} ₽'
                        i +=  1
                    else:
                        if lenght > 1:
                            keyboard.add(InlineKeyboardButton(text = f'{emoji_list[i]}', callback_data = f'delete-research&{research_id}'))
                        cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
                    i +=  1
                else:
                    indxs = ' '.join(str(i)).split(' ')
                    new_list = []
                    for indx in indxs:
                        new_list.append(emoji_list[int(indx)])
                    if lenght > 1:
                        keyboard.add(InlineKeyboardButton(text = f'{"".join(new_list)}', callback_data = f'delete-research&{research_id}'))
                    cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
                    i +=  1
        if services:
            for service_id, service_data in services.items():
                name = service_data[0]
                cost = service_data[1]
                res_cost = await get_formating_cost(cost)
                if '*' in service_data[0]:
                    name = service_data[0].replace('*', '"')
                if i <=  10:
                    if i  ==  0:
                        if lenght > 1:
                            keyboard.add(InlineKeyboardButton(text = f'{emoji_list[1]}', callback_data = f'delete-service&{service_id}'))
                        cart_text = f'1. {name} - {res_cost} ₽'
                        i +=  1
                    else:
                        if lenght > 1:
                            keyboard.add(InlineKeyboardButton(text = f'{emoji_list[i]}', callback_data = f'delete-service&{service_id}'))
                        cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
                    i +=  1
                else:
                    indxs = ' '.join(str(i)).split(' ')
                    new_list = []
                    for indx in indxs:
                        new_list.append(emoji_list[int(indx)])
                    if lenght > 1:
                        keyboard.add(InlineKeyboardButton(text = f'{"".join(new_list)}', callback_data = f'delete-service&{service_id}'))
                    cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
                    i +=  1
        if actions:
            for action_id, action_data in actions.items():
                name = action_data[0]
                cost = action_data[1]
                res_cost = await get_formating_cost(cost)
                if '*' in action_data[0]:
                    name = action_data[0].replace('*', '"')
                if i <=  10:
                    if i  ==  0:
                        if lenght > 1:
                            keyboard.add(InlineKeyboardButton(text = f'{emoji_list[1]}', callback_data = f'delete-action&{action_id}'))
                        cart_text = f'1. {name} - {res_cost} ₽'
                        i +=  1
                    else:
                        if lenght > 1:
                            keyboard.add(InlineKeyboardButton(text = f'{emoji_list[i]}', callback_data = f'delete-action&{action_id}'))
                        cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
                    i +=  1
                else:
                    indxs = ' '.join(str(i)).split(' ')
                    new_list = []
                    for indx in indxs:
                        new_list.append(emoji_list[int(indx)])
                    if lenght > 1:
                        keyboard.add(InlineKeyboardButton(text = f'{"".join(new_list)}', callback_data = f'delete-action&{action_id}'))
                    cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
                    i +=  1
        if additional_services:
            k = 0
            for additional_service_id, additional_service_data in additional_services.items():
                name = additional_service_data[0]
                cost = additional_service_data[1]
                if k  ==  0:
                    additional_services_text = f'\n\n<b>Доп. услуги:</b> {name} ({int(cost)} ₽)'
                    k +=  1
                else: 
                    additional_services_text = additional_services_text + f', {name} ({int(cost)} ₽)'
                    k +=  1
        tres_cost = await get_formating_cost(total_cost)
        if additional_services_text !=  '':
            output_text = cart_text + additional_services_text + '.' + f'\n\n<b>Итоговая цена:</b> {tres_cost} ₽'
        else: output_text = cart_text + f'\n\n<b>Итоговая цена:</b> {tres_cost} ₽'
        keyboard.adjust(1,1,3)
        del_text = ''
        if lenght > 1: del_text = '❌Удалить все'
        else: del_text = '❌Удалить'
        keyboard.row(InlineKeyboardButton(text = del_text, callback_data = 'delete_all'), width = 1)
        keyboard.row(InlineKeyboardButton(text = '⏪Выйти', callback_data = 'cart_exit'), width = 1)
        print(f'RESULT TEXT {cart_text}')
        if get_text: return output_text
        if order: return int(total_cost)
        else: return output_text, keyboard.as_markup()
    elif not total_cost and message_cart:
        return None, None
    else:
        await del_cart(tg_id)
        return None, None

async def order_data(tg_id, order_id, page_count, page):
    order_id = int(order_id)
    order = await get_orders(tg_id, order_id)
    order_text = ''
    order_info = ''
    additional_services_text = ''
    # paid_info = ''
    keyboard = InlineKeyboardBuilder()
    if order:
        if order.Paid:
            paid_info = 'Оплачен'
        else: paid_info = 'Не оплачен'
        if order.Status:
            status = 'Выполнен'
        elif order.Status  ==  None:
            status = 'В ожидании (посетите лаб. отделение)'
        else:
            status = 'Выполняется'
        researches, additional_services, services, actions, total_cost = await get_order_data(tg_id, order)
        i = 1
        if researches:
            for research_data in researches.values():
                name = research_data[0]
                cost = research_data[1]
                res_cost = await get_formating_cost(cost)
                if '*' in research_data[0]:
                    name = research_data[0].replace('*', '"')
                if i  ==  1:
                    order_info = f'{i}. {name} - {res_cost} ₽'
                    i +=  1
                else:
                    order_info = order_info + f'\n{i}. {name} - {res_cost} ₽'
                    i +=  1
        if services:
            for service_data in services.values():
                name = service_data[0]
                cost = service_data[1]
                res_cost = await get_formating_cost(cost)
                if '*' in service_data[0]:
                    name = service_data[0].replace('*', '"')
                if i  ==  1:
                    order_info = f'{i}. {name} - {res_cost} ₽'
                    i +=  1
                else:
                    order_info = order_info + f'\n{i}. {name} - {res_cost} ₽'
                    i +=  1
        if actions:
            for action_data in actions.values():
                name = action_data[0]
                cost = action_data[1]
                res_cost = await get_formating_cost(cost)
                if '*' in action_data[0]:
                    name = action_data[0].replace('*', '"')
                if i  ==  1:
                    order_info = f'{i}. {name} - {res_cost} ₽'
                    i +=  1
                else:
                    order_info = order_info + f'\n{i}. {name} - {res_cost} ₽'
                    i +=  1
        if additional_services:
            k = 0
            for additional_service_data in additional_services.values():
                name = additional_service_data[0]
                cost = additional_service_data[1]
                if k  ==  0:
                    additional_services_text = f'\nДоп. услуги: {name} ({int(cost)} ₽)'
                    k +=  1
                else: 
                    additional_services_text = additional_services_text + f', {name} ({int(cost)} ₽)'
                    k +=  1
        order_text = f'<b>Заказ №{order.OrderNum}</b> [{paid_info}]\n<b>Дата оформления:</b> {order.RegistrationDate.date()}\n<b>Статус заказа:</b> {status}\n\nСостав заказа:\n{order_info}'
        if additional_services_text !=  '':
            order_text = order_text + f'{additional_services_text}.'
        tres_cost = await get_formating_cost(total_cost)
        order_text = order_text + f'\n\n<b>Цена:</b> {tres_cost} ₽'
        print(f'RESULT TEXT {order_text}')
        # keyboard.add(InlineKeyboardButton(text = f'Заказ №{order.OrderNum} {order.RegistrationDate.date()}', callback_data = f'order&{order_id}#{tg_id}/{page_count}#{page}'))
        keyboard.add(InlineKeyboardButton(text = '⬅️Назад', callback_data = f'order_back_to_pagination&{page_count}#{page}'))
    return order_text, keyboard.adjust(1).as_markup()


async def get_formating_cost(cost):
    res_cost = ''
    if len(str(cost).split('.')[0])  ==  4:
        temp_cost = str(cost).split('.')[0]
        res_cost = temp_cost[:1]+' '+temp_cost[1:]
    elif len(str(cost).split('.')[0])  ==  5:
        temp_cost = str(cost).split('.')[0]
        res_cost = temp_cost[:2]+' '+temp_cost[2:]
    elif len(str(cost).split('.')[0])  ==  6:
        temp_cost = str(cost).split('.')[0]
        res_cost = temp_cost[:3]+' '+temp_cost[3:]
    else: res_cost = str(cost).split('.')[0]
    return res_cost
