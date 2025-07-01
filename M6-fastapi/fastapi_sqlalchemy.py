"""
FastAPI + SQLAlchemy + MySQL
============================

Ejemplo didáctico para CRUD (solo Create + Read) de libros.
La BD `books_simple_db` se crea/puebla automáticamente mediante los scripts
en `seed/mysql_init/` del docker-compose del curso.

---------------------
"""

import secrets
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy import Integer, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)

# --------------------------------------------------------------------------- #
#               1. CONFIGURACIÓN DE BASE DE DATOS                             #
# --------------------------------------------------------------------------- #

DATABASE_URL = (
    "mysql+pymysql://example_user:example_password@127.0.0.1:3306/books_simple_db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarativa para los modelos ORM."""


class Book(Base):
    """Tabla `books` — un registro por libro."""

    __tablename__ = "books"

    id: Mapped[str] = mapped_column(
        String(24),
        primary_key=True,
        default=lambda: secrets.token_hex(12),
        comment="Clave primaria hexadecimal de 24 caracteres",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    pages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# --------------------------------------------------------------------------- #
#               2. ESQUEMAS Pydantic                                          #
# --------------------------------------------------------------------------- #

class BookCreate(BaseModel):
    """Payload de entrada para crear un libro."""
    title: str = Field(..., example="Clean Code")
    author: str = Field(..., example="Robert C. Martin")
    pages: int = Field(0, ge=0, example=464)


class BookResponse(BaseModel):
    """Objeto devuelto en las respuestas."""
    id: str
    title: str
    author: str
    pages: int

    class Config:
        from_attributes = True  # convierte Book (ORM) -> BookResponse


# --------------------------------------------------------------------------- #
#               3. DEPENDENCY: sesión de BD                                   #
# --------------------------------------------------------------------------- #

def get_db() -> Session:
    """Crea y cierra la sesión SQLAlchemy por petición."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DB = Annotated[Session, Depends(get_db)]  # azúcar sintáctico


# --------------------------------------------------------------------------- #
#               4. FastAPI + Endpoints                                        #
# --------------------------------------------------------------------------- #

app = FastAPI(
    title="Books API",
    description="Ejemplo de API REST para libros con FastAPI + MySQL",
    version="1.0.0",
    contact={"name": "Curso Python Avanzado", "email": "profe@example.com"},
    tags_metadata=[
        {"name": "books", "description": "Operaciones CRUD sobre libros"},
    ],
)


@app.post(
    "/books/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["books"],
    summary="Crear un libro",
    description="Inserta un nuevo libro y devuelve el registro completo.",
)
def create_book(book_in: BookCreate, db: DB):
    book = Book(**book_in.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@app.get(
    "/books/{book_id}",
    response_model=BookResponse,
    tags=["books"],
    summary="Obtener un libro por ID",
)
def get_book(
    book_id: Annotated[
        str,
        Path(description="ID hexadecimal de 24 caracteres", min_length=24, max_length=24),
    ],
    db: DB,
):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.get(
    "/books/",
    response_model=list[BookResponse],
    tags=["books"],
    summary="Listar todos los libros",
)
def list_books(db: DB):
    return db.query(Book).all()


# --------------------------------------------------------------------------- #
#               5. Punto de entrada                                           #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
