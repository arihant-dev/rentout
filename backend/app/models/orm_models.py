from sqlalchemy import Column, Integer, String, Float, JSON # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore

Base = declarative_base()

class Property(Base):
    __tablename__ = "properties"
    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String)
    address = Column(String)
    price = Column(Float)
    meta = Column(JSON)