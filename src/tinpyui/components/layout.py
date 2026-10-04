"""Declarative layout containers and visual surfaces."""
from typing import Any, Callable, List, Optional, Union, Dict, Tuple
from ..core.node import Node

def _process_visual_props(**kwargs) -> Dict[str, Any]:
    """Helper to process visual styling props (morphism, scroll reveal, glow, etc.)."""
    props = dict(kwargs)
    classes = []
    
    orig_class = props.get("class_", props.get("class", ""))
    if orig_class:
        classes.append(str(orig_class))

    morphism = props.pop("morphism", None)
    if morphism:
        m_str = str(morphism).strip().lower()
        if m_str in ("glass", "frosted-glass"):
            m_str = "glass-morphism"
        elif m_str in ("neu", "neumorphism", "neumorphic"):
            m_str = "neu-morphism"
        elif m_str in ("clay", "claymorphism", "claymorphic"):
            m_str = "clay-morphism"
        elif m_str in ("holo", "holomorphism", "holomorphic"):
            m_str = "holo-morphism"
        elif not m_str.endswith("-morphism"):
            m_str = f"{m_str}-morphism"
        classes.append(m_str)
        props["data-morphism"] = m_str

    reveal = props.pop("reveal_on_scroll", None) or props.pop("scroll_reveal", None)
    if reveal:
        classes.append("reveal-on-scroll")
        props["data-scroll-reveal"] = "true"

    movable = props.pop("movable", None) or props.pop("draggable", None)
    if movable:
        props["data-movable"] = "true"

    glow = props.pop("glow", None)
    if glow is not None and glow is not False:
        props["data-glow"] = str(glow)

    redirect = props.pop("redirect_to", None) or props.pop("page_redirect", None)
    if redirect:
        props["data-redirect-to"] = str(redirect)

    if classes:
        final_class = " ".join(classes)
        props["class_"] = final_class
        if "class" in props:
            props["class"] = final_class

    return props

class Section(Node):
    def __init__(self, **kwargs): super().__init__("Section", **_process_visual_props(**kwargs))

class Row(Node):
    def __init__(self, **kwargs): super().__init__("Row", **_process_visual_props(**kwargs))

class Column(Node):
    def __init__(self, align_items: str = "", **kwargs):
        super().__init__("Column", align_items=align_items, **_process_visual_props(**kwargs))

class Card(Node):
    def __init__(self, **kwargs): super().__init__("Card", **_process_visual_props(**kwargs))

class Container(Node):
    def __init__(self, **kwargs): super().__init__("Container", **_process_visual_props(**kwargs))

class Grid(Node):
    def __init__(self, cols: Union[int, str] = 1, gap: Union[int, str] = 16, **kwargs):
        super().__init__("Grid", cols=str(cols), gap=str(gap), **_process_visual_props(**kwargs))

class Surface(Node):
    def __init__(self, **kwargs): super().__init__("Surface", **_process_visual_props(**kwargs))

class HeroContainer(Node):
    def __init__(self, **kwargs): super().__init__("HeroContainer", **_process_visual_props(**kwargs))

class LayoutWindow(Node):
    def __init__(self, title: str = "", blur: bool = False, **kwargs):
        super().__init__("Window", title=title, blur=blur, **_process_visual_props(**kwargs))

class Spacer(Node):
    def __init__(self, **kwargs): super().__init__("Spacer", **kwargs)

class Divider(Node):
    def __init__(self, **kwargs): super().__init__("Divider", **kwargs)

class AnimatedBackground(Node):
    def __init__(self, effect: str = "cyber-wave", primaryColor: str = "#00f2fe", secondaryColor: str = "#9b51e0", **kwargs):
        super().__init__("AnimatedBackground", effect=effect, primaryColor=primaryColor, secondaryColor=secondaryColor, **kwargs)

class Navbar(Node):
    def __init__(self, title: str = "", blur: bool = True, **kwargs):
        super().__init__("Navbar", title=title, blur=blur, **_process_visual_props(**kwargs))

class Header(Node):
    def __init__(self, **kwargs): super().__init__("Header", **_process_visual_props(**kwargs))

class Footer(Node):
    def __init__(self, **kwargs): super().__init__("Footer", **_process_visual_props(**kwargs))

class Main(Node):
    def __init__(self, **kwargs): super().__init__("Main", **_process_visual_props(**kwargs))

class Marquee(Node):
    def __init__(self, **kwargs): super().__init__("Marquee", **_process_visual_props(**kwargs))

class Modal(Node):
    def __init__(self, open: bool = False, **kwargs):
        super().__init__("Modal", open=open, **_process_visual_props(**kwargs))

class Tooltip(Node):
    def __init__(self, text: str = "", **kwargs):
        super().__init__("Tooltip", text=text, **_process_visual_props(**kwargs))

class ShaderLayer(Node):
    def __init__(self, effect: str = "black_hole", speed: Union[float, str] = 1.0, intensity: Union[float, str] = 1.0, **kwargs):
        super().__init__("ShaderLayer", effect=effect, speed=str(speed), intensity=str(intensity), **_process_visual_props(**kwargs))

class WebGLCanvas(Node):
    def __init__(self, id: str = "shader-canvas", preset: str = "black_hole", fragmentCode: str = "", **kwargs):
        super().__init__("WebGLCanvas", id=id, preset=preset, fragmentCode=fragmentCode, **_process_visual_props(**kwargs))

class ParticleField(Node):
    def __init__(self, count: int = 60, color: str = "neon-purple", speed: float = 1.0, interactive: bool = True, **kwargs):
        super().__init__("ParticleField", count=str(count), color=color, speed=str(speed), interactive=interactive, **_process_visual_props(**kwargs))
