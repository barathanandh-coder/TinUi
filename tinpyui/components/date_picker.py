"""
TinPyUI DatePicker & Interactive Calendar Components
Supports single date & range selection, month navigation, presets, and reactive signals.
"""

import calendar
import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from ..core.node import Node
from ..core.signals import Signal

class Calendar(Node):
    """Interactive monthly calendar grid."""

    def __init__(
        self,
        year: Optional[int] = None,
        month: Optional[int] = None,
        selected_date: Optional[Union[str, Signal]] = None,
        on_select: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        now = datetime.date.today()
        self._year = year or now.year
        self._month = month or now.month
        self.on_select = on_select

        if isinstance(selected_date, Signal):
            self._date_signal = selected_date
            self._selected_date = str(selected_date.value or now.isoformat())
            selected_date.subscribe(self._on_signal_update)
        else:
            self._date_signal = None
            self._selected_date = str(selected_date or now.isoformat())

        super().__init__(
            "Calendar",
            year=self._year,
            month=self._month,
            selected_date=self._selected_date,
            month_matrix=self.get_month_matrix(),
            on_select=self._handle_select,
            **kwargs
        )

    def _on_signal_update(self, val):
        self._selected_date = str(val)
        self.props["selected_date"] = self._selected_date

    def _handle_select(self, date_str: str):
        self.select_date(date_str)

    def select_date(self, date_str: str):
        """Sets selected date and triggers on_select."""
        self._selected_date = date_str
        self.props["selected_date"] = date_str
        if self._date_signal:
            self._date_signal.value = date_str
        if self.on_select:
            try:
                self.on_select(date_str)
            except Exception:
                pass

    def get_month_matrix(self) -> List[List[int]]:
        """Returns 2D grid matrix of day numbers for current month."""
        return calendar.monthcalendar(self._year, self._month)

    def next_month(self):
        """Navigates to next month."""
        if self._month == 12:
            self._month = 1
            self._year += 1
        else:
            self._month += 1
        self.props["year"] = self._year
        self.props["month"] = self._month
        self.props["month_matrix"] = self.get_month_matrix()

    def prev_month(self):
        """Navigates to previous month."""
        if self._month == 1:
            self._month = 12
            self._year -= 1
        else:
            self._month -= 1
        self.props["year"] = self._year
        self.props["month"] = self._month
        self.props["month_matrix"] = self.get_month_matrix()


class DatePicker(Node):
    """Input field with popup Calendar dropdown, presets, and format configuration."""

    def __init__(
        self,
        value: Optional[Union[str, Signal]] = None,
        placeholder: str = "Select date...",
        date_format: str = "%Y-%m-%d",
        min_date: Optional[str] = None,
        max_date: Optional[str] = None,
        presets: bool = True,
        on_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        self.date_format = date_format
        self.on_change = on_change

        if isinstance(value, Signal):
            self._val_signal = value
            self._current_val = str(value.value or datetime.date.today().strftime(date_format))
            value.subscribe(self._on_signal_update)
        else:
            self._val_signal = None
            self._current_val = str(value or datetime.date.today().strftime(date_format))

        super().__init__(
            "DatePicker",
            value=self._current_val,
            placeholder=placeholder,
            format=date_format,
            min_date=min_date,
            max_date=max_date,
            presets=presets,
            on_change=self._handle_change,
            **kwargs
        )

    def _on_signal_update(self, val):
        self._current_val = str(val)
        self.props["value"] = self._current_val

    def _handle_change(self, val: str):
        self.set_value(val)

    def set_value(self, val: str):
        self._current_val = val
        self.props["value"] = val
        if self._val_signal:
            self._val_signal.value = val
        if self.on_change:
            try:
                self.on_change(val)
            except Exception:
                pass
