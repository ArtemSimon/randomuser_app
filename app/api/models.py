from enum import Enum as PyEnum
from sqlalchemy import DateTime,ForeignKey,Text,Column,Integer,String,Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Gender(str, PyEnum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(UUID(as_uuid=True), unique=True, index=True)  # UUID из API
    gender = Column(Enum(Gender))
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)  # Формат: +XXXXXXXXXXX
    street = Column(String(100))
    city = Column(String(50))
    state = Column(String(50))
    country = Column(String(50))
    postcode = Column(String(20))
    picture_thumbnail = Column(String(200))
    profile_url = Column(String(200))