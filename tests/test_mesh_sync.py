"""
Unit tests for TinPyUI Distributed Multi-Node State Sync & Mesh Networking (CRDT)
"""

import time
import unittest
from tinpyui.net.mesh import (
    VectorClock, LWWRegister, MeshState,
    PresenceTracker, MeshNode, use_mesh_state
)

class TestMeshSync(unittest.TestCase):

    def test_vector_clock_causality_and_concurrency(self):
        c1 = VectorClock({"A": 1, "B": 0})
        c2 = VectorClock({"A": 1, "B": 1})

        # c1 strictly precedes c2
        self.assertEqual(c1.compare(c2), -1)
        self.assertEqual(c2.compare(c1), 1)

        # Equal clocks
        self.assertEqual(c1.compare(VectorClock({"A": 1, "B": 0})), 0)

        # Concurrent clocks: A has higher on A, B has higher on B
        c_a = VectorClock({"A": 2, "B": 0})
        c_b = VectorClock({"A": 1, "B": 1})
        self.assertIsNone(c_a.compare(c_b))

        # Merge / update
        c_a.update(c_b)
        self.assertEqual(c_a.clock, {"A": 2, "B": 1})

    def test_lww_register_conflict_resolution(self):
        # Earlier write vs later write
        reg1 = LWWRegister(value="draft 1", timestamp=100.0, node_id="nodeA")
        reg2 = LWWRegister(value="draft 2", timestamp=105.0, node_id="nodeB")

        changed = reg1.merge(reg2)
        self.assertTrue(changed)
        self.assertEqual(reg1.value, "draft 2")
        self.assertEqual(reg1.node_id, "nodeB")

        # Reverse merge with older write does not overwrite
        reg3 = LWWRegister(value="old draft", timestamp=90.0, node_id="nodeC")
        changed2 = reg1.merge(reg3)
        self.assertFalse(changed2)
        self.assertEqual(reg1.value, "draft 2")

        # Tie-breaker: equal timestamps, lexicographical comparison of node_id
        reg_low = LWWRegister(value="valA", timestamp=200.0, node_id="aaa")
        reg_high = LWWRegister(value="valB", timestamp=200.0, node_id="zzz")

        reg_low.merge(reg_high)
        self.assertEqual(reg_low.value, "valB")  # 'zzz' > 'aaa'

    def test_mesh_state_convergence(self):
        # Simulate two distributed nodes syncing state
        node1 = MeshNode("peer_alpha")
        node2 = MeshNode("peer_beta")

        node1.state.set("document_title", "Q3 Report", timestamp=10.0)
        node1.state.set("author", "Alice", timestamp=10.0)

        node2.state.set("document_title", "Q3 Strategic Report", timestamp=15.0)
        node2.state.set("status", "Review", timestamp=12.0)

        # Peer 2 syncs into Peer 1
        updated_1 = node1.state.merge_state(node2.state.export_state())
        self.assertIn("document_title", updated_1)
        self.assertIn("status", updated_1)
        self.assertEqual(node1.state.get("document_title"), "Q3 Strategic Report")
        self.assertEqual(node1.state.get("author"), "Alice")
        self.assertEqual(node1.state.get("status"), "Review")

        # Peer 1 syncs into Peer 2
        updated_2 = node2.state.merge_state(node1.state.export_state())
        self.assertIn("author", updated_2)

        # Both nodes converge to identical state
        self.assertEqual(node1.state.get("document_title"), node2.state.get("document_title"))
        self.assertEqual(node1.state.get("author"), node2.state.get("author"))
        self.assertEqual(node1.state.get("status"), node2.state.get("status"))

    def test_presence_and_cursor_tracking(self):
        tracker = PresenceTracker(timeout_seconds=0.5)

        tracker.heartbeat("user_101", {"name": "Barath", "role": "admin"})
        tracker.update_cursor("user_101", 340.5, 780.0)

        tracker.heartbeat("user_102", {"name": "Sarah"})

        active = tracker.get_active_peers()
        self.assertEqual(len(active), 2)

        user_101 = next(p for p in active if p["node_id"] == "user_101")
        self.assertEqual(user_101["cursor"]["x"], 340.5)
        self.assertEqual(user_101["metadata"]["name"], "Barath")

        # Test timeout pruning
        time.sleep(0.6)
        pruned = tracker.prune_expired()
        self.assertIn("user_101", pruned)
        self.assertIn("user_102", pruned)
        self.assertEqual(len(tracker.get_active_peers()), 0)

    def test_use_mesh_state_hook(self):
        node = MeshNode("test_hook_node")
        sig, set_state = use_mesh_state("shared_counter", default=0, node=node)
        self.assertEqual(sig.value, 0)

        set_state(42)
        self.assertEqual(sig.value, 42)
        self.assertEqual(node.state.get("shared_counter"), 42)

if __name__ == "__main__":
    unittest.main()
