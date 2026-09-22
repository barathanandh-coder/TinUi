"""Low-code data display components."""
from typing import Any, Callable, List, Optional, Union, Dict, Tuple, TYPE_CHECKING
from ..core.node import Node
from ..core.primitives import eval_prop
from .layout import Card, Spacer
from .typography import Heading

if TYPE_CHECKING:
    from ..data.database import Table
else:
    Table = Any

class DataTable(Node):
    """Enterprise Data Grid Table Component supporting static data, dictionaries, Tables, and LiveQueries."""
    def __init__(self, columns: Optional[List[str]] = None, data: Any = None, **kwargs):
        cols = columns or []
        super().__init__("DataTable", columns=cols, data=data or [], **kwargs)


class LiveDataTable(Node):
    """Low-Code Reactive Data Table automatically wired to a Database Table, Collection, or LiveQuery."""
    def __init__(self, target: Any, columns: Optional[List[str]] = None, **kwargs):
        if isinstance(target, str):
            table_inst = db.table(target)
            live_data = table_inst.live_query()
        elif hasattr(target, "live_query"):
            table_inst = target
            live_data = target.live_query()
        elif isinstance(target, LiveQuery):
            table_inst = getattr(target, "table", None) or getattr(target, "collection", None)
            live_data = target
        else:
            table_inst = None
            live_data = target

        cols = columns
        if not cols and table_inst and hasattr(table_inst, "columns"):
            cols = table_inst.columns()
        if not cols and hasattr(live_data, "value") and live_data.value and isinstance(live_data.value, list) and len(live_data.value) > 0:
            if isinstance(live_data.value[0], dict):
                cols = list(live_data.value[0].keys())

        super().__init__("DataTable", columns=cols or [], data=live_data, **kwargs)


class AutoCRUD(Node):
    """1-Line Low-Code Full CRUD Interface Generator (Header, Live Grid, Action triggers)."""
    def __init__(self, target: Union[Table, str], title: str = "", **kwargs):
        table_inst = db.table(target) if isinstance(target, str) else target
        display_title = title or f"Manage {table_inst.name.capitalize()}"
        super().__init__("Card", padding="20px", border="1px solid #2B2D30", **kwargs)
        self.children.append(Heading(text=display_title, size="lg", color="#00f2fe"))
        self.children.append(Spacer())
        self.children.append(LiveDataTable(table_inst))

class Form(Node):
    """Enterprise Form Validation Container."""
    def __init__(self, on_submit: Optional[Callable[[Dict[str, Any]], None]] = None, **kwargs):
        super().__init__("Form", on_submit=on_submit, **kwargs)

