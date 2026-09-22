"""Core layout and runtime primitives."""
import sys
import os
import ctypes
import threading
from typing import Any, Callable, List, Optional, Union, Dict, Tuple

# Enable Windows High-DPI Awareness
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

class Rect:
    """Pure Python Rect bounding box primitive for zero-dependency layout engine."""
    def __init__(self, x: int = 0, y: int = 0, w: int = 0, h: int = 0):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    @property
    def width(self) -> int: return self.w
    @property
    def height(self) -> int: return self.h

    def collidepoint(self, pos: Tuple[int, int]) -> bool:
        if not pos: return False
        px, py = pos[0], pos[1]
        return self.x <= px <= (self.x + self.w) and self.y <= py <= (self.y + self.h)

# Context Stack for Declarative Nesting
_context_stack: List['Node'] = []

def eval_prop(prop: Any, default: Any = None) -> Any:
    """Evaluates dynamic signal, callable, or constant property values."""
    if prop is None:
        return default
    if callable(prop):
        try:
            res = prop()
            return res if res is not None else default
        except Exception:
            return default
    if isinstance(prop, Signal):
        return prop.value if prop.value is not None else default
    return prop

def safe_eval_prop(node: Any, key: str, default: Any = None) -> Any:
    """Bulletproof null-safe property evaluator preventing KeyError and NoneType crashes."""
    if not node or not hasattr(node, "props") or not isinstance(node.props, dict):
        return default
    val = node.props.get(key)
    return eval_prop(val, default)


def failsafe_guard(default_return: Any = None):
    """Decorator shielding C-FFI callbacks and render loops from native OS crashes."""
    def _decorator(func):
        def _wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return default_return
        return _wrapper
    return _decorator



class RecursionGuard:
    """Recursion Depth Cap Guard for Deep Component Trees (Max Depth = 100)."""
    @staticmethod
    def is_safe_depth(depth: int, max_depth: int = 100) -> bool:
        return depth < max_depth


class ThreadDispatcher:
    """Async GUI Thread Dispatcher keeping the main loop at 120 FPS."""
    @staticmethod
    def run_async(func: Callable[[], None]):
        threading.Thread(target=func, daemon=True).start()


def parse_color(c: Union[str, Tuple[int, int, int], Callable]) -> Tuple[int, int, int]:
    c = eval_prop(c)
    if isinstance(c, (tuple, list)):
        return (int(c[0]), int(c[1]), int(c[2]))
    if not isinstance(c, str):
        return (255, 255, 255)
    c = c.strip()
    if c == "white" or c == "#FFFFFF": return (255, 255, 255)
    if c == "black" or c == "#000000" or c == "#050505" or c == "#0B0B0B" or c == "#0D0D0D": return (11, 11, 11)
    if c == "bg-primary": return (24, 24, 26)     # Fleet/VSCode main background
    if c == "bg-surface": return (30, 30, 32)     # Fleet/VSCode surface
    if c == "border-dim": return (43, 45, 48)     # subtle borders
    if c == "purple": return (155, 81, 224)
    if c == "cyan" or c == "neon-cyan": return (0, 242, 254)
    if c == "pink" or c == "neon-pink": return (255, 0, 127)
    if c == "green" or c == "#34C759" or c == "#00FF00": return (52, 199, 89)
    if c == "red" or c == "#FF3B30": return (255, 59, 48)
    if c == "muted": return (148, 163, 184)
    if c.startswith("#"):
        c = c.lstrip("#")
        if len(c) == 3: c = "".join([x*2 for x in c])
        if len(c) == 6:
            return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
    return (212, 212, 212)

