"""
Local SQLite persistence layer for caching API query responses.
"""
import sqlite3
import json
import time
from typing import Optional, Dict, Any

class SQLiteCache:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        if self.db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:")
            self._init_db(self._conn)
        else:
            self._conn = None
            with self._get_connection() as conn:
                self._init_db(conn)

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn:
            return self._conn
        return sqlite3.connect(self.db_path)

    def _init_db(self, conn: sqlite3.Connection):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_cache (
                query_key TEXT PRIMARY KEY,
                response_json TEXT NOT NULL,
                created_at REAL NOT NULL
            );
        """)
        conn.commit()

    def get(self, key: str, max_age_seconds: int = 86400) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT response_json, created_at FROM api_cache WHERE query_key = ?", (key,))
        row = cursor.fetchone()
        if not row:
            return None
        response_json, created_at = row
        if (time.time() - created_at) > max_age_seconds:
            return None  # Expired
        return json.loads(response_json)

    def set(self, key: str, value: Dict[str, Any]):
        conn = self._get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO api_cache (query_key, response_json, created_at) VALUES (?, ?, ?)",
            (key, json.dumps(value), time.time())
        )
        conn.commit()

    def clear(self):
        conn = self._get_connection()
        conn.execute("DELETE FROM api_cache")
        conn.commit()
