from app.database.models import async_session
from app.database.models import User, Research, Service, Price_Research, Price_Service, Action, Price_Action, Order

from sqlalchemy import select, func
from datetime import datetime, timedelta

async def get_nonadmin_ids():
    async with async_session() as session:
        return await session.scalars(select(User.ID).where(User.Admin == False))        

async def get_admin_ids():
    async with async_session() as session:
        return await session.scalars(select(User.ID).where(User.Admin == True))        

async def get_all_users():
    async with async_session() as session:
        return await session.scalars(select(User))

async def get_all_users_ids(block: bool | None):
    async with async_session() as session:
        if block == None: return await session.scalars(select(User.ID))
        elif block: return await session.scalars(select(User.ID).where(User.Ban == True))
        else: return await session.scalars(select(User.ID).where(User.Ban == False))

async def block_or_unblock_user(tg_id: int , block: bool):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.ID == tg_id))
        if user:
            if block:
                user.Ban = True
                await session.commit()
            else:
                user.Ban = False
                await session.commit()
            return True
        else: return False

async def count_of_users(new: bool, period: int = None) -> str: # 0 - сегодня, 1 - неделя, 2 - месяц
    async with async_session() as session:
        if not new:
            count = len([item for item in await session.scalars(select(User).where(User.Admin == False))])
            text = f'Всего пользователей бота: {count}'
        else:
            if period == 0:
                count = len([user for user in await session.scalars(select(User).where(User.Admin == False).where(func.DATE(User.RegDate) == datetime.today().date()))])
                text = f'Новых пользователей за сегодня: {count}'
            elif period == 1:
                count = len([item for item in await session.scalars(select(User).where(User.Admin == False).where(func.DATE(User.RegDate) >= (datetime.now()-timedelta(days = 7)).date()))])
                text = f'Новых пользователей за неделю: {count}'
            else:
                count = len([item for item in await session.scalars(select(User).where(User.Admin == False).where(func.DATE(User.RegDate) >= (datetime.now()-timedelta(days = 30)).date()))])
                text = f'Новых пользователей за месяц: {count}'
        return text

async def count_of_orders(period: int):
    async with async_session() as session:
        # orders = await session.scalars(select(Order))
        if period == 0:
            print(datetime.today().date())
            return len([item for item in await session.scalars(select(Order).where(func.DATE(Order.RegistrationDate) == datetime.today().date()))]), None
        elif period == 1:
            print((datetime.now()-timedelta(days = 7)).date())
            return (len([item for item in await session.scalars(select(Order).where(func.DATE(Order.RegistrationDate) >= (datetime.now()-timedelta(days = 7)).date()))]),
                    await session.scalars(select(Order.RegistrationDate).where(func.DATE(Order.RegistrationDate) >= (datetime.now()-timedelta(days = 7)).date())))
        elif period == 2:
            print((datetime.now()-timedelta(days = 30)).date())
            return (len([item for item in await session.scalars(select(Order).where(func.DATE(Order.RegistrationDate) >= (datetime.now()-timedelta(days = 30)).date()))]),
                    await session.scalars(select(Order.RegistrationDate).where(func.DATE(Order.RegistrationDate) >= (datetime.now()-timedelta(days = 30)).date())))
        
        else:
            print((datetime.now()-timedelta(days = 365)).date())
            return (len([item for item in await session.scalars(select(Order).where(func.DATE(Order.RegistrationDate) >= (datetime.now()-timedelta(days = 365)).date()))]),
                    await session.scalars(select(Order.RegistrationDate).where(func.DATE(Order.RegistrationDate) >= (datetime.now()-timedelta(days = 365)).date())))
        
async def get_all_orders():
    async with async_session() as session:
            return await session.scalars(select(Order))

