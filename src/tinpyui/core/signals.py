"""Reactive signal and fine-grained dirty-bit state cells."""
from typing import Any, Callable, List, Dict, Tuple, Optional

_SIGNAL_ID_COUNTER = 0

def _get_next_signal_id() -> int:
    global _SIGNAL_ID_COUNTER
    _SIGNAL_ID_COUNTER += 1
    return _SIGNAL_ID_COUNTER

class Signal:
    """
    Reactive signal primitive cell with fine-grained dirty-bit slot tracking.
    Enables O(1) direct node mutations without virtual DOM reconciliation.
    """
    def __init__(self, initial_value: Any):
        self._slot_id: int = _get_next_signal_id()
        self._value = initial_value
        self._subscribers: List[Callable[[Any], None]] = []
        self._bindings: List[Tuple[int, str]] = []  # (node_id, property_key)
        self._is_dirty: bool = False

    @property
    def slot_id(self) -> int:
        return self._slot_id

    @property
    def is_dirty(self) -> bool:
        return self._is_dirty

    def clear_dirty(self):
        self._is_dirty = False

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_val: Any):
        if self._value != new_val:
            self._value = new_val
            self._is_dirty = True
            for sub in self._subscribers:
                try:
                    sub(new_val)
                except Exception:
                    pass

    def bind_target(self, node_id: int, property_key: str):
        """Binds this signal directly to a node attribute slot."""
        self._bindings.append((node_id, property_key))

    def get_mutations(self) -> List[Dict[str, Any]]:
        """Produces direct targeted mutation commands for dirty slots."""
        if not self._is_dirty:
            return []
        mutations = []
        for node_id, prop_key in self._bindings:
            mutations.append({
                "op": "SET_ATTRIBUTE" if prop_key != "text" else "SET_TEXT",
                "id": node_id,
                "key": prop_key,
                "value": str(self._value)
            })
        self._is_dirty = False
        return mutations

    def set(self, new_val: Any):
        """Sets new signal value and notifies reactive subscribers."""
        self.value = new_val
        return self

    def get(self) -> Any:
        """Gets current signal value."""
        return self.value

    def update(self, fn: Callable[[Any], Any]):
        """Updates signal value via transforming callback."""
        self.value = fn(self.value)
        return self

    def subscribe(self, callback: Callable[[Any], None]):
        self._subscribers.append(callback)

    def __str__(self):
        return str(self._value)


class State(Signal):
    """Reactive State Primitive Cell (Alias for Signal with numerical convenience methods)."""
    def add(self, amount: int = 1):
        self.value += amount

    def toggle(self):
        self.value = not self.value
