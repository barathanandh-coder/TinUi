"""
TinPyUI Hierarchical TreeView & TreeNode Component
Supports nested collapsible folders, selection state, and custom glyphs/icons.
"""

from typing import Any, Callable, Dict, List, Optional, Union
from ..core.node import Node
from ..core.signals import Signal

class TreeNode:
    """Represents a hierarchical node in a TreeView."""
    def __init__(
        self,
        id: str,
        label: str,
        icon: Optional[str] = None,
        children: Optional[List["TreeNode"]] = None,
        expanded: bool = False,
        data: Any = None
    ):
        self.id = str(id)
        self.label = label
        self.icon = icon or ("📁" if children else "📄")
        self.children = children or []
        self.expanded = expanded
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "icon": self.icon,
            "expanded": self.expanded,
            "data": self.data,
            "children": [c.to_dict() for c in self.children]
        }


class TreeView(Node):
    """Interactive Collapsible TreeView component."""

    def __init__(
        self,
        nodes: Optional[List[Union[TreeNode, Dict[str, Any]]]] = None,
        selected_id: Optional[str] = None,
        on_select: Optional[Callable[[Dict[str, Any]], None]] = None,
        **kwargs
    ):
        self.on_select = on_select
        self._selected_id = selected_id

        raw_nodes = nodes or []
        normalized: List[Dict[str, Any]] = []
        for n in raw_nodes:
            if isinstance(n, TreeNode):
                normalized.append(n.to_dict())
            elif isinstance(n, dict):
                normalized.append(n)

        self._nodes = normalized

        super().__init__(
            "TreeView",
            nodes=self._nodes,
            selected_id=self._selected_id,
            on_select=self._handle_select,
            **kwargs
        )

    def _handle_select(self, node_data: Dict[str, Any]):
        node_id = node_data.get("id") if isinstance(node_data, dict) else str(node_data)
        self.select_node(node_id)

    def select_node(self, node_id: str):
        """Sets the selected node ID and fires callback."""
        self._selected_id = node_id
        self.props["selected_id"] = node_id
        if self.on_select:
            node = self.find_node(node_id)
            if node:
                try:
                    self.on_select(node)
                except Exception:
                    pass

    def find_node(self, node_id: str, nodes_list: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
        """Finds a node dictionary by ID recursively."""
        search_in = self._nodes if nodes_list is None else nodes_list
        for n in search_in:
            if n.get("id") == node_id:
                return n
            if n.get("children"):
                found = self.find_node(node_id, n["children"])
                if found:
                    return found
        return None

    def toggle_expand(self, node_id: str):
        """Toggles the expanded state of a node."""
        node = self.find_node(node_id)
        if node and "children" in node and node["children"]:
            node["expanded"] = not node.get("expanded", False)
            self.props["nodes"] = list(self._nodes)
