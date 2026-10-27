import os
from typing import List, Optional
from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class BookModel(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    author = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    summary = Column(Text, nullable=True)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library API",
    description="A PostgreSQL-backed library management API built with FastAPI using secure environment variables.",
    version="1.0.0",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    year: int = Field(gt=0)
    summary: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    author: Optional[str] = Field(default=None, min_length=1)
    year: Optional[int] = Field(default=None, gt=0)
    summary: Optional[str] = None

    @field_validator("title", "author", "year")
    @classmethod
    def required_fields_cannot_be_null(cls, value):
        if value is None:
            raise ValueError("This field cannot be null")
        return value


class Book(BookCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BookResponse(BaseModel):
    message: str
    book: Book


def find_book_or_404(db: Session, book_id: int) -> BookModel:
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.get("/books", response_model=List[Book])
def get_books(db: Session = Depends(get_db)):
    books = db.query(BookModel).all()
    return books


@app.post("/books", status_code=201, response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    new_book = BookModel(
        title=book.title,
        author=book.author,
        year=book.year,
        summary=book.summary
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return {"message": "Book created successfully", "book": new_book}


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return find_book_or_404(db, book_id)


@app.patch("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    book = find_book_or_404(db, book_id)
    
    update_data = book_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)
        
    db.commit()
    db.refresh(book)
    return {"message": "Book updated successfully", "book": book}


@app.delete("/books/{book_id}", response_model=BookResponse)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = find_book_or_404(db, book_id)
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully", "book": book}