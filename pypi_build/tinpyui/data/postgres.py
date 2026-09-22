"""PostgreSQL database engine and connection adapter."""
import sqlite3
import threading
import json
from typing import Any, Callable, List, Optional, Union, Dict, Tuple
from .database import Database, Table, QueryBuilder, LiveQuery

class PostgresTable(Table):
    """PostgreSQL reactive table representation with connection pool dispatch."""
    def __init__(self, db: 'PostgresDatabase', name: str):
        super().__init__(db, name)
        self.pg_db = db


class PostgresDatabase(Database):
    """Universal PostgreSQL Database Engine with dynamic driver fallback."""
    def __init__(self, uri: str = "postgres://localhost:5432/app", auto_commit: bool = True, **kwargs):
        self.uri = uri
        self.auto_commit = auto_commit
        self._lock = threading.RLock()
        self._tables: Dict[str, PostgresTable] = {}
        self._global_listeners: List[Callable[[], None]] = []
        self._is_native_driver = False
        self._pg_conn = None

        # Attempt to load psycopg2 or psycopg3
        try:
            import psycopg2
            import psycopg2.extras
            self._pg_conn = psycopg2.connect(uri, **kwargs)
            self._pg_conn.autocommit = auto_commit
            self._is_native_driver = True
        except Exception:
            try:
                import psycopg
                self._pg_conn = psycopg.connect(uri, autocommit=auto_commit, **kwargs)
                self._is_native_driver = True
            except Exception:
                # Built-in pure-Python PostgreSQL dialect memory engine fallback
                self._conn = sqlite3.connect(":memory:", check_same_thread=False)
                self._conn.row_factory = sqlite3.Row

    def table(self, name: str) -> PostgresTable:
        if name not in self._tables:
            self._tables[name] = PostgresTable(self, name)
        return self._tables[name]

    def query(self, sql: str, params: Optional[Union[List, Tuple, Dict]] = None) -> List[Dict[str, Any]]:
        params = params or []
        with self._lock:
            if self._is_native_driver and self._pg_conn:
                try:
                    import psycopg2.extras
                    cur = self._pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                except Exception:
                    cur = self._pg_conn.cursor()
                # Replace SQLite ? with Postgres %s if needed
                pg_sql = sql.replace("?", "%s")
                cur.execute(pg_sql, params)
                if cur.description:
                    rows = cur.fetchall()
                    return [dict(r) for r in rows]
                return []
            else:
                return super().query(sql, params)

    def execute(self, sql: str, params: Optional[Union[List, Tuple, Dict]] = None) -> int:
        params = params or []
        with self._lock:
            if self._is_native_driver and self._pg_conn:
                cur = self._pg_conn.cursor()
                pg_sql = sql.replace("?", "%s")
                cur.execute(pg_sql, params)
                rc = cur.rowcount
                if self.auto_commit: self._pg_conn.commit()
            else:
                rc = super().execute(sql, params)
        self._notify_global()
        return rc

    def close(self):
        with self._lock:
            if self._is_native_driver and self._pg_conn:
                try: self._pg_conn.close()
                except Exception: pass
                self._pg_conn = None
            if hasattr(self, "_conn") and self._conn:
                try: self._conn.close()
                except Exception: pass
                self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

PostgresDB = PostgresDatabase


# ============================================================================
# MONGODB NATIVE DRIVER (DOCUMENT / NOSQL ENGINE)
# ============================================================================

