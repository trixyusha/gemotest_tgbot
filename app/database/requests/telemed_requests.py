from sqlalchemy import select

from app.database.models import async_session
from app.database.models import Service, Telemed



async def get_telemed_data():
    async with async_session() as session:
        return await session.execute(select(Service.ID, Service.Name, Telemed.URL).where(Telemed.ServiceID == Service.ID))
