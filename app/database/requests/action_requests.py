from sqlalchemy import select

from app.database.models import async_session
from app.database.models import Action_Category, Action, Action_Subcategory, Price_Action



async def get_action_categories(cat_id = None):
    async with async_session() as session:
        if cat_id:
            return await session.scalar(select(Action_Category).where(Action_Category.ID == cat_id))
        else:
            return await session.scalars(select(Action_Category))

async def get_action_subcategories(action_category_id):
    async with async_session() as session:
        return await session.scalars(select(Action_Subcategory).where(Action_Subcategory.ActionCategoryID == action_category_id).where(Action_Subcategory.ID == Action.ActionSubcategoryID))

async def get_action_subcategory_name(action_subcategory_id):
    async with async_session() as session:
        name = await session.scalar(select(Action_Subcategory.Name).where(Action_Subcategory.ID == action_subcategory_id))
        return name

async def get_action_data(action_id):
    async with async_session() as session:
        return await session.scalar(select(Action).where(Action.ID == action_id))

async def get_action_price(action_id):
    async with async_session() as session:
        return await session.scalar(select(Price_Action).where(Price_Action.ActionID == action_id))

async def get_actions(action_category_id, action_subcategory_id):
    async with async_session() as session:
        return await session.scalars(select(Action).where(Action.ActionCategoryID == action_category_id).where(Action.ActionSubcategoryID == action_subcategory_id))
