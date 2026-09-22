import mmap
import ctypes
import os
import sys
import threading
import time

from .protocol import ControlBlock, MutationCommand, UIEvent
from .compiler import compile_to_ram

class EngineBridge:
    def __init__(self):
        # Dynamically load the correct native engine binary
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Determine appropriate library extension
        if sys.platform == "win32":
            lib_name = "tinui_engine.dll"
        elif sys.platform == "darwin":
            lib_name = "tinui_engine.dylib"
        else:
            lib_name = "tinui_engine.so"
            
        lib_path = os.path.join(current_dir, lib_name)
        
        # Note: If the native engine DLL does not exist yet, we mock the call for now
        # until the C++ side is compiled.
        if os.path.exists(lib_path):
            self.dll = ctypes.CDLL(lib_path)
            # Define C-function signature: void BootNativeWindow(void* shared_mem_ptr)
            if hasattr(self.dll, 'BootNativeWindow'):
                self.dll.BootNativeWindow.argtypes = [ctypes.c_void_p]
                self.dll.BootNativeWindow.restype = None
        else:
            self.dll = None
            print(f"[Warning] Native engine {lib_name} not found at {lib_path}. Running in headless mock mode.")

class SpringPhysics:
    """
    Continuous Hooke's Law Spring Solver:
    F = -stiffness * (position - target) - damping * velocity
    Calculates physically-accurate spring dynamics every 8ms (120 FPS).
    """
    def __init__(self, stiffness: float = 180.0, damping: float = 12.0, mass: float = 1.0, initial: float = 1.0):
        self.stiffness = stiffness
        self.damping = damping
        self.mass = mass
        self.current = initial
        self.target = initial
        self.velocity = 0.0
        self.settled_threshold = 0.0005
        self.is_active = False

    def trigger_impulse(self, impulse: float):
        """Attaches a velocity vector to trigger an instant kinetic compress/bounce."""
        self.velocity += impulse
        self.is_active = True

    def set_target(self, target: float):
        self.target = target
        self.is_active = True

    def step(self, dt: float = 0.00833) -> float:
        """Step the spring simulation by dt seconds (0.00833s = ~120 FPS)."""
        if not self.is_active:
            return self.current

        displacement = self.current - self.target
        force = -self.stiffness * displacement - self.damping * self.velocity
        acceleration = force / self.mass

        self.velocity += acceleration * dt
        self.current += self.velocity * dt

        if abs(self.velocity) < self.settled_threshold and abs(self.current - self.target) < self.settled_threshold:
            self.current = self.target
            self.velocity = 0.0
            self.is_active = False

        return self.current

class PythonEventLoop:
    def __init__(self, shared_mem, callback_registry):
        self.mem = shared_mem
        self.callbacks = callback_registry # { node_id: [func1, func2] }
        self.springs = {}                  # { node_id: SpringPhysics }
        
        # Read the Control Block from offset 0
        self.ctrl = ControlBlock.from_buffer(self.mem, 0)
        
        # Event Queue B starts at 1MB offset (0x100000)
        self.event_base = 0x100000
        # Mutation Queue A starts at 0x20
        self.queue_a_base = 0x20

    def start(self):
        print("[TinPyUI] Starting background event loop thread with 120 FPS spring solver...")
        worker = threading.Thread(target=self._poll_events, daemon=True)
        worker.start()

    def _poll_events(self):
        tail = self.ctrl.b_tail
        while self.ctrl.status == 1:
            head = self.ctrl.b_head

            if tail == head:
                # No events; yield CPU time slice briefly (sub-millisecond pause)
                time.sleep(0.0005)
                continue

            # Read event struct from RAM
            offset = self.event_base + (tail * ctypes.sizeof(UIEvent))
            event = UIEvent.from_buffer(self.mem, offset)

            # Fire user callback
            if event.node_id in self.callbacks:
                for cb in self.callbacks[event.node_id]:
                    cb()

            # Attach kinetic tactile impulse to clicked elements (tactile bounce)
            if event.event_type == 1:
                if event.node_id not in self.springs:
                    self.springs[event.node_id] = SpringPhysics(stiffness=240.0, damping=16.0, initial=1.0)
                self.springs[event.node_id].trigger_impulse(-0.12)

            # Advance tail pointer to release slot
            tail = (tail + 1) % 65536
            self.ctrl.b_tail = tail

            # Step active spring simulations and write scale uniforms to Queue A
            if self.springs:
                active_keys = list(self.springs.keys())
                for nid in active_keys:
                    sp = self.springs[nid]
                    if sp.is_active:
                        scale_val = sp.step(0.00833)
                        a_head = self.ctrl.a_head
                        cmd_offset = self.queue_a_base + (a_head * ctypes.sizeof(MutationCommand))
                        cmd = MutationCommand.from_buffer(self.mem, cmd_offset)
                        cmd.node_id = nid
                        cmd.property_id = 10 # PROP_SCALE
                        cmd.value_type = 0   # INT (Scale * 1000)
                        cmd.payload = int(scale_val * 1000)
                        self.ctrl.a_head = (a_head + 1) % 65536
                    else:
                        del self.springs[nid]

class MemoryMappedRuntime:
    def __init__(self, target_file: str):
        self.target_file = target_file
        
        # Allocate 4MB of anonymous shared memory (aligns with 4096-byte pages)
        self.mem_size = 4 * 1024 * 1024
        
        print("[TinPyUI] Requesting 4MB of anonymous shared memory from the OS...")
        # Windows requires different mmap flags than Unix
        if sys.platform == "win32":
            self.shared_mem = mmap.mmap(-1, self.mem_size)
        else:
            self.shared_mem = mmap.mmap(-1, self.mem_size, mmap.MAP_ANONYMOUS | mmap.MAP_SHARED)
            
        self.buffer_address = ctypes.addressof(ctypes.c_char.from_buffer(self.shared_mem))
        
        # Initialize Control Block metadata (Magic, Status)
        ctrl = ControlBlock.from_buffer(self.shared_mem, 0)
        ctrl.magic = 0x54494E55 # "TINU"
        ctrl.status = 1         # 1 = Running
        
        self.engine = EngineBridge()
        self.callback_registry = {} # To be populated during compilation

    def ignite(self):
        """Passes the memory pointer to C++ and blocks until the window closes"""
        print(f"[TinPyUI] Compiling {self.target_file} to raw binary structs...")
        
        # Write the initial UI layout to the memory block Queue A and String Arena
        self.callback_registry = compile_to_ram(self.target_file, self.shared_mem)
        
        # Start Python Worker Thread to listen for clicks/events
        event_loop = PythonEventLoop(self.shared_mem, self.callback_registry)
        event_loop.start()
        
        # Pass the raw memory pointer to the C++ DLL.
        # This function blocks the Python main thread while the C++ Window is open.
        print("[TinPyUI] Handing Thread 0 to C++ Native Engine...")
        if self.engine.dll and hasattr(self.engine.dll, 'BootNativeWindow'):
            self.engine.dll.BootNativeWindow(self.buffer_address)
        else:
            print("[TinPyUI] Native engine missing. Mock execution finished.")
            time.sleep(1) # Simulate running
            
        # When user closes the native window, BootNativeWindow returns.
        print("[TinPyUI] Engine shut down cleanly. OS reclaiming RAM.")
        # Signal event loop to exit
        ctrl = ControlBlock.from_buffer(self.shared_mem, 0)
        ctrl.status = 0
