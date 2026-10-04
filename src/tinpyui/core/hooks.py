"""
TinPyUI Reactive Hooks & Context System
Provides React-like declarative ergonomics (use_state, use_effect, use_memo, use_ref, use_context)
powered by O(1) fine-grained reactive signals without Virtual DOM tree diffing or rerender traps.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from .signals import Signal

class Ref:
    """A mutable container object that persists across operations without triggering reactive cascades."""
    def __init__(self, current: Any = None):
        self.current = current

    def __repr__(self) -> str:
        return f"Ref(current={self.current!r})"


# Global Context Registry for provide_context / use_context
_GLOBAL_CONTEXT_REGISTRY: Dict[str, Any] = {}


def use_state(initial: Any) -> Tuple[Signal, Callable[[Union[Any, Callable[[Any], Any]]], None]]:
    """
    Creates a reactive state pair: (state_signal, set_state).
    
    Example:
        count, set_count = tin.use_state(0)
        set_count(count.value + 1)
        # or functional updater:
        set_count(lambda prev: prev + 1)
    """
    sig = Signal(initial)

    def set_state(val_or_updater: Union[Any, Callable[[Any], Any]]):
        if callable(val_or_updater):
            new_val = val_or_updater(sig.value)
        else:
            new_val = val_or_updater
        sig.value = new_val

    return sig, set_state


def use_signal(initial: Any) -> Signal:
    """Creates a fine-grained reactive Signal cell."""
    return Signal(initial)


def use_effect(fn: Callable[[], Optional[Callable[[], None]]], deps: Optional[List[Signal]] = None) -> Callable[[], None]:
    """
    Executes a side-effect function when any Signal in `deps` mutates.
    Supports cleanup functions returned by `fn()`.
    
    Example:
        def on_change():
            print("Counter changed to", count.value)
            return lambda: print("Cleaning up previous run")
        tin.use_effect(on_change, [count])
    """
    cleanup_ref = Ref(None)

    def run_effect(_=None):
        if callable(cleanup_ref.current):
            try:
                cleanup_ref.current()
            except Exception as e:
                print(f"[TinPyUI use_effect cleanup error]: {e}")
            cleanup_ref.current = None

        res = fn()
        if callable(res):
            cleanup_ref.current = res

    # Run immediately on mount
    run_effect()

    # Subscribe to dependency signals
    if deps:
        for d in deps:
            if isinstance(d, Signal):
                d.subscribe(run_effect)

    # Return manual trigger / teardown handle
    def dispose():
        if callable(cleanup_ref.current):
            cleanup_ref.current()
            cleanup_ref.current = None

    return dispose


def use_memo(fn: Callable[[], Any], deps: List[Signal]) -> Signal:
    """
    Returns a reactive Signal that recomputes only when any Signal in `deps` changes.
    
    Example:
        doubled = tin.use_memo(lambda: count.value * 2, [count])
    """
    initial_val = fn()
    memo_signal = Signal(initial_val)

    def recompute(_=None):
        memo_signal.value = fn()

    for d in deps:
        if isinstance(d, Signal):
            d.subscribe(recompute)

    return memo_signal


def use_ref(initial: Any = None) -> Ref:
    """Returns a mutable Ref object whose .current property holds a persistent value."""
    return Ref(initial)


def create_context(name: str, default: Any = None):
    """Initializes a named context key with a default value."""
    if name not in _GLOBAL_CONTEXT_REGISTRY:
        _GLOBAL_CONTEXT_REGISTRY[name] = default
    return name


def provide_context(name: str, value: Any):
    """
    Sets a context value accessible anywhere in the component hierarchy via use_context.
    
    Example:
        tin.provide_context("theme", "cyber-dark")
        tin.provide_context("auth_user", {"id": 101, "name": "Alice"})
    """
    _GLOBAL_CONTEXT_REGISTRY[name] = value


def use_context(name: str, default: Any = None) -> Any:
    """
    Retrieves a context value by name, falling back to default if not found.
    
    Example:
        theme = tin.use_context("theme", "light")
    """
    return _GLOBAL_CONTEXT_REGISTRY.get(name, default)
