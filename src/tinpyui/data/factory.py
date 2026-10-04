"""Universal connection dispatcher."""
from typing import Union
from .database import Database
from .postgres import PostgresDatabase
from .mongo import MongoDatabase
from .redis import RedisDatabase
from .duckdb import DuckDBDatabase, ClickHouseDatabase

def connect(uri_or_path: str = ":memory:", **kwargs) -> Union[Database, PostgresDatabase, MongoDatabase, RedisDatabase, DuckDBDatabase]:
    """Universal Connection Factory automatically routing SQLite, PostgreSQL, MongoDB, Redis, DuckDB, and ClickHouse URIs.
    
    Examples:
        - tin.connect("postgres://user:pass@localhost:5432/dbname") -> PostgresDatabase
        - tin.connect("mongodb://localhost:27017/dbname")          -> MongoDatabase
        - tin.connect("redis://localhost:6379/0")                  -> RedisDatabase
        - tin.connect("duckdb://analytics.db")                     -> DuckDBDatabase
        - tin.connect("clickhouse://localhost:9000/default")       -> ClickHouseDatabase
        - tin.connect("sqlite:///app.db")                          -> Database (SQLite)
        - tin.connect(":memory:")                                  -> Database (In-Memory)
    """
    uri_str = str(uri_or_path).strip()
    if uri_str.startswith("postgres://") or uri_str.startswith("postgresql://"):
        return PostgresDatabase(uri_str, **kwargs)
    elif uri_str.startswith("mongodb://") or uri_str.startswith("mongodb+srv://"):
        return MongoDatabase(uri_str, **kwargs)
    elif uri_str.startswith("redis://") or uri_str.startswith("rediss://"):
        return RedisDatabase(uri_str, **kwargs)
    elif uri_str.startswith("duckdb://"):
        return DuckDBDatabase(uri_str, **kwargs)
    elif uri_str.startswith("clickhouse://"):
        return ClickHouseDatabase(uri_str, **kwargs)
    elif uri_str.startswith("sqlite:///"):
        path = uri_str.replace("sqlite:///", "")
        return Database(path, **kwargs)
    else:
        return Database(uri_str, **kwargs)
