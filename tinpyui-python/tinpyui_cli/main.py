import os
import sys
import subprocess

def run():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    binary = os.path.join(base_dir, "bin", "tinpy.exe")
    
    if not os.path.exists(binary):
        print(f"[Error] The TinPyUI core executable was not found at {binary}")
        sys.exit(1)

    # Pass all arguments to the Go binary
    try:
        sys.exit(subprocess.call([binary] + sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(0)
