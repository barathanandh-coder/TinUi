"""Media and avatar presentation."""
from typing import Any, Callable, List, Optional, Union, Dict, Tuple
from ..core.node import Node

class Avatar(Node):
    def __init__(self, src: str = "assets/app_icon.png", size: int = 40, **kwargs):
        super().__init__("Avatar", src=src, size=size, **kwargs)

class Image(Node):
    def __init__(self, src: str = "assets/app_icon.png", width: int = 120, height: int = 120, **kwargs):
        super().__init__("Image", src=src, width=width, height=height, **kwargs)

