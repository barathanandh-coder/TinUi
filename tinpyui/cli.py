"""
TinPyUI Unified Developer CLI v1.7.0
Single unified entrypoint for creating, running, interactive REPL, live-reload dev, and multi-platform packaging.
"""

import sys
import argparse
import os
import shutil
import http.server
import socketserver
import webbrowser
import threading
import time
import code
import subprocess
from typing import Optional, Dict

from .runtime import MemoryMappedRuntime
from .__main__ import scaffold_project_interactive
from .mobile_export import export_android_project, export_ios_project
from .core.aot_compiler import build_aot_static_bundle, AOTCompiler
from .core.hmr import HMRTracker

CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
WHITE = "\033[1;97m"
DIM = "\033[90m"
RESET = "\033[0m"

def find_target_file(provided_file: Optional[str] = None) -> Optional[str]:
    """Finds the most logical UI file if not explicitly specified."""
    if provided_file and os.path.exists(provided_file):
        return provided_file
    for candidate in ["main.tin", "index.tin", "app.tin", "main.py"]:
        if os.path.exists(candidate):
            return candidate
    return provided_file

def ensure_web_assets(out_dir: str = "dist", target_file: str = "main.tin"):
    """Bundles static WebAssembly runtime, HTML shell, and IR for web deployment."""
    os.makedirs(out_dir, exist_ok=True)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.getcwd()

    # 1. Copy WASM Engine
    for cand in [
        os.path.join(current_dir, "tinui_engine.wasm"),
        os.path.join(project_root, "public", "tinui_engine.wasm"),
        os.path.join(project_root, "tinui_engine.wasm"),
    ]:
        if os.path.exists(cand):
            shutil.copyfile(cand, os.path.join(out_dir, "tinui_engine.wasm"))
            shutil.copyfile(cand, os.path.join(out_dir, "app.wasm"))
            break

    # 2. Copy wasm_exec.js and tin-runtime.js
    for asset in ["wasm_exec.js", "tin-runtime.js"]:
        for cand in [
            os.path.join(current_dir, asset),
            os.path.join(project_root, "public", asset),
            os.path.join(project_root, asset),
        ]:
            if os.path.exists(cand):
                shutil.copyfile(cand, os.path.join(out_dir, asset))
                break

    # 3. Copy or generate index.html
    html_src = os.path.join(project_root, "public", "index.html")
    if not os.path.exists(html_src):
        html_src = os.path.join(project_root, "index.html")

    if os.path.exists(html_src):
        shutil.copyfile(html_src, os.path.join(out_dir, "index.html"))
    else:
        minimal_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TinPyUI Application</title>
</head>
<body style="margin:0; background:#0a0b10; color:#fff; overflow:hidden;">
    <div id="error-overlay" style="display:none; padding:24px; color:#ff4d4d; background:#0a0a0a; font-family:monospace; position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:999999;">
        <h2 style="margin:0 0 16px 0; border-bottom:1px solid #ff4d4d; padding-bottom:8px;">⚠️ TinPyUI Engine Panic</h2>
        <pre id="error-log" style="margin:0; white-space:pre-wrap;"></pre>
    </div>
    <canvas id="tin-canvas" style="display:block; width:100vw; height:100vh;"></canvas>
    <div id="tinui-root"></div>
    <script src="wasm_exec.js"></script>
    <script src="tin-runtime.js"></script>
