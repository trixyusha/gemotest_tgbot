import os
from dotenv import load_dotenv

from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from datetime import datetime

# from config import DB_URL
load_dotenv()
# engine = create_async_engine(url = os.getenv('DB_URL'))
engine = create_async_engine(url = os.getenv('SQLALCHEMY_URL'))
# engine = create_async_engine(url = DB_URL, echo = True)

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass
    
class User(Base):
    __tablename__ = 'users'
        
    ID = mapped_column(BigInteger, primary_key = True)
    # TelegramID = mapped_column(BigInteger)
    UserName: Mapped[str] = mapped_column(nullable = True)
    RegDate: Mapped[datetime] = mapped_column()
    PhoneHash: Mapped[str] = mapped_column(nullable = True)
    QR: Mapped[bool] = mapped_column(nullable = True)
    Admin: Mapped[bool] = mapped_column()
    Ban: Mapped[bool] = mapped_column()
    CityID: Mapped[int] = mapped_column(ForeignKey('cities.ID'))
    CardHash: Mapped[str] = mapped_column(nullable = True)

class Cart(Base):
    __tablename__ = 'carts'
    
    ID: Mapped[int] = mapped_column(primary_key = True)
    ServiceIDs: Mapped[str] = mapped_column(nullable = True)
    ResearchIDs: Mapped[str] = mapped_column(nullable = True) # в скобках содержатся идентификаторы доп. услуг (взятие и т.д.)
    ActionIDs: Mapped[str] = mapped_column(nullable = True)
    TotalCost: Mapped[float] = mapped_column()
    UserID: Mapped[int] = mapped_column(ForeignKey('users.ID')) # это идентификатор телеграм
    # CityID: Mapped[int] = mapped_column(ForeignKey('cities.ID'))

class Order(Base):
    __tablename__ = 'orders'
    
    ID: Mapped[int] = mapped_column(primary_key = True)
    OrderNum: Mapped[str] = mapped_column()
    RegistrationDate: Mapped[datetime] = mapped_column() # дата оформления заказа онлайн
    DateStart: Mapped[datetime] = mapped_column(nullable = True) # дата прихода пациента в лабораторное отделение для исполнения заказа (дата начала исполнения заказа)
    ServiceIDs: Mapped[str] = mapped_column(nullable = True)
    ResearchIDs: Mapped[str] = mapped_column(nullable = True)
    ActionIDs: Mapped[str] = mapped_column(nullable = True)
    TotalCost: Mapped[float] = mapped_column()
    Paid: Mapped[bool] = mapped_column()
    Status: Mapped[bool] = mapped_column(nullable = True) # True - выполнен, False - выполняется, None - в ожидании
    UserID: Mapped[int] = mapped_column(ForeignKey('users.ID')) # это идентификатор телеграм
    Anon: Mapped[bool] = mapped_column()

class City(Base):
    __tablename__ = 'cities'
        
    ID: Mapped[int] = mapped_column(primary_key = True)
    Name: Mapped[str] = mapped_column()
    URL: Mapped[str] = mapped_column()
    
class Research_Category(Base):
    __tablename__ = 'researches_categories'
        
    ID: Mapped[int] = mapped_column(primary_key = True)
    Name: Mapped[str] = mapped_column()

class Service_Category(Base):
    __tablename__ = 'services_categories'
        
    ID: Mapped[int] = mapped_column(primary_key = True)
    Name: Mapped[str] = mapped_column()

class Action_Category(Base):
    __tablename__ = 'actions_categories'
        
    ID: Mapped[int] = mapped_column(primary_key = True)
    Name: Mapped[str] = mapped_column()

class Research_Subcategory(Base):
    __tablename__ = 'researches_subcategories'
        
    ID: Mapped[int] = mapped_column(primary_key = True)
    Name: Mapped[str] = mapped_column()
    ResearchCategoryID: Mapped[int] = mapped_column(ForeignKey('researches_categories.ID'))

class Service_Subcategory(Base):
    __tablename__ = 'services_subcategories'
        
    ID: Mapped[int] = mapped_column(primary_key = True)
    Name: Mapped[str] = mapped_column()
    ServiceCategoryID: Mapped[int] = mapped_column(ForeignKey('services_categories.ID'))
        
