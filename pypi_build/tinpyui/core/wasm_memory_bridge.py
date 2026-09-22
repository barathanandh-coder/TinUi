"""
Wasm Linear Memory Direct State Bridge.
Maps layout matrices and shader uniforms into a fixed linear memory segment (SharedArrayBuffer)
for zero-serialization transfer directly into WebGL and WebAssembly render loops.
"""

import ctypes
import struct
from typing import Dict, Any, Optional, List

WASM_BRIDGE_MAGIC = 0x54494E57  # 'TINW' (TinUI Wasm)

# Linear Memory Segment Offsets (within Wasm 64KB Page 0 & 1)
OFFSET_CONTROL = 0x0000       # 0x0000 - 0x0FFF: Control headers & atomic counters
OFFSET_TRANSFORMS = 0x1000    # 0x1000 - 0x3FFF: 12KB Transform & Uniform Matrix (256 nodes * 12 floats)
OFFSET_EVENTS = 0x4000        # 0x4000 - 0x7FFF: Bidirectional event queue

# Node Transform & Uniform Stride: 12 float32 values (48 bytes per node slot)
# [0] pos_x, [1] pos_y, [2] scale_x, [3] scale_y, [4] rotation_rad, [5] opacity
# [6] uniform_time, [7] uniform_speed, [8] uniform_intensity, [9] u0, [10] u1, [11] u2
FLOATS_PER_NODE = 12
BYTES_PER_NODE = FLOATS_PER_NODE * 4

class ControlBlock(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("magic", ctypes.c_uint32),
        ("frame_counter", ctypes.c_uint32),
        ("active_nodes", ctypes.c_uint32),
        ("dirty_mask", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32 * 4),
    ]

class WasmMemoryBridge:
    """Python-side controller for the Wasm Linear Memory Shared Bridge."""

    def __init__(self, memory_buffer: Optional[bytearray] = None, capacity_nodes: int = 256):
        self.capacity = capacity_nodes
        self.total_size = OFFSET_TRANSFORMS + (self.capacity * BYTES_PER_NODE)
        
        if memory_buffer is not None:
            self._buf = memory_buffer
        else:
            self._buf = bytearray(self.total_size)

        # Initialize control header
        self._init_header()

    def _init_header(self):
        struct.pack_into("<IIII", self._buf, OFFSET_CONTROL, WASM_BRIDGE_MAGIC, 0, 0, 0)

    def read_control(self) -> Dict[str, int]:
        """Reads control headers and atomic counters."""
        magic, frame_counter, active_nodes, dirty_mask = struct.unpack_from("<IIII", self._buf, OFFSET_CONTROL)
        return {
            "magic": magic,
            "frame_counter": frame_counter,
            "active_nodes": active_nodes,
            "dirty_mask": dirty_mask
        }

    def advance_frame(self, active_nodes: Optional[int] = None) -> int:
        """Increments the frame counter and optionally updates active node count."""
        ctrl = self.read_control()
        new_fc = ctrl["frame_counter"] + 1
        an = active_nodes if active_nodes is not None else ctrl["active_nodes"]
        struct.pack_into("<IIII", self._buf, OFFSET_CONTROL, WASM_BRIDGE_MAGIC, new_fc, an, ctrl["dirty_mask"])
        return new_fc

    @property
    def buffer(self) -> bytearray:
        return self._buf

    def write_node_state(
        self,
        node_id: int,
        pos_x: float = 0.0,
        pos_y: float = 0.0,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
        rotation: float = 0.0,
        opacity: float = 1.0,
        speed: float = 1.0,
        intensity: float = 1.0,
        custom_u0: float = 0.0,
        custom_u1: float = 0.0,
        custom_u2: float = 0.0
    ):
        """Writes spatial transforms and shader parameters directly into linear memory."""
        slot = node_id % self.capacity
        offset = OFFSET_TRANSFORMS + (slot * BYTES_PER_NODE)
        struct.pack_into(
            "<12f",
            self._buf,
            offset,
            float(pos_x),
            float(pos_y),
            float(scale_x),
            float(scale_y),
            float(rotation),
            float(opacity),
            0.0, # u_time placeholder
            float(speed),
            float(intensity),
            float(custom_u0),
            float(custom_u1),
            float(custom_u2)
        )

    def read_node_state(self, node_id: int) -> Dict[str, float]:
        """Reads node spatial transforms and uniform values directly from memory."""
        slot = node_id % self.capacity
        offset = OFFSET_TRANSFORMS + (slot * BYTES_PER_NODE)
        values = struct.unpack_from("<12f", self._buf, offset)
        return {
            "pos_x": values[0],
            "pos_y": values[1],
            "scale_x": values[2],
            "scale_y": values[3],
            "rotation": values[4],
            "opacity": values[5],
            "speed": values[7],
            "intensity": values[8],
            "u0": values[9],
            "u1": values[10],
            "u2": values[11]
        }
