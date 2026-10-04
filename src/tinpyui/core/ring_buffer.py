"""
Lockless Shared Memory Circular Ring Buffer for Sub-Microsecond IPC.
Provides zero-copy event communication between Python and the Native/Wasm UI Engine.
"""

import ctypes
import mmap
import os
import struct
from typing import Optional, Dict, Any

RING_MAGIC = 0x54494E55  # "TINU"
DEFAULT_CAPACITY = 2048

class RingHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("magic", ctypes.c_uint32),
        ("capacity", ctypes.c_uint32),
        ("slot_size", ctypes.c_uint32),
        ("head", ctypes.c_uint32),
        ("tail", ctypes.c_uint32),
        ("dropped", ctypes.c_uint32),
    ]

class UIEventSlot(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("node_id", ctypes.c_uint32),
        ("event_type", ctypes.c_uint16),
        ("flags", ctypes.c_uint16),
        ("arg1", ctypes.c_int32),
        ("arg2", ctypes.c_int32),
        ("timestamp_us", ctypes.c_uint64),
    ]

HEADER_SIZE = ctypes.sizeof(RingHeader)
SLOT_SIZE = ctypes.sizeof(UIEventSlot)

class RingBufferIPC:
    """
    High-throughput lockless circular ring buffer mapped into OS shared memory.
    """
    def __init__(self, capacity: int = DEFAULT_CAPACITY, shm_buffer: Optional[Any] = None):
        self.capacity = capacity
        self.total_size = HEADER_SIZE + (self.capacity * SLOT_SIZE)

        if shm_buffer is not None:
            self._buf = shm_buffer
            self._owns_shm = False
        else:
            # Anonymous memory map (supports cross-thread / process fork zero-copy)
            self._buf = mmap.mmap(-1, self.total_size)
            self._owns_shm = True

        # Initialize header
        self._header = RingHeader.from_buffer(self._buf, 0)
        if self._header.magic != RING_MAGIC:
            self._header.magic = RING_MAGIC
            self._header.capacity = self.capacity
            self._header.slot_size = SLOT_SIZE
            self._header.head = 0
            self._header.tail = 0
            self._header.dropped = 0

    @property
    def buffer(self):
        return self._buf

    def is_empty(self) -> bool:
        return self._header.head == self._header.tail

    def is_full(self) -> bool:
        next_head = (self._header.head + 1) % self.capacity
        return next_head == self._header.tail

    def available(self) -> int:
        head = self._header.head
        tail = self._header.tail
        if head >= tail:
            return head - tail
        return (self.capacity - tail) + head

    def push(self, node_id: int, event_type: int = 1, arg1: int = 0, arg2: int = 0, flags: int = 0, timestamp_us: int = 0) -> bool:
        """
        Pushes a UIEvent into the ring buffer.
        Returns True if successful, False if queue is full.
        """
        head = self._header.head
        next_head = (head + 1) % self.capacity
        if next_head == self._header.tail:
            # Buffer is full, drop event and record metric
            self._header.dropped += 1
            return False

        slot_offset = HEADER_SIZE + (head * SLOT_SIZE)
        slot = UIEventSlot.from_buffer(self._buf, slot_offset)
        slot.node_id = node_id
        slot.event_type = event_type
        slot.flags = flags
        slot.arg1 = arg1
        slot.arg2 = arg2
        slot.timestamp_us = timestamp_us

        # Atomic commit
        self._header.head = next_head
        return True

    def pop(self) -> Optional[Dict[str, Any]]:
        """
        Pops the next available event from the queue.
        Returns event dictionary or None if empty.
        """
        tail = self._header.tail
        if tail == self._header.head:
            return None

        slot_offset = HEADER_SIZE + (tail * SLOT_SIZE)
        slot = UIEventSlot.from_buffer(self._buf, slot_offset)
        result = {
            "node_id": slot.node_id,
            "event_type": slot.event_type,
            "flags": slot.flags,
            "arg1": slot.arg1,
            "arg2": slot.arg2,
            "timestamp_us": slot.timestamp_us,
        }

        # Advance tail
        self._header.tail = (tail + 1) % self.capacity
        return result

    def close(self):
        if self._owns_shm and self._buf:
            try:
                self._buf.close()
            except Exception:
                pass
