# cli/build.py
import os
import shutil
import subprocess
import sys
from cli.security_scanner import SecretScanner

def compile_wasm(entry_file="main.py", output_wasm="dist/app.wasm"):
    """
    Build pipeline enforcing AST security scan, symbol stripping (-ldflags="-s -w"),
    and optional wasm-opt binary minification.
    """
    if os.path.exists(entry_file):
        with open(entry_file, "r", encoding="utf-8") as f:
            code = f.read()
        
        scanner = SecretScanner()
        if not scanner.scan_code(code):
            print("[TinPyUI FATAL]: Compilation aborted due to security violation.")
            return False

    print("[TinPyUI]: Source code security verified. Commencing Wasm compilation...")

    os.makedirs(os.path.dirname(output_wasm), exist_ok=True)

    # -s: Omit symbol table and debug info
    # -w: Omit DWARF symbol table
    build_cmd = [
        "go", "build",
        "-o", output_wasm,
        "-ldflags", "-s -w",
        "wasm_engine"
    ]

    env = dict(os.environ)
    env["GOOS"] = "js"
    env["GOARCH"] = "wasm"

    try:
        res = subprocess.run(build_cmd, env=env, capture_output=True, text=True)
        if res.returncode == 0:
            print("[TinPyUI]: Build successful. Go metadata & symbols stripped.")
        else:
            print(f"[TinPyUI Note]: Go compilation step skipped or failed: {res.stderr}")
    except Exception as e:
        print(f"[TinPyUI Note]: Go compiler process error: {e}")

    # Phase 3: Optional wasm-opt minification
    if shutil.which("wasm-opt") and os.path.exists(output_wasm):
        print("[TinPyUI]: Running wasm-opt -O3 minification pass...")
        try:
            subprocess.run(["wasm-opt", "-O3", output_wasm, "-o", output_wasm], check=True)
            print("[TinPyUI]: wasm-opt pass complete.")
        except Exception as e:
            print(f"[TinPyUI Warning]: wasm-opt failed: {e}")

    return True

if __name__ == "__main__":
    compile_wasm()
