import json
import segno
from os import mkdir
from io import BytesIO
from hashlib import sha256
from datetime import datetime
from sqlalchemy import select

from .city_requests import get_city_id

from app.database.models import async_session
from app.database.models import User, Research, Service, Price_Research, Price_Service, Action, Additional_Service, Price_Action, Price_Additional_Service



def get_hash_data(data):
    if isinstance(data, int):
        data = str(data)
    return sha256(data.encode("utf-8")).hexdigest()    

async def disconnect_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.ID == tg_id))
        if not user:
            return False
        user.PhoneHash = None
        await session.commit()
        return True

async def set_user(tg_id, username = None, city_id = 0, phone_number = None):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.ID == tg_id))
        if not user:
            if city_id !=  0:
                session.add(User(ID = tg_id, UserName = username, RegDate = datetime.now(), PhoneHash = phone_number, QR = False, Admin = False, Ban = False, CityID = int(city_id), CardHash = None))
                await session.commit()
                return False, False
            else:
                return False, False
        else:
            phone = user.PhoneHash
            if phone_number !=  None:
                user.PhoneHash = phone_number
                await session.commit()
            else:
                if phone !=  None: 
                    return True, True
                else: return True, False

async def for_get_cart_and_order_data(user, data, with_add_serv, action):
    async with async_session() as session:
        researches = {}
        services = {}
        actions = {}
        additional_services = {}
        if with_add_serv:
            if not action:
                for research_as_id in data.split(','):
                    if '/' in research_as_id:
                        research_id = int(research_as_id.split('/')[0])
                        add_serv_id = int(research_as_id.split('/')[1])
                        add_serv_name = await session.scalar(select(Additional_Service.Name).where(Additional_Service.ID == add_serv_id))
                        add_serv_price = await session.scalar(select(Price_Additional_Service.Cost).filter(Price_Additional_Service.CityID == user.CityID).where(Price_Additional_Service.AdditionalServiceID == add_serv_id))
                        additional_services[add_serv_id] = [add_serv_name, add_serv_price]
                    else: 
                        research_id = int(research_as_id)
                        additional_services = None
                    research_name = await session.scalar(select(Research.Name).where(Research.ID == research_id))
                    research_price = await session.scalar(select(Price_Research.Cost).filter(Price_Research.CityID == user.CityID).where(Price_Research.ResearchID == research_id))
                    researches[research_id] = [research_name, research_price]
                return researches, additional_services
            else:
                for action_as_id in data.split(','):
                    if '/' in action_as_id:
                        action_id = int(action_as_id.split('/')[0])
                        add_serv_id = int(action_as_id.split('/')[1])
                        add_serv_name = await session.scalar(select(Additional_Service.Name).where(Additional_Service.ID == add_serv_id))
                        add_serv_price = await session.scalar(select(Price_Additional_Service.Cost).filter(Price_Additional_Service.CityID == user.CityID).where(Price_Additional_Service.AdditionalServiceID == add_serv_id))
                        additional_services[add_serv_id] = [add_serv_name, add_serv_price]
                    else: 
                        action_id = int(action_as_id)
                        additional_services = None
                    action_name = await session.scalar(select(Action.Name).where(Action.ID == action_id))
                    action_price = await session.scalar(select(Price_Action.Cost).where(Price_Action.ActionID == action_id))
                    actions[action_id] = [action_name, action_price]
                return actions, additional_services
        else:
            for service_id in data.split(','):
                service_name = await session.scalar(select(Service.Name).where(Service.ID == int(service_id)))
                service_price = await session.scalar(select(Price_Service.Cost).filter(Price_Service.CityID == user.CityID).where(Price_Service.ServiceID == int(service_id)))
                services[int(service_id)] = [service_name, service_price]
            return services

