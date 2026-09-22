"""MongoDB native driver and document engine."""
import hashlib
import random
import time
import threading
from typing import Any, Callable, List, Optional, Union, Dict
from .database import LiveQuery

class MongoCollection:
    """Reactive MongoDB Collection with live document reactivity and fluent querying."""
    def __init__(self, db: 'MongoDatabase', name: str):
        self.db = db
        self.name = name
        self._listeners: List[Callable[[], None]] = []
        self._docs: List[Dict[str, Any]] = []

    def _matches_filter(self, doc: Dict[str, Any], filter_dict: Dict[str, Any]) -> bool:
        """Evaluates document against MongoDB query operators & dot notation."""
        if not filter_dict:
            return True
        for key, expected in filter_dict.items():
            # Dot notation navigation: e.g. "specs.ram"
            val = doc
            for part in key.split("."):
                if isinstance(val, dict):
                    val = val.get(part)
                else:
                    val = None
                    break

            if isinstance(expected, dict):
                # MongoDB Query Operators
                for op, op_val in expected.items():
                    if op == "$eq" and val != op_val: return False
                    elif op == "$ne" and val == op_val: return False
                    elif op == "$gt" and not (val is not None and val > op_val): return False
                    elif op == "$gte" and not (val is not None and val >= op_val): return False
                    elif op == "$lt" and not (val is not None and val < op_val): return False
                    elif op == "$lte" and not (val is not None and val <= op_val): return False
                    elif op == "$in" and val not in op_val: return False
                    elif op == "$nin" and val in op_val: return False
            else:
                if val != expected:
                    return False
        return True

    def insert_one(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Inserts a single document and returns result with inserted _id."""
        with self.db._lock:
            doc = dict(document)
            if "_id" not in doc:
                doc["_id"] = hashlib.md5(f"{time.time()}-{random.random()}".encode()).hexdigest()[:12]
            if "id" not in doc:
                doc["id"] = doc["_id"]
            self._docs.append(doc)

        self._notify_change()
        return {"inserted_id": doc["_id"], "document": doc}

    def insert(self, **kwargs) -> str:
        """Convenience keyword argument insert."""
        res = self.insert_one(kwargs)
        return str(res["inserted_id"])

    def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Bulk inserts multiple documents."""
        ids = []
        with self.db._lock:
            for d in documents:
                doc = dict(d)
                if "_id" not in doc:
                    doc["_id"] = hashlib.md5(f"{time.time()}-{random.random()}".encode()).hexdigest()[:12]
                if "id" not in doc:
                    doc["id"] = doc["_id"]
                self._docs.append(doc)
                ids.append(doc["_id"])
        self._notify_change()
        return ids

    def find(self, filter_dict: Optional[Dict[str, Any]] = None, limit: Optional[int] = None, skip: int = 0) -> List[Dict[str, Any]]:
        """Finds documents matching query filter."""
        filter_dict = filter_dict or {}
        with self.db._lock:
            matches = [dict(d) for d in self._docs if self._matches_filter(d, filter_dict)]
            if skip > 0:
                matches = matches[skip:]
            if limit is not None and limit > 0:
                matches = matches[:limit]
            return matches

    def find_one(self, filter_dict: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Returns the first document matching filter or None."""
        res = self.find(filter_dict, limit=1)
        return res[0] if res else None

    def get(self, id: Optional[Any] = None, **where) -> Optional[Dict[str, Any]]:
        """Fetches document by _id or kwargs filter."""
        conds = dict(where)
        if id is not None:
            conds["_id"] = id
        return self.find_one(conds)

    def where(self, **filters) -> 'MongoQueryBuilder':
        """Starts a fluent MongoQueryBuilder."""
        return MongoQueryBuilder(self, filters)

    def all(self) -> List[Dict[str, Any]]:
        """Returns all documents in the collection."""
        return self.find()

    def update_one(self, filter_dict: Dict[str, Any], update_doc: Dict[str, Any]) -> int:
        """Updates the first matching document."""
        with self.db._lock:
            for doc in self._docs:
                if self._matches_filter(doc, filter_dict):
                    # Handle $set or direct update
                    sets = update_doc.get("$set", update_doc)
                    for k, v in sets.items():
                        doc[k] = v
                    self._notify_change()
                    return 1
        return 0

    def update_many(self, filter_dict: Dict[str, Any], update_doc: Dict[str, Any]) -> int:
        """Updates all matching documents."""
        count = 0
        with self.db._lock:
            sets = update_doc.get("$set", update_doc)
            for doc in self._docs:
                if self._matches_filter(doc, filter_dict):
                    for k, v in sets.items():
                        doc[k] = v
                    count += 1
        if count > 0:
            self._notify_change()
        return count

    def update(self, where: Optional[Dict[str, Any]] = None, **data) -> int:
        return self.update_many(where or {}, data)

    def delete_one(self, filter_dict: Dict[str, Any]) -> int:
        with self.db._lock:
            for i, doc in enumerate(self._docs):
                if self._matches_filter(doc, filter_dict):
                    self._docs.pop(i)
                    self._notify_change()
                    return 1
        return 0

    def delete_many(self, filter_dict: Dict[str, Any]) -> int:
        with self.db._lock:
            orig_len = len(self._docs)
            self._docs = [d for d in self._docs if not self._matches_filter(d, filter_dict)]
            count = orig_len - len(self._docs)
        if count > 0:
            self._notify_change()
        return count

    def delete(self, where: Optional[Dict[str, Any]] = None, **filters) -> int:
        conds = dict(where or {})
        conds.update(filters)
        return self.delete_many(conds)

    def count_documents(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        return len(self.find(filter_dict))

    def count(self, **filters) -> int:
        return self.count_documents(filters)

    def columns(self) -> List[str]:
        """Dynamically inspects and collects all unique field keys across collection documents."""
        with self.db._lock:
            keys = set()
            for doc in self._docs:
                keys.update(doc.keys())
            return sorted(list(keys))

    def live_query(self, filter_dict: Optional[Dict[str, Any]] = None, **filters) -> 'LiveQuery':
        conds = dict(filter_dict or {})
        conds.update(filters)
        return LiveQuery(self, self.where(**conds))

    def subscribe(self, callback: Callable[[], None]):
        self._listeners.append(callback)

    def _notify_change(self):
        for listener in list(self._listeners):
            try: listener()
            except Exception: pass
        self.db._notify_global()


class MongoQueryBuilder:
    """Fluent query builder for MongoDB collections."""
    def __init__(self, collection: MongoCollection, initial_filter: Optional[Dict[str, Any]] = None):
        self.collection = collection
        self._filter = dict(initial_filter or {})
        self._sort_key = None
        self._sort_desc = False
        self._limit_val = None
        self._skip_val = 0

    def where(self, key: str, op_or_val: Any = None, val: Any = None) -> 'MongoQueryBuilder':
        if val is not None:
            # e.g. .where("age", ">=", 18)
            op_map = {">": "$gt", ">=": "$gte", "<": "$lt", "<=": "$lte", "!=": "$ne", "=": "$eq", "==": "$eq"}
            mongo_op = op_map.get(op_or_val, "$eq")
            self._filter[key] = {mongo_op: val}
        elif op_or_val is not None:
            self._filter[key] = op_or_val
        return self

    def gt(self, key: str, val: Any) -> 'MongoQueryBuilder':
        self._filter[key] = {"$gt": val}
        return self

    def gte(self, key: str, val: Any) -> 'MongoQueryBuilder':
        self._filter[key] = {"$gte": val}
        return self

    def lt(self, key: str, val: Any) -> 'MongoQueryBuilder':
        self._filter[key] = {"$lt": val}
        return self

    def lte(self, key: str, val: Any) -> 'MongoQueryBuilder':
        self._filter[key] = {"$lte": val}
        return self

    def order_by(self, key: str, desc: bool = False) -> 'MongoQueryBuilder':
        self._sort_key = key
        self._sort_desc = desc
        return self

    def limit(self, n: int) -> 'MongoQueryBuilder':
        self._limit_val = int(n)
        return self

    def skip(self, n: int) -> 'MongoQueryBuilder':
        self._skip_val = int(n)
        return self

    def all(self) -> List[Dict[str, Any]]:
        docs = self.collection.find(self._filter, skip=self._skip_val)
        if self._sort_key:
            docs.sort(key=lambda x: x.get(self._sort_key, 0), reverse=self._sort_desc)
        if self._limit_val is not None:
            docs = docs[:self._limit_val]
        return docs

    def first(self) -> Optional[Dict[str, Any]]:
        res = self.limit(1).all()
        return res[0] if res else None

    def count(self) -> int:
        return len(self.all())

    def to_live_query(self) -> 'LiveQuery':
        return LiveQuery(self.collection, self)


class MongoDatabase:
    """Universal MongoDB Database Engine with dynamic document persistence."""
    def __init__(self, uri: str = "mongodb://localhost:27017/app", **kwargs):
        self.uri = uri
        self._lock = threading.RLock()
        self._collections: Dict[str, MongoCollection] = {}
        self._global_listeners: List[Callable[[], None]] = []

    def collection(self, name: str) -> MongoCollection:
        if name not in self._collections:
            self._collections[name] = MongoCollection(self, name)
        return self._collections[name]

    def table(self, name: str) -> MongoCollection:
        """Alias for collection()."""
        return self.collection(name)

    def __getitem__(self, name: str) -> MongoCollection:
        return self.collection(name)

    def __getattr__(self, name: str) -> MongoCollection:
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        return self.collection(name)

    def collections(self) -> List[str]:
        return list(self._collections.keys())

    def drop_collection(self, name: str):
        with self._lock:
            self._collections.pop(name, None)
        self._notify_global()

    def subscribe(self, callback: Callable[[], None]):
        self._global_listeners.append(callback)

    def _notify_global(self):
        for listener in list(self._global_listeners):
            try: listener()
            except Exception: pass

    def close(self):
        pass

MongoDB = MongoDatabase


# ============================================================================
# UNIFIED DATABASE CONNECTION FACTORY (tin.connect)
# ============================================================================

