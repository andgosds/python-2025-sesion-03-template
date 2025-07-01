"""
Flask + SQLAlchemy + MySQL
==========================

Mini-API CRUD (Create + Read) de libros.

La base `books_simple_db` y el usuario `example_user` se crean desde el
`docker-compose` del curso; ajusta DATABASE_URL si usas otras credenciales.
"""

from __future__ import annotations

import secrets
from typing import Generator, List

from flask import Flask, abort, jsonify, request
from sqlalchemy import Integer, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)

# --------------------------------------------------------------------------- #
# 1. CONFIGURACIÓN DE BASE DE DATOS                                           #
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


# --------------------------------------------------------------------------- #
# 2. MODELO ORM                                                               #
# --------------------------------------------------------------------------- #

class Base(DeclarativeBase):
    pass


class Book(Base):
    """Tabla `books`."""

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


# Crea la tabla si aún no existe
Base.metadata.create_all(bind=engine)


# --------------------------------------------------------------------------- #
# 3. FACTORÍA / DEPENDENCIA DE SESIONES                                       #
# --------------------------------------------------------------------------- #

def get_db() -> Generator[Session, None, None]:
    """Sesión por petición (estilo FastAPI)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------------------------------- #
# 4. APP Y ENDPOINTS                                                          #
# --------------------------------------------------------------------------- #

app = Flask(__name__)


def to_dict(book: Book) -> dict:
    """Convierte Book (ORM) → dict serializable."""
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "pages": book.pages,
    }


@app.post("/books/")
def create_book():
    """Crear un libro."""
    payload = request.get_json(force=True) or {}
    for field in ("title", "author", "pages"):
        if field not in payload:
            abort(400, f"Missing field: {field}")

    with SessionLocal() as db:
        book = Book(**payload)
        db.add(book)
        db.commit()
        db.refresh(book)
        return jsonify(to_dict(book)), 201


@app.get("/books/<string:book_id>")
def get_book(book_id: str):
    """Obtener un libro por ID (hex 24)."""
    if len(book_id) != 24:
        abort(400, "ID must be 24-character hex")

    with SessionLocal() as db:
        book = db.get(Book, book_id)
        if book is None:
            abort(404, "Book not found")
        return jsonify(to_dict(book))


@app.get("/books/")
def list_books():
    """Listar todos los libros."""
    with SessionLocal() as db:
        books: List[Book] = db.query(Book).all()
        return jsonify([to_dict(b) for b in books])


# --------------------------------------------------------------------------- #
# 5. EJECUCIÓN DIRECTA                                                        #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    # `debug=True` recarga y muestra trazas como hacía uvicorn --reload
    app.run(host="0.0.0.0", port=5000, debug=True)
