# from math import ceil

# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
# from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
# from aiogram.filters.callback_data import CallbackData

# # from app.database.models import Service, Research
# from app.database.main_requests import (get_cities, get_research_categories, get_research_subcategories, get_research_subcategory_name,
#                                     get_researches, get_service_categories, get_service_subcategories, get_services, get_service_subcategory_name, get_city_id,
#                                     get_research_data, get_research_price, get_service_data, get_service_price, get_cart, get_telemed_data,
#                                     get_action_categories, get_action_subcategories, get_actions, get_action_subcategory_name, get_action_data, get_action_price, del_cart,
#                                     get_orders, get_order_data
#                                 )


# user_main = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = '📝Оформить предварительный заказ')],
#                                      [KeyboardButton(text = '🛒Корзина')],
#                                      [KeyboardButton(text = '🧾История заказов'), KeyboardButton(text = '⚙️Помощь')],
#                                      [KeyboardButton(text = '❌Отключиться от услуги')]],
#                            resize_keyboard = True,
#                            input_field_placeholder = 'Выберите пункт меню...')

# guest_main = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = '📝Оформить предварительный заказ')],
#                                      [KeyboardButton(text = '🛒Корзина'), KeyboardButton(text = '⚙️Помощь')],
#                                      [KeyboardButton(text = '🧾Заказы')],
#                                      [KeyboardButton(text = '🆕Подключить получение результатов')]],
#                            resize_keyboard = True,
#                            input_field_placeholder = 'Выберите пункт меню...')

# approval = InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text = '✅Соглашаюсь', callback_data = 'agree'), 
#                                                   InlineKeyboardButton(text = '❌Не соглашаюсь', callback_data = 'disagree')]])

# question_re_sending = InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text = 'Да', callback_data = 'yes_resend'), 
#                                                   InlineKeyboardButton(text = 'Нет', callback_data = 'no_resend')]])


#////////////////////////////////////////////////////////////////////////////////////////
# cart = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = '🛒Корзина')]],
#                             resize_keyboard = True
#                         )

# contin = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = 'Продолжить')]],
#                             resize_keyboard = True,
#                             input_field_placeholder = 'Прочтите инструкцию!'
#                         )
#////////////////////////////////////////////////////////////////////////////////////////


# researches_or_services = InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text = '💉Исследования', callback_data = 'researches')],
#                                        [InlineKeyboardButton(text = '🧑‍⚕️Медицинские услуги', callback_data = 'services')],
#                                        [InlineKeyboardButton(text = '🛍️Акции', callback_data = 'actions')],
#                                        [InlineKeyboardButton(text = '⏪Покинуть меню', callback_data = 'exit_or_exit')]])


        
# async def default_keyboard_builder(
#     text: str | list[str], 
#     callback_data: str | list[str] = None, 
#     sizes: int | list[int] = 2,
#     request_cont: bool = False,
#     **kwargs) -> InlineKeyboardBuilder | ReplyKeyboardBuilder:
#     if callback_data:
#         builder = InlineKeyboardBuilder()
#         # builder.as_markup(resize_keyboard = True)
#     else:
#         builder = ReplyKeyboardBuilder()
#     if isinstance(text, str):
#         text = [text]
#     if callback_data and isinstance(callback_data, str):
#         callback_data = [callback_data]
#     if isinstance(sizes, int):
#         sizes = [sizes]
#     if isinstance(builder, InlineKeyboardBuilder):
#         [builder.button(text = txt, callback_data = cbd) for txt, cbd in zip(text, callback_data)]
#     else:
#         if request_cont:
#             [builder.button(text = txt, request_contact = request_cont) for txt in text]
#         else: [builder.button(text = txt) for txt in text]
#     builder.adjust(*sizes)
#     return builder.as_markup(**kwargs)


# если пользователь нажимает на кнопку исследования, то подгружается список категорий, после выбора категории подгружается список подкатегорий, 
# далее подгружается список исследований
# async def cities():
#     all_cities = await get_cities()
#     keyboard = InlineKeyboardBuilder()
#     for city in all_cities:
#         keyboard.add(InlineKeyboardButton(text = city.Name, callback_data = f'city_{city.ID}'))
#     return keyboard.adjust(2).as_markup()    

# async def research_categories(tg_id):
#     city_id = await get_city_id(tg_id)
#     all_research_categories = await get_research_categories(city_id)
#     keyboard = InlineKeyboardBuilder()
#     buf = -1
#     for research_category in all_research_categories:
#             if buf  ==  0:
#                 buf = research_category.ID
#             elif buf  ==  research_category.ID:
#                 continue
#             elif buf !=  research_category.ID:
#                 keyboard.add(InlineKeyboardButton(text = research_category.Name, callback_data = f'research-category_{research_category.ID}'))
#                 buf = 0
#     keyboard.add(InlineKeyboardButton(text = '⬅️Назад в меню', callback_data = 'exit_to_research_or_service'))
#     return keyboard.adjust(1).as_markup()

# async def research_subcategories(research_category_id, only_cat_name, tg_id):
#     research_category_id = int(research_category_id)
#     city_id = await get_city_id(tg_id)
#     cat = await get_research_categories(None, research_category_id)
#     if not only_cat_name:
#         all_research_subcategories = await get_research_subcategories(research_category_id, city_id)
#         keyboard = InlineKeyboardBuilder()
#         buf = -1
#         for research_subcategory in all_research_subcategories:
#             if buf  ==  0:
#                 buf = research_subcategory.ID
#             elif buf  ==  research_subcategory.ID:
#                 continue
#             elif buf !=  research_subcategory.ID:
#                 keyboard.add(InlineKeyboardButton(text = research_subcategory.Name, callback_data = f'research-subcategory_{research_category_id}#{research_subcategory.ID}'))
#                 buf = 0
#         keyboard.add(InlineKeyboardButton(text = '⬅️Назад к категориям', callback_data = 'back_research_categories'))
#         keyboard.add(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service'))
#         return cat.Name, keyboard.adjust(1).as_markup()
#     else: return cat.Name

# async def researches(data, tg_id, only_dict = False):
#     ids = data.split('#')
#     research_category_id = int(ids[0])
#     research_subcategory_id = int(ids[1])
#     city_id = await get_city_id(tg_id)
#     research_subcategory_name = await get_research_subcategory_name(research_subcategory_id)
#     researches = await get_researches(research_category_id, research_subcategory_id, city_id)
#     res_dict = {}
#     rlist = [[i.ID, i.Name, i.ResearchCategoryID, i.ResearchSubcategoryID] for i in researches]
#     count = len(rlist)
#     pages_count = ceil(count/10)
#     split = lambda lst, n: [lst[i::n] for i in range(n)]
#     for i, item in enumerate(split(rlist, pages_count), start = 1):
#         res_dict[i] = item
#     if only_dict:
#         return res_dict
#     else: return research_subcategory_name, count, res_dict

# async def research_data(research_id, tg_id, page_count, page):
#     research_id = int(research_id)
#     city_id = await get_city_id(tg_id)
#     data = await get_research_data(research_id)
#     price = await get_research_price(research_id, city_id)
#     researches_count = len([i for i in await get_researches(data.ResearchCategoryID, data.ResearchSubcategoryID, city_id)])
#     keyboard = InlineKeyboardBuilder()
#     if price is not None:
#         keyboard.add(InlineKeyboardButton(text = '🛒В корзину', callback_data = f'to_cart_research#{data.ID}&{data.ResearchCategoryID}#{data.ResearchSubcategoryID}/{researches_count}_{page_count}#{page}'))
#     keyboard.add(InlineKeyboardButton(text = '⬅️Назад', callback_data = f'rback-to-pagination&{data.ResearchCategoryID}#{data.ResearchSubcategoryID}/{researches_count}_{page_count}#{page}'))
#     keyboard.add(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service'))
#     # print(f'\nRESEARCH GET DATA\nPAGE COUNT {page_count}\nPAGE {page}\n')
#     if price is not None:
#         return data.Name, data.Description, price.Cost, keyboard.adjust(1).as_markup()
#     else:
#         return data.Name, data.Description, price, keyboard.adjust(1).as_markup()

