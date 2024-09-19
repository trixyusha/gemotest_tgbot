from datetime import datetime
from sqlalchemy import select, desc

from app.database.models import async_session
from app.database.models import User, Cart, Order
from app.database.requests.main_requests import for_get_cart_and_order_data, get_QR_code



async def place_order(tg_id, order_num = None, paid = None, anon = None):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.ID == tg_id))
        print(f'USER QR {user.QR}')
        if order_num:
            cart = await session.scalar(select(Cart).where(Cart.UserID == tg_id))
            order = await session.scalar(select(Order).where(Order.OrderNum == order_num).where(Order.UserID == tg_id))
            if not order:
                if cart:
                    session.add(Order(OrderNum = order_num, RegistrationDate = datetime.now(), DateStart = None, ServiceIDs = cart.ServiceIDs, 
                                    ResearchIDs = cart.ResearchIDs, ActionIDs = cart.ActionIDs, TotalCost = cart.TotalCost, Paid = paid, 
                                    Status = None, UserID = tg_id, Anon = bool(int(anon))))
                    await session.delete(cart)
                    # await session.commit()
                    if not user.CardHash:
                        qr, buff = await get_QR_code(tg_id = tg_id, order_num = order_num)
                        user.QR = qr
                        await session.commit()
                        return buff
                    else: 
                        await session.commit()
                        return
        else:
            if user.CardHash:
                qr, buff = await get_QR_code(tg_id = tg_id, id_card = user.CardHash)
                user.QR = qr
                await session.commit()
                return buff

async def get_order_number(num):
    async with async_session() as session:
        order = await session.scalar(select(Order.OrderNum).where(Order.OrderNum == num))
        if order:
            return False
        else: return True

async def get_orders(tg_id, order_id = False):
    async with async_session() as session:
        if order_id:
            return await session.scalar(select(Order).where(Order.ID == order_id).where(Order.UserID == tg_id))
        else:
            return await session.scalars(select(Order).order_by(desc(Order.RegistrationDate)).where(Order.UserID == tg_id))

async def get_order_data(tg_id, order):
    async with async_session() as session:
        researches = {}
        services = {}
        actions = {}
        additional_services = {}
        user = await session.scalar(select(User).where(User.ID == tg_id))
        if order:
            if order.ResearchIDs:
                researches, additional_services = await for_get_cart_and_order_data(user, order.ResearchIDs, True, False)
            elif additional_services !=  None and len(additional_services) == 0:
                additional_services = None
            if not order.ResearchIDs:
                researches = None
            if order.ServiceIDs:
                services = await for_get_cart_and_order_data(user, order.ServiceIDs, False, False)
            else: services = None
            if order.ActionIDs:
                actions, additional_services = await for_get_cart_and_order_data(user, order.ActionIDs, True, True)
            elif additional_services !=  None and len(additional_services) == 0:
                additional_services = None
            if not order.ActionIDs:
                actions = None
            total_cost = order.TotalCost
            return researches, additional_services, services, actions, total_cost
        else: return None, None, None, None, None