async def get_QR_code(tg_id, id_card = None, order_num = None, dont_need_bool = None):
    boolQR = None
    qr_buffer = BytesIO()
    if id_card: 
        boolQR = True
        CardID = id_card
        OrderNumber = None
    else: 
        CardID = id_card
        if order_num: OrderNumber = get_hash_data(order_num)
        else: OrderNumber = order_num
    if tg_id: TelegramID = get_hash_data(tg_id)
    else: TelegramID = tg_id
    dict_data = {'CardID': CardID, 'TelegramID': TelegramID, 'OrderNumber': OrderNumber}
    json_data = json.dumps(dict_data)
    qrcode = segno.make_qr(json_data)
    try: mkdir('.temp')
    except: pass
    qrcode.save(qr_buffer, kind='png', dark = '#007934', border = 6, scale = 10)
    # qrcode.show()
    if dont_need_bool: return qr_buffer
    else: return boolQR, qr_buffer

async def get_hashid_card(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User.CardHash).where(User.ID == tg_id))

async def get_search(tg_id, text, notice = False):
    async with async_session() as session:
        city_id = await get_city_id(tg_id)
        researches_list = []
        services_list = []
        result_researches = await session.scalars(select(Research).where(Research.ID == Price_Research.ResearchID).where(Price_Research.CityID == city_id).filter(Research.Name.ilike('%'+text+'%')))
        res_r_list = [[res_r.ID, res_r.Name] for res_r in result_researches]
        if len(res_r_list):
            result_rprices = await session.scalars(select(Price_Research.Cost).where(Research.ID == Price_Research.ResearchID).where(Price_Research.CityID == city_id).filter(Research.Name.ilike('%'+text+'%')))
            res_rp_list = [res_p for res_p in result_rprices]
            i = 0
            for res_r in res_r_list:
                researches_list.append([res_r[0], res_r[1], res_rp_list[i], 'research'])
                i += 1
        result_services = await session.scalars(select(Service).where(Service.ID == Price_Service.ServiceID).where(Price_Service.CityID == city_id).filter(Service.Name.ilike('%'+text+'%')))
        res_s_list = [[res_s.ID, res_s.Name] for res_s in result_services]
        if len(res_s_list):
            result_sprices = await session.scalars(select(Price_Service.Cost).where(Service.ID == Price_Service.ServiceID).where(Price_Service.CityID == city_id).filter(Service.Name.ilike('%'+text+'%')))
            res_sp_list = [res_p for res_p in result_sprices]
            i = 0
            for res_s in res_s_list:
                services_list.append([res_s[0], res_s[1], res_sp_list[i], 'service'])
                i += 1
        if not notice: return researches_list, services_list
        else: return researches_list# добавление в корзину исследования или услуги






