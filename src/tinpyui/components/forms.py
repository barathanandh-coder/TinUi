"""
TinPyUI Two-Way Reactive Form State & Live Validation Suite
Beats React-Hook-Form and Formik with zero boilerplate, fine-grained validation signals, and auto-error rendering.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Union
from ..core.node import Node
from ..core.signals import Signal

# =============================================================================
# 1. Validation Rule Primitives
# =============================================================================

def required(msg: str = "This field is required") -> Callable[[Any], Optional[str]]:
    """Validates that a value is non-empty."""
    def rule(val: Any) -> Optional[str]:
        if val is None:
            return msg
        if isinstance(val, str) and not val.strip():
            return msg
        if isinstance(val, (list, dict)) and len(val) == 0:
            return msg
        return None
    return rule


def min_length(length: int, msg: Optional[str] = None) -> Callable[[Any], Optional[str]]:
    """Validates that a string or collection has at least `length` items."""
    default_msg = f"Must be at least {length} characters"
    error_msg = msg or default_msg
    def rule(val: Any) -> Optional[str]:
        if val is None:
            return None
        if len(str(val)) < length:
            return error_msg
        return None
    return rule


def max_length(length: int, msg: Optional[str] = None) -> Callable[[Any], Optional[str]]:
    """Validates that a string or collection has at most `length` items."""
    default_msg = f"Must be at most {length} characters"
    error_msg = msg or default_msg
    def rule(val: Any) -> Optional[str]:
        if val is None:
            return None
        if len(str(val)) > length:
            return error_msg
        return None
    return rule


def email(msg: str = "Please enter a valid email address") -> Callable[[Any], Optional[str]]:
    """Validates that a value matches standard email format."""
    email_regex = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    def rule(val: Any) -> Optional[str]:
        if not val:
            return None
        if not email_regex.match(str(val)):
            return msg
        return None
    return rule


def numeric(msg: str = "Must be a valid numeric value") -> Callable[[Any], Optional[str]]:
    """Validates that a value can be parsed as a number."""
    def rule(val: Any) -> Optional[str]:
        if val is None or val == "":
            return None
        try:
            float(val)
            return None
        except ValueError:
            return msg
    return rule


def pattern(regex_str: str, msg: str = "Invalid format") -> Callable[[Any], Optional[str]]:
    """Validates that a value matches the specified regular expression."""
    compiled = re.compile(regex_str)
    def rule(val: Any) -> Optional[str]:
        if not val:
            return None
        if not compiled.search(str(val)):
            return msg
        return None
    return rule


def custom(fn: Callable[[Any], bool], msg: str = "Validation failed") -> Callable[[Any], Optional[str]]:
    """Validates against a custom boolean predicate function."""
    def rule(val: Any) -> Optional[str]:
        try:
            passed = fn(val)
            return None if passed else msg
        except Exception as e:
            return f"Validation error: {e}"
    return rule


# =============================================================================
# 2. FormField Component
# =============================================================================

class FormField(Node):
    """
    Controlled input with two-way Signal data binding, label, and reactive validation errors.
    """
    def __init__(
        self,
        label: str = "",
        bind: Optional[Signal] = None,
        name: Optional[str] = None,
        type: str = "text",
        placeholder: str = "",
        rules: Optional[List[Callable[[Any], Optional[str]]]] = None,
        helper_text: str = "",
        required: bool = False,
        **kwargs
    ):
        self.field_name = name or label.lower().replace(" ", "_") or "field"
        self.bind_signal = bind if isinstance(bind, Signal) else Signal(bind or "")
        self.rules = list(rules or [])
        if required and not any(r.__name__ == 'rule' for r in self.rules):
            self.rules.insert(0, globals()["required"]())

        self.error_signal = Signal("")
        self.is_valid_signal = Signal(True)
        self.is_dirty = Signal(False)

        # Validate on signal mutations
        self.bind_signal.subscribe(self._on_value_change)

        super().__init__(
            "FormField",
            label=label,
            field_name=self.field_name,
            input_type=type,
            placeholder=placeholder,
            value=self.bind_signal,
            error=self.error_signal,
            is_valid=self.is_valid_signal,
            helper_text=helper_text,
            is_required=required,
            **kwargs
        )

    def _on_value_change(self, val):
        self.is_dirty.value = True
        err = self.validate()
        self.error_signal.value = err or ""
        self.is_valid_signal.value = err is None

    def validate(self) -> Optional[str]:
        val = self.bind_signal.value
        for r in self.rules:
            res = r(val)
            if res:
                return res
        return None


# =============================================================================
# 3. Form Container
# =============================================================================

class Form(Node):
    """
    Declarative Form container that coordinates child FormFields, tracks form-wide validity,
    and executes callbacks on submission.
    """
    def __init__(
        self,
        on_submit: Optional[Callable[[Dict[str, Any], bool], None]] = None,
        on_change: Optional[Callable[[Dict[str, Any]], None]] = None,
        gap: int = 16,
        padding: int = 24,
        card: bool = True,
        title: Optional[str] = None,
        **kwargs
    ):
        self.on_submit = on_submit
        self.on_change = on_change
        self.is_form_valid = Signal(True)
        self._fields: List[FormField] = []

        super().__init__(
            "Form",
            title=title or "",
            is_valid=self.is_form_valid,
            gap=str(gap),
            padding=str(padding),
            card=card,
            on_submit=self.submit,
            **kwargs
        )

    def add(self, *nodes: Node):
        for n in nodes:
            if isinstance(n, FormField):
                self._fields.append(n)
        return super().add(*nodes)

    def __enter__(self):
        super().__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Discover child FormFields added within context block
        for child in self.children:
            self._collect_fields(child)
        super().__exit__(exc_type, exc_val, exc_tb)

    def _collect_fields(self, node: Node):
        if isinstance(node, FormField) and node not in self._fields:
            self._fields.append(node)
        for c in node.children:
            self._collect_fields(c)

    def get_values(self) -> Dict[str, Any]:
        """Collects current values of all registered fields."""
        return {f.field_name: f.bind_signal.value for f in self._fields}

    def validate(self) -> bool:
        """Validates all fields in the form and updates error states."""
        all_valid = True
        for f in self._fields:
            err = f.validate()
            f.error_signal.value = err or ""
            f.is_valid_signal.value = err is None
            if err:
                all_valid = False
        self.is_form_valid.value = all_valid
        return all_valid

    def submit(self) -> bool:
        """Executes form submission handler with validated data."""
        is_valid = self.validate()
        data = self.get_values()
        if self.on_submit:
            self.on_submit(data, is_valid)
        return is_valid

    def reset(self):
        """Resets all fields to their default state."""
        for f in self._fields:
            f.bind_signal.value = ""
            f.error_signal.value = ""
            f.is_valid_signal.value = True
            f.is_dirty.value = False
        self.is_form_valid.value = True
