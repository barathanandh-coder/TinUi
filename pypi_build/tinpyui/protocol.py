import ctypes

class ControlBlock(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("magic", ctypes.c_uint32),
        ("a_head", ctypes.c_uint32),
        ("a_tail", ctypes.c_uint32),
        ("b_head", ctypes.c_uint32),
        ("b_tail", ctypes.c_uint32),
        ("status", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
    ]

class MutationCommand(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("node_id", ctypes.c_uint32),
        ("property_id", ctypes.c_uint16),
        ("value_type", ctypes.c_uint16),
        ("payload", ctypes.c_uint32),
        ("payload_len", ctypes.c_uint32),
    ]

class UIEvent(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("node_id", ctypes.c_uint32),
        ("event_type", ctypes.c_uint16),
        ("modifier", ctypes.c_uint16),
        ("arg1", ctypes.c_int32),
        ("arg2", ctypes.c_int32),
    ]

# 4. Batched Vertex Structure for Combined Uber-Shader Pass
class VertexBatch(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("pos_x", ctypes.c_float),
        ("pos_y", ctypes.c_float),
        ("uv_x", ctypes.c_float),
        ("uv_y", ctypes.c_float),
        ("clip_min_x", ctypes.c_float),
        ("clip_min_y", ctypes.c_float),
        ("clip_max_x", ctypes.c_float),
        ("clip_max_y", ctypes.c_float),
        ("vertex_type", ctypes.c_int32),  # 0 = SDF Shape / Button, 1 = MSDF Text
    ]

# SDF & MSDF Property IDs
PROP_CREATE = 0
PROP_TEXT = 1
PROP_WIDTH = 2
PROP_HEIGHT = 3
PROP_RADIUS = 4
PROP_BORDER_WIDTH = 5
PROP_BG_COLOR = 6
PROP_BORDER_COLOR = 7
PROP_SHADOW_COLOR = 8
PROP_SHADOW_SOFTNESS = 9
PROP_SCALE = 10
PROP_CLIP_RECT = 11
PROP_SCROLL_Y = 12
PROP_SELECTION = 13

