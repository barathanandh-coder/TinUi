"""Client-side routing engine."""
from typing import Dict, Any, Optional
from ..core.signals import Signal
from typing import Any, Callable, List, Optional, Union, Dict, Tuple
from ..core.node import Node

class Router:
    """Enterprise Multi-Page View Navigation Router."""
    def __init__(self):
        self.routes: Dict[str, Callable[[], Node]] = {}
        self.current_route = Signal("/")

    def add_route(self, path: str, view_fn: Callable[[], Node]):
        self.routes[path] = view_fn
        return self

    def navigate(self, path: str):
        if path in self.routes:
            self.current_route.value = path
        return self

    def render(self) -> Node:
        view_fn = self.routes.get(self.current_route.value)
        if view_fn:
            return view_fn()
        return Text("404 View Route Not Found")


