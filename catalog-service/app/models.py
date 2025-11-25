from sqlalchemy import Column, Integer, String, Float
from .db import Base

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    author = Column(String)
    publisher = Column(String)
    genre = Column(String)
    price = Column(Float)
    description = Column(String)