# async def add_to_cart(tg_id, Rid = None, Sid = None, Aid = None):
#     async with async_session() as session:
#         # сделать отдельные колонки для услуг и исследований в таблице CART
#         print(f'TelegramINFO [ADD TO CART]: Rid: {Rid}, Sid: {Sid}, Aid: {Aid}')
#         city_id = await get_city_id(tg_id)
#         cart = await session.scalar(select(Cart).where(Cart.UserID == tg_id))
#         researchid_str = None
#         serviceid_str = None
#         actionid_str = None
#         # cost = None
#         if Rid !=  None:
#             add_serv_id = await session.scalar(select(Research_Additional_Service.AdditionalServiceID).where(Research_Additional_Service.ResearchID == Rid))
#             cost_research = await session.scalar(select(Price_Research.Cost).filter(Price_Research.CityID == city_id).where(Price_Research.ResearchID == Rid))
#             cost_add_serv = await session.scalar(select(Price_Additional_Service.Cost).filter(Price_Additional_Service.CityID == city_id).where(Price_Additional_Service.AdditionalServiceID == add_serv_id))
#             print(f'TelegramINFO [ADD TO CART]: Research ID: {Rid}, Additional Service ID: {add_serv_id}\nResearch Cost: {cost_research}, Additional Service Cost: {cost_add_serv}')
#             if add_serv_id:
#                 researchid_str = str(f'{Rid}/{add_serv_id}')
#                 if cart and cart.ResearchIDs:
#                     resids = cart.ResearchIDs.split(',')
#                     for resid in resids:
#                         if '/' in resid:
#                             buf_add_serv_id = resid.split('/')[1]
#                             if add_serv_id == int(buf_add_serv_id): 
#                                 # print('ДОПОЛНИТЕЛЬНАЯ УСЛУГА УЖЕ ЕСТЬ')
#                                 cost = cost_research
#                                 break
#                             else: cost = cost_research + cost_add_serv
#                 else: cost = cost_research + cost_add_serv
#             else:
#                 researchid_str = str(Rid)
#                 cost = cost_research
#             # print(f'\nRESEARCH PRICE {cost_research}\nADDITIONAL SERVICE PRICE {cost_add_serv}\nSUM COST {cost}\n')
#         if Sid !=  None:
#             cost = await session.scalar(select(Price_Service.Cost).filter(Price_Service.CityID == city_id).where(Price_Service.ServiceID == Sid))
#             serviceid_str = str(Sid)
#         if Aid !=  None:
#             add_serv_id = await session.scalar(select(Action_Additional_Service.AdditionalServiceID).where(Action_Additional_Service.ActionID == Aid))
#             cost_action = await session.scalar(select(Price_Action.Cost).where(Price_Action.ActionID == Aid))
#             cost_add_serv = await session.scalar(select(Price_Additional_Service.Cost).filter(Price_Additional_Service.CityID == city_id).where(Price_Additional_Service.AdditionalServiceID == add_serv_id))
#             if add_serv_id:
#                 actionid_str = str(f'{Aid}/{add_serv_id}')
#                 if cart and cart.ActionIDs:
#                     actids = cart.ActionIDs.split(',')
#                     for actid in actids:
#                         if '/' in actid:
#                             buf_add_serv_id = actid.split('/')[1]
#                             if add_serv_id == int(buf_add_serv_id): 
#                                 # print('ДОПОЛНИТЕЛЬНАЯ УСЛУГА УЖЕ ЕСТЬ')
#                                 cost = cost_action
#                                 break
#                             else: cost = cost_action + cost_add_serv
#                 else: cost = cost_action + cost_add_serv
#             else:
#                 actionid_str = str(Aid)
#                 cost = cost_action
#         # добавление первый раз
#         if not cart:
#             session.add(Cart(ResearchIDs = researchid_str, ServiceIDs = serviceid_str, ActionIDs = actionid_str, TotalCost = cost, UserID = tg_id))
#             print(f'TelegramINFO [SESSION ADD]: Data: RIDs = {researchid_str}, SIDs = {serviceid_str}, AIDs = {actionid_str}, TotalCost = {cost}, UserID = {tg_id}')
#             await session.commit()
#             return True
#         # пополнение уже существующей корзины
#         else:
#             if cart.ResearchIDs:
#                 # проверка на уже добавленное исследование
#                 for item in cart.ResearchIDs.split(','):
#                     if item == researchid_str:
#                         await session.commit()
#                         return False
#                 if researchid_str:
#                     cart.ResearchIDs = ','.join([cart.ResearchIDs, researchid_str])
#                     print(f'TelegramINFO [ADD NEW INFO] {researchid_str}\nRESULT {cart.ResearchIDs}')
#             else: 
#                 print('::WHAT?')
#                 cart.ResearchIDs = researchid_str
#             if cart.ServiceIDs:
#                 for item in cart.ServiceIDs.split(','):
#                     if item == serviceid_str:
#                         await session.commit()
#                         return False
#                 if serviceid_str: 
#                     cart.ServiceIDs = ','.join([cart.ServiceIDs, serviceid_str])
#                     print(f'TelegramINFO [ADD NEW INFO] {serviceid_str}\nRESULT {cart.ServiceIDs}')
#             else: 
#                 print('::WHAT?')
#                 cart.ServiceIDs = serviceid_str
#             if cart.ActionIDs:
#                 for item in cart.ActionIDs.split(','):
#                     if item == actionid_str:
#                         await session.commit()
#                         return False
#                 if actionid_str: 
#                     cart.ActionIDs = ','.join([cart.ActionIDs, actionid_str])
#                     print(f'TelegramINFO [ADD NEW INFO] {actionid_str}\nRESULT {cart.ActionIDs}')
#             else: cart.ActionIDs = actionid_str
#             if cost:
#                 cart.TotalCost = cart.TotalCost + cost
#             await session.commit()
#             return True