</body>
</html>"""
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(minimal_html)

    # 4. Generate app.ir.json placeholder if not generated yet
    ir_dst = os.path.join(out_dir, "app.ir.json")
    if not os.path.exists(ir_dst):
        root_ir = os.path.join(project_root, "app.ir.json")
        if os.path.exists(root_ir):
            shutil.copyfile(root_ir, ir_dst)
        else:
            with open(ir_dst, "w", encoding="utf-8") as f:
                f.write('{"instructions":[]}')


def start_live_dev_server(target_file: str, port: int = 8080):
    """Launches local dev server with SSE live reload and automatic file watching."""
    serve_dir = "dist"
    ensure_web_assets(serve_dir, target_file)

    sse_clients = []
    clients_lock = threading.Lock()

    class DevHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=serve_dir, **kwargs)

        def do_GET(self):
            if self.path.startswith('/__tin_live_reload'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Connection', 'keep-alive')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with clients_lock:
                    sse_clients.append(self.wfile)
                try:
                    while True:
                        time.sleep(1)
                except Exception:
                    with clients_lock:
                        if self.wfile in sse_clients:
                            sse_clients.remove(self.wfile)
                return
            return super().do_GET()

        def log_message(self, format, *args):
            pass

    try:
        server = socketserver.TCPServer(("", port), DevHandler)
    except OSError:
        port += 1
        server = socketserver.TCPServer(("", port), DevHandler)

    print(f"\n{CYAN}[*] [TinPyUI Dev Server] Live at: {WHITE}http://localhost:{port}{RESET}")
    print(f"{DIM}Watching {target_file}, shaders/, and static assets for live hot-reload... (Ctrl+C to stop){RESET}\n")

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    # File watcher background thread with HMR incremental diffing
    hmr_tracker = HMRTracker()
    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as tf:
                hmr_tracker.last_source = tf.read()
        except Exception:
            pass

    def watch_files():
        last_mtimes = {}
        while True:
            time.sleep(0.5)
            changed = False
            for root, _, files in os.walk("."):
                if "dist" in root or ".git" in root or "__pycache__" in root or "build" in root:
                    continue
                for f in files:
                    if f.endswith((".tin", ".py", ".frag", ".vert", ".html", ".js")):
                        path = os.path.join(root, f)
                        try:
                            mtime = os.path.getmtime(path)
                            if path in last_mtimes and mtime > last_mtimes[path]:
                                changed = True
                            last_mtimes[path] = mtime
                        except Exception:
                            pass
            if changed:
                ensure_web_assets(serve_dir, target_file)
                patches = []
                if os.path.exists(target_file):
                    try:
                        with open(target_file, "r", encoding="utf-8") as tf:
                            new_content = tf.read()
                        if hmr_tracker.last_source:
                            patches = hmr_tracker.compute_diff(hmr_tracker.last_source, new_content)
                        hmr_tracker.last_source = new_content
                    except Exception:
                        patches = [{"type": "reload_ir"}]
                if not patches:
                    patches = [{"type": "reload_ir"}]

                import json
                for p in patches:
                    msg = f"data: {json.dumps(p)}\n\n".encode("utf-8")
                    with clients_lock:
                        dead = []
                        for c in sse_clients:
                            try:
                                c.write(msg)
                                c.flush()
                            except Exception:
                                dead.append(c)
                        for d in dead:
                            if d in sse_clients:
                                sse_clients.remove(d)

    watcher_thread = threading.Thread(target=watch_files, daemon=True)
    watcher_thread.start()

    time.sleep(0.3)
    webbrowser.open(f"http://localhost:{port}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[TinPyUI] Dev server stopped.{RESET}")
        server.shutdown()


def cmd_repl(args):
    """Boots an interactive Python REPL with TinPyUI preloaded."""
    print(f"\n{CYAN}+==============================================================================+{RESET}")
    print(f"{CYAN}|   [*] TinPyUI Interactive REPL & State Inspector                             |{RESET}")
    print(f"{CYAN}+==============================================================================+{RESET}")
    print(f"{WHITE}Preloaded modules: {GREEN}tin{WHITE}, {GREEN}tinpyui{WHITE}, {GREEN}db{WHITE}, {GREEN}Signal{WHITE}, {GREEN}State{RESET}")
    print(f"{DIM}Type help(tin) or inspect reactive signals live. Press Ctrl+Z or exit() to quit.{RESET}\n")

    import pypi_build.tinpyui as tin
    local_vars = {
        "tin": tin,
        "tinpyui": tin,
        "db": getattr(tin, "db", None),
        "Signal": getattr(tin, "Signal", None),
        "State": getattr(tin, "State", None),
        "connect": getattr(tin, "connect", None),
    }
    code.interact(banner="", local=local_vars)


def cmd_new(args):
    """Scaffold a new project."""
    target_name = args.name if hasattr(args, 'name') and args.name else ""
    scaffold_project_interactive(target_name)


def cmd_run(args):
    """Run the application."""
    target_file = find_target_file(args.file)
    if not target_file or not os.path.exists(target_file):
        print(f"{YELLOW}[Error] No .tin or Python file found to run. Specify one, e.g.: tinpyui run main.tin{RESET}")
        sys.exit(1)

    # If --web flag or file is specifically run in web mode:
    if getattr(args, 'web', False) or getattr(args, 'dev', False):
        start_live_dev_server(target_file, port=args.port if hasattr(args, 'port') else 8080)
        return

    print(f"{CYAN}[TinPyUI] Booting zero-copy native engine for {WHITE}{target_file}{CYAN}...{RESET}")
    runtime = MemoryMappedRuntime(target_file)
    runtime.ignite()


def package_desktop_binary(target_file: str, out_dir: str = "build/desktop", app_name: str = "TinPyUI App"):
    """Packages the application into a standalone desktop bundle."""
    os.makedirs(out_dir, exist_ok=True)
    pyinstaller_cmd = shutil.which("pyinstaller")
    print(f"{CYAN}[TinPyUI Package] Staging standalone desktop bundle into {WHITE}{out_dir}/{CYAN}...{RESET}")

    # Generate desktop launcher entrypoint
    launcher_path = os.path.join(out_dir, "desktop_entry.py")
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(f"""import tinpyui as tin
if __name__ == "__main__":
    app = tin.App("{app_name}", width=1280, height=800)
    app.run()
