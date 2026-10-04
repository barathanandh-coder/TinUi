"""
TinPyUI Modern ColorPicker Component
Supports Hex, RGB, HSL, alpha channel slider, preset palettes, and reactive signals.
"""

from typing import Any, Callable, List, Optional, Union
from ..core.node import Node
from ..core.signals import Signal

DEFAULT_PRESETS = [
    "#00f2fe", "#4facfe", "#00c6ff", "#0072ff",
    "#f857a6", "#ff5858", "#ffaa00", "#ffd200",
    "#00f5a0", "#00d9f5", "#a18cd1", "#fbc2eb",
    "#ffffff", "#888888", "#1e1e24", "#0a0b10"
]

class ColorPicker(Node):
    """Interactive ColorPicker with Hex/RGB/Alpha selection and reactive Signal binding."""

    def __init__(
        self,
        value: Union[str, Signal] = "#00f2fe",
        presets: Optional[List[str]] = None,
        show_alpha: bool = True,
        show_presets: bool = True,
        on_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        self.on_change = on_change
        self._show_alpha = show_alpha
        self._presets = presets or DEFAULT_PRESETS

        if isinstance(value, Signal):
            self._color_signal = value
            self._current_color = str(value.value or "#00f2fe")
            value.subscribe(self._on_color_signal_update)
        else:
            self._color_signal = None
            self._current_color = str(value or "#00f2fe")

        super().__init__(
            "ColorPicker",
            value=self._current_color,
            presets=self._presets,
            show_alpha=show_alpha,
            show_presets=show_presets,
            on_change=self._handle_color_change,
            **kwargs
        )

    def _on_color_signal_update(self, new_val):
        self._current_color = str(new_val)
        self.props["value"] = self._current_color

    def _handle_color_change(self, new_color: str):
        self.set_color(new_color)

    def set_color(self, hex_or_rgba: str):
        """Updates the active color and notifies observers."""
        self._current_color = hex_or_rgba
        self.props["value"] = hex_or_rgba
        if self._color_signal:
            self._color_signal.value = hex_or_rgba
        if self.on_change:
            try:
                self.on_change(hex_or_rgba)
            except Exception:
                pass

    @property
    def color(self) -> str:
        return self._current_color
