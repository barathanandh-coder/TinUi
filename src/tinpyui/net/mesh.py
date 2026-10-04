"""
TinPyUI v1.7.0 — Distributed Multi-Node State Sync & Mesh Networking (CRDT)
Provides decentralized real-time state synchronization, Conflict-Free Replicated Data Types (CRDTs),
Vector Clocks, Last-Write-Wins (LWW) Registers, and peer presence tracking.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Callable, Tuple, Union
from ..core.signals import Signal

class VectorClock:
    """
    Vector clock for causality and concurrency tracking across distributed mesh nodes.
    """
    def __init__(self, clock: Optional[Dict[str, int]] = None):
        self.clock: Dict[str, int] = dict(clock) if clock else {}

    def increment(self, node_id: str) -> int:
        """Increment the logical timestamp for a specific node."""
        self.clock[node_id] = self.clock.get(node_id, 0) + 1
        return self.clock[node_id]

    def update(self, other: "VectorClock"):
        """Merge with another vector clock taking the maximum of each node timestamp."""
        for nid, val in other.clock.items():
            self.clock[nid] = max(self.clock.get(nid, 0), val)

    def compare(self, other: "VectorClock") -> Optional[int]:
        """
        Compare two vector clocks:
         1: self strictly succeeds other (self > other)
        -1: self strictly precedes other (self < other)
         0: self is identical to other (self == other)
        None: concurrent / divergent clocks (neither dominates)
        """
        greater = False
        lesser = False
        all_keys = set(self.clock.keys()) | set(other.clock.keys())

        for k in all_keys:
            v1 = self.clock.get(k, 0)
            v2 = other.clock.get(k, 0)
            if v1 > v2:
                greater = True
            elif v1 < v2:
                lesser = True

        if greater and not lesser:
            return 1
        elif lesser and not greater:
            return -1
        elif not greater and not lesser:
            return 0
        return None  # Concurrent

    def to_dict(self) -> Dict[str, int]:
        return dict(self.clock)

    def copy(self) -> "VectorClock":
        return VectorClock(self.clock)


class LWWRegister:
    """
    Last-Write-Wins (LWW) Register with deterministic conflict resolution
    based on wall-clock timestamp and lexicographical node-ID tie-breaking.
    """
    def __init__(self, value: Any = None, timestamp: float = 0.0, node_id: str = "", clock: Optional[VectorClock] = None):
        self.value = value
        self.timestamp = timestamp or time.time()
        self.node_id = node_id or str(uuid.uuid4())[:8]
        self.clock = clock.copy() if clock else VectorClock()

    def merge(self, other: "LWWRegister") -> bool:
        """
        Merge with an incoming register.
        Returns True if this register's state was updated, False otherwise.
        """
        # 1. Compare wall-clock timestamps
        if other.timestamp > self.timestamp:
            self._adopt(other)
            return True
        elif other.timestamp < self.timestamp:
            return False

        # 2. Tie-breaker: lexicographical node_id comparison
        if other.node_id > self.node_id:
            self._adopt(other)
            return True

        return False

    def _adopt(self, other: "LWWRegister"):
        self.value = other.value
        self.timestamp = other.timestamp
        self.node_id = other.node_id
        self.clock.update(other.clock)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "timestamp": self.timestamp,
            "node_id": self.node_id,
            "clock": self.clock.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LWWRegister":
        return cls(
            value=data.get("value"),
            timestamp=data.get("timestamp", 0.0),
            node_id=data.get("node_id", ""),
            clock=VectorClock(data.get("clock", {}))
        )


class MeshState:
    """
    Collaborative reactive state dictionary synchronized across peer nodes via CRDT.
    """
    def __init__(self, node_id: Optional[str] = None):
        self.node_id = node_id or f"node_{uuid.uuid4().hex[:8]}"
        self._clock = VectorClock()
        self._registers: Dict[str, LWWRegister] = {}
        self._listeners: Dict[str, List[Callable[[Any], None]]] = {}
        self._global_listeners: List[Callable[[str, Any], None]] = []

    def set(self, key: str, value: Any, timestamp: Optional[float] = None) -> LWWRegister:
        """Set a key on the mesh state with local node authorship."""
        ts = timestamp or time.time()
        self._clock.increment(self.node_id)
        reg = LWWRegister(value=value, timestamp=ts, node_id=self.node_id, clock=self._clock)
        self._registers[key] = reg
        self._notify(key, value)
        return reg

    def get(self, key: str, default: Any = None) -> Any:
        """Get the current value for a key."""
        reg = self._registers.get(key)
        return reg.value if reg is not None else default

    def export_state(self) -> Dict[str, Dict[str, Any]]:
        """Export the full state payload as JSON-serializable dictionary."""
        return {k: reg.to_dict() for k, reg in self._registers.items()}

    def merge_state(self, remote_state: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Merge an incoming remote state payload into the local mesh state.
        Returns a list of updated keys.
        """
        updated_keys = []
        for key, raw_reg in remote_state.items():
            incoming_reg = LWWRegister.from_dict(raw_reg)
            if key not in self._registers:
                self._registers[key] = incoming_reg
                self._clock.update(incoming_reg.clock)
                self._notify(key, incoming_reg.value)
                updated_keys.append(key)
            else:
                changed = self._registers[key].merge(incoming_reg)
                if changed:
                    self._clock.update(incoming_reg.clock)
                    self._notify(key, self._registers[key].value)
                    updated_keys.append(key)
        return updated_keys

    def subscribe(self, key: str, callback: Callable[[Any], None]):
        """Subscribe to mutations of a specific key."""
        if key not in self._listeners:
            self._listeners[key] = []
        self._listeners[key].append(callback)

    def on_change(self, callback: Callable[[str, Any], None]):
        """Subscribe to all mutations across the mesh state."""
        self._global_listeners.append(callback)

    def _notify(self, key: str, value: Any):
        if key in self._listeners:
            for cb in self._listeners[key]:
                try:
                    cb(value)
                except Exception:
                    pass
        for cb in self._global_listeners:
            try:
                cb(key, value)
            except Exception:
                pass


