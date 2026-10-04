"""
TinPyUI Modern Accessible Component Primitives (The "Shadcn / Radix" Suite)
Includes Dialog/Modal, Tabs, Accordion, Select/Dropdown, Popover, Tooltip, and Toast notification system.
"""

import time
from typing import Any, Callable, Dict, List, Optional, Union
from ..core.node import Node
from ..core.signals import Signal

# =============================================================================
# 1. Dialog & Modal Primitive
# =============================================================================

class Dialog(Node):
    """
    Accessible, backdrop-blurred Modal Dialog with keyboard ESC dismissal,
    focus management, and spring scale animations.
    """
    def __init__(
        self,
        title: str = "",
        open: Union[bool, Signal] = False,
        on_close: Optional[Callable[[], None]] = None,
        width: str = "540px",
        show_close_button: bool = True,
        **kwargs
    ):
        self.open_signal = open if isinstance(open, Signal) else Signal(bool(open))
        self.on_close = on_close
        self.show_close_button = show_close_button

        tag_name = kwargs.pop("tag", None) or self.__class__.__name__
        super().__init__(
            tag_name,
            title=title,
            open=self.open_signal,
            width=width,
            show_close_button=show_close_button,
            on_close=self.close,
            **kwargs
        )

    def show(self):
        """Opens the dialog."""
        self.open_signal.value = True

    def close(self):
        """Closes the dialog."""
        self.open_signal.value = False
        if self.on_close:
            self.on_close()

    def toggle(self):
        """Toggles the open state of the dialog."""
        if self.open_signal.value:
            self.close()
        else:
            self.show()


class Modal(Dialog):
    """Alias for Dialog component."""
    pass


# =============================================================================
# 2. Tabs Suite (TabList, TabTrigger, TabContent)
# =============================================================================

class Tabs(Node):
    """
    Accessible Tab switcher with animated indicator and keyboard arrow navigation.
    """
    def __init__(
        self,
        default_value: str = "",
        value: Optional[Union[str, Signal]] = None,
        on_change: Optional[Callable[[str], None]] = None,
        variant: str = "underline",  # "underline" | "pills" | "contained"
        **kwargs
    ):
        init_val = value.value if isinstance(value, Signal) else (value or default_value)
        self.active_signal = value if isinstance(value, Signal) else Signal(init_val)
        self.on_change = on_change

        super().__init__(
            "Tabs",
            active_value=self.active_signal,
            variant=variant,
            **kwargs
        )

    def set_active(self, tab_value: str):
        self.active_signal.value = tab_value
        if self.on_change:
            self.on_change(tab_value)


class TabList(Node):
    """Horizontal container for TabTrigger elements."""
    def __init__(self, gap: int = 8, **kwargs):
        super().__init__("TabList", gap=str(gap), **kwargs)


class TabTrigger(Node):
    """Interactive tab button that activates a matching TabContent."""
    def __init__(self, label: str, value: str, icon: Optional[str] = None, **kwargs):
        super().__init__("TabTrigger", label=label, value=value, icon=icon or "", **kwargs)


class TabContent(Node):
    """Container panel whose visibility is bound to the active Tab value."""
    def __init__(self, value: str, **kwargs):
        super().__init__("TabContent", value=value, **kwargs)


# =============================================================================
# 3. Accordion & AccordionItem (Collapsible Panels)
# =============================================================================

class Accordion(Node):
    """
    Expandable accordion panels with spring height animation and chevron rotation.
    """
    def __init__(self, multiple: bool = False, **kwargs):
        self.multiple = multiple
        super().__init__("Accordion", multiple=multiple, **kwargs)


class AccordionItem(Node):
    """Single expandable panel within an Accordion."""
    def __init__(
        self,
        title: str,
        open: Union[bool, Signal] = False,
        icon: Optional[str] = None,
        on_toggle: Optional[Callable[[bool], None]] = None,
        **kwargs
    ):
        self.open_signal = open if isinstance(open, Signal) else Signal(bool(open))
        self.on_toggle = on_toggle

        super().__init__(
            "AccordionItem",
            title=title,
            open=self.open_signal,
            icon=icon or "",
            on_click=self.toggle,
            **kwargs
        )

    def toggle(self):
        new_val = not self.open_signal.value
        self.open_signal.value = new_val
        if self.on_toggle:
            self.on_toggle(new_val)


