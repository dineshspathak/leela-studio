import sqlite3
from abc import ABC, abstractmethod
from typing import Any


class BaseDatabase(ABC):
    @abstractmethod
    def execute(self, query: str, params: tuple = ()) -> list[Any]:
        pass


class SQLiteDatabase(BaseDatabase):
    def __init__(self, db_path: str = "workspace/cache/metadata.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, val TEXT)")
        conn.commit()
        conn.close()

    def execute(self, query: str, params: tuple = ()) -> list[Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.commit()
        conn.close()
        return rows
