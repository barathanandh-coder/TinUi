"""
TinPyUI Reactive Redis Database & Cache Store
Supports live pub/sub signals, key-value caching, hash operations, and automatic mock fallback.
"""

import json
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Union
from ..core.signals import Signal

class MockPubSub:
    """Thread-safe PubSub mock for in-memory Redis simulation."""
    def __init__(self, parent_store):
        self._store = parent_store
        self._callbacks: Dict[str, List[Callable[[str, Any], None]]] = {}
        self._lock = threading.RLock()

    def subscribe(self, channel: str, callback: Callable[[str, Any], None]):
        with self._lock:
            if channel not in self._callbacks:
                self._callbacks[channel] = []
            self._callbacks[channel].append(callback)

    def publish(self, channel: str, message: Any):
        with self._lock:
            listeners = list(self._callbacks.get(channel, []))
        for cb in listeners:
            try:
                cb(channel, message)
            except Exception:
                pass


class RedisDatabase:
    """Reactive Redis database client supporting real-time signals, PubSub, and caching."""

    def __init__(self, uri: str = "redis://localhost:6379/0", **kwargs):
        self.uri = uri
        self.kwargs = kwargs
        self._signals: Dict[str, Signal] = {}
        self._pubsub_signals: Dict[str, Signal] = {}
        self._lock = threading.RLock()

        # In-memory storage structures for fallback / local testing
        self._mock_data: Dict[str, Any] = {}
        self._mock_expiry: Dict[str, float] = {}
        self._mock_hashes: Dict[str, Dict[str, Any]] = {}
        self._mock_lists: Dict[str, List[Any]] = {}
        self._pubsub = MockPubSub(self)

        self._client = None
        self._is_mock = False

        # Attempt to connect to real redis if library is installed
        try:
            import redis
            self._client = redis.Redis.from_url(self.uri, **self.kwargs)
            # Test ping
            self._client.ping()
        except Exception:
            # Seamless fallback to mock engine
            self._is_mock = True
            self._client = None

    @property
    def is_mock(self) -> bool:
        """Returns True if running on in-memory mock engine."""
        return self._is_mock

    def _purge_expired(self, key: str):
        if key in self._mock_expiry and time.time() > self._mock_expiry[key]:
            self._mock_data.pop(key, None)
            self._mock_expiry.pop(key, None)

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Sets a key to value with optional expiration in seconds."""
        serialized = json.dumps(value) if not isinstance(value, (str, int, float, bytes)) else value
        with self._lock:
            if self._client and not self._is_mock:
                try:
                    res = self._client.set(key, serialized, ex=ex)
                except Exception:
                    self._is_mock = True
                    self._client = None
                    return self.set(key, value, ex=ex)
            else:
                self._mock_data[key] = value
                if ex:
                    self._mock_expiry[key] = time.time() + ex
                elif key in self._mock_expiry:
                    del self._mock_expiry[key]
                res = True

            if key in self._signals:
                self._signals[key].value = value
            return bool(res)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves key value, parsing JSON if applicable."""
        with self._lock:
            if self._client and not self._is_mock:
                try:
                    val = self._client.get(key)
                    if val is None:
                        return default
                    if isinstance(val, bytes):
                        val = val.decode("utf-8")
                    try:
                        return json.loads(val)
                    except Exception:
                        return val
                except Exception:
                    self._is_mock = True
                    self._client = None

            self._purge_expired(key)
            return self._mock_data.get(key, default)

    def delete(self, *keys: str) -> int:
        """Deletes one or more keys."""
        deleted_count = 0
        with self._lock:
            for k in keys:
                if self._client and not self._is_mock:
                    try:
                        deleted_count += self._client.delete(k)
                    except Exception:
                        self._is_mock = True
                        self._client = None
                else:
                    if k in self._mock_data:
                        del self._mock_data[k]
                        deleted_count += 1
                    self._mock_expiry.pop(k, None)

                if k in self._signals:
                    self._signals[k].value = None
        return deleted_count

    def exists(self, key: str) -> bool:
        with self._lock:
            if self._client and not self._is_mock:
                try:
                    return bool(self._client.exists(key))
                except Exception:
                    self._is_mock = True
                    self._client = None
            self._purge_expired(key)
            return key in self._mock_data

    def incr(self, key: str, amount: int = 1) -> int:
        """Increments integer value of a key."""
        with self._lock:
            val = self.get(key, 0)
            try:
                new_val = int(val) + amount
            except Exception:
                new_val = amount
            self.set(key, new_val)
            return new_val

    def decr(self, key: str, amount: int = 1) -> int:
        """Decrements integer value of a key."""
        return self.incr(key, -amount)

    # Hash operations
    def hset(self, name: str, key: str, value: Any):
        with self._lock:
            if self._client and not self._is_mock:
                try:
                    ser = json.dumps(value) if not isinstance(value, (str, int, float)) else str(value)
                    return self._client.hset(name, key, ser)
                except Exception:
                    self._is_mock = True
                    self._client = None
            if name not in self._mock_hashes:
                self._mock_hashes[name] = {}
            self._mock_hashes[name][key] = value
            return 1

    def hget(self, name: str, key: str, default: Any = None) -> Any:
        with self._lock:
            if self._client and not self._is_mock:
                try:
                    val = self._client.hget(name, key)
                    if val is None:
                        return default
                    if isinstance(val, bytes):
                        val = val.decode("utf-8")
                    try:
                        return json.loads(val)
                    except Exception:
                        return val
                except Exception:
                    self._is_mock = True
                    self._client = None
            return self._mock_hashes.get(name, {}).get(key, default)

    def hgetall(self, name: str) -> Dict[str, Any]:
        with self._lock:
            if self._client and not self._is_mock:
                try:
                    raw = self._client.hgetall(name)
                    return {k.decode("utf-8") if isinstance(k, bytes) else k: v.decode("utf-8") if isinstance(v, bytes) else v for k, v in raw.items()}
                except Exception:
                    self._is_mock = True
                    self._client = None
            return dict(self._mock_hashes.get(name, {}))

    # Pub / Sub
    def publish(self, channel: str, message: Any) -> int:
        """Publishes a message to a channel."""
        with self._lock:
            if self._client and not self._is_mock:
                try:
                    ser = json.dumps(message) if not isinstance(message, (str, int, float)) else str(message)
                    return self._client.publish(channel, ser)
                except Exception:
                    self._is_mock = True
                    self._client = None

            self._pubsub.publish(channel, message)
            return 1

    def subscribe(self, channel: str, callback: Callable[[str, Any], None]):
        """Subscribes callback to channel messages."""
        self._pubsub.subscribe(channel, callback)

    def pubsub_signal(self, channel: str, default: Any = None) -> Signal:
        """Creates a reactive Signal synced to channel messages."""
        with self._lock:
            if channel not in self._pubsub_signals:
                sig = Signal(default)
                def _handle_msg(ch, msg):
                    sig.value = msg
                self.subscribe(channel, _handle_msg)
                self._pubsub_signals[channel] = sig
            return self._pubsub_signals[channel]

    def signal(self, key: str, default: Any = None) -> Signal:
        """Creates a reactive Signal synced to key-value updates."""
        with self._lock:
            if key not in self._signals:
                initial = self.get(key, default)
                sig = Signal(initial)
                def _on_signal_change(new_val):
                    self.set(key, new_val)
                sig.subscribe(_on_signal_change)
                self._signals[key] = sig
            return self._signals[key]

    def flushdb(self):
        """Clears all keys in the current database."""
        with self._lock:
            if self._client and not self._is_mock:
                try:
                    self._client.flushdb()
                except Exception:
                    pass
            self._mock_data.clear()
            self._mock_expiry.clear()
            self._mock_hashes.clear()
            self._mock_lists.clear()

    def close(self):
        with self._lock:
            if self._client and not self._is_mock:
                try:
                    self._client.close()
                except Exception:
                    pass
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

RedisStore = RedisDatabase
RedisDB = RedisDatabase
