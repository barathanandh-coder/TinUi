"""
TinPyUI v1.8.0 — Production-Grade Hardware-Accelerated Universal Python GUI Framework Library
Blazing-fast 120 FPS vector UI engine & IPC Pipeline for Desktop (Win/macOS/Linux), Mobile (Android/iOS), & Web.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from tinpyui import *
from tinpyui import __version__

if __name__ == "__main__":
    from tinpyui.app import App
    from tinpyui.cli import main as cli_main

    if len(sys.argv) > 1:
        cli_main()
    else:
        app = App()
        app.run(prompt_target=True)

