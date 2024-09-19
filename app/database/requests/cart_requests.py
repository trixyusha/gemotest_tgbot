from sqlalchemy import select

from app.database.requests.main_requests import for_get_cart_and_order_data, get_city_id
# from city_requests import get_city_id

from app.database.models import async_session
from app.database.models import User, Price_Research, Price_Service, Price_Action, Price_Additional_Service, Research_Additional_Service, Cart, Action_Additional_Service



async def add_to_cart(tg_id, Rid = None, Sid = None, Aid = None):
    async with async_session() as session:
        # сделать отдельные колонки для услуг и исследований в таблице CART

        city_id = await get_city_id(tg_id)
        cart = await session.scalar(select(Cart).where(Cart.UserID == tg_id))
        researchid_str = None
        serviceid_str = None
        actionid_str = None
        # cost = None
        if Rid !=  None:
            add_serv_id = await session.scalar(select(Research_Additional_Service.AdditionalServiceID).where(Research_Additional_Service.ResearchID == Rid))
            cost_research = await session.scalar(select(Price_Research.Cost).filter(Price_Research.CityID == city_id).where(Price_Research.ResearchID == Rid))
            cost_add_serv = await session.scalar(select(Price_Additional_Service.Cost).filter(Price_Additional_Service.CityID == city_id).where(Price_Additional_Service.AdditionalServiceID == add_serv_id))
            if add_serv_id:
                researchid_str = str(f'{Rid}/{add_serv_id}')
                if cart and cart.ResearchIDs:
                    resids = cart.ResearchIDs.split(',')
                    for resid in resids:
                        if '/' in resid:
                            buf_add_serv_id = resid.split('/')[1]
                            if add_serv_id == int(buf_add_serv_id): 
                                cost = cost_research
                                break
                            else: cost = cost_research + cost_add_serv
                else: cost = cost_research + cost_add_serv
            else:
                researchid_str = str(Rid)
                cost = cost_research
            # print(f'\nRESEARCH PRICE {cost_research}\nADDITIONAL SERVICE PRICE {cost_add_serv}\nSUM COST {cost}\n')
        if Sid !=  None:
            cost = await session.scalar(select(Price_Service.Cost).filter(Price_Service.CityID == city_id).where(Price_Service.ServiceID == Sid))
            serviceid_str = str(Sid)
        if Aid !=  None:
            add_serv_id = await session.scalar(select(Action_Additional_Service.AdditionalServiceID).where(Action_Additional_Service.ActionID == Aid))
            cost_action = await session.scalar(select(Price_Action.Cost).where(Price_Action.ActionID == Aid))
            cost_add_serv = await session.scalar(select(Price_Additional_Service.Cost).filter(Price_Additional_Service.CityID == city_id).where(Price_Additional_Service.AdditionalServiceID == add_serv_id))
            if add_serv_id:
                actionid_str = str(f'{Aid}/{add_serv_id}')
                if cart and cart.ActionIDs:
                    actids = cart.ActionIDs.split(',')
                    for actid in actids:
                        if '/' in actid:
                            buf_add_serv_id = actid.split('/')[1]
                            if add_serv_id == int(buf_add_serv_id): 
                                # print('ДОПОЛНИТЕЛЬНАЯ УСЛУГА УЖЕ ЕСТЬ')
                                cost = cost_action
                                break
                            else: cost = cost_action + cost_add_serv
                else: cost = cost_action + cost_add_serv
            else:
                actionid_str = str(Aid)
                cost = cost_action
        # добавление первый раз
        if not cart:
            session.add(Cart(ResearchIDs = researchid_str, ServiceIDs = serviceid_str, ActionIDs = actionid_str, TotalCost = cost, UserID = tg_id))
            print(f'TelegramINFO [SESSION ADD]: Data: RIDs = {researchid_str}, SIDs = {serviceid_str}, AIDs = {actionid_str}, TotalCost = {cost}, UserID = {tg_id}')
            await session.commit()
            return True
        # пополнение уже существующей корзины
        else:
            if cart.ResearchIDs:
                # проверка на уже добавленное исследование
                for item in cart.ResearchIDs.split(','):
                    if item == researchid_str:
                        await session.commit()
                        return False
                if researchid_str:
                    cart.ResearchIDs = ','.join([cart.ResearchIDs, researchid_str])
                    print(f'TelegramINFO [ADD NEW INFO] {researchid_str}\nRESULT {cart.ResearchIDs}')
            else: 
                print('::WHAT?')
                cart.ResearchIDs = researchid_str
            if cart.ServiceIDs:
                for item in cart.ServiceIDs.split(','):
                    if item == serviceid_str:
                        await session.commit()
                        return False
                if serviceid_str: 
                    cart.ServiceIDs = ','.join([cart.ServiceIDs, serviceid_str])
                    print(f'TelegramINFO [ADD NEW INFO] {serviceid_str}\nRESULT {cart.ServiceIDs}')
            else: 
                print('::WHAT?')
                cart.ServiceIDs = serviceid_str
            if cart.ActionIDs:
                for item in cart.ActionIDs.split(','):
                    if item == actionid_str:
                        await session.commit()
                        return False
                if actionid_str: 
                    cart.ActionIDs = ','.join([cart.ActionIDs, actionid_str])
                    print(f'TelegramINFO [ADD NEW INFO] {actionid_str}\nRESULT {cart.ActionIDs}')
            else: cart.ActionIDs = actionid_str
            if cost:
                cart.TotalCost = cart.TotalCost + cost
            await session.commit()
            return True