# вывод данных корзины пользователя
# async def get_cart(tg_id):
#     async with async_session() as session:
#         researches = {}
#         services = {}
#         actions = {}
#         additional_services = {}
#         user = await session.scalar(select(User).where(User.ID == tg_id))
#         cart = await session.scalar(select(Cart).where(Cart.UserID == tg_id))
#         if cart:
#             if cart.ResearchIDs:
#                 researches, additional_services = await for_get_cart_and_order_data(user, cart.ResearchIDs, True, False)
#             elif additional_services !=  None and len(additional_services) == 0: 
#                 additional_services = None
#             if not cart.ResearchIDs:
#                 researches = None
#             if cart.ServiceIDs:
#                 services = await for_get_cart_and_order_data(user, cart.ServiceIDs, False, False)
#             else: services = None
#             if cart.ActionIDs:
#                 actions, additional_services = await for_get_cart_and_order_data(user, cart.ActionIDs, True, True)
#             elif additional_services !=  None and len(additional_services) == 0: 
#                 additional_services = None
#             if not cart.ActionIDs:
#                 actions = None
#             total_cost = cart.TotalCost
#             # print(f'TelegramINFO [GET CART]: Return\nList of researches {researches}\nList of additional services {additional_services}\nList of services {services}\nList of actions {actions}')
#             return researches, additional_services, services, actions, total_cost
#         else: return None, None, None, None, None

# изменение состава корзины (удаление из корзины услуги или исследования)        
# async def edit_cart(tg_id, item_id, what_is):
#     async with async_session() as session:
#         # total_cost не меняется, реализовать
#         city_id = await session.scalar(select(User.CityID).where(User.ID == tg_id))
#         cart = await session.scalar(select(Cart).where(Cart.UserID == tg_id))
#         add_serv_ids = []
#         if cart:
#             if what_is == 'research':
#                 res_ids = []
#                 if ',' in cart.ResearchIDs:
#                     list_resids = cart.ResearchIDs.split(',')
#                 else:
#                     list_resids = [cart.ResearchIDs]
#                 for add_serv_id in list_resids:
#                     add_serv_ids.append(add_serv_id.split('/')[1])
#                 for list_item in list_resids:
#                     if '/' in list_item:
#                         if list_item.split('/')[0] !=  item_id:
#                             res_ids.append(list_item)
#                         else:
#                             res_price = await session.scalar(select(Price_Research.Cost).filter(Price_Research.CityID == city_id).where(Price_Research.ResearchID == int(item_id)))
#                             cart.TotalCost = cart.TotalCost - res_price
#                             if add_serv_ids.count(list_item.split('/')[1]) == 1:
#                                 add_serv_price = await session.scalar(select(Price_Additional_Service.Cost).filter(Price_Additional_Service.CityID == city_id).where(Price_Additional_Service.AdditionalServiceID == int(list_item.split('/')[1])))
#                                 cart.TotalCost = cart.TotalCost - add_serv_price
#                     else:
#                         if list_item !=  item_id:
#                             res_ids.append(list_item)
#                         else: 
#                             res_price = await session.scalar(select(Price_Research.Cost).filter(Price_Research.CityID == city_id).where(Price_Research.ResearchID == int(item_id)))
#                             cart.TotalCost = cart.TotalCost - res_price
#                 if len(res_ids) > 1: cart.ResearchIDs = ','.join(res_ids)
#                 elif len(res_ids) == 1: cart.ResearchIDs = res_ids[0]
#                 else: cart.ResearchIDs = None
#                 await session.commit()
#             elif what_is == 'service':
#                 serv_ids = []
#                 if ',' in cart.ServiceIDs:
#                     list_servids = cart.ServiceIDs.split(',')
#                 else:
#                     list_servids = [cart.ServiceIDs]
#                 for list_item in list_servids:
#                     if list_item !=  item_id:
#                         serv_ids.append(list_item)
#                     else:
#                         serv_price = await session.scalar(select(Price_Service.Cost).filter(Price_Service.CityID == city_id).where(Price_Service.ServiceID == int(item_id)))
#                         cart.TotalCost = cart.TotalCost - serv_price
#                 if len(serv_ids) > 1: cart.ServiceIDs = ','.join(serv_ids)
#                 elif len(serv_ids) == 1: cart.ServiceIDs = serv_ids[0]
#                 else: cart.ServiceIDs = None
#                 await session.commit()
#             elif what_is == 'action':
#                 act_ids = []
#                 if ',' in cart.ActionIDs:
#                     list_actids = cart.ActionIDs.split(',')
#                 else:
#                     list_actids = [cart.ActionIDs]
#                 for add_serv_id in list_actids:
#                     add_serv_ids.append(add_serv_id.split('/')[1])
#                 for list_item in list_actids:
#                     if '/' in list_item:
#                         if list_item.split('/')[0] !=  item_id:
#                             act_ids.append(list_item)
#                         else:
#                             act_price = await session.scalar(select(Price_Action.Cost).where(Price_Action.ActionID == int(item_id)))
#                             cart.TotalCost = cart.TotalCost - act_price
#                             if add_serv_ids.count(list_item.split('/')[1]) == 1:
#                                 add_serv_price = await session.scalar(select(Price_Additional_Service.Cost).filter(Price_Additional_Service.CityID == city_id).where(Price_Additional_Service.AdditionalServiceID == int(list_item.split('/')[1])))
#                                 cart.TotalCost = cart.TotalCost - add_serv_price
#                     else:
#                         if list_item !=  item_id:
#                             act_ids.append(list_item)
#                         else: 
#                             act_price = await session.scalar(select(Price_Action.Cost).where(Price_Action.ActionID == int(item_id)))
#                             cart.TotalCost = cart.TotalCost - act_price
#                 if len(act_ids) > 1: cart.ActionIDs = ','.join(act_ids)
#                 elif len(act_ids) == 1: cart.ActionIDs = act_ids[0]
#                 else: cart.ActionIDs = None
#                 await session.commit()
                    