async def get_top():
    async with async_session() as session:
        orders = await get_all_orders()
        if orders:
            order_researches = []
            order_actions = []
            order_services = []
            for order in orders:
                if order.ResearchIDs:
                    order_researches.append(await for_get_cart_and_order_data(order.ResearchIDs, True))
                if order.ActionIDs:
                    order_actions.append(await for_get_cart_and_order_data(order.ActionIDs, None))
                if order.ServiceIDs:
                    order_services.append(await for_get_cart_and_order_data(order.ServiceIDs, False))
            order_researches = [item for sublist in order_researches for item in sublist]
            order_actions = [item for sublist in order_actions for item in sublist]
            order_services = [item for sublist in order_services for item in sublist]
            duplicates_researches = list(set([(order_researches.count(x), x) for x in order_researches if order_researches.count(x) > 1]))
            duplicates_actions = list(set([(order_actions.count(x), x) for x in order_actions if order_actions.count(x) > 1]))
            duplicates_services = list(set([(order_services.count(x), x) for x in order_services if order_services.count(x) > 1]))
            # print(f'>>> GET TOP\n>>> RESEARCHES\n{order_researches}\n>>> ACTIONS\n{order_actions}\n>>> SERVICES\n{order_services}')
            # print(f'>>> GET TOP\n>>> DRESEARCHES\n{duplicates_researches}\n>>> DACTIONS\n{duplicates_actions}\n>>> DSERVICES\n{duplicates_services}')
            res = []
            if duplicates_researches or duplicates_actions or duplicates_services:
                for item in duplicates_researches+duplicates_actions+duplicates_services:
                    res += [item]
                # print('>>> RES LIST\n', res)
            else:
                for item in order_researches+order_actions+order_services:
                    res += [(1, item)]
                # print('>>> RES1 LIST\n', res)
            text = ''
            w = 0
            d_max = []
            dup_counts = [item[0] for item in res]
            # print('>>> DUP COUNTS: ', dup_counts)
            while w <=  max(dup_counts):
                temp = max(dup_counts)
                d_max.append(temp)
                dup_counts.remove(temp)
                if w < len(dup_counts): w += 1
                else: break
            # print('>>> MAXES: ', d_max)
            i = 1
            for maxi in d_max:
                for item in res:
                    if item[0]  ==  maxi:
                        # d_max.remove(item[0])
                        if item[1][1] in text:
                            continue
                        name = item[1][1].replace('*','"') if '*' in item[1][1] else item[1][1]
                        if i == 1:
                            text += f'{i}. {name} [{item[0]}]'
                            i += 1
                        else: 
                            text += f'\n{i}. {name} [{item[0]}]'
                            i += 1
                        break
            # print('>>> RES TEXT: ', text)
            return text
        else: return 'Пока заказы не оформляли'
        
async def for_get_cart_and_order_data(data, what): # research = True, action = None, service = False
    async with async_session() as session:
        researches = []
        services = []
        actions = []
        # print(f'>>> DATA {data}')
        if what:
            for research_id in data.split(','):
                if '/' in research_id:
                    research_id = int(research_id.split('/')[0])
                else: 
                    research_id = int(research_id)
                research_name = await session.scalar(select(Research.Name).where(Research.ID  ==  research_id))
                research_price = await session.scalar(select(Price_Research.Cost).where(Price_Research.ResearchID  ==  research_id))
                researches.append((research_id, research_name, research_price))
            return researches
        elif what  ==  None:
            for action_id in data.split(','):
                if '/' in action_id:
                    action_id = int(action_id.split('/')[0])
                else: 
                    action_id = int(action_id)
                action_name = await session.scalar(select(Action.Name).where(Action.ID  ==  action_id))
                action_price = await session.scalar(select(Price_Action.Cost).where(Price_Action.ActionID  ==  action_id))
                actions.append((action_id, action_name, action_price))
            return actions
        else:
            for service_id in data.split(','):
                service_name = await session.scalar(select(Service.Name).where(Service.ID  ==  int(service_id)))
                service_price = await session.scalar(select(Price_Service.Cost).where(Price_Service.ServiceID  ==  int(service_id)))
                services.append((int(service_id), service_name, service_price))
            return services
