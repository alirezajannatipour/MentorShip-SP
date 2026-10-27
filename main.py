from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator, ConfigDict
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import BookModel  # must be imported before create_all so the table is registered

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library API",
    description="A PostgreSQL-backed library management API built with FastAPI using secure environment variables.",
    version="1.0.0",
)


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(gt=0)
    summary: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    author: Optional[str] = Field(default=None, min_length=1, max_length=100)
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
    return db.query(BookModel).order_by(BookModel.id).all()


@app.post("/books", status_code=201, response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    new_book = BookModel(
        title=book.title,
        author=book.author,
        year=book.year,
        summary=book.summary,
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
