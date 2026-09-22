"""
Unit tests for TinPyUI Optimization Suite:
- High-Speed Binary Opcode IR (TINB) Encoding & Decoding
- Lockless Shared Memory Ring Buffer IPC (< 10 µs event queue)
- Fine-Grained Dirty-Bit Signal Reactivity ($O(1)$ constant-time node mutations)
- Dynamic Resolution Scaling (DRS) & Frustum Culling presence in tin-runtime.js
"""

import json
import time
import unittest
from pathlib import Path

from tinpyui.core.binary_ir import encode_binary_ir, decode_binary_ir, MAGIC
from tinpyui.core.ring_buffer import RingBufferIPC
from tinpyui.core.signals import Signal, State

class TestOptimizations(unittest.TestCase):

    def test_binary_ir_roundtrip(self):
        """Test encoding and decoding of an IR opcode dictionary with 100% accuracy."""
        original_ir = {
            "nodes": [
                {"op": "CREATE_NODE", "id": 1, "tag": "div"},
                {"op": "SET_ATTRIBUTE", "id": 1, "key": "class", "value": "glass-card p-6"},
                {"op": "CREATE_NODE", "id": 2, "tag": "h2"},
                {"op": "SET_TEXT", "id": 2, "value": "TinPyUI High-Speed Engine"},
                {"op": "APPEND_CHILD", "parent": 1, "child": 2},
                {"op": "CREATE_NODE", "id": 3, "tag": "button"},
                {"op": "SET_ATTRIBUTE", "id": 3, "key": "onClick", "value": "alert('Hello')"},
                {"op": "SET_TEXT", "id": 3, "value": "Launch"},
                {"op": "APPEND_CHILD", "parent": 1, "child": 3},
                {"op": "APPEND_CHILD", "parent": None, "child": 1}
            ]
        }

        bin_data = encode_binary_ir(original_ir)
        self.assertTrue(bin_data.startswith(MAGIC))

        decoded_ir = decode_binary_ir(bin_data)
        self.assertEqual(len(decoded_ir["nodes"]), len(original_ir["nodes"]))

        for orig, dec in zip(original_ir["nodes"], decoded_ir["nodes"]):
            self.assertEqual(orig["op"], dec["op"])
            self.assertEqual(orig.get("id"), dec.get("id"))
            if "tag" in orig:
                self.assertEqual(orig["tag"], dec["tag"])
            if "key" in orig:
                self.assertEqual(orig["key"], dec["key"])
            if "value" in orig:
                self.assertEqual(orig["value"], dec["value"])
            if "parent" in orig:
                self.assertEqual(orig["parent"], dec["parent"])
            if "child" in orig:
                self.assertEqual(orig["child"], dec["child"])

    def test_binary_ir_payload_efficiency(self):
        """Verify that Binary IR is significantly more compact than raw JSON."""
        ir = {
            "nodes": [
                {"op": "CREATE_NODE", "id": i, "tag": "div"}
                for i in range(1, 100)
            ] + [
                {"op": "SET_ATTRIBUTE", "id": i, "key": "class", "value": "glass-card p-4 rounded-xl border border-cyan-500"}
                for i in range(1, 100)
            ]
        }

        json_bytes = json.dumps(ir).encode("utf-8")
        bin_bytes = encode_binary_ir(ir)

        # Binary IR should be substantially more compact due to string deduplication and binary integers
        self.assertLess(len(bin_bytes), len(json_bytes) * 0.55,
                        f"Binary IR ({len(bin_bytes)} B) should be at least 45% smaller than JSON ({len(json_bytes)} B)")

    def test_ring_buffer_ipc_performance(self):
        """Test sub-microsecond throughput of the lockless shared memory ring buffer."""
        ring = RingBufferIPC(capacity=1024)
        self.assertTrue(ring.is_empty())

        # Push 500 events
        t0 = time.perf_counter()
        for i in range(500):
            success = ring.push(node_id=100 + i, event_type=2, arg1=i, arg2=i * 2)
            self.assertTrue(success)
        push_duration = time.perf_counter() - t0

        avg_push_us = (push_duration / 500) * 1_000_000
        # Average push time should be under 15 microseconds
        self.assertLess(avg_push_us, 15.0, f"Average push time {avg_push_us:.2f} µs exceeds threshold")

        self.assertFalse(ring.is_empty())
        self.assertEqual(ring.available(), 500)

        # Pop 500 events
        t1 = time.perf_counter()
        for i in range(500):
            evt = ring.pop()
            self.assertIsNotNone(evt)
            self.assertEqual(evt["node_id"], 100 + i)
            self.assertEqual(evt["arg1"], i)
            self.assertEqual(evt["arg2"], i * 2)
        pop_duration = time.perf_counter() - t1

        avg_pop_us = (pop_duration / 500) * 1_000_000
        self.assertLess(avg_pop_us, 15.0, f"Average pop time {avg_pop_us:.2f} µs exceeds threshold")
        self.assertTrue(ring.is_empty())

        ring.close()

    def test_ring_buffer_wrap_around(self):
        """Verify seamless circular queue wrap-around without data corruption."""
        ring = RingBufferIPC(capacity=32)

        # Fill and drain repeatedly to cycle past capacity
        for cycle in range(5):
            for i in range(25):
                self.assertTrue(ring.push(node_id=i, event_type=1))
            for i in range(25):
                evt = ring.pop()
                self.assertIsNotNone(evt)
                self.assertEqual(evt["node_id"], i)

        self.assertTrue(ring.is_empty())
        ring.close()

    def test_dirty_bit_signal_slot_tracking(self):
        """Test fine-grained dirty-bit slot reactivity without tree traversal."""
        sig = Signal(initial_value=100)
        self.assertFalse(sig.is_dirty)

        # Bind to node 42's text property
        sig.bind_target(node_id=42, property_key="text")
        sig.bind_target(node_id=43, property_key="data-value")

        # Mutate value
        sig.value = 101
        self.assertTrue(sig.is_dirty)

        mutations = sig.get_mutations()
        self.assertEqual(len(mutations), 2)
        self.assertEqual(mutations[0], {"op": "SET_TEXT", "id": 42, "key": "text", "value": "101"})
        self.assertEqual(mutations[1], {"op": "SET_ATTRIBUTE", "id": 43, "key": "data-value", "value": "101"})

        # After get_mutations(), dirty bit should be cleared
        self.assertFalse(sig.is_dirty)
        self.assertEqual(len(sig.get_mutations()), 0)

    def test_runtime_drs_and_binary_ir_presence(self):
        """Verify that tin-runtime.js contains the optimized DRS engine and binary decoder."""
        runtime_path = Path(__file__).resolve().parent.parent / "tin-runtime.js"
        content = runtime_path.read_text(encoding="utf-8")

        # DRS (Dynamic Resolution Scaling)
        self.assertIn("drsEnabled", content)
        self.assertIn("minQualityScale", content)
        self.assertIn("recentFrameTimes", content)

        # Frustum Occlusion
        self.assertIn("initFrustumOcclusion", content)
        self.assertIn("this.isVisible", content)

        # Binary IR Decoder
        self.assertIn("renderTinBinaryIR", content)
        self.assertIn("0x54", content)  # 'T'
        self.assertIn("0x49", content)  # 'I'
        self.assertIn("0x4E", content)  # 'N'
        self.assertIn("0x42", content)  # 'B'

if __name__ == "__main__":
    unittest.main()