# async def service_categories(tg_id):
#     city_id = await get_city_id(tg_id)
#     print(f'[SERVICE CATEGORY] CITY ID {city_id}')
#     all_service_categories = await get_service_categories(city_id)
#     telemed = None
#     keyboard = InlineKeyboardBuilder()
#     buf = -1
#     for service_category in all_service_categories:
#         if service_category.Name !=  'Телемедицина':
#             if buf  ==  0:
#                 buf = service_category.ID
#             elif buf  ==  service_category.ID:
#                 continue
#             elif buf !=  service_category.ID:
#                 keyboard.add(InlineKeyboardButton(text = service_category.Name, callback_data = f'service-category_{service_category.ID}'))
#                 buf = 0
#         else:
#             telemed = service_category
#     keyboard.add(InlineKeyboardButton(text = telemed.Name, callback_data = f'telemed-category_{telemed.ID}'))
#     keyboard.add(InlineKeyboardButton(text = '⬅️Назад в меню', callback_data = 'exit_to_research_or_service'))
#     return keyboard.adjust(1).as_markup()

# async def service_subcategories(service_category_id, only_cat_name, tg_id):
#     service_category_id = int(service_category_id)
#     city_id = await get_city_id(tg_id)
#     cat = await get_service_categories(None, service_category_id)
#     if not only_cat_name:
#         all_service_subcategories = await get_service_subcategories(service_category_id, city_id)
#         keyboard = InlineKeyboardBuilder()
#         buf = -1
#         for service_subcategory in all_service_subcategories:
#             if buf  ==  0:
#                 buf = service_subcategory.ID
#             elif buf  ==  service_subcategory.ID:
#                 continue
#             elif buf !=  service_subcategory.ID:
#                 keyboard.add(InlineKeyboardButton(text = service_subcategory.Name, callback_data = f'service-subcategory_{service_category_id}#{service_subcategory.ID}'))
#                 buf = 0
#         keyboard.add(InlineKeyboardButton(text = '⬅️Назад к категориям', callback_data = 'back_service_categories'))
#         keyboard.add(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service'))
#         return cat.Name, keyboard.adjust(1).as_markup()
#     else: return cat.Name

# async def services(data, tg_id, only_dict = False):
#     city_id = await get_city_id(tg_id)
#     ids = data.split('#')
#     service_category_id = int(ids[0])
#     service_subcategory_id = int(ids[1])
#     service_subcategory_name = await get_service_subcategory_name(service_subcategory_id)
#     services = await get_services(service_category_id, service_subcategory_id, city_id)
#     serv_dict = {}
#     slist = [[i.ID, i.Name, i.ServiceCategoryID, i.ServiceSubcategoryID] for i in services]
#     count = len(slist)
#     pages_count = ceil(count/10)
#     split = lambda lst, n: [lst[i::n] for i in range(n)]
#     for i, item in enumerate(split(slist, pages_count), start = 1):
#         serv_dict[i] = item
#     if only_dict:
#         return serv_dict
#     else: return service_subcategory_name, count, serv_dict

# async def service_data(service_id, tg_id, page_count, page):
#     service_id = int(service_id)
#     city_id, city_name = await get_city_id(tg_id, True)
#     data = await get_service_data(service_id)
#     price = await get_service_price(service_id, city_id)
#     services_count = len([i for i in await get_services(data.ServiceCategoryID, data.ServiceSubcategoryID, city_id)])
#     keyboard = InlineKeyboardBuilder()
#     if price is not None:
#         keyboard.add(InlineKeyboardButton(text = '🛒В корзину', callback_data = f'to_cart_service#{data.ID}&{data.ServiceCategoryID}#{data.ServiceSubcategoryID}/{services_count}_{page_count}#{page}'))
#     keyboard.add(InlineKeyboardButton(text = '⬅️Назад', callback_data = f'sback-to-pagination&{data.ServiceCategoryID}#{data.ServiceSubcategoryID}/{services_count}_{page_count}#{page}'))
#     print(f'\nSERVICE GET DATA\nPAGE COUNT {page_count}\nPAGE {page}\nCITY NAME {city_name}')
#     if price is not None:
#         return data.Name, price.Cost, city_name, keyboard.adjust(1).as_markup()
#     else:
#         return data.Name, price, city_name, keyboard.adjust(1).as_markup()

