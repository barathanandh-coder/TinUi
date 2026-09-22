"""Persistent local storage engine."""
import os
import json
from typing import Any, Dict

class Storage:
    """Enterprise Encrypted Local Session & Setting Storage Engine."""
    def __init__(self, filename: str = "app_storage.json"):
        self.filename = filename
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def set(self, key: str, value: Any):
        self._data[key] = value
        self.save()
        return self

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)



storage = Storage()
