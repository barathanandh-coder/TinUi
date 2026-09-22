"""Dynamic scroll velocity and inertia control helpers."""
from typing import Union

class ScrollSpeedPreset:
    """Predefined scroll velocity multipliers."""
    GLIDE = 0.5      # Gentle smooth glide
    STANDARD = 1.0   # 1.0x native standard scroll
    TURBO = 2.0      # 2.0x accelerated speed
    HYPER = 3.5      # 3.5x hyper-speed inertia

def set_scroll_speed(multiplier: Union[float, str]) -> str:
    """Returns the JavaScript invocation to set dynamic scroll velocity."""
    return f"setScrollSpeedMultiplier({float(multiplier)})"

def toggle_auto_scroll(active: Union[bool, None] = None) -> str:
    """Returns the JavaScript invocation to start/pause the auto-scroll tour."""
    if active is None:
        return "toggleAutoScroll()"
    return f"toggleAutoScroll({'true' if active else 'false'})"