# async def actions_categories():
#     all_action_categories = await get_action_categories()
#     keyboard = InlineKeyboardBuilder()
#     buf = -1
#     for action_category in all_action_categories:
#             if buf  ==  0:
#                 buf = action_category.ID
#             elif buf  ==  action_category.ID:
#                 continue
#             elif buf !=  action_category.ID:
#                 keyboard.add(InlineKeyboardButton(text = action_category.Name, callback_data = f'action-category_{action_category.ID}'))
#                 buf = 0
#     keyboard.add(InlineKeyboardButton(text = '⬅️Назад в меню', callback_data = 'exit_to_research_or_service'))
#     return keyboard.adjust(1).as_markup()

# async def actions_subcategories(action_category_id, only_cat_name):
#     action_category_id = int(action_category_id)
#     cat = await get_action_categories(action_category_id)
#     if not only_cat_name:
#         all_action_subcategories = await get_action_subcategories(action_category_id)
#         keyboard = InlineKeyboardBuilder()
#         buf = -1
#         for action_subcategory in all_action_subcategories:
#             # print(f'\nRESEARCH {research_subcategory.ID} - {research_subcategory.Name}')
#             if buf  ==  0:
#                 buf = action_subcategory.ID
#             elif buf  ==  action_subcategory.ID:
#                 continue
#             elif buf !=  action_subcategory.ID:
#                 keyboard.add(InlineKeyboardButton(text = action_subcategory.Name, callback_data = f'action-subcategory_{action_category_id}#{action_subcategory.ID}'))
#                 buf = 0
#         keyboard.add(InlineKeyboardButton(text = '⬅️Назад к категориям', callback_data = 'back_action_categories'))
#         keyboard.add(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service'))
#         return cat.Name, keyboard.adjust(1).as_markup()
#     else: return cat.Name

# async def actions(data, only_dict = False):
#     ids = data.split('#')
#     action_category_id = int(ids[0])
#     action_subcategory_id = int(ids[1])
#     action_subcategory_name = await get_action_subcategory_name(action_subcategory_id)
#     actions = await get_actions(action_category_id, action_subcategory_id)
#     act_dict = {}
#     alist = [[i.ID, i.Name, i.Description, i.ActionCategoryID, i.ActionSubcategoryID] for i in actions]
#     # print(f'\n\nRESEARCHES\n{rlist}\n\n')
#     count = len(alist)
#     pages_count = ceil(count/10)
#     split = lambda lst, n: [lst[i::n] for i in range(n)]
#     for i, item in enumerate(split(alist, pages_count), start = 1):
#         act_dict[i] = item
#     if only_dict:
#         return act_dict
#     else: return action_subcategory_name, count, act_dict

# async def action_data(action_id, page_count, page):
#     action_id = int(action_id)
#     data = await get_action_data(action_id)
#     price = await get_action_price(action_id)
#     actions_count = len([i for i in await get_actions(data.ActionCategoryID, data.ActionSubcategoryID)])
#     keyboard = InlineKeyboardBuilder()
#     if price is not None:
#         keyboard.add(InlineKeyboardButton(text = '🛒В корзину', callback_data = f'to_cart_action#{data.ID}&{data.ActionCategoryID}#{data.ActionSubcategoryID}/{actions_count}_{page_count}#{page}'))
#     keyboard.add(InlineKeyboardButton(text = '⬅️Назад', callback_data = f'aback-to-pagination&{data.ActionCategoryID}#{data.ActionSubcategoryID}/{actions_count}_{page_count}#{page}'))
#     if price is not None:
#         return data.Name, data.Description, price.Cost, keyboard.adjust(1).as_markup()
#     else:
#         return data.Name, data.Description, price, keyboard.adjust(1).as_markup()

