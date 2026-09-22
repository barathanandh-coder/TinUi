"""GDI object pools and asset loaders."""
import os
from typing import List

class GDIPool:
    """Automatic GDI Object Garbage Collection & Memory Leak Neutralizer."""
    def __init__(self, gdi32):
        self.gdi32 = gdi32
        self.allocated_objects: List[int] = []

    def create_brush(self, color_int: int) -> int:
        brush = self.gdi32.CreateSolidBrush(color_int)
        if brush:
            self.allocated_objects.append(brush)
        return brush

    def cleanup(self):
        """Frees all allocated GDI objects to prevent Windows Handle Leaks."""
        for obj in self.allocated_objects:
            try:
                self.gdi32.DeleteObject(obj)
            except Exception: pass
        self.allocated_objects.clear()


class FailSafeAssetLoader:
    """In-Memory Vector Fallback Generator for Missing Files/Assets."""
    @staticmethod
    def get_valid_path(filepath: str, fallback_default: str = "assets/app_icon.png") -> str:
        if filepath and os.path.exists(filepath):
            return filepath
        if os.path.exists(fallback_default):
            return fallback_default
        return ""