# async def del_cart(tg_id):
#     async with async_session() as session:
#         cart = await session.scalar(select(Cart).where(Cart.UserID == tg_id))
#         await session.delete(cart)
#         await session.commit()


# # пользователь нажал на кнопку оформить закза
# async def place_order(tg_id, order_num = None, paid = None, anon = None):
#     async with async_session() as session:
#         user = await session.scalar(select(User).where(User.ID == tg_id))
#         print(f'USER QR {user.QR}')
#         if order_num:
#             cart = await session.scalar(select(Cart).where(Cart.UserID == tg_id))
#             order = await session.scalar(select(Order).where(Order.OrderNum == order_num).where(Order.UserID == tg_id))
#             if not order:
#                 if cart:
#                     session.add(Order(OrderNum = order_num, RegistrationDate = datetime.now(), DateStart = None, ServiceIDs = cart.ServiceIDs, 
#                                     ResearchIDs = cart.ResearchIDs, ActionIDs = cart.ActionIDs, TotalCost = cart.TotalCost, Paid = paid, 
#                                     Status = None, UserID = tg_id, Anon = bool(int(anon))))
#                     await session.delete(cart)
#                     # await session.commit()
#                     if not user.CardHash:
#                         qr, buff = await get_QR_code(tg_id = tg_id, order_num = order_num)
#                         user.QR = qr
#                         await session.commit()
#                         return buff
#                     else: 
#                         await session.commit()
#                         return
#         else:
#             if user.CardHash:
#                 qr, buff = await get_QR_code(tg_id = tg_id, id_card = user.CardHash)
#                 user.QR = qr
#                 await session.commit()
#                 return buff

# async def get_order_number(num):
#     async with async_session() as session:
#         order = await session.scalar(select(Order.OrderNum).where(Order.OrderNum == num))
#         if order:
#             return False
#         else: return True

