"""Universal embedded SQLite database engine & live queries."""
import sqlite3
import csv
import json
import threading
import os
from typing import Any, Callable, List, Optional, Union, Dict, Tuple
from ..core.signals import Signal
from ..core.node import Node
from ..core.primitives import eval_prop

class Table:
    """Zero-boilerplate reactive table representation with automatic schema evolution."""
    def __init__(self, db: 'Database', name: str):
        self.db = db
        self.name = name
        self._listeners: List[Callable[[], None]] = []

    def _ensure_table(self, sample_data: Dict[str, Any]):
        """Dynamically creates or extends table schema based on inserted dictionary fields."""
        if not sample_data:
            return
        with self.db._lock:
            cur = self.db._conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.name,))
            if not cur.fetchone():
                cols = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
                for k, v in sample_data.items():
                    if k == "id": continue
                    col_type = "TEXT"
                    if isinstance(v, int): col_type = "INTEGER"
                    elif isinstance(v, float): col_type = "REAL"
                    elif isinstance(v, (bytes, bytearray)): col_type = "BLOB"
                    cols.append(f'"{k}" {col_type}')
                sql = f'CREATE TABLE IF NOT EXISTS "{self.name}" ({", ".join(cols)})'
                cur.execute(sql)
                self.db._conn.commit()
            else:
                cur.execute(f'PRAGMA table_info("{self.name}")')
                existing_cols = {row[1] for row in cur.fetchall()}
                for k, v in sample_data.items():
                    if k not in existing_cols:
                        col_type = "TEXT"
                        if isinstance(v, int): col_type = "INTEGER"
                        elif isinstance(v, float): col_type = "REAL"
                        elif isinstance(v, (bytes, bytearray)): col_type = "BLOB"
                        try:
                            cur.execute(f'ALTER TABLE "{self.name}" ADD COLUMN "{k}" {col_type}')
                            self.db._conn.commit()
                        except Exception:
                            pass

    def insert(self, **data) -> int:
        """Inserts a new record and returns the new row id. Triggers live query subscribers."""
        self._ensure_table(data)
        keys = list(data.keys())
        placeholders = ", ".join(["?"] * len(keys))
        cols = ", ".join([f'"{k}"' for k in keys])
        values = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in data.values()]
        
        with self.db._lock:
            cur = self.db._conn.cursor()
            sql = f'INSERT INTO "{self.name}" ({cols}) VALUES ({placeholders})'
            cur.execute(sql, values)
            last_id = cur.lastrowid
            self.db._conn.commit()
        
        self._notify_change()
        return last_id

    def insert_many(self, items: List[Dict[str, Any]]) -> List[int]:
        """Bulk inserts multiple records in a single transaction."""
        if not items: return []
        self._ensure_table(items[0])
        ids = []
        with self.db._lock:
            cur = self.db._conn.cursor()
            for item in items:
                keys = list(item.keys())
                placeholders = ", ".join(["?"] * len(keys))
                cols = ", ".join([f'"{k}"' for k in keys])
                values = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in item.values()]
                sql = f'INSERT INTO "{self.name}" ({cols}) VALUES ({placeholders})'
                cur.execute(sql, values)
                ids.append(cur.lastrowid)
            self.db._conn.commit()
        self._notify_change()
        return ids

    def upsert(self, where: Dict[str, Any], **data) -> int:
        """Updates if row matching 'where' exists; otherwise inserts new record."""
        existing = self.get(**where)
        if existing:
            self.update(where=where, **data)
            return existing.get("id", 0)
        else:
            merged = {**where, **data}
            return self.insert(**merged)

    def get(self, id: Optional[Any] = None, **where) -> Optional[Dict[str, Any]]:
        """Fetches a single record by id or filter conditions."""
        if id is not None:
            where["id"] = id
        res = self.where(**where).limit(1).all()
        return res[0] if res else None

    def where(self, **filters) -> 'QueryBuilder':
        """Starts a fluent QueryBuilder filtered by equality conditions."""
        qb = QueryBuilder(self)
        for k, v in filters.items():
            qb.where(k, "=", v)
        return qb

    filter = where

    def all(self) -> List[Dict[str, Any]]:
        """Returns all records in the table as dictionaries."""
        return QueryBuilder(self).all()

    def update(self, where: Optional[Dict[str, Any]] = None, **data) -> int:
        """Updates records matching 'where' conditions. Triggers live query subscribers."""
        if not data: return 0
        set_clauses = [f'"{k}" = ?' for k in data.keys()]
        values = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in data.values()]
        
        where_clauses = []
        where_vals = []
        if where:
            for k, v in where.items():
                where_clauses.append(f'"{k}" = ?')
                where_vals.append(v)
        
        where_str = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        sql = f'UPDATE "{self.name}" SET {", ".join(set_clauses)}{where_str}'
        
        with self.db._lock:
            cur = self.db._conn.cursor()
            try:
                cur.execute(sql, values + where_vals)
                row_count = cur.rowcount
                self.db._conn.commit()
            except Exception:
                row_count = 0
                
        self._notify_change()
        return row_count

    def delete(self, where: Optional[Dict[str, Any]] = None, **filters) -> int:
        """Deletes records matching 'where' or kwargs filters. Triggers live query subscribers."""
        conds = dict(where or {})
        conds.update(filters)
        where_clauses = []
        where_vals = []
        for k, v in conds.items():
            where_clauses.append(f'"{k}" = ?')
            where_vals.append(v)
        
        where_str = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        sql = f'DELETE FROM "{self.name}"{where_str}'
        
        with self.db._lock:
            cur = self.db._conn.cursor()
            try:
                cur.execute(sql, where_vals)
                row_count = cur.rowcount
                self.db._conn.commit()
            except Exception:
                row_count = 0
                
        self._notify_change()
        return row_count

    def count(self, **filters) -> int:
        """Returns total matching rows count."""
        return self.where(**filters).count()

    def columns(self) -> List[str]:
        """Returns list of column names for this table."""
        with self.db._lock:
            cur = self.db._conn.cursor()
            try:
                cur.execute(f'PRAGMA table_info("{self.name}")')
                return [row[1] for row in cur.fetchall()]
            except Exception:
                return []

    def live_query(self, **filters) -> 'LiveQuery':
        """Returns a reactive LiveQuery signal that automatically refreshes when table data changes."""
        return LiveQuery(self, self.where(**filters))

    def subscribe(self, callback: Callable[[], None]):
        """Subscribes a listener to table data change events."""
        self._listeners.append(callback)

    def _notify_change(self):
        """Notifies all registered table and live-query subscribers."""
        for listener in list(self._listeners):
            try:
                listener()
            except Exception:
                pass
        self.db._notify_global()


