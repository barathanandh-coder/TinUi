"""Node hierarchy base class."""
from typing import Any, Callable, List, Dict
from .primitives import Rect, _context_stack
from .signals import Signal

class Node:
    """Base Node primitive for declarative layout hierarchy."""
    def __init__(self, tag: str, **kwargs):
        self.tag = tag
        self.props = kwargs
        self.children: List['Node'] = []
        self.rect = Rect(0, 0, 0, 0)
        self.is_focused = False
        self.is_hovered = False

        if _context_stack:
            _context_stack[-1].children.append(self)

    def add(self, *nodes: 'Node'):
        """Appends child nodes to this node container."""
        self.children.extend(nodes)
        return self

    def __enter__(self):
        _context_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _context_stack and _context_stack[-1] is self:
            _context_stack.pop()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag": self.tag,
            "props": {k: (str(v) if isinstance(v, Signal) else v) for k, v in self.props.items() if not callable(v)},
            "children": [c.to_dict() for c in self.children]
        }

