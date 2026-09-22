"""Interactive input widgets."""
from typing import Any, Callable, List, Optional, Union, Dict, Tuple
from ..core.node import Node

class Button(Node):
    def __init__(self, text: Any = "Button", on_click: Optional[Union[str, Callable]] = None, variant: str = "primary", **kwargs):
        super().__init__("Button", text=text, on_click=on_click, variant=variant, **kwargs)

class Input(Node):
    def __init__(self, placeholder: str = "", variable: Any = None, value: Any = None, **kwargs):
        sig = value if value is not None else variable
        super().__init__("Input", placeholder=placeholder, variable=sig, value=sig, text_value="", **kwargs)

class NavItem(Node):
    def __init__(self, text: Any = "", icon: str = "", active: Any = False, on_click: Optional[Callable] = None, **kwargs):
        super().__init__("NavItem", text=text, icon=icon, active=active, on_click=on_click, **kwargs)


class Slider(Node):
    def __init__(self, value: Any = 50, min: int = 0, max: int = 100, on_change: Optional[Callable] = None, **kwargs):
        super().__init__("Slider", value=value, min=min, max=max, on_change=on_change, **kwargs)

class Switch(Node):
    def __init__(self, active: Any = True, on_change: Optional[Callable] = None, **kwargs):
        super().__init__("Switch", active=active, on_change=on_change, **kwargs)

class Progress(Node):
    def __init__(self, value: Any = 50, max: int = 100, color: str = "#00f2fe", **kwargs):
        super().__init__("Progress", value=value, max=max, color=color, **kwargs)

class ProgressBar(Progress):
    """Alias for Progress bar component."""
    pass

