from sqlalchemy import Column, Integer, String, Text
from database import Base

class BookModel(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    author = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    summary = Column(Text, nullable=True)