async def get_cart(tg_id):
    async with async_session() as session:
        researches = {}
        services = {}
        actions = {}
        additional_services = {}
        user = await session.scalar(select(User).where(User.ID == tg_id))
        cart = await session.scalar(select(Cart).where(Cart.UserID == tg_id))
        if cart:
            if cart.ResearchIDs:
                researches, additional_services = await for_get_cart_and_order_data(user, cart.ResearchIDs, True, False)
            elif additional_services !=  None and len(additional_services) == 0: 
                additional_services = None
            if not cart.ResearchIDs:
                researches = None
            if cart.ServiceIDs:
                services = await for_get_cart_and_order_data(user, cart.ServiceIDs, False, False)
            else: services = None
            if cart.ActionIDs:
                actions, additional_services = await for_get_cart_and_order_data(user, cart.ActionIDs, True, True)
            elif additional_services !=  None and len(additional_services) == 0: 
                additional_services = None
            if not cart.ActionIDs:
                actions = None
            total_cost = cart.TotalCost
            # print(f'TelegramINFO [GET CART]: Return\nList of researches {researches}\nList of additional services {additional_services}\nList of services {services}\nList of actions {actions}')
            return researches, additional_services, services, actions, total_cost
        else: return None, None, None, None, None

async def edit_cart(tg_id, item_id, what_is):
    async with async_session() as session:
        # total_cost не меняется, реализовать
        city_id = await session.scalar(select(User.CityID).where(User.ID == tg_id))
        cart = await session.scalar(select(Cart).where(Cart.UserID == tg_id))
        add_serv_ids = []
        if cart:
            if what_is == 'research':
                res_ids = []
                if ',' in cart.ResearchIDs:
                    list_resids = cart.ResearchIDs.split(',')
                else:
                    list_resids = [cart.ResearchIDs]
                for add_serv_id in list_resids:
                    add_serv_ids.append(add_serv_id.split('/')[1])
                for list_item in list_resids:
                    if '/' in list_item:
                        if list_item.split('/')[0] !=  item_id:
                            res_ids.append(list_item)
                        else:
                            res_price = await session.scalar(select(Price_Research.Cost).filter(Price_Research.CityID == city_id).where(Price_Research.ResearchID == int(item_id)))
                            cart.TotalCost = cart.TotalCost - res_price
                            if add_serv_ids.count(list_item.split('/')[1]) == 1:
                                add_serv_price = await session.scalar(select(Price_Additional_Service.Cost).filter(Price_Additional_Service.CityID == city_id).where(Price_Additional_Service.AdditionalServiceID == int(list_item.split('/')[1])))
                                cart.TotalCost = cart.TotalCost - add_serv_price
                    else:
                        if list_item !=  item_id:
                            res_ids.append(list_item)
                        else: 
                            res_price = await session.scalar(select(Price_Research.Cost).filter(Price_Research.CityID == city_id).where(Price_Research.ResearchID == int(item_id)))
                            cart.TotalCost = cart.TotalCost - res_price
                if len(res_ids) > 1: cart.ResearchIDs = ','.join(res_ids)
                elif len(res_ids) == 1: cart.ResearchIDs = res_ids[0]
                else: cart.ResearchIDs = None
                await session.commit()
            elif what_is == 'service':
                serv_ids = []
                if ',' in cart.ServiceIDs:
                    list_servids = cart.ServiceIDs.split(',')
                else:
                    list_servids = [cart.ServiceIDs]
                for list_item in list_servids:
                    if list_item !=  item_id:
                        serv_ids.append(list_item)
                    else:
                        serv_price = await session.scalar(select(Price_Service.Cost).filter(Price_Service.CityID == city_id).where(Price_Service.ServiceID == int(item_id)))
                        cart.TotalCost = cart.TotalCost - serv_price
                if len(serv_ids) > 1: cart.ServiceIDs = ','.join(serv_ids)
                elif len(serv_ids) == 1: cart.ServiceIDs = serv_ids[0]
                else: cart.ServiceIDs = None
                await session.commit()
            elif what_is == 'action':
                act_ids = []
                if ',' in cart.ActionIDs:
                    list_actids = cart.ActionIDs.split(',')
                else:
                    list_actids = [cart.ActionIDs]
                for add_serv_id in list_actids:
                    add_serv_ids.append(add_serv_id.split('/')[1])
                for list_item in list_actids:
                    if '/' in list_item:
                        if list_item.split('/')[0] !=  item_id:
                            act_ids.append(list_item)
                        else:
                            act_price = await session.scalar(select(Price_Action.Cost).where(Price_Action.ActionID == int(item_id)))
                            cart.TotalCost = cart.TotalCost - act_price
                            if add_serv_ids.count(list_item.split('/')[1]) == 1:
                                add_serv_price = await session.scalar(select(Price_Additional_Service.Cost).filter(Price_Additional_Service.CityID == city_id).where(Price_Additional_Service.AdditionalServiceID == int(list_item.split('/')[1])))
                                cart.TotalCost = cart.TotalCost - add_serv_price
                    else:
                        if list_item !=  item_id:
                            act_ids.append(list_item)
                        else: 
                            act_price = await session.scalar(select(Price_Action.Cost).where(Price_Action.ActionID == int(item_id)))
                            cart.TotalCost = cart.TotalCost - act_price
                if len(act_ids) > 1: cart.ActionIDs = ','.join(act_ids)
                elif len(act_ids) == 1: cart.ActionIDs = act_ids[0]
                else: cart.ActionIDs = None
                await session.commit()
                    
async def del_cart(tg_id):
    async with async_session() as session:
        cart = await session.scalar(select(Cart).where(Cart.UserID == tg_id))
        await session.delete(cart)
        await session.commit()