# async def orders(tg_id, only_dict = False):
#     orders = await get_orders(tg_id)
#     if orders:
#         orders_dict = {}
#         olist = [[i.ID, i.OrderNum, i.RegistrationDate] for i in orders]
#         count = len(olist)
#         pages_count = ceil(count/10)
#         split = lambda lst, n: [lst[i::n] for i in range(n)]
#         for i, item in enumerate(split(olist, pages_count), start = 1):
#             orders_dict[i] = item
#         if only_dict:
#             return orders_dict
#         else: return count, orders_dict
#     else: return None, None

# async def order_data(tg_id, order_id, page_count, page):
#     order_id = int(order_id)
#     order = await get_orders(tg_id, order_id)
#     order_text = ''
#     order_info = ''
#     additional_services_text = ''
#     # paid_info = ''
#     keyboard = InlineKeyboardBuilder()
#     if order:
#         if order.Paid:
#             paid_info = 'Оплачен'
#         else: paid_info = 'Не оплачен'
#         if order.Status:
#             status = 'Выполнен'
#         elif order.Status  ==  None:
#             status = 'В ожидании (посетите лаб. отделение)'
#         else:
#             status = 'Выполняется'
#         researches, additional_services, services, actions, total_cost = await get_order_data(tg_id, order)
#         i = 1
#         if researches:
#             for research_data in researches.values():
#                 name = research_data[0]
#                 cost = research_data[1]
#                 res_cost = get_formating_cost(cost)
#                 if '*' in research_data[0]:
#                     name = research_data[0].replace('*', '"')
#                 if i  ==  1:
#                     order_info = f'{i}. {name} - {res_cost} ₽'
#                     i +=  1
#                 else:
#                     order_info = order_info + f'\n{i}. {name} - {res_cost} ₽'
#                     i +=  1
#         if services:
#             for service_data in services.values():
#                 name = service_data[0]
#                 cost = service_data[1]
#                 res_cost = get_formating_cost(cost)
#                 if '*' in service_data[0]:
#                     name = service_data[0].replace('*', '"')
#                 if i  ==  1:
#                     order_info = f'{i}. {name} - {res_cost} ₽'
#                     i +=  1
#                 else:
#                     order_info = order_info + f'\n{i}. {name} - {res_cost} ₽'
#                     i +=  1
#         if actions:
#             for action_data in actions.values():
#                 name = action_data[0]
#                 cost = action_data[1]
#                 res_cost = get_formating_cost(cost)
#                 if '*' in action_data[0]:
#                     name = action_data[0].replace('*', '"')
#                 if i  ==  1:
#                     order_info = f'{i}. {name} - {res_cost} ₽'
#                     i +=  1
#                 else:
#                     order_info = order_info + f'\n{i}. {name} - {res_cost} ₽'
#                     i +=  1
#         if additional_services:
#             k = 0
#             for additional_service_data in additional_services.values():
#                 name = additional_service_data[0]
#                 cost = additional_service_data[1]
#                 if k  ==  0:
#                     additional_services_text = f'\nДоп. услуги: {name} ({int(cost)} ₽)'
#                     k +=  1
#                 else: 
#                     additional_services_text = additional_services_text + f', {name} ({int(cost)} ₽)'
#                     k +=  1
#         order_text = f'<b>Заказ №{order.OrderNum}</b> [{paid_info}]\n<b>Дата оформления:</b> {order.RegistrationDate.date()}\n<b>Статус заказа:</b> {status}\n\nСостав заказа:\n{order_info}'
#         if additional_services_text !=  '':
#             order_text = order_text + f'{additional_services_text}.'
#         tres_cost = get_formating_cost(total_cost)
#         order_text = order_text + f'\n\n<b>Цена:</b> {tres_cost} ₽'
#         print(f'RESULT TEXT {order_text}')
#         # keyboard.add(InlineKeyboardButton(text = f'Заказ №{order.OrderNum} {order.RegistrationDate.date()}', callback_data = f'order&{order_id}#{tg_id}/{page_count}#{page}'))
#         keyboard.add(InlineKeyboardButton(text = '⬅️Назад', callback_data = f'order_back_to_pagination&{page_count}#{page}'))
#     return order_text, keyboard.adjust(1).as_markup()
    

# async def get_telemed_buttons():
#     keyboard = InlineKeyboardBuilder()
#     telemed_data = await get_telemed_data()
#     for item in telemed_data:
#         print(f'[DATA ITEM] TELEMED {item}')
#         keyboard.add(InlineKeyboardButton(text = item[1], callback_data = f'telemed-serviceid_{item[0]}', url = item[2]))
#     keyboard.add(InlineKeyboardButton(text = '⬅️Назад к категориям', callback_data = f'back_service_categories'))
#     keyboard.add(InlineKeyboardButton(text = f'⏪Выйти', callback_data = f'exit_to_research_or_service'))
#     return keyboard.adjust(1).as_markup()

# async def get_cat_subcat_names(cat_id, subcat_id, what_is):
#     cat_id = int(cat_id)
#     subcat_id = int(subcat_id)
#     if what_is  ==  'research':
#         cat = await get_research_categories(None, cat_id)
#         subcat_name = await get_research_subcategory_name(subcat_id)
#         # print(f'\nGET CATEGORY AND SUBCATEGORY RESEARCH NAMES\nCATEGORY NAME {cat.Name} SUBCATEGORY NAME {subcat_name}\n')
#         return cat.Name, subcat_name
#     elif what_is  ==  'service':
#         cat = await get_service_categories(None, cat_id)
#         subcat_name = await get_service_subcategory_name(subcat_id)
#         # print(f'\nGET CATEGORY AND SUBCATEGORY SERVICE NAMES\nCATEGORY NAME {cat.Name} SUBCATEGORY NAME {subcat_name}\n')
#         return cat.Name, subcat_name
#     elif what_is  ==  'action':
#         cat = await get_action_categories(cat_id)
#         subcat_name = await get_action_subcategory_name(subcat_id)
#         # print(f'\nGET CATEGORY AND SUBCATEGORY RESEARCH NAMES\nCATEGORY NAME {cat.Name} SUBCATEGORY NAME {subcat_name}\n')
#         return cat.Name, subcat_name

