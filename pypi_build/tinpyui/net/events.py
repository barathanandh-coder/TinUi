"""Global event bus."""
from typing import Callable, Dict, List, Any

class EventBus:
    """Enterprise Micro-Component Pub/Sub Event Broker."""
    _listeners: Dict[str, List[Callable[[Any], None]]] = {}

    @classmethod
    def on(cls, event_name: str, handler: Callable[[Any], None]):
        if event_name not in cls._listeners:
            cls._listeners[event_name] = []
        cls._listeners[event_name].append(handler)

    @classmethod
    def emit(cls, event_name: str, data: Any = None):
        for handler in cls._listeners.get(event_name, []):
            try:
                handler(data)
            except Exception:
                pass


