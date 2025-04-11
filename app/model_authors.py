import sqlite3
from dataclasses import dataclass
from typing import Optional, Union, List, Dict

from constant import (DATABASE_NAME,
                      AUTHORS_TABLE_NAME,
                      BOOKS_TABLE_NAME )



@dataclass
class Author:
    first_name:str
    last_name:str
    middle_name:Optional[str] = None
    id: Optional[int] = None

    def __getitem__(self, item: str) -> Union[int, str]:
        return getattr(self, item)

def get_author_obj_from_row(row: tuple) -> Author:
    return Author(id=row[0], first_name=row[1], middle_name=row[2], last_name = row[3])

def create_author_table(data:List[Dict]) ->None:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')
        cursor.execute(
            f"""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name= '{AUTHORS_TABLE_NAME}';
            """
        )
        exists = cursor.fetchone()
        if not exists:
            cursor.executescript(
                f"""
                CREATE TABLE {AUTHORS_TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                first_name TEXT NOT NULL, 
                middle_name TEXT, 
                last_name TEXT NOT NULL)
                """
            )

            cursor.executemany(
                f"""
                INSERT INTO '{AUTHORS_TABLE_NAME}' 
                ( first_name, middle_name, last_name)
                VALUES(?, ?, ?)
                """, ((item['first_name'], item['middle_name'], item['last_name']) for item in data)
            )
            conn.commit()

def get_all_authors():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        authors = cursor.execute(
            f"""
            SELECT * FROM {AUTHORS_TABLE_NAME}
            """
        ).fetchall()
        return [get_author_obj_from_row(row)  for row in authors]

def get_author_by_id(id:int ) -> Author:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        author = cursor.execute(
            f"""
            SELECT * FROM {AUTHORS_TABLE_NAME}
            WHERE id = ?
            """, (id,)
        ).fetchone()
        return get_author_obj_from_row(author)

def get_books_by_author_id(id: int):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        books = cursor.execute(
            f"""
            select {BOOKS_TABLE_NAME}.id, title from {BOOKS_TABLE_NAME}
            join {AUTHORS_TABLE_NAME} on {BOOKS_TABLE_NAME}.author = {AUTHORS_TABLE_NAME}.id
            where {AUTHORS_TABLE_NAME}.id = ?
            """, (id, )
        ).fetchall()
        if books:
            return [{'id': row[0], 'title' : row[1], 'author' : str(id)} for row in books]

def delete_author_by_id(id:int )-> None:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')
        cursor.execute(
            f"""
            DELETE FROM {AUTHORS_TABLE_NAME}
            WHERE {AUTHORS_TABLE_NAME}.id = ?
            """, (id, )
        )
        conn.commit()

def add_author(author: Author) -> Author:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor= conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO {AUTHORS_TABLE_NAME}
            ( first_name, middle_name, last_name)
                VALUES(?, ?, ?)
            """, (author.first_name, author.middle_name, author.last_name)
        )
        author.id = cursor.lastrowid
        return author