# async def get_orders(tg_id, order_id = False):
#     async with async_session() as session:
#         if order_id:
#             return await session.scalar(select(Order).where(Order.ID == order_id).where(Order.UserID == tg_id))
#         else:
#             return await session.scalars(select(Order).order_by(desc(Order.RegistrationDate)).where(Order.UserID == tg_id))

# async def get_order_data(tg_id, order):
#     async with async_session() as session:
#         researches = {}
#         services = {}
#         actions = {}
#         additional_services = {}
#         user = await session.scalar(select(User).where(User.ID == tg_id))
#         if order:
#             if order.ResearchIDs:
#                 researches, additional_services = await for_get_cart_and_order_data(user, order.ResearchIDs, True, False)
#             elif additional_services !=  None and len(additional_services) == 0:
#                 additional_services = None
#             if not order.ResearchIDs:
#                 researches = None
#             if order.ServiceIDs:
#                 services = await for_get_cart_and_order_data(user, order.ServiceIDs, False, False)
#             else: services = None
#             if order.ActionIDs:
#                 actions, additional_services = await for_get_cart_and_order_data(user, order.ActionIDs, True, True)
#             elif additional_services !=  None and len(additional_services) == 0:
#                 additional_services = None
#             if not order.ActionIDs:
#                 actions = None
#             total_cost = order.TotalCost
#             return researches, additional_services, services, actions, total_cost
#         else: return None, None, None, None, None




# async def get_cities():
#     async with async_session() as session:
#         return await session.scalars(select(City))

# async def get_research_categories(city_id, cat_id = None):
#     async with async_session() as session:
#         if cat_id:
#             return await session.scalar(select(Research_Category).where(Research_Category.ID == cat_id))
#         elif city_id: 
#             return await session.scalars(select(Research_Category).where(Research_Category.ID == Research.ResearchCategoryID).where(Price_Research.ResearchID == Research.ID).filter(Price_Research.CityID == city_id))
#             # for r in res:
#             #     print(f'\nRES == {r.ID}, {r.Name}')
#             # return await session.scalars(select(Research_Category))

# async def get_service_categories(city_id, cat_id = None):
#     async with async_session() as session:
#         if cat_id:
#             return await session.scalar(select(Service_Category).where(Service_Category.ID == cat_id))
#         elif city_id:
#             return await session.scalars(select(Service_Category).where(Service_Category.ID == Service.ServiceCategoryID).where(Price_Service.ServiceID == Service.ID).filter(Price_Service.CityID == city_id))
            # for r in res:
            #     print(f'\nRES == {r.ID}, {r.Name}')
            # return await session.scalars(select(Service_Category))

# async def get_action_categories(cat_id = None):
#     async with async_session() as session:
#         if cat_id:
#             return await session.scalar(select(Action_Category).where(Action_Category.ID == cat_id))
#         else:
#             return await session.scalars(select(Action_Category))
        
# async def get_research_subcategories(research_category_id, city_id):
#     async with async_session() as session:
#         return await session.scalars(select(Research_Subcategory).where(Research_Subcategory.ID == Research.ResearchSubcategoryID).where(Price_Research.ResearchID == Research.ID).filter(Price_Research.CityID == city_id).where(Research.ResearchCategoryID == research_category_id))
        # subquery = select(Research.ResearchSubcategoryID).where(Research.ResearchCategoryID == research_category_id).exists()
        # for r in res:
        #     print(f'\nRES == {r.ID}, {r.Name}')
        # return await session.scalars(select(Research_Subcategory).where(Research_Subcategory.ID == Research.ResearchSubcategoryID).where(Research.ResearchCategoryID == research_category_id))

# async def get_research_subcategory_name(research_subcategory_id):
#     async with async_session() as session:
#         name = await session.scalar(select(Research_Subcategory.Name).where(Research_Subcategory.ID == research_subcategory_id))
#         return name
    
# async def get_service_subcategories(service_category_id, city_id):
#     async with async_session() as session:
#         return await session.scalars(select(Service_Subcategory).where(Service_Subcategory.ID == Service.ServiceSubcategoryID).where(Price_Service.ServiceID == Service.ID).filter(Price_Service.CityID == city_id).where(Service.ServiceCategoryID == service_category_id))
        # for r in res:
        #     print(f'\nRES == {r.ID}, {r.Name}')
        # return await session.scalars(select(Service_Subcategory).where(Service_Subcategory.ID == Service.ServiceSubcategoryID).where(Service.ServiceCategoryID == service_category_id))

