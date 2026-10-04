"""
TinPyUI Declarative Client-Side Router with Dynamic Route Parameters (:param) & Browser History Sync
Enables Single-Page Application (SPA) navigation without page reloads.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Union
from ..core.node import Node
from ..core.signals import Signal

class Route(Node):
    """
    Defines a mapped route matching a URL path pattern to a UI component or builder.
    Supports dynamic parameters, e.g. path="/users/:id"
    """
    def __init__(
        self,
        path: str,
        component: Optional[Union[Node, Callable[..., Node]]] = None,
        title: Optional[str] = None,
        **kwargs
    ):
        clean_path = path.rstrip("/") or "/"
        self.pattern_path = clean_path
        self.component = component
        self.title = title

        # Compile path into regex for matching dynamic parameters like :id
        self._param_names = re.findall(r":([a-zA-Z_][a-zA-Z0-9_]*)", clean_path)
        regex_pattern = "^" + re.sub(r":([a-zA-Z_][a-zA-Z0-9_]*)", r"(?P<\1>[^/]+)", clean_path) + "$"
        self._compiled_regex = re.compile(regex_pattern)

        super().__init__("Route", path=clean_path, title=title or "", **kwargs)

    def match(self, current_url: str) -> Optional[Dict[str, str]]:
        """Matches a URL against this route pattern, returning extracted params or None."""
        clean_url = current_url.split("?")[0].rstrip("/") or "/"
        clean_pattern = self.pattern_path.rstrip("/") or "/"
        
        if clean_url == clean_pattern:
            return {}

        match = self._compiled_regex.match(clean_url)
        if match:
            return match.groupdict()
        return None


class Router(Node):
    """
    Declarative Router component coordinating active Route selection and URL navigation.
    """
    def __init__(
        self,
        routes: Optional[List[Route]] = None,
        initial_path: str = "/",
        mode: str = "history",  # "history" | "hash"
        **kwargs
    ):
        self.mode = mode
        self.current_path = Signal(initial_path)
        self.current_route = self.current_path  # Backward compatibility alias
        self.params = Signal({})
        self.active_route = Signal(None)
        self.routes: List[Route] = list(routes or [])

        super().__init__(
            "Router",
            current_path=self.current_path,
            mode=mode,
            params=self.params,
            **kwargs
        )

    def add_route(self, path: str, component: Union[Node, Callable[..., Node]], title: Optional[str] = None) -> Route:
        route = Route(path=path, component=component, title=title)
        self.routes.append(route)
        self.children.append(route)
        return route

    def navigate(self, to: str):
        """Navigates to a new URL and triggers active route recalculation."""
        self.current_path.value = to
        self._resolve_active_route()

    def render(self) -> Optional[Node]:
        """Renders the current active route component or view function."""
        active = self.active_route.value
        if not active:
            active = self._resolve_active_route()
        if active and active.component:
            if callable(active.component):
                return active.component()
            return active.component
        return None

    def _resolve_active_route(self):
        url = self.current_path.value
        for route in self.routes:
            matched_params = route.match(url)
            if matched_params is not None:
                self.params.value = matched_params
                self.active_route.value = route
                return route
        self.active_route.value = None
        self.params.value = {}
        return None

    def __enter__(self):
        super().__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for child in self.children:
            if isinstance(child, Route) and child not in self.routes:
                self.routes.append(child)
        self._resolve_active_route()
        super().__exit__(exc_type, exc_val, exc_tb)
