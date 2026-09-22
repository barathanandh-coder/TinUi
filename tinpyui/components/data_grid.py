"""
TinPyUI High-Performance Enterprise DataGrid Component
Features column sorting, search filtering, pagination, selection, and CSV/JSON export.
"""

import csv
import io
import json
from typing import Any, Callable, Dict, List, Optional, Union
from ..core.node import Node
from ..core.signals import Signal

class DataGrid(Node):
    """Enterprise DataGrid with column sorting, live search filtering, pagination, and data export."""

    def __init__(
        self,
        columns: Optional[List[Union[str, Dict[str, Any]]]] = None,
        data: Any = None,
        page_size: int = 10,
        searchable: bool = True,
        sortable: bool = True,
        selectable: bool = False,
        exportable: bool = True,
        on_row_click: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_selection_change: Optional[Callable[[List[Dict[str, Any]]], None]] = None,
        **kwargs
    ):
        raw_cols = columns or []
        normalized_cols: List[Dict[str, Any]] = []
        for c in raw_cols:
            if isinstance(c, str):
                normalized_cols.append({"key": c, "label": c.replace("_", " ").title(), "sortable": True})
            elif isinstance(c, dict):
                normalized_cols.append(c)

        self._columns = normalized_cols
        self._raw_data = data or []
        self._page_size = page_size
        self._current_page = 1
        self._sort_col: Optional[str] = None
        self._sort_asc: bool = True
        self._search_query: str = ""
        self._selected_indices: set = set()

        # If data is a reactive Signal, bind it
        if isinstance(data, Signal):
            self._raw_data = data.value or []
            data.subscribe(self._on_data_signal_update)

        # Infer columns if not provided
        if not self._columns and isinstance(self._raw_data, list) and len(self._raw_data) > 0:
            first = self._raw_data[0]
            if isinstance(first, dict):
                for k in first.keys():
                    self._columns.append({"key": k, "label": str(k).replace("_", " ").title(), "sortable": True})

        super().__init__(
            "DataGrid",
            columns=self._columns,
            data=self._raw_data,
            page_size=page_size,
            searchable=searchable,
            sortable=sortable,
            selectable=selectable,
            exportable=exportable,
            on_row_click=on_row_click,
            on_selection_change=on_selection_change,
            **kwargs
        )

    def _on_data_signal_update(self, new_val):
        self._raw_data = new_val or []
        self.props["data"] = self.get_processed_data()

    def set_search(self, query: str):
        """Sets the search filter string."""
        self._search_query = (query or "").strip().lower()
        self._current_page = 1
        self.props["search_query"] = self._search_query

    def sort_by(self, col_key: str, ascending: Optional[bool] = None):
        """Toggles or sets sort order on a column."""
        if self._sort_col == col_key and ascending is None:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col_key
            self._sort_asc = True if ascending is None else ascending
        self.props["sort_column"] = self._sort_col
        self.props["sort_asc"] = self._sort_asc

    def set_page(self, page_number: int):
        """Switches current page."""
        max_p = self.total_pages()
        self._current_page = max(1, min(page_number, max_p or 1))
        self.props["current_page"] = self._current_page

    def total_pages(self) -> int:
        """Returns total number of pages based on filtered records."""
        filtered = self.get_filtered_data()
        if not filtered:
            return 1
        return max(1, (len(filtered) + self._page_size - 1) // self._page_size)

    def get_filtered_data(self) -> List[Dict[str, Any]]:
        """Applies search filtering to data rows."""
        items = self._raw_data if isinstance(self._raw_data, list) else []
        if not self._search_query:
            filtered = list(items)
        else:
            q = self._search_query
            filtered = []
            for row in items:
                if isinstance(row, dict):
                    if any(q in str(v).lower() for v in row.values()):
                        filtered.append(row)
                elif q in str(row).lower():
                    filtered.append(row)

        if self._sort_col:
            key = self._sort_col
            filtered.sort(
                key=lambda r: (r.get(key) is None, r.get(key) if isinstance(r, dict) else ""),
                reverse=not self._sort_asc
            )
        return filtered

    def get_processed_data(self) -> List[Dict[str, Any]]:
        """Returns the current page slice of filtered and sorted data."""
        filtered = self.get_filtered_data()
        start = (self._current_page - 1) * self._page_size
        end = start + self._page_size
        return filtered[start:end]

    def export_csv(self) -> str:
        """Exports currently filtered data as CSV text string."""
        filtered = self.get_filtered_data()
        if not filtered:
            return ""
        output = io.StringIO()
        fieldnames = [c["key"] for c in self._columns] if self._columns else list(filtered[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in filtered:
            if isinstance(row, dict):
                writer.writerow({k: row.get(k, "") for k in fieldnames})
        return output.getvalue()

    def export_json(self) -> str:
        """Exports currently filtered data as formatted JSON string."""
        return json.dumps(self.get_filtered_data(), indent=2, default=str)
