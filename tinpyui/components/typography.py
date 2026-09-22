"""Typography and text presentation."""
from typing import Any, Callable, List, Optional, Union, Dict, Tuple
from ..core.node import Node
from .layout import _process_visual_props

class Heading(Node):
    def __init__(self, text: Any = "", color: str = "", size: str = "", **kwargs):
        super().__init__("Heading", text=text, color=color, size=size, **_process_visual_props(**kwargs))

class Text(Node):
    def __init__(self, text: Any = "", color: str = "", size: str = "", font_family: str = "", **kwargs):
        super().__init__("Text", text=text, color=color, size=size, font_family=font_family, **_process_visual_props(**kwargs))

class GradientText(Node):
    def __init__(self, text: Any = "", gradient: List[str] = None, **kwargs):
        super().__init__("GradientText", text=text, gradient=gradient or ["#00ffff", "#cfbcff"], **_process_visual_props(**kwargs))

class Badge(Node):
    def __init__(self, text: Any = "", variant: str = "#00ffff", **kwargs):
        super().__init__("Badge", text=text, variant=variant, **_process_visual_props(**kwargs))

class Icon(Node):
    def __init__(self, name: str = "", size: str = "", color: str = "", **kwargs):
        super().__init__("Icon", name=name, text=name, size=size, color=color, **_process_visual_props(**kwargs))

class Link(Node):
    def __init__(self, text: Any = "", href: str = "#", target: str = "", onClick: str = "", **kwargs):
        super().__init__("Link", text=text, href=href, target=target, onClick=onClick, **_process_visual_props(**kwargs))