""")

    if pyinstaller_cmd and target_file.endswith(".py"):
        print(f"{CYAN}[TinPyUI Package] PyInstaller detected. Compiling single-file native executable...{RESET}")
        try:
            cmd = [pyinstaller_cmd, "--onefile", "--windowed", f"--name={app_name.replace(' ', '_')}", "--distpath", out_dir, target_file]
            subprocess.run(cmd, check=True)
            print(f"{GREEN}[+] Standalone desktop binary generated successfully in {out_dir}!{RESET}")
            return
        except Exception as e:
            print(f"{YELLOW}[!] PyInstaller notice: {e}. Defaulting to standard desktop staged bundle.{RESET}")

    print(f"{GREEN}[+] Desktop distribution bundle created at: {WHITE}{os.path.abspath(out_dir)}{RESET}")
    print(f"  * Launcher:  {launcher_path}")
    print(f"  * Run via:   python {launcher_path}")


def cmd_build(args):
    """Unified build & export command for Web, Desktop, Android, and iOS."""
    target_arg = args.file
    is_mobile_android = getattr(args, 'mobile', False) or getattr(args, 'android', False)
    is_mobile_ios = getattr(args, 'ios', False)

    # Allow syntax: `tinpyui export mobile` or `tinpyui export ios`
    if target_arg and target_arg.lower() in ("mobile", "android"):
        is_mobile_android = True
        target_arg = getattr(args, 'target_file', None)
    elif target_arg and target_arg.lower() in ("ios", "apple"):
        is_mobile_ios = True
        target_arg = getattr(args, 'target_file', None)

    target_file = find_target_file(target_arg)
    if not target_file:
        target_file = "main.tin"

    is_desktop = getattr(args, 'desktop', False)

    target_choice = (getattr(args, 'target', None) or "").lower()
    if target_choice in ("mobile", "android"):
        is_mobile_android = True
    elif target_choice in ("ios", "apple"):
        is_mobile_ios = True
    elif target_choice in ("desktop",):
        is_desktop = True

    if is_mobile_ios:
        out_dir = args.out if hasattr(args, 'out') and args.out and args.out != "dist" else "build/mobile/ios"
        app_name = getattr(args, 'app_name', None) or "TinPyUI App"
        bundle_id = getattr(args, 'bundle_id', None) or getattr(args, 'package', None) or "com.tinpyui.app"
        build_ipa = getattr(args, 'ipa', False) or getattr(args, 'build_ipa', False)
        export_ios_project(
            target_file=target_file,
            output_dir=out_dir,
            app_name=app_name,
            bundle_id=bundle_id,
            build_ipa=build_ipa
        )
    elif is_mobile_android:
        out_dir = args.out if hasattr(args, 'out') and args.out and args.out != "dist" else "build/mobile/android"
        app_name = getattr(args, 'app_name', None) or "TinPyUI App"
        pkg_name = getattr(args, 'package', None) or "com.tinpyui.app"
        build_apk = getattr(args, 'apk', False) or getattr(args, 'build_apk', False)
        export_android_project(
            target_file=target_file,
            output_dir=out_dir,
            app_name=app_name,
            package_name=pkg_name,
            build_apk=build_apk
        )
    elif is_desktop:
        out_dir = args.out if hasattr(args, 'out') and args.out and args.out != "dist" else "build/desktop"
        app_name = getattr(args, 'app_name', None) or "TinPyUI App"
        package_desktop_binary(target_file=target_file, out_dir=out_dir, app_name=app_name)
    else:
        out_dir = args.out if hasattr(args, 'out') and args.out else "dist"
        app_name = getattr(args, 'app_name', None) or "TinPyUI Application"
        print(f"{CYAN}[TinPyUI AOT Build] Compiling static AOT bundle into {WHITE}{out_dir}/{CYAN}...{RESET}")
        build_res = build_aot_static_bundle(entry_file=target_file, out_dir=out_dir, app_name=app_name)
        print(f"{GREEN}[+] [TinPyUI AOT Build] Complete! Production bundle ready in {out_dir}/")
        print(f"    • Binary Matrix: {build_res['binary_matrix_size']} bytes (Zero client-side parsing)")
        print(f"    • Node Count:    {build_res['node_count']} nodes compiled")
        print(f"    • Entrypoint:    {out_dir}/index.html (Ready for Cloudflare, Netlify, GitHub Pages, Vercel){RESET}")


def main():
    # Direct execution shorthand: `tinpyui app.tin`
    if len(sys.argv) == 2 and (sys.argv[1].endswith(".tin") or sys.argv[1].endswith(".py")):
        dummy_args = argparse.Namespace(file=sys.argv[1], web=False, dev=False, port=8080)
        cmd_run(dummy_args)
        return

    parser = argparse.ArgumentParser(
        prog="tinpyui",
        description="TinPyUI — Ultra-fast Bare-Metal GUI & Cross-Platform UI Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Examples:
  tinpyui new my_app           # 1. Create a new project
  tinpyui repl                 # 2. Interactive debug shell
  tinpyui run main.tin         # 3. Run native desktop app
  tinpyui run main.tin --web   #    Or run in browser with hot live-reload
  tinpyui build --mobile       # 4. Export standalone Android Gradle project & APK
  tinpyui build --ios          # 5. Export standalone Apple iOS Xcode project
  tinpyui build --desktop      # 6. Build native standalone desktop bundle
  tinpyui build --web          # 7. Build static web bundle for CDN deployment
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # 1. NEW
    p_new = subparsers.add_parser("new", aliases=["create", "init"], help="Scaffold a new project")
    p_new.add_argument("name", nargs="?", default="", help="Project name/directory")
    p_new.set_defaults(func=cmd_new)

    # 2. REPL
    p_repl = subparsers.add_parser("repl", aliases=["shell"], help="Launch interactive Python REPL & State Inspector")
    p_repl.set_defaults(func=cmd_repl)

    # 3. RUN / DEV
    p_run = subparsers.add_parser("run", aliases=["dev"], help="Run application (native desktop or live dev server)")
    p_run.add_argument("file", nargs="?", default=None, help="File to run (default: main.tin / index.tin)")
    p_run.add_argument("--web", action="store_true", help="Launch live dev server in web browser")
    p_run.add_argument("--port", type=int, default=8080, help="Dev server port (default: 8080)")
    p_run.set_defaults(func=cmd_run)

    # 4. BUILD / EXPORT
    p_build = subparsers.add_parser("build", aliases=["export", "package"], help="Package application for web, desktop, android, or ios")
    p_build.add_argument("file", nargs="?", default=None, help="Entry file (default: main.tin) or target ('mobile' / 'ios')")
    p_build.add_argument("target_file", nargs="?", default=None, help="Optional secondary file if target was specified")
    p_build.add_argument("--target", default=None, choices=["web", "webgl", "desktop", "mobile", "android", "ios", "apple"], help="Target platform")
    p_build.add_argument("--web", action="store_true", help="Build static WebAssembly bundle (dist/)")
    p_build.add_argument("--desktop", action="store_true", help="Build standalone native desktop binary/bundle")
    p_build.add_argument("--mobile", "--android", dest="mobile", action="store_true", help="Export standalone Android Gradle project & APK")
    p_build.add_argument("--ios", action="store_true", help="Export standalone Apple iOS Xcode project")
    p_build.add_argument("--apk", action="store_true", help="Automatically compile debug APK if gradle is available")
    p_build.add_argument("--ipa", action="store_true", help="Automatically compile IPA if xcodebuild is available")
    p_build.add_argument("--out", "--dist", dest="out", default=None, help="Output directory (default: dist)")
    p_build.add_argument("--app-name", default="TinPyUI App", help="Application Name")
    p_build.add_argument("--package", default="com.tinpyui.app", help="Android Package ID / iOS Bundle ID")
    p_build.add_argument("--bundle-id", default="com.tinpyui.app", help="iOS Bundle Identifier")
    p_build.set_defaults(func=cmd_build)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