# async def get_cart_buttons(tg_id, order = False, message_cart = False, get_text = False):
#     researches, additional_services, services, actions, total_cost = await get_cart(tg_id)
#     if total_cost:
#         emoji_list = ['0️⃣','1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
#         keyboard = InlineKeyboardBuilder()
#         keyboard.add(InlineKeyboardButton(text = '🚚Оформить заказ', callback_data = 'place_an_order'))
#         # keyboard.add(InlineKeyboardButton(text = 'Удалить:', callback_data = 'cart_del_instruction'))
#         i = 0
#         cart_text = ''
#         additional_services_text = ''
#         lenght = 0
#         if researches:
#             lenght +=  len(researches)
#         if services:
#             lenght +=  len(services)
#         if actions:
#             lenght +=  len(actions)
#         if lenght > 1:
#             keyboard.add(InlineKeyboardButton(text = 'Удалить:', callback_data = 'cart_del_instruction'))
#         if researches:
#             for research_id, research_data in researches.items():
#                 name = research_data[0]
#                 cost = research_data[1]
#                 res_cost = get_formating_cost(cost)
#                 if '*' in research_data[0]:
#                     name = research_data[0].replace('*', '"')
#                 if i <=  10:
#                     if i  ==  0:
#                         if lenght > 1:
#                             keyboard.add(InlineKeyboardButton(text = f'{emoji_list[1]}', callback_data = f'delete-research&{research_id}'))
#                         cart_text = f'1. {name} - {res_cost} ₽'
#                         i +=  1
#                     else:
#                         if lenght > 1:
#                             keyboard.add(InlineKeyboardButton(text = f'{emoji_list[i]}', callback_data = f'delete-research&{research_id}'))
#                         cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
#                     i +=  1
#                 else:
#                     indxs = ' '.join(str(i)).split(' ')
#                     new_list = []
#                     for indx in indxs:
#                         new_list.append(emoji_list[int(indx)])
#                     if lenght > 1:
#                         keyboard.add(InlineKeyboardButton(text = f'{"".join(new_list)}', callback_data = f'delete-research&{research_id}'))
#                     cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
#                     i +=  1
#         if services:
#             for service_id, service_data in services.items():
#                 name = service_data[0]
#                 cost = service_data[1]
#                 res_cost = get_formating_cost(cost)
#                 if '*' in service_data[0]:
#                     name = service_data[0].replace('*', '"')
#                 if i <=  10:
#                     if i  ==  0:
#                         if lenght > 1:
#                             keyboard.add(InlineKeyboardButton(text = f'{emoji_list[1]}', callback_data = f'delete-service&{service_id}'))
#                         cart_text = f'1. {name} - {res_cost} ₽'
#                         i +=  1
#                     else:
#                         if lenght > 1:
#                             keyboard.add(InlineKeyboardButton(text = f'{emoji_list[i]}', callback_data = f'delete-service&{service_id}'))
#                         cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
#                     i +=  1
#                 else:
#                     indxs = ' '.join(str(i)).split(' ')
#                     new_list = []
#                     for indx in indxs:
#                         new_list.append(emoji_list[int(indx)])
#                     if lenght > 1:
#                         keyboard.add(InlineKeyboardButton(text = f'{"".join(new_list)}', callback_data = f'delete-service&{service_id}'))
#                     cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
#                     i +=  1
#         if actions:
#             for action_id, action_data in actions.items():
#                 name = action_data[0]
#                 cost = action_data[1]
#                 res_cost = get_formating_cost(cost)
#                 if '*' in action_data[0]:
#                     name = action_data[0].replace('*', '"')
#                 if i <=  10:
#                     if i  ==  0:
#                         if lenght > 1:
#                             keyboard.add(InlineKeyboardButton(text = f'{emoji_list[1]}', callback_data = f'delete-action&{action_id}'))
#                         cart_text = f'1. {name} - {res_cost} ₽'
#                         i +=  1
#                     else:
#                         if lenght > 1:
#                             keyboard.add(InlineKeyboardButton(text = f'{emoji_list[i]}', callback_data = f'delete-action&{action_id}'))
#                         cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
#                     i +=  1
#                 else:
#                     indxs = ' '.join(str(i)).split(' ')
#                     new_list = []
#                     for indx in indxs:
#                         new_list.append(emoji_list[int(indx)])
#                     if lenght > 1:
#                         keyboard.add(InlineKeyboardButton(text = f'{"".join(new_list)}', callback_data = f'delete-action&{action_id}'))
#                     cart_text = cart_text + f'\n{i}. {name} - {res_cost} ₽'
#                     i +=  1
#         if additional_services:
#             k = 0
#             for additional_service_id, additional_service_data in additional_services.items():
#                 name = additional_service_data[0]
#                 cost = additional_service_data[1]
#                 if k  ==  0:
#                     additional_services_text = f'\n\n<b>Доп. услуги:</b> {name} ({int(cost)} ₽)'
#                     k +=  1
#                 else: 
#                     additional_services_text = additional_services_text + f', {name} ({int(cost)} ₽)'
#                     k +=  1
#         tres_cost = get_formating_cost(total_cost)
#         if additional_services_text !=  '':
#             output_text = cart_text + additional_services_text + '.' + f'\n\n<b>Итоговая цена:</b> {tres_cost} ₽'
#         else: output_text = cart_text + f'\n\n<b>Итоговая цена:</b> {tres_cost} ₽'
#         keyboard.adjust(1,1,3)
#         del_text = ''
#         if lenght > 1: del_text = '❌Удалить все'
#         else: del_text = '❌Удалить'
#         keyboard.row(InlineKeyboardButton(text = del_text, callback_data = 'delete_all'), width = 1)
#         keyboard.row(InlineKeyboardButton(text = '⏪Выйти', callback_data = 'cart_exit'), width = 1)
#         print(f'RESULT TEXT {cart_text}')
#         if get_text: return output_text
#         if order: return int(total_cost)
#         else: return output_text, keyboard.as_markup()
#     elif not total_cost and message_cart:
#         return None, None
#     else:
#         await del_cart(tg_id)
#         return None, None