class Research(Base):
    __tablename__ = 'researches'
        
    ID: Mapped[int] = mapped_column(primary_key = True)
    Name: Mapped[str] = mapped_column()
    Description: Mapped[str] = mapped_column()
    ResearchCategoryID: Mapped[int] = mapped_column(ForeignKey('researches_categories.ID'))
    ResearchSubcategoryID: Mapped[int] = mapped_column(ForeignKey('researches_subcategories.ID'))
    
class Service(Base):
    __tablename__ = 'services'
        
    ID: Mapped[int] = mapped_column(primary_key = True)
    Name: Mapped[str] = mapped_column()
    ServiceCategoryID: Mapped[int] = mapped_column(ForeignKey('services_categories.ID'))
    ServiceSubcategoryID: Mapped[int] = mapped_column(ForeignKey('services_subcategories.ID'))

class Price_Research(Base):
    __tablename__ = 'prices_researches'
        
    ID: Mapped[int] = mapped_column(primary_key = True)
    Cost: Mapped[float] = mapped_column()
    CityID: Mapped[int] = mapped_column(ForeignKey('cities.ID'))
    ResearchID: Mapped[int] = mapped_column(ForeignKey('researches.ID'))

class Price_Service(Base):
    __tablename__ = 'prices_services'
        
    ID: Mapped[int] = mapped_column(primary_key = True)
    Cost: Mapped[float] = mapped_column()
    CityID: Mapped[int] = mapped_column(ForeignKey('cities.ID'))
    ServiceID: Mapped[int] = mapped_column(ForeignKey('services.ID'))

class Action(Base):
    __tablename__ = 'actions'
        
    ID: Mapped[int] = mapped_column(primary_key = True)
    Name: Mapped[str] = mapped_column()
    Description: Mapped[str] = mapped_column()
    ActionCategoryID: Mapped[int] = mapped_column(ForeignKey('actions_categories.ID'))
    ActionSubcategoryID: Mapped[int] = mapped_column(ForeignKey('actions_subcategories.ID'))

class Action_Subcategory(Base):
    __tablename__ = 'actions_subcategories'
    
    ID: Mapped[int] = mapped_column(primary_key = True)
    Name: Mapped[str] = mapped_column()
    ActionCategoryID: Mapped[int] = mapped_column(ForeignKey('actions_categories.ID'))

class Additional_Service(Base):
    __tablename__ = 'additional_services'
    
    ID: Mapped[int] = mapped_column(primary_key = True)
    Name: Mapped[str] = mapped_column()

class Price_Action(Base):
    __tablename__ = 'prices_actions'
    
    ID: Mapped[int] = mapped_column(primary_key = True)
    Cost: Mapped[float] = mapped_column()
    ActionID: Mapped[int] = mapped_column(ForeignKey('actions.ID'))

class Price_Additional_Service(Base):
    __tablename__ = 'prices_additional_services'
    
    ID: Mapped[int] = mapped_column(primary_key = True)
    Cost: Mapped[float] = mapped_column()
    CityID: Mapped[int] = mapped_column(ForeignKey('cities.ID'))
    AdditionalServiceID: Mapped[int] = mapped_column(ForeignKey('additional_services.ID'))

class Research_Additional_Service(Base):
    __tablename__ = 'researches_additional_services'
    
    ID: Mapped[int] = mapped_column(primary_key = True)
    AdditionalServiceID: Mapped[int] = mapped_column(ForeignKey('additional_services.ID'))
    ResearchID: Mapped[int] = mapped_column(ForeignKey('researches.ID'))

class Action_Additional_Service(Base):
    __tablename__ = 'actions_additional_services'
    
    ID: Mapped[int] = mapped_column(primary_key = True)
    AdditionalServiceID: Mapped[int] = mapped_column(ForeignKey('additional_services.ID'))
    ActionID: Mapped[int] = mapped_column(ForeignKey('actions.ID'))

class Telemed(Base):
    __tablename__ = 'telemed'
    
    ID: Mapped[int] = mapped_column(primary_key = True)
    URL: Mapped[str] = mapped_column()
    ServiceID: Mapped[int] = mapped_column(ForeignKey('services.ID'))

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)