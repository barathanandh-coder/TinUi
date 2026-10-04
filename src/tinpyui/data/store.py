"""Reactive KeyValue store and declarative active record models."""
import json
from typing import Any, Dict
from ..core.signals import Signal
from .database import Database, db

class ModelWrapper:
    pass

class KeyValueStore:
    """1-line reactive persistent key-value storage engine."""
    def __init__(self, db_path: str = "app_store.db", table_name: str = "kv_store"):
        self.db = Database(db_path)
        self.table = self.db.table(table_name)
        self._signals: Dict[str, Signal] = {}

    def set(self, key: str, value: Any) -> Any:
        self.table.upsert(where={"key": key}, key=key, value=json.dumps(value))
        if key in self._signals:
            self._signals[key].value = value
        return value

    def get(self, key: str, default: Any = None) -> Any:
        row = self.table.get(key=key)
        if row and "value" in row:
            try: return json.loads(row["value"])
            except Exception: return row["value"]
        return default

    def signal(self, key: str, default: Any = None) -> Signal:
        """Returns a reactive Signal automatically tied and persisted to the key-value store."""
        if key not in self._signals:
            initial_val = self.get(key, default)
            sig = Signal(initial_val)
            def _on_sig_change(new_val):
                self.table.upsert(where={"key": key}, key=key, value=json.dumps(new_val))
            sig.subscribe(_on_sig_change)
            self._signals[key] = sig
        return self._signals[key]

    def delete(self, key: str):
        self.table.delete(key=key)
        if key in self._signals:
            self._signals[key].value = None

    def close(self):
        if hasattr(self, "db") and self.db:
            try:
                self.db.close()
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


def use_store(db_path: str = "app_store.db", table: str = "kv_store") -> KeyValueStore:
    """Instant 1-line reactive persistent store."""
    return KeyValueStore(db_path, table)


def model(cls):
    """Declarative Data Model class decorator providing active record style CRUD methods."""
    table_name = getattr(cls, "__table__", cls.__name__.lower() + "s")
    _table = db.table(table_name)
    
    class ModelWrapper(cls):
        _tbl = _table
        
        @classmethod
        def create(cls, **kwargs):
            row_id = _table.insert(**kwargs)
            return _table.get(id=row_id)
            
        @classmethod
        def all(cls):
            return _table.all()
            
        @classmethod
        def get(cls, id=None, **where):
            return _table.get(id=id, **where)
            
        @classmethod
        def where(cls, **filters):
            return _table.where(**filters)
            
        @classmethod
        def live_query(cls, **filters):
            return _table.live_query(**filters)
            
        @classmethod
        def count(cls, **filters):
            return _table.count(**filters)
            
        @classmethod
        def delete(cls, where=None, **filters):
            return _table.delete(where=where, **filters)

    ModelWrapper.__name__ = cls.__name__
    return ModelWrapper


