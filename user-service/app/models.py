from sqlalchemy import Column, Integer, String
from .db import Base

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    display_name = Column(String)
    bio = Column(String)
    contact_email = Column(String)
