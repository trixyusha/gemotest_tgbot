from sqlalchemy import select

from app.database.models import async_session
from app.database.models import Research_Category, Research_Subcategory, Research, Price_Research



async def get_research_categories(city_id, cat_id = None):
    async with async_session() as session:
        if cat_id:
            return await session.scalar(select(Research_Category).where(Research_Category.ID == cat_id))
        elif city_id: 
            return await session.scalars(select(Research_Category).where(Research_Category.ID == Research.ResearchCategoryID).where(Price_Research.ResearchID == Research.ID).filter(Price_Research.CityID == city_id))

async def get_research_subcategories(research_category_id, city_id):
    async with async_session() as session:
        return await session.scalars(select(Research_Subcategory).where(Research_Subcategory.ID == Research.ResearchSubcategoryID).where(Price_Research.ResearchID == Research.ID).filter(Price_Research.CityID == city_id).where(Research.ResearchCategoryID == research_category_id))

async def get_research_subcategory_name(research_subcategory_id):
    async with async_session() as session:
        name = await session.scalar(select(Research_Subcategory.Name).where(Research_Subcategory.ID == research_subcategory_id))
        return name

async def get_researches(research_category_id, research_subcategory_id, city_id):
    async with async_session() as session:
        return await session.scalars(select(Research).where(Research.ID == Price_Research.ResearchID).filter(Price_Research.CityID == city_id).where(Research.ResearchCategoryID == research_category_id).where(Research.ResearchSubcategoryID == research_subcategory_id))

async def get_research_data(research_id):
    async with async_session() as session:
        return await session.scalar(select(Research).where(Research.ID == research_id))

async def get_research_price(research_id, city_id):
    async with async_session() as session:
        return await session.scalar(select(Price_Research).where(Price_Research.CityID == city_id).where(Price_Research.ResearchID == research_id))

async def get_prices_researches(city_id):
    async with async_session() as session:
        return await session.scalars(select(Price_Research).where(Price_Research.CityID == city_id))
