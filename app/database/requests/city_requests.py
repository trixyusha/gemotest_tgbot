from sqlalchemy import select

from app.database.models import User, City
from app.database.models import async_session




async def get_cities():
    async with async_session() as session:
        return await session.scalars(select(City))

async def get_city_id(tg_id, need_name = False):
    async with async_session() as session:
        print(f'[GET CITY ID] TGID {tg_id}')
        if need_name:
            city_id = await session.scalar(select(User.CityID).where(User.ID == tg_id))
            city_name = await session.scalar(select(City.Name).where(City.ID == city_id))
            return city_id, city_name
        else: return await session.scalar(select(User.CityID).where(User.ID == tg_id))
