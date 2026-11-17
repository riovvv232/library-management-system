import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

DB_PATH = Path(os.getenv("DATABASE_PATH", "books.db"))

app = FastAPI(
    title="图书管理系统",
    version="1.0.0",
    description="课堂随堂练习用的最简图书 CRUD API",
)


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


init_db()


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=0, le=2100)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=0, le=2100)


class BookOut(BookBase):
    id: int
    created_at: str


def row_to_book(row: sqlite3.Row) -> dict:
    return dict(row)


def get_book_or_404(conn: sqlite3.Connection, book_id: int) -> sqlite3.Row:
    row = conn.execute(
        "SELECT id, title, author, year, created_at FROM books WHERE id = ?",
        (book_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return row


@app.get("/")
def root() -> dict:
    return {"message": "图书管理系统 API", "docs": "/docs"}


@app.get("/books", response_model=List[BookOut])
def list_books() -> List[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, title, author, year, created_at FROM books ORDER BY id"
        ).fetchall()
        return [row_to_book(row) for row in rows]


@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int) -> dict:
    with get_db() as conn:
        return row_to_book(get_book_or_404(conn, book_id))


@app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate) -> dict:
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
            (payload.title, payload.author, payload.year),
        )
        row = conn.execute(
            "SELECT id, title, author, year, created_at FROM books WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return row_to_book(row)


@app.put("/books/{book_id}", response_model=BookOut)
def update_book(book_id: int, payload: BookUpdate) -> dict:
    with get_db() as conn:
        get_book_or_404(conn, book_id)
        updates = payload.model_dump(exclude_unset=True)
        if updates:
            columns = ", ".join(f"{key} = ?" for key in updates)
            conn.execute(
                f"UPDATE books SET {columns} WHERE id = ?",
                (*updates.values(), book_id),
            )
        row = conn.execute(
            "SELECT id, title, author, year, created_at FROM books WHERE id = ?",
            (book_id,),
        ).fetchone()
        return row_to_book(row)


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int) -> None:
    with get_db() as conn:
        get_book_or_404(conn, book_id)
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
