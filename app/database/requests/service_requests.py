from sqlalchemy import select

from app.database.models import async_session
from app.database.models import Service_Category, Service_Subcategory, Service, Price_Service



async def get_service_categories(city_id, cat_id = None):
    async with async_session() as session:
        if cat_id:
            return await session.scalar(select(Service_Category).where(Service_Category.ID == cat_id))
        elif city_id:
            return await session.scalars(select(Service_Category).where(Service_Category.ID == Service.ServiceCategoryID).where(Price_Service.ServiceID == Service.ID).filter(Price_Service.CityID == city_id))

async def get_service_subcategories(service_category_id, city_id):
    async with async_session() as session:
        return await session.scalars(select(Service_Subcategory).where(Service_Subcategory.ID == Service.ServiceSubcategoryID).where(Price_Service.ServiceID == Service.ID).filter(Price_Service.CityID == city_id).where(Service.ServiceCategoryID == service_category_id))

async def get_service_subcategory_name(service_subcategory_id):
    async with async_session() as session:
        name = await session.scalar(select(Service_Subcategory.Name).where(Service_Subcategory.ID == service_subcategory_id))
        return name

async def get_services(service_category_id, service_subcategory_id, city_id):
    async with async_session() as session:
        return await session.scalars(select(Service).where(Service.ID == Price_Service.ServiceID).filter(Price_Service.CityID == city_id).where(Service.ServiceCategoryID == service_category_id).where(Service.ServiceSubcategoryID == service_subcategory_id))

async def get_service_data(service_id):
    async with async_session() as session:
        return await session.scalar(select(Service).where(Service.ID == service_id))

async def get_service_price(service_id, city_id):
    async with async_session() as session:
        return await session.scalar(select(Price_Service).where(Price_Service.CityID == city_id).where(Price_Service.ServiceID == service_id))

