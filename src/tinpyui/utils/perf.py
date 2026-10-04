"""Performance and FPS telemetry."""
import time
from ..core.signals import Signal

class PerformanceMonitor:
    """Real-Time Live Frame Rate & Render Latency Telemetry Sampler."""
    def __init__(self):
        self.frame_count = 0
        self.last_time = time.time()
        self.fps = Signal(60.0)
        self.render_latency_ms = Signal(0.5)

    def sample_frame(self):
        self.frame_count += 1
        now = time.time()
        delta = now - self.last_time
        if delta >= 1.0:
            current_fps = round(self.frame_count / delta, 1)
            self.fps.value = current_fps
            self.render_latency_ms.value = round((delta / max(1, self.frame_count)) * 1000, 2)
            self.frame_count = 0
            self.last_time = now


perf_monitor = PerformanceMonitor()
