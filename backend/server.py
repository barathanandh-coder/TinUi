"""
TinPyUI v1.6.0 Sample Project — Backend Services
Provides real-time telemetry streaming, device synchronization, and security telemetry.
"""

import time
import random
import threading
import os
import sys
from typing import Dict, Any, List

# Ensure project root is in sys.path when executed standalone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TelemetryStreamService:
    """Simulates high-speed 120 FPS device telemetry streaming for universal fleet nodes."""
    def __init__(self):
        self._running = False
        self._thread = None
        self.latest_telemetry: Dict[str, Any] = {
            "fps": 120.0,
            "latency_us": 412,
            "active_devices": 5,
            "spring_tension": 180.0,
            "spring_friction": 20.0,
            "security_status": "ARMED_ENCRYPTED",
            "virtual_stack_items": 50000
        }

    def get_latest_metrics(self) -> Dict[str, Any]:
        """Returns snapshot of current device fleet performance metrics."""
        self.latest_telemetry["fps"] = round(118.5 + random.uniform(0.0, 3.0), 1)
        self.latest_telemetry["latency_us"] = int(380 + random.randint(0, 45))
        return dict(self.latest_telemetry)

    def generate_virtual_events(self, count: int = 100) -> List[str]:
        """Generates mock telemetry events for high-volume VirtualStack demonstration."""
        platforms = ["Desktop (Win32)", "Android Mobile", "Apple iOS", "Tablet iPad", "WebAssembly"]
        events = []
        for i in range(count):
            plat = random.choice(platforms)
            latency = random.randint(350, 520)
            events.append(f"[{plat}] Event #{i+1:05d}: Hardware Frame Synced in {latency} us @ 120 FPS")
        return events

    def start_stream(self, interval_seconds: float = 1.0):
        """Starts asynchronous telemetry broadcast."""
        if self._running:
            return
        self._running = True
        
        def _loop():
            while self._running:
                self.get_latest_metrics()
                time.sleep(interval_seconds)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop_stream(self):
        self._running = False

# Global Singleton Service
telemetry_service = TelemetryStreamService()

if __name__ == "__main__":
    print("[TinPyUI Backend] Telemetry Service running...")
    metrics = telemetry_service.get_latest_metrics()
    print(f"[TinPyUI Backend] Initial metrics: {metrics}")
    events = telemetry_service.generate_virtual_events(5)
    for e in events:
        print("  ->", e)