# async def get_payment_buttons(order_number, anon: int):
#     keyboard = InlineKeyboardBuilder()
#     keyboard.add(InlineKeyboardButton(text = 'Онлайн', callback_data = f'online_payment#{order_number}/{anon}'))
#     keyboard.add(InlineKeyboardButton(text = 'В отделении', callback_data = f'offline_payment#{order_number}/{anon}'))
#     return keyboard.as_markup()



# class Pagination(CallbackData, prefix = 'pag'):
#     action: str
#     query: str
#     page: int
#     all_pages: int
#     many: int
    
    
# def paginator(query: str, all_pages: int, page: int = 1, item_id: int = 0, what_is: str = 'none', many: bool = False):
#     builder = InlineKeyboardBuilder()
#     if not many:
#         builder.add(InlineKeyboardButton(text = '🛒В корзину', callback_data = f'search-item_id/{what_is}#{item_id}'))
#     if page == 1:
#         prev_page = '⛔️'
#         prev_cb_data = 'stop_stop'
#         next_page = '➡️'
#         next_cb_data = Pagination(query = query, action = 'next', page = page, all_pages = all_pages, many = int(many)).pack()
#     elif page == all_pages:
#         next_page = '⛔️'
#         next_cb_data = 'stop_stop'
#         prev_page = '⬅️'
#         prev_cb_data = Pagination(query = query, action = 'prev', page = page, all_pages = all_pages, many = int(many)).pack()
#     else: 
#         prev_page = '⬅️'
#         prev_cb_data = Pagination(query = query, action = 'prev', page = page, all_pages = all_pages, many = int(many)).pack()
#         next_page = '➡️'
#         next_cb_data = Pagination(query = query, action = 'next', page = page, all_pages = all_pages, many = int(many)).pack()
#     if all_pages > 1:
#         builder.row(
#             InlineKeyboardButton(text = prev_page, callback_data = prev_cb_data),
#             InlineKeyboardButton(text = f'{page}/{all_pages}', callback_data = Pagination(query = query, action = 'now', page = page, all_pages = all_pages, many = int(many)).pack()),
#             InlineKeyboardButton(text = next_page, callback_data = next_cb_data)
#         )
#     builder.add(InlineKeyboardButton(text = '⏪Выйти', callback_data = 'pag_exit'))
#     if not many: builder.adjust(1,3,1)
#     else: builder.adjust(3,1)
#     return builder.as_markup()



# def get_formating_cost(cost):
#     res_cost = ''
#     if len(str(cost).split('.')[0])  ==  4:
#         temp_cost = str(cost).split('.')[0]
#         res_cost = temp_cost[:1]+' '+temp_cost[1:]
#     elif len(str(cost).split('.')[0])  ==  5:
#         temp_cost = str(cost).split('.')[0]
#         res_cost = temp_cost[:2]+' '+temp_cost[2:]
#     elif len(str(cost).split('.')[0])  ==  6:
#         temp_cost = str(cost).split('.')[0]
#         res_cost = temp_cost[:3]+' '+temp_cost[3:]
#     else: res_cost = str(cost).split('.')[0]
#     return res_cost
