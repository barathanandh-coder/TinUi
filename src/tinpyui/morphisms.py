"""Modern UI Morphism styles and design system definitions."""
from typing import Dict, List, Optional

class Morphism:
    """The 4 modern UI Morphisms supported natively by TinPyUI."""
    GLASS = "glass-morphism"
    NEUMORPHIC = "neu-morphism"
    CLAY = "clay-morphism"
    HOLO = "holo-morphism"

    ALL = [GLASS, NEUMORPHIC, CLAY, HOLO]

    STYLES = {
        "glass-morphism": "backdrop-filter: blur(16px); background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(255, 255, 255, 0.1);",
        "neu-morphism": "background: #0d121d; box-shadow: 8px 8px 20px #04060a, -8px -8px 20px #162034; border: 1px solid rgba(255, 255, 255, 0.05);",
        "clay-morphism": "background: rgba(30, 41, 59, 0.8); border-radius: 24px; box-shadow: inset 4px 4px 8px rgba(255,255,255,0.1), inset -4px -4px 8px rgba(0,0,0,0.4), 0 12px 24px rgba(0,0,0,0.5);",
        "holo-morphism": "background: linear-gradient(135deg, rgba(6,182,212,0.12), rgba(168,85,247,0.12)); border: 1px solid rgba(168,85,247,0.4); box-shadow: 0 0 25px rgba(168,85,247,0.25);"
    }

def get_morphism_style(morphism_name: str) -> str:
    """Returns CSS style string for a given morphism preset."""
    name = morphism_name.strip().lower()
    if name in ("glass", "frosted-glass"):
        name = "glass-morphism"
    elif name in ("neu", "neumorphism", "neumorphic"):
        name = "neu-morphism"
    elif name in ("clay", "claymorphism", "claymorphic"):
        name = "clay-morphism"
    elif name in ("holo", "holomorphism", "holomorphic"):
        name = "holo-morphism"
    elif not name.endswith("-morphism"):
        name = f"{name}-morphism"
        
    return Morphism.STYLES.get(name, "")
