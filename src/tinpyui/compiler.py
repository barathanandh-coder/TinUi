import ctypes
from .protocol import MutationCommand, ControlBlock

def compile_to_ram(target_file: str, shared_mem) -> dict:
    """
    Translates the .tin file into binary structs and writes them directly into the shared RAM map.
    Returns a callback_registry mapping node_ids to python functions.
    
    1. Lexical Analysis (Mocked)
    2. AST Builder (Mocked)
    3. Linearization (Mocked)
    4. String Arena Extraction
    5. Binary Forge (Struct packing)
    """
    
    # 0x000020 - 0x0FFFFF : Mutation Queue A
    queue_a_base = 0x20
    # 0x200000 - 0x3FFFFF : String & Binary Arena (Starts at 2MB mark)
    arena_base = 0x200000
    arena_offset = 0
    
    callbacks = {}
    
    # Let's mock parsing a simple UI:
    # Window
    #   Row
    #     Button text="Click Me"
    
    # We will write these directly to Queue A.
    ctrl = ControlBlock.from_buffer(shared_mem, 0)
    
    # Function to write string to Arena
    def push_string(text: str) -> int:
        nonlocal arena_offset
        encoded = text.encode('utf-8')
        length = len(encoded)
        
        # Write bytes
        for i, b in enumerate(encoded):
            shared_mem[arena_base + arena_offset + i] = b
            
        # Null terminator
        shared_mem[arena_base + arena_offset + length] = 0
        
        start_offset = arena_base + arena_offset
        arena_offset += length + 1
        return start_offset, length
    
    # Node 1: Window creation
    cmd1 = MutationCommand()
    cmd1.node_id = 1
    cmd1.property_id = 0 # CREATE
    cmd1.value_type = 0  # INT (Type Window = 1)
    cmd1.payload = 1     
    
    # Node 2: Row creation
    cmd2 = MutationCommand()
    cmd2.node_id = 2
    cmd2.property_id = 0 # CREATE
    cmd2.value_type = 0  # INT (Type Row = 2)
    cmd2.payload = 2
    
    # Node 3: Button creation
    cmd3 = MutationCommand()
    cmd3.node_id = 3
    cmd3.property_id = 0 # CREATE
    cmd3.value_type = 0  # INT (Type Button = 3)
    cmd3.payload = 3
    
    # Node 3: Button Text
    cmd4 = MutationCommand()
    cmd4.node_id = 3
    cmd4.property_id = 1 # TEXT
    cmd4.value_type = 2  # STRING OFFSET
    
    str_offset, str_len = push_string("Click Me!")
    cmd4.payload = str_offset
    cmd4.payload_len = str_len
    
    # Write structs to RAM
    ctypes.memmove(ctypes.addressof(ctypes.c_char.from_buffer(shared_mem, queue_a_base + (0 * 16))), ctypes.addressof(cmd1), 16)
    ctypes.memmove(ctypes.addressof(ctypes.c_char.from_buffer(shared_mem, queue_a_base + (1 * 16))), ctypes.addressof(cmd2), 16)
    ctypes.memmove(ctypes.addressof(ctypes.c_char.from_buffer(shared_mem, queue_a_base + (2 * 16))), ctypes.addressof(cmd3), 16)
    ctypes.memmove(ctypes.addressof(ctypes.c_char.from_buffer(shared_mem, queue_a_base + (3 * 16))), ctypes.addressof(cmd4), 16)
    
    # Update Queue A head
    ctrl.a_head = 4
    
    print(f"[Compiler] Wrote 4 MutationCommands to RAM. String Arena size: {arena_offset} bytes.")
    
    # Mocking Python Callback Registration
    def on_button_click():
        print("[Python] Received CLICK event from C++ directly in Memory Map! Node 3 was clicked.")
        
    callbacks[3] = [on_button_click]
    
    return callbacks