class PresenceTracker:
    """
    Peer presence and real-time cursor/activity tracking for distributed mesh nodes.
    """
    def __init__(self, timeout_seconds: float = 10.0):
        self.timeout_seconds = timeout_seconds
        self._peers: Dict[str, Dict[str, Any]] = {}

    def heartbeat(self, node_id: str, metadata: Optional[Dict[str, Any]] = None):
        """Update or register a peer node's heartbeat."""
        now = time.time()
        if node_id not in self._peers:
            self._peers[node_id] = {"node_id": node_id, "first_seen": now, "cursor": None, "metadata": {}}
        self._peers[node_id]["last_seen"] = now
        if metadata:
            self._peers[node_id]["metadata"].update(metadata)

    def update_cursor(self, node_id: str, x: float, y: float):
        """Update peer cursor coordinates for multi-user collaboration."""
        self.heartbeat(node_id)
        self._peers[node_id]["cursor"] = {"x": x, "y": y, "updated_at": time.time()}

    def get_active_peers(self) -> List[Dict[str, Any]]:
        """Returns list of all active peer nodes that have sent heartbeats within timeout."""
        now = time.time()
        active = []
        for nid, data in list(self._peers.items()):
            if now - data.get("last_seen", 0) <= self.timeout_seconds:
                active.append(dict(data))
        return active

    def prune_expired(self) -> List[str]:
        """Prunes stale peers and returns their node IDs."""
        now = time.time()
        pruned = []
        for nid, data in list(self._peers.items()):
            if now - data.get("last_seen", 0) > self.timeout_seconds:
                pruned.append(nid)
                del self._peers[nid]
        return pruned


class MeshNode:
    """
    High-level distributed peer mesh coordinator.
    Encapsulates local MeshState, PresenceTracker, and network transport hooks.
    """
    def __init__(self, node_id: Optional[str] = None):
        self.node_id = node_id or f"peer_{uuid.uuid4().hex[:6]}"
        self.state = MeshState(node_id=self.node_id)
        self.presence = PresenceTracker()
        self._transport_send: Optional[Callable[[Dict[str, Any]], None]] = None

    def set_transport(self, send_callback: Callable[[Dict[str, Any]], None]):
        """Attach a network transport callback (e.g. WebSocket or WebRTC send)."""
        self._transport_send = send_callback

    def broadcast_state(self):
        """Broadcast the local state to connected mesh peers."""
        if self._transport_send:
            payload = {
                "type": "MESH_SYNC",
                "sender": self.node_id,
                "state": self.state.export_state(),
                "timestamp": time.time()
            }
            self._transport_send(payload)

    def handle_message(self, message: Dict[str, Any]) -> List[str]:
        """Handle an incoming network message from another mesh peer."""
        msg_type = message.get("type")
        sender = message.get("sender")

        if sender:
            self.presence.heartbeat(sender, metadata=message.get("metadata"))

        if msg_type == "MESH_SYNC":
            remote_state = message.get("state", {})
            return self.state.merge_state(remote_state)
        elif msg_type == "PRESENCE_CURSOR":
            if sender and "cursor" in message:
                c = message["cursor"]
                self.presence.update_cursor(sender, c.get("x", 0), c.get("y", 0))
        return []


# Global default mesh node
_default_mesh = MeshNode()

def use_mesh_state(key: str, default: Any = None, node: Optional[MeshNode] = None) -> Tuple[Signal, Callable[[Any], None]]:
    """
    Declarative hook binding a reactive Signal to the distributed mesh state.
    Returns: (signal, set_value_fn)
    """
    m_node = node or _default_mesh
    current_val = m_node.state.get(key, default)
    sig = Signal(current_val)

    def _setter(new_val: Any):
        sig.value = new_val
        m_node.state.set(key, new_val)
        m_node.broadcast_state()

    m_node.state.subscribe(key, lambda val: setattr(sig, "value", val))
    return sig, _setter