# async def get_service_subcategory_name(service_subcategory_id):
#     async with async_session() as session:
#         name = await session.scalar(select(Service_Subcategory.Name).where(Service_Subcategory.ID == service_subcategory_id))
#         return name

# async def get_action_subcategories(action_category_id):
#     async with async_session() as session:
#         return await session.scalars(select(Action_Subcategory).where(Action_Subcategory.ActionCategoryID == action_category_id).where(Action_Subcategory.ID == Action.ActionSubcategoryID))

# async def get_action_subcategory_name(action_subcategory_id):
#     async with async_session() as session:
#         name = await session.scalar(select(Action_Subcategory.Name).where(Action_Subcategory.ID == action_subcategory_id))
#         return name
    
# async def get_researches(research_category_id, research_subcategory_id, city_id):
#     async with async_session() as session:
#         return await session.scalars(select(Research).where(Research.ID == Price_Research.ResearchID).filter(Price_Research.CityID == city_id).where(Research.ResearchCategoryID == research_category_id).where(Research.ResearchSubcategoryID == research_subcategory_id))
        # return await session.scalars(select(Research).where(Research.ResearchCategoryID == research_category_id).where(Research.ResearchSubcategoryID == research_subcategory_id))

# async def get_research_data(research_id):
#     async with async_session() as session:
#         return await session.scalar(select(Research).where(Research.ID == research_id))

# async def get_research_price(research_id, city_id):
#     async with async_session() as session:
#         return await session.scalar(select(Price_Research).where(Price_Research.CityID == city_id).where(Price_Research.ResearchID == research_id))

# async def get_services(service_category_id, service_subcategory_id, city_id):
#     async with async_session() as session:
#         return await session.scalars(select(Service).where(Service.ID == Price_Service.ServiceID).filter(Price_Service.CityID == city_id).where(Service.ServiceCategoryID == service_category_id).where(Service.ServiceSubcategoryID == service_subcategory_id))
        # return await session.scalars(select(Service).where(Service.ServiceCategoryID == service_category_id).where(Service.ServiceSubcategoryID == service_subcategory_id))

# async def get_service_data(service_id):
#     async with async_session() as session:
#         return await session.scalar(select(Service).where(Service.ID == service_id))

# async def get_service_price(service_id, city_id):
#     async with async_session() as session:
#         return await session.scalar(select(Price_Service).where(Price_Service.CityID == city_id).where(Price_Service.ServiceID == service_id))

# async def get_action_data(action_id):
#     async with async_session() as session:
#         return await session.scalar(select(Action).where(Action.ID == action_id))

# async def get_action_price(action_id):
#     async with async_session() as session:
#         return await session.scalar(select(Price_Action).where(Price_Action.ActionID == action_id))

# async def get_telemed_data():
#     async with async_session() as session:
#         return await session.execute(select(Service.ID, Service.Name, Telemed.URL).where(Telemed.ServiceID == Service.ID))

# async def get_actions(action_category_id, action_subcategory_id):
#     async with async_session() as session:
#         return await session.scalars(select(Action).where(Action.ActionCategoryID == action_category_id).where(Action.ActionSubcategoryID == action_subcategory_id))

# async def get_prices_researches(city_id):
#     async with async_session() as session:
#         return await session.scalars(select(Price_Research).where(Price_Research.CityID == city_id))


# async def get_city_id(tg_id, need_name = False):
#     async with async_session() as session:
#         print(f'[GET CITY ID] TGID {tg_id}')
#         if need_name:
#             city_id = await session.scalar(select(User.CityID).where(User.ID == tg_id))
#             city_name = await session.scalar(select(City.Name).where(City.ID == city_id))
#             return city_id, city_name
#         else: return await session.scalar(select(User.CityID).where(User.ID == tg_id))