# =============================================================================
# 4. Select & Dropdown Primitive
# =============================================================================

class Select(Node):
    """
    Searchable, keyboard-navigable Dropdown Select with custom options and Signal binding.
    """
    def __init__(
        self,
        options: List[Union[str, Dict[str, str]]],
        bind: Optional[Signal] = None,
        placeholder: str = "Select an option...",
        label: str = "",
        on_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        normalized_options = []
        for opt in options:
            if isinstance(opt, dict):
                normalized_options.append(opt)
            else:
                normalized_options.append({"label": str(opt), "value": str(opt)})

        default_val = normalized_options[0]["value"] if normalized_options else ""
        self.selected_signal = bind if isinstance(bind, Signal) else Signal(default_val)
        self.on_change = on_change

        tag_name = kwargs.pop("tag", None) or self.__class__.__name__
        super().__init__(
            tag_name,
            label=label,
            options=normalized_options,
            value=self.selected_signal,
            placeholder=placeholder,
            on_change=self._handle_change,
            **kwargs
        )

    def _handle_change(self, new_val: str):
        self.selected_signal.value = new_val
        if self.on_change:
            self.on_change(new_val)


class Dropdown(Select):
    """Alias for Select component."""
    pass


# =============================================================================
# 5. Tooltip & Popover Primitives
# =============================================================================

class Tooltip(Node):
    """Contextual floating tooltip displayed on hover or focus."""
    def __init__(self, content: str = "", position: str = "top", text: Optional[str] = None, **kwargs):
        tip_text = text if text is not None else content
        super().__init__("Tooltip", content=tip_text, text=tip_text, position=position, **kwargs)


class Popover(Node):
    """Anchored floating popover card for rich interactive menus and forms."""
    def __init__(
        self,
        title: str = "",
        open: Union[bool, Signal] = False,
        position: str = "bottom",
        **kwargs
    ):
        self.open_signal = open if isinstance(open, Signal) else Signal(bool(open))
        super().__init__("Popover", title=title, open=self.open_signal, position=position, **kwargs)


# =============================================================================
# 6. Toast Notification System (tin.toast)
# =============================================================================

class ToastManager:
    """Reactive manager for stacking toast alerts."""
    def __init__(self):
        self.toasts: Signal = Signal([])
        self._counter: int = 0

    def show(self, message: str, variant: str = "info", duration: float = 3.5, title: Optional[str] = None):
        """Pushes a new toast notification."""
        self._counter += 1
        toast_id = f"toast_{int(time.time() * 1000)}_{self._counter}"
        new_toast = {
            "id": toast_id,
            "title": title or variant.capitalize(),
            "message": message,
            "variant": variant,  # "success" | "error" | "warning" | "info"
            "duration": duration
        }
        current = list(self.toasts.value or [])
        current.append(new_toast)
        self.toasts.value = current
        return toast_id

    def success(self, message: str, title: str = "Success", duration: float = 3.5):
        return self.show(message, variant="success", title=title, duration=duration)

    def error(self, message: str, title: str = "Error", duration: float = 4.5):
        return self.show(message, variant="error", title=title, duration=duration)

    def warning(self, message: str, title: str = "Warning", duration: float = 4.0):
        return self.show(message, variant="warning", title=title, duration=duration)

    def info(self, message: str, title: str = "Info", duration: float = 3.5):
        return self.show(message, variant="info", title=title, duration=duration)

    def dismiss(self, toast_id: str):
        current = list(self.toasts.value or [])
        self.toasts.value = [t for t in current if t["id"] != toast_id]

    def clear(self):
        self.toasts.value = []


# Global toast instance accessible via tin.toast
toast = ToastManager()


class ToastContainer(Node):
    """Floating onscreen container that renders active toasts."""
    def __init__(self, position: str = "bottom-right", **kwargs):
        super().__init__("ToastContainer", position=position, toasts=toast.toasts, **kwargs)