class QueryBuilder:
    """Fluent SQL query generator for chaining where, order_by, limit, and offset."""
    def __init__(self, table: Table):
        self.table = table
        self._where_clauses: List[str] = []
        self._params: List[Any] = []
        self._order_by: Optional[str] = None
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None

    def where(self, column: str, op: str = "=", value: Any = None) -> 'QueryBuilder':
        """Adds a WHERE condition clause."""
        if value is None and op not in ("IS NULL", "IS NOT NULL"):
            self._where_clauses.append(f'"{column}" = ?')
            self._params.append(op)
        elif op in ("IS NULL", "IS NOT NULL"):
            self._where_clauses.append(f'"{column}" {op}')
        else:
            self._where_clauses.append(f'"{column}" {op} ?')
            self._params.append(value)
        return self

    def like(self, column: str, pattern: str) -> 'QueryBuilder':
        return self.where(column, "LIKE", pattern)

    def gt(self, column: str, val: Any) -> 'QueryBuilder':
        return self.where(column, ">", val)

    def gte(self, column: str, val: Any) -> 'QueryBuilder':
        return self.where(column, ">=", val)

    def lt(self, column: str, val: Any) -> 'QueryBuilder':
        return self.where(column, "<", val)

    def lte(self, column: str, val: Any) -> 'QueryBuilder':
        return self.where(column, "<=", val)

    def order_by(self, column: str, desc: bool = False) -> 'QueryBuilder':
        direction = "DESC" if desc else "ASC"
        self._order_by = f'"{column}" {direction}'
        return self

    def limit(self, n: int) -> 'QueryBuilder':
        self._limit = int(n)
        return self

    def offset(self, n: int) -> 'QueryBuilder':
        self._offset = int(n)
        return self

    def _build_sql(self, select_expr: str = "*") -> Tuple[str, List[Any]]:
        sql = f'SELECT {select_expr} FROM "{self.table.name}"'
        if self._where_clauses:
            sql += f" WHERE {' AND '.join(self._where_clauses)}"
        if self._order_by:
            sql += f" ORDER BY {self._order_by}"
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
        if self._offset is not None:
            sql += f" OFFSET {self._offset}"
        return sql, self._params

    def all(self) -> List[Dict[str, Any]]:
        """Executes the query and returns all matching records as a list of dicts."""
        sql, params = self._build_sql("*")
        with self.table.db._lock:
            cur = self.table.db._conn.cursor()
            try:
                cur.execute(sql, params)
                cols = [desc[0] for desc in cur.description] if cur.description else []
                rows = cur.fetchall()
                results = []
                for row in rows:
                    row_dict = {}
                    for col, val in zip(cols, row):
                        if isinstance(val, str) and (val.startswith("{") or val.startswith("[")):
                            try: row_dict[col] = json.loads(val)
                            except Exception: row_dict[col] = val
                        else:
                            row_dict[col] = val
                    results.append(row_dict)
                return results
            except Exception:
                return []

    def first(self) -> Optional[Dict[str, Any]]:
        """Returns the first matching record or None."""
        self._limit = 1
        res = self.all()
        return res[0] if res else None

    def count(self) -> int:
        """Returns count of matching records."""
        sql, params = self._build_sql("COUNT(*)")
        with self.table.db._lock:
            cur = self.table.db._conn.cursor()
            try:
                cur.execute(sql, params)
                row = cur.fetchone()
                return row[0] if row else 0
            except Exception:
                return 0

    def to_live_query(self) -> 'LiveQuery':
        """Converts query builder to a reactive LiveQuery."""
        return LiveQuery(self.table, self)


class LiveQuery(Signal):
    """Reactive Signal that automatically updates its value whenever the underlying DB table changes."""
    def __init__(self, table: Table, query: Optional[QueryBuilder] = None):
        self.table = table
        self.query = query if query is not None else QueryBuilder(table)
        initial_data = self.query.all()
        super().__init__(initial_data)
        self.table.subscribe(self.refresh)

    def refresh(self):
        """Re-evaluates query and notifies reactive subscribers with new data."""
        self.value = self.query.all()

    def __len__(self):
        return len(self.value) if isinstance(self.value, list) else 0

    def __iter__(self):
        return iter(self.value if isinstance(self.value, list) else [])


class Database:
    """Universal Zero-Boilerplate Embedded & Cloud-Ready Database Engine."""
    def __init__(self, path: str = ":memory:", auto_commit: bool = True):
        self.path = path
        self.auto_commit = auto_commit
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._tables: Dict[str, Table] = {}
        self._global_listeners: List[Callable[[], None]] = []

    def table(self, name: str) -> Table:
        """Gets or registers a Table instance for the given name."""
        if name not in self._tables:
            self._tables[name] = Table(self, name)
        return self._tables[name]

    def __getitem__(self, name: str) -> Table:
        return self.table(name)

    def __getattr__(self, name: str) -> Table:
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return self.table(name)

    def query(self, sql: str, params: Optional[Union[List, Tuple, Dict]] = None) -> List[Dict[str, Any]]:
        """Executes raw parameterized SQL query and returns list of dicts."""
        params = params or []
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(sql, params)
            if not cur.description:
                if self.auto_commit: self._conn.commit()
                return []
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return [dict(zip(cols, row)) for row in rows]

    def execute(self, sql: str, params: Optional[Union[List, Tuple, Dict]] = None) -> int:
        """Executes SQL statement and returns affected row count."""
        params = params or []
        with self._lock:
            cur = self._conn.cursor()
            cur.execute(sql, params)
            if self.auto_commit: self._conn.commit()
            rc = cur.rowcount
        self._notify_global()
        return rc

    def tables(self) -> List[str]:
        """Lists all user table names in the database."""
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            return [row[0] for row in cur.fetchall()]

    def drop_table(self, name: str):
        """Drops table and notifies subscribers."""
        self.execute(f'DROP TABLE IF EXISTS "{name}"')
        self._tables.pop(name, None)

    def export_json(self, filepath: Optional[str] = None) -> str:
        """Dumps all database tables into JSON string or writes to filepath."""
        dump = {}
        for tbl in self.tables():
            dump[tbl] = self.table(tbl).all()
        json_str = json.dumps(dump, indent=2, default=str)
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
        return json_str

    def import_json(self, data_or_filepath: Union[str, Dict[str, Any]]):
        """Imports tables and rows from JSON file or dictionary."""
        if isinstance(data_or_filepath, str):
            if os.path.exists(data_or_filepath):
                with open(data_or_filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = json.loads(data_or_filepath)
        else:
            data = data_or_filepath
            
        for table_name, rows in data.items():
            if isinstance(rows, list):
                self.table(table_name).insert_many(rows)

    def export_csv(self, table_name: str, filepath: str):
        """Exports a table to a CSV file."""
        rows = self.table(table_name).all()
        if not rows: return
        keys = list(rows[0].keys())
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

    def import_csv(self, table_name: str, filepath: str):
        """Imports CSV file rows into a table."""
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [dict(r) for r in reader]
            self.table(table_name).insert_many(rows)

    def subscribe(self, callback: Callable[[], None]):
        self._global_listeners.append(callback)

    def _notify_global(self):
        for listener in list(self._global_listeners):
            try: listener()
            except Exception: pass

    def close(self):
        with self._lock:
            if hasattr(self, "_conn") and self._conn:
                try:
                    self._conn.close()
                except Exception:
                    pass
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

SQLiteDatabase = Database
DB = Database
SQLiteDB = Database

# Global zero-config database instance
db = Database(":memory:")


# ============================================================================
# POSTGRESQL NATIVE DRIVER (POSTGRESQL RELATIONAL ENGINE)
# ============================================================================

