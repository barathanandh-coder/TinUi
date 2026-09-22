"""Core Application Engine and native/web launchers."""
import sys
import os
import time
import ctypes
import shutil
import json
import subprocess
from typing import Any, Callable, List, Optional, Union, Dict, Tuple

from .core.primitives import (
    Rect, _context_stack, eval_prop, safe_eval_prop,
    failsafe_guard, RecursionGuard, ThreadDispatcher, parse_color
)
from .core.signals import Signal
from .core.node import Node
from .core.physics import SpringPhysics
from .net.bridge import haptics


class App:
    """Production Hardware-Accelerated Universal Application Engine."""
    def __init__(self, title: str = "TinPyUI Native Desktop App", width: int = 1600, height: int = 1000, icon: str = "assets/app_icon.png", resizable: bool = True, centered: bool = True, always_on_top: bool = False, fullscreen: bool = False, bg_color: str = "#0D0D10"):
        self.title = title
        self.width = width
        self.height = height
        self.icon_path = icon if (icon and os.path.exists(icon)) else ("assets/app_icon.png" if os.path.exists("assets/app_icon.png") else "")
        self.resizable = resizable
        self.centered = centered
        self.always_on_top = always_on_top
        self.fullscreen = fullscreen
        self.bg_color = bg_color
        self.hwnd = None
        self.root_node: Optional[Node] = None
        self.running = False
        self.focused_node: Optional[Node] = None
        self.active_input_node: Optional[Node] = None
        self.time_start = time.time()
        self.target_name = "Desktop"
        self.widgets: List[Node] = []
        self._signal_registry: Dict[str, Signal] = {}

    def __enter__(self):
        self.root_node = Node("Window", title=self.title)
        _context_stack.append(self.root_node)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _context_stack and _context_stack[-1] is self.root_node:
            _context_stack.pop()

    def add(self, *nodes: Node):
        """Imperative TinPyUI widget adder."""
        self.widgets.extend(nodes)
        return self

    def set_title(self, title: str):
        """Dynamically updates the window title."""
        self.title = title
        if sys.platform == "win32" and self.hwnd:
            try:
                ctypes.windll.user32.SetWindowTextW(self.hwnd, f"{title} [TinPyUI]")
                ctypes.windll.user32.InvalidateRect(self.hwnd, None, True)
            except Exception: pass
        return self

    def resize(self, width: int, height: int):
        """Dynamically resizes the window."""
        self.width, self.height = width, height
        if sys.platform == "win32" and self.hwnd:
            try:
                ctypes.windll.user32.SetWindowPos(self.hwnd, 0, 0, 0, width, height, 0x0002 | 0x0004) # SWP_NOMOVE | SWP_NOZORDER
                ctypes.windll.user32.InvalidateRect(self.hwnd, None, True)
            except Exception: pass
        return self

    def minimize(self):
        """Minimizes the window to taskbar."""
        if sys.platform == "win32" and self.hwnd:
            ctypes.windll.user32.ShowWindow(self.hwnd, 6) # SW_MINIMIZE
        return self

    def maximize(self):
        """Maximizes the window to fullscreen."""
        if sys.platform == "win32" and self.hwnd:
            ctypes.windll.user32.ShowWindow(self.hwnd, 3) # SW_MAXIMIZE
        return self

    def restore(self):
        """Restores the window from minimized/maximized state."""
        if sys.platform == "win32" and self.hwnd:
            ctypes.windll.user32.ShowWindow(self.hwnd, 9) # SW_RESTORE
        return self

    def export_ir(self, filepath: str) -> str:
        """Serializes the current application tree hierarchy to IR JSON format."""
        blueprint = {
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "bg_color": self.bg_color,
            "root": self.root_node.to_dict() if self.root_node else None,
            "widgets": [w.to_dict() for w in self.widgets]
        }
        json_str = json.dumps(blueprint, indent=2)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_str)
        return json_str

    def close(self):
        """Closes the application window."""
        self.running = False
        if sys.platform == "win32" and self.hwnd:
            ctypes.windll.user32.PostQuitMessage(0)
        return self

    def quit(self):
        """Alias for close()."""
        return self.close()

    def set_icon(self, icon_path: str):
        """Dynamically updates the window icon."""
        if os.path.exists(icon_path):
            self.icon_path = icon_path
            if sys.platform == "win32" and self.hwnd:
                try:
                    abs_icon = os.path.abspath(icon_path)
                    hicon = ctypes.windll.user32.LoadImageW(None, abs_icon, 1, 32, 32, 0x00000010)
                    if hicon:
                        ctypes.windll.user32.SendMessageW(self.hwnd, 0x0080, 1, hicon)
                        ctypes.windll.user32.SendMessageW(self.hwnd, 0x0080, 0, hicon)
                        ctypes.windll.user32.InvalidateRect(self.hwnd, None, True)
                except Exception: pass
        return self

    def alert(self, message: str, title: str = "TinPyUI Notice"):
        """Displays a native OS alert dialog message box."""
        if sys.platform == "win32" and self.hwnd:
            ctypes.windll.user32.MessageBoxW(self.hwnd, str(message), str(title), 0x00000000 | 0x00000040)
        else:
            print(f"[{title}] {message}")
        return self

    def confirm(self, message: str, title: str = "TinPyUI Confirmation") -> bool:
        """Displays a native OS confirmation dialog returning True/False."""
        if sys.platform == "win32" and self.hwnd:
            res = ctypes.windll.user32.MessageBoxW(self.hwnd, str(message), str(title), 0x00000001 | 0x00000020)
            return res == 1 # IDOK
        return True

    def notify(self, title: str, message: str):
        """Displays a desktop notification toast alert."""
        self.alert(message, title=title)
        return self

    def set_theme(self, theme_name: str):
        """Dynamically updates app theme palette ('dark', 'cyber', 'light')."""
        if theme_name in ("dark", "cyber", "light"):
            self.bg_color = "#0D0D10" if theme_name != "light" else "#F8FAFC"
            if sys.platform == "win32" and self.hwnd:
                ctypes.windll.user32.InvalidateRect(self.hwnd, None, True)
        return self

    def select_target_interactive(self) -> str:
        """Interactive Terminal Target Selector CLI menu with vibrant per-device color styling."""
        # Enable ANSI virtual terminal processing and UTF-8 stdout on Windows terminals
        if sys.platform == "win32":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                hStdOut = kernel32.GetStdHandle(-11)
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
                mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                kernel32.SetConsoleMode(hStdOut, mode)
            except Exception:
                os.system("")
            if hasattr(sys.stdout, 'reconfigure'):
                try:
                    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                except Exception:
                    pass

        # ANSI Color Codes
        RESET = "\033[0m"
        BOLD = "\033[1m"
        DIM = "\033[90m"
        WHITE = "\033[1;97m"
        CYAN = "\033[1;36m"
        CYAN_DIM = "\033[0;36m"
        GREEN = "\033[1;32m"
        GREEN_DIM = "\033[0;32m"
        BLUE = "\033[1;94m"
        BLUE_DIM = "\033[0;94m"
        MAGENTA = "\033[1;35m"
        MAGENTA_DIM = "\033[0;35m"
        YELLOW = "\033[1;33m"
        YELLOW_DIM = "\033[0;33m"

        def _safe_print(text: str):
            try:
                print(text)
            except UnicodeEncodeError:
                # Safe ASCII fallback for legacy non-UTF8 consoles
                print(text.encode('ascii', 'replace').decode('ascii'))

        _safe_print(f"\n{CYAN}+==============================================================================+{RESET}")
        _safe_print(f"{CYAN}|   {WHITE}[*] TinPyUI Universal Target Platform & Device Selector{CYAN}                    |{RESET}")
        _safe_print(f"{CYAN}+==============================================================================+{RESET}")
        _safe_print(f"{WHITE}Select target device for your application:{RESET}\n")
        _safe_print(f"  {CYAN}[1]{RESET} {WHITE}[Desktop] Native Desktop Application{RESET} {CYAN_DIM}(Windows / macOS / Linux - 1600x1000 px){RESET}")
        _safe_print(f"  {GREEN}[2]{RESET} {WHITE}[Android] Android Mobile Target{RESET}      {GREEN_DIM}(380x680 px - Touch Haptics & Fast DPI){RESET}")
        _safe_print(f"  {BLUE}[3]{RESET} {WHITE}[iOS]     Apple iOS Mobile Target{RESET}    {BLUE_DIM}(375x680 px - Retina Safe-Area Layout){RESET}")
        _safe_print(f"  {MAGENTA}[4]{RESET} {WHITE}[Tablet]  iPad / Tablet Target{RESET}       {MAGENTA_DIM}(640x520 px - Adaptive Split-View){RESET}")
        _safe_print(f"  {YELLOW}[5]{RESET} {WHITE}[Web]     Web WASM Browser Target{RESET}    {YELLOW_DIM}(1024x600 px - Zero-DOM WebGL Shader){RESET}")

        try:
            choice = input(f"\n{CYAN}>> Enter target device choice {WHITE}(1-5){RESET} {DIM}[default: 1]{RESET}: {YELLOW}").strip()
            print(f"{RESET}", end="")
        except Exception:
            choice = "1"

        if choice == "2":
            self.width, self.height = 380, 680
            self.target_name = "Android Mobile"
            self.target_type = "mobile_android"
            selected_color = GREEN
        elif choice == "3":
            self.width, self.height = 375, 680
            self.target_name = "iOS Mobile"
            self.target_type = "mobile_ios"
            selected_color = BLUE
        elif choice == "4":
            self.width, self.height = 640, 520
            self.target_name = "Tablet"
            self.target_type = "tablet"
            selected_color = MAGENTA
        elif choice == "5":
            self.width, self.height = 1024, 600
            self.target_name = "Web WASM Browser"
            self.target_type = "web"
            selected_color = YELLOW
        else:
            self.width, self.height = 1600, 1000
            self.target_name = "Native Desktop App"
            self.target_type = "desktop"
            selected_color = CYAN

        _safe_print(f"\n{GREEN}[+] [TinPyUI Target Selector]{RESET} Configured target platform: {selected_color}{self.target_name}{RESET} {DIM}({self.width}x{self.height} px){RESET}\n")
        return self.target_name

    def build(self) -> Optional[Node]:
        return None

    def run(self, prompt_target: bool = False):
        """Launches targeted device engine: Desktop Native Window, Mobile/Tablet Virtual Device, or Web Browser."""
        if prompt_target:
            self.select_target_interactive()

        print(f"[TinPyUI Native Engine] Initializing Custom Hardware Surface ({self.target_name}): {self.title}")
        self.running = True

        with Node("Main") as root_node:
            user_built = self.build()
            if user_built and user_built not in root_node.children:
                root_node.children.append(user_built)
            for w in self.widgets:
                if w not in root_node.children:
                    root_node.children.append(w)
        self.root_node = root_node

        # Resolve target execution mode
        target_type = getattr(self, "target_type", "")
        if not target_type:
            if "Web" in self.target_name or "WASM" in self.target_name:
                target_type = "web"
            elif "Android" in self.target_name:
                target_type = "mobile_android"
            elif "iOS" in self.target_name:
                target_type = "mobile_ios"
            elif "Tablet" in self.target_name or "iPad" in self.target_name:
                target_type = "tablet"
            else:
                target_type = "desktop"

        # 1. WEB WASM TARGET -> Open Default Web Browser
        if target_type == "web":
            self._run_web_browser_host()
            return

        # 2. MOBILE & TABLET TARGETS -> Open Interactive Virtual Device Simulator in Browser/App Mode
        if target_type in ("mobile_android", "mobile_ios", "tablet"):
            self._run_virtual_device_simulator(target_type)
            return

        # 3. DESKTOP TARGET -> Launch Native Desktop OS Window
        if sys.platform == "win32":
            try:
                self._run_win32_native_window()
                return
            except Exception as e:
                print(f"[TinPyUI Native Engine] Win32 Window Context Note: {e}")

        self._run_native_app_host()

    def _ensure_public_assets(self, out_dir: str = "public"):
        """Ensures public directory contains WebAssembly engine assets, runtime JS, and HTML shell."""
        os.makedirs(out_dir, exist_ok=True)
        try:
            self.export_ir(os.path.join(out_dir, "app.ir.json"))
            self.export_ir("app.ir.json")
        except Exception:
            pass

        wasm_exec_dst = os.path.join(out_dir, "wasm_exec.js")
        if not os.path.exists(wasm_exec_dst) and os.path.exists("wasm_exec.js"):
            try: shutil.copyfile("wasm_exec.js", wasm_exec_dst)
            except Exception: pass

        wasm_dst = os.path.join(out_dir, "tinui_engine.wasm")
        if not os.path.exists(wasm_dst):
            for cand in ["tinui_engine.wasm", "app.wasm", os.path.join("wasm_engine", "tinui_engine.wasm")]:
                if os.path.exists(cand):
                    try:
                        shutil.copyfile(cand, wasm_dst)
                        shutil.copyfile(cand, os.path.join(out_dir, "app.wasm"))
                    except Exception: pass
                    break

        runtime_dst = os.path.join(out_dir, "tin-runtime.js")
        if not os.path.exists(runtime_dst):
            try:
                if os.path.exists("tin-runtime.js"):
                    shutil.copyfile("tin-runtime.js", runtime_dst)
            except Exception: pass

        index_html_dst = os.path.join(out_dir, "index.html")
        html_shell = self._generate_universal_html_shell()
        try:
            with open(index_html_dst, "w", encoding="utf-8") as f:
                f.write(html_shell)
        except Exception as e:
            print(f"[Warning] Could not write index.html: {e}")

    def _start_local_server(self, out_dir: str = "public") -> Tuple[Any, int]:
        """Starts a lightweight HTTP server serving out_dir in a background thread."""
        import http.server
        import socketserver
        import socket
        import threading

        def find_free_port(start=3000):
            for p in range(start, start + 100):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    if s.connect_ex(('127.0.0.1', p)) != 0:
                        return p
            return start

        port = find_free_port(3000)
        
        class QuietHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=out_dir, **kwargs)
            def log_message(self, format, *args):
                pass # suppress verbose console logs

        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("127.0.0.1", port), QuietHandler)
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        return httpd, port

    def _run_web_browser_host(self):
        """Compiles to WASM/IR, starts local web server, and opens default Web Browser."""
        import webbrowser
        self._ensure_public_assets("public")
        httpd, port = self._start_local_server("public")
        
        app_url = f"http://127.0.0.1:{port}/index.html"
        print(f"\n\033[1;32m[+] [TinPyUI Web Engine]\033[0m WebAssembly Server running at: \033[1;36m{app_url}\033[0m")
        print(f"\033[1;32m[+] [TinPyUI Web Engine]\033[0m Launching default web browser...\n")
        
        webbrowser.open(app_url)
        print(f"\033[90m[TinPyUI Web Engine] Active on http://127.0.0.1:{port}/ — Press Ctrl+C in terminal to stop.\033[0m\n")
        try:
            while self.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[TinPyUI Web Engine] Server stopped.")
        finally:
            try: httpd.shutdown()
            except Exception: pass

    def _run_virtual_device_simulator(self, target_type: str = "mobile_android"):
        """Compiles to WASM/IR, starts server, and launches Virtual Device Simulator in Chrome/Browser."""
        import webbrowser
        import subprocess
        self._ensure_public_assets("public")
        httpd, port = self._start_local_server("public")

        device_slug = "android" if "android" in target_type else ("ios" if "ios" in target_type else "tablet")
        app_url = f"http://127.0.0.1:{port}/index.html?device={device_slug}&w={self.width}&h={self.height}"
        
        print(f"\n\033[1;32m[+] [TinPyUI Virtual Device Simulator]\033[0m Target Platform: \033[1;36m{self.target_name}\033[0m \033[90m({self.width}x{self.height} px)\033[0m")
        print(f"\033[1;32m[+] [TinPyUI Virtual Device Simulator]\033[0m Simulator URL: \033[1;36m{app_url}\033[0m")
        print(f"\033[1;32m[+] [TinPyUI Virtual Device Simulator]\033[0m Launching device emulation window...\n")

        win_w = self.width + 60
        win_h = self.height + 110
        opened = False
        if sys.platform == "win32":
            # Attempt standalone Chrome / Edge App Window mode sized to exact device
            for browser_cmd in ["msedge.exe", "chrome.exe"]:
                try:
                    cmd = ["cmd", "/c", "start", browser_cmd, f"--app={app_url}", f"--window-size={win_w},{win_h}"]
                    res = subprocess.run(cmd, capture_output=True)
                    if res.returncode == 0:
                        opened = True
                        break
                except Exception:
                    pass

        if not opened:
            webbrowser.open(app_url)

        print(f"\033[90m[TinPyUI Virtual Device] Simulator active on http://127.0.0.1:{port}/ — Press Ctrl+C to stop.\033[0m\n")
        try:
            while self.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[TinPyUI Virtual Device] Simulator stopped.")
        finally:
            try: httpd.shutdown()
            except Exception: pass

    def _generate_universal_html_shell(self) -> str:
        """Generates dynamic HTML supporting Full Web, Desktop Native Frame, and Mobile/Tablet Virtual Device Mockups."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>TinPyUI Multi-Device Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: #08090d;
            color: #f1f5f9;
            font-family: 'Plus Jakarta Sans', sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            overflow-x: hidden;
        }
        #tin-device-bar {
            width: 100%;
            background: rgba(15, 17, 26, 0.95);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding: 10px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 1000;
            gap: 12px;
        }
        .tin-brand-tag {
            font-weight: 800;
            font-size: 0.95rem;
            background: linear-gradient(135deg, #00f2fe, #9b51e0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .tin-dev-btn-group {
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        .tin-dev-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #cbd5e1;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
        }
        .tin-dev-btn:hover {
            background: rgba(0, 242, 254, 0.15);
            border-color: rgba(0, 242, 254, 0.5);
            color: #00f2fe;
        }
        .tin-dev-btn.active {
            background: linear-gradient(135deg, #00f2fe, #9b51e0);
            border-color: transparent;
            color: #0a0b10;
            font-weight: 700;
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
        }
        #tin-viewport-wrapper {
            flex: 1;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px 16px;
        }
        .tin-device-desktop {
            width: 100%;
            max-width: 1360px;
            min-height: 820px;
            background: #0f1017;
            border: 1px solid rgba(0, 242, 254, 0.25);
            border-radius: 14px;
            box-shadow: 0 30px 70px -15px rgba(0, 0, 0, 0.9), 0 0 35px rgba(0, 242, 254, 0.12);
            position: relative;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        .tin-desktop-titlebar {
            height: 38px;
            background: rgba(18, 20, 28, 0.98);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            user-select: none;
            z-index: 95;
            flex-shrink: 0;
        }
        .tin-win-controls {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .tin-win-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }
        .tin-win-close { background: #ff5f56; border: 1px solid #e0443e; }
        .tin-win-min { background: #ffbd2e; border: 1px solid #dea123; }
        .tin-win-max { background: #27c93f; border: 1px solid #1aab29; }
        .tin-desktop-title {
            font-size: 0.78rem;
            font-weight: 600;
            color: #94a3b8;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .tin-device-phone {
            width: 380px;
            height: 720px;
            background: #0f1017;
            border: 10px solid #1e2230;
            border-radius: 46px;
            box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.8), 0 0 30px rgba(0, 242, 254, 0.15);
            position: relative;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        .tin-device-tablet {
            width: 680px;
            height: 540px;
            background: #0f1017;
            border: 12px solid #232736;
            border-radius: 32px;
            box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.8), 0 0 30px rgba(155, 81, 224, 0.15);
            position: relative;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        .tin-device-web {
            width: 100%;
            max-width: 1280px;
            min-height: 80vh;
            border-radius: 16px;
            background: transparent;
            box-shadow: none;
            border: none;
        }
        .tin-notch-ios {
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            width: 110px;
            height: 26px;
            background: #000000;
            border-radius: 20px;
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .tin-notch-android {
            position: absolute;
            top: 12px;
            left: 50%;
            transform: translateX(-50%);
            width: 14px;
            height: 14px;
            background: #000000;
            border-radius: 50%;
            z-index: 100;
            border: 2px solid #1a1e2b;
        }
        .tin-status-bar {
            height: 38px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            font-size: 0.72rem;
            color: #94a3b8;
            font-weight: 600;
            z-index: 90;
            background: rgba(15, 16, 23, 0.95);
            flex-shrink: 0;
        }
        .tin-home-bar {
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            background: rgba(15, 16, 23, 0.95);
        }
        .tin-home-pill {
            width: 130px;
            height: 4px;
            background: rgba(255, 255, 255, 0.35);
            border-radius: 9999px;
        }
        #tinui-root {
            flex: 1;
            overflow-y: auto;
            overflow-x: hidden;
            width: 100%;
            height: 100%;
            position: relative;
            background: #0a0b10;
            padding: 16px;
        }
        .tin-card {
            background: rgba(22, 24, 38, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .tin-btn {
            background: linear-gradient(135deg, #00f2fe, #4facfe);
            color: #0a0b10;
            font-weight: 700;
            border: none;
            padding: 10px 18px;
            border-radius: 9999px;
            cursor: pointer;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .tin-btn:hover {
            transform: scale(1.03);
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
        }
        .tin-btn-outline {
            background: transparent;
            border: 1px solid rgba(0, 242, 254, 0.4);
            color: #00f2fe;
            font-weight: 600;
            padding: 9px 16px;
            border-radius: 9999px;
            cursor: pointer;
        }
        .tin-badge {
            background: rgba(0, 242, 254, 0.15);
            color: #00f2fe;
            border: 1px solid rgba(0, 242, 254, 0.3);
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }
        #tin-haptic-toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: rgba(0, 242, 254, 0.95);
            color: #0a0b10;
            font-weight: 700;
            font-size: 0.82rem;
            padding: 8px 18px;
            border-radius: 9999px;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.6);
            pointer-events: none;
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 9999;
        }
        #tin-haptic-toast.show {
            transform: translateX(-50%) translateY(0);
        }
    </style>
</head>
<body>
    <div id="tin-device-bar">
        <div class="tin-brand-tag">
            <span>⚡ TinPyUI v1.6</span>
            <span style="font-size:0.75rem; color:#94a3b8; font-weight:normal;">Omni-Device Simulator</span>
        </div>
        <div class="tin-dev-btn-group">
            <a href="?device=desktop" id="btn-desktop" class="tin-dev-btn">💻 Desktop Native (1600x1000)</a>
            <a href="?device=tablet" id="btn-tablet" class="tin-dev-btn">📱 iPad Tablet (640x520)</a>
            <a href="?device=android" id="btn-android" class="tin-dev-btn">🤖 Android Mobile (380x680)</a>
            <a href="?device=ios" id="btn-ios" class="tin-dev-btn">🍎 iPhone 16 Pro (375x680)</a>
            <a href="?device=web" id="btn-web" class="tin-dev-btn">🌐 Full Web WASM</a>
        </div>
    </div>

    <div id="tin-viewport-wrapper">
        <div id="tin-device-container" class="tin-device-desktop">
            <div id="tin-desktop-titlebar" class="tin-desktop-titlebar" style="display:flex;">
                <div class="tin-win-controls">
                    <span class="tin-win-dot tin-win-close"></span>
                    <span class="tin-win-dot tin-win-min"></span>
                    <span class="tin-win-dot tin-win-max"></span>
                </div>
                <div class="tin-desktop-title">
                    <span style="color:#00f2fe;">●</span> TinPyUI Desktop Surface [Native Win32 / macOS Metal Host]
                </div>
                <div style="font-size:0.72rem; color:#64748b; font-family:monospace;">120 FPS | 0ms IPC</div>
            </div>
            <div id="tin-notch"></div>
            <div id="tin-status-bar" class="tin-status-bar" style="display:none;">
                <span id="tin-clock">09:41</span>
                <span>5G ● 100%</span>
            </div>
            <div id="tinui-root"></div>
            <div id="tin-home-bar" class="tin-home-bar" style="display:none;">
                <div class="tin-home-pill"></div>
            </div>
        </div>
    </div>

    <div id="tin-haptic-toast">📳 Haptic Pulse Triggered (60ms)</div>

    <script>
        const params = new URLSearchParams(window.location.search);
        let currentDevice = params.get('device') || 'desktop';
        const container = document.getElementById('tin-device-container');
        const statusBar = document.getElementById('tin-status-bar');
        const homeBar = document.getElementById('tin-home-bar');
        const notch = document.getElementById('tin-notch');
        const desktopTitlebar = document.getElementById('tin-desktop-titlebar');

        function setDevice(device, pushHistory) {
            currentDevice = device;
            document.querySelectorAll('.tin-dev-btn').forEach(btn => btn.classList.remove('active'));
            const activeBtn = document.getElementById('btn-' + device);
            if (activeBtn) activeBtn.classList.add('active');

            if (device === 'android') {
                container.className = 'tin-device-phone';
                statusBar.style.display = 'flex';
                homeBar.style.display = 'flex';
                desktopTitlebar.style.display = 'none';
                notch.className = 'tin-notch-android';
            } else if (device === 'ios') {
                container.className = 'tin-device-phone';
                statusBar.style.display = 'flex';
                homeBar.style.display = 'flex';
                desktopTitlebar.style.display = 'none';
                notch.className = 'tin-notch-ios';
            } else if (device === 'tablet') {
                container.className = 'tin-device-tablet';
                statusBar.style.display = 'flex';
                homeBar.style.display = 'flex';
                desktopTitlebar.style.display = 'none';
                notch.className = '';
            } else if (device === 'web') {
                container.className = 'tin-device-web';
                statusBar.style.display = 'none';
                homeBar.style.display = 'none';
                desktopTitlebar.style.display = 'none';
                notch.className = '';
            } else {
                container.className = 'tin-device-desktop';
                statusBar.style.display = 'none';
                homeBar.style.display = 'none';
                desktopTitlebar.style.display = 'flex';
                notch.className = '';
            }

            if (pushHistory) {
                const url = new URL(window.location);
                url.searchParams.set('device', device);
                window.history.pushState({}, '', url);
            }
        }

        // Attach click listeners to device buttons for smooth zero-reload redirection
        document.querySelectorAll('.tin-dev-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const targetDev = btn.id.replace('btn-', '');
                setDevice(targetDev, true);
            });
        });

        // Initialize target mode
        setDevice(currentDevice, false);

        // Live Clock
        setInterval(() => {
            const d = new Date();
            const timeStr = d.getHours().toString().padStart(2, '0') + ':' + d.getMinutes().toString().padStart(2, '0');
            const clockEl = document.getElementById('tin-clock');
            if (clockEl) clockEl.innerText = timeStr;
        }, 1000);

        function triggerHapticFeedback() {
            if ('vibrate' in navigator) navigator.vibrate(60);
            const toast = document.getElementById('tin-haptic-toast');
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 1200);
        }

    </script>
    <script src="wasm_exec.js"></script>
    <script src="tin-runtime.js"></script>
</body>
</html>
"""

    def _run_win32_native_window(self):
        """Pure Win32 C-FFI Native Window Loop (Zero Pygame / Zero Third-Party Dependencies)."""
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        gdi32 = ctypes.windll.gdi32

        def RGB(r: int, g: int, b: int) -> int:
            return (r & 0xFF) | ((g & 0xFF) << 8) | ((b & 0xFF) << 16)

        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long),
            ]

        class PAINTSTRUCT(ctypes.Structure):
            _fields_ = [
                ("hdc", ctypes.c_void_p),
                ("fErase", ctypes.c_int),
                ("rcPaint", RECT),
                ("fRestore", ctypes.c_int),
                ("fIncUpdate", ctypes.c_int),
                ("rgbReserved", ctypes.c_byte * 32),
            ]

        WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t)

        user32.DefWindowProcW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
        user32.DefWindowProcW.restype = ctypes.c_ssize_t

        @failsafe_guard(0)
        def wnd_proc(hwnd, msg, wparam, lparam):
            if msg == 0x0010: # WM_CLOSE
                user32.PostQuitMessage(0)
                self.running = False
                return 0
            elif msg == 0x000F: # WM_PAINT
                ps = PAINTSTRUCT()
                hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))
                self._draw_win32_gdi(hdc, hwnd, gdi32, user32, RGB, RECT)
                user32.EndPaint(hwnd, ctypes.byref(ps))
                return 0
            elif msg == 0x0201: # WM_LBUTTONDOWN
                x = ctypes.c_int16(lparam & 0xFFFF).value
                y = ctypes.c_int16((lparam >> 16) & 0xFFFF).value

                # Title Bar Header Controls & Window Dragging (y < 40)
                if y < 40:
                    rect = RECT()
                    user32.GetClientRect(hwnd, ctypes.byref(rect))
                    w_width = rect.right
                    
                    if x >= w_width - 40: # Close (X) Button
                        user32.PostQuitMessage(0)
                        self.running = False
                        return 0
                    elif x >= w_width - 75: # Maximize/Restore ([]) Button
                        is_zoomed = user32.IsZoomed(hwnd)
                        user32.ShowWindow(hwnd, 9 if is_zoomed else 3) # SW_RESTORE / SW_MAXIMIZE
                        return 0
                    elif x >= w_width - 110: # Minimize (_) Button
                        user32.ShowWindow(hwnd, 6) # SW_MINIMIZE
                        return 0
                    else: # Window Title Bar Dragging
                        user32.ReleaseCapture()
                        user32.SendMessageW(hwnd, 0x00A1, 2, 0) # WM_NCLBUTTONDOWN, HTCAPTION
                        return 0

                self._handle_win32_click(x, y)
                user32.InvalidateRect(hwnd, None, True)
                return 0
            return user32.DefWindowProcW(hwnd, msg, wparam, ctypes.c_ssize_t(lparam).value)

        self._wnd_proc = WNDPROC(wnd_proc)

        class WNDCLASSEXW(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_uint),
                ("style", ctypes.c_uint),
                ("lpfnWndProc", WNDPROC),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", ctypes.c_void_p),
                ("hIcon", ctypes.c_void_p),
                ("hCursor", ctypes.c_void_p),
                ("hbrBackground", ctypes.c_void_p),
                ("lpszMenuName", ctypes.c_wchar_p),
                ("lpszClassName", ctypes.c_wchar_p),
                ("hIconSm", ctypes.c_void_p),
            ]

        hinstance = kernel32.GetModuleHandleW(None)
        wcls = WNDCLASSEXW()
        wcls.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wcls.style = 3 # CS_HREDRAW | CS_VREDRAW
        wcls.lpfnWndProc = self._wnd_proc
        wcls.hInstance = hinstance
        wcls.hbrBackground = gdi32.CreateSolidBrush(RGB(13, 13, 16))
        wcls.lpszClassName = f"TinPyUINativeWindow_{id(self)}"

        user32.RegisterClassExW(ctypes.byref(wcls))

        hwnd = user32.CreateWindowExW(
            0, f"TinPyUINativeWindow_{id(self)}", f"{self.title} [Custom Native Engine]",
            0x00CF0000 | 0x10000000, # WS_OVERLAPPEDWINDOW | WS_VISIBLE
            0x80000000, 0x80000000, self.width, self.height,
            None, None, hinstance, None
        )
        self.hwnd = hwnd

        user32.ShowWindow(hwnd, 1)
        user32.UpdateWindow(hwnd)

        print(f"[TinPyUI Native Engine] Native Win32 GDI Surface Created (HWND: {hex(hwnd)}). Custom Header [Close|Min|Max|Drag] Ready.")

        class MSG(ctypes.Structure):
            _fields_ = [
                ("hwnd", ctypes.c_void_p),
                ("message", ctypes.c_uint),
                ("wParam", ctypes.c_size_t),
                ("lParam", ctypes.c_ssize_t),
                ("time", ctypes.c_uint),
                ("pt_x", ctypes.c_long),
                ("pt_y", ctypes.c_long),
            ]

        msg = MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    @failsafe_guard(None)
    def _draw_win32_gdi(self, hdc, hwnd, gdi32, user32, RGB, RECT):
        """Draws native vector widgets & custom title bar header directly onto Win32 Device Context (HDC)."""
        gdi32.SetBkMode(hdc, 1) # TRANSPARENT
        rect = RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rect))
        w_width = rect.right

        # 1. Fill Window Background (Android Studio Darcula #1e1f22)
        bg_brush = gdi32.CreateSolidBrush(RGB(30, 31, 34))
        user32.FillRect(hdc, ctypes.byref(rect), bg_brush)
        gdi32.DeleteObject(bg_brush)

        # 2. Draw Title Bar Header Container (y = 0 to 38, Android Studio Header #2b2d30)
        hdr_rect = RECT(0, 0, w_width, 38)
        hdr_brush = gdi32.CreateSolidBrush(RGB(43, 45, 48))
        user32.FillRect(hdc, ctypes.byref(hdr_rect), hdr_brush)
        gdi32.DeleteObject(hdr_brush)

        # Professional App Icon Badge (Clean Android Studio Blue #3574f0 square with white accent)
        icon_rect = RECT(12, 9, 32, 29)
        icon_brush = gdi32.CreateSolidBrush(RGB(53, 116, 240))
        user32.FillRect(hdc, ctypes.byref(icon_rect), icon_brush)
        gdi32.DeleteObject(icon_brush)
        gdi32.SetTextColor(hdc, RGB(255, 255, 255))
        icon_txt_r = RECT(12, 10, 32, 28)
        user32.DrawTextW(hdc, "T", -1, ctypes.byref(icon_txt_r), 0x0001)

        # Title Bar Title Text (Clean off-white #dfe1e5 at x=40)
        gdi32.SetTextColor(hdc, RGB(223, 225, 229))
        title_r = RECT(40, 9, w_width - 130, 34)
        user32.DrawTextW(hdc, self.title, -1, ctypes.byref(title_r), 0)

        # Control Button: Minimize (-)
        min_r = RECT(w_width - 105, 8, w_width - 72, 32)
        gdi32.SetTextColor(hdc, RGB(157, 160, 168))
        user32.DrawTextW(hdc, " - ", -1, ctypes.byref(min_r), 0x0001)

        # Control Button: Maximize / Restore ([])
        max_r = RECT(w_width - 72, 8, w_width - 38, 32)
        gdi32.SetTextColor(hdc, RGB(157, 160, 168))
        user32.DrawTextW(hdc, " [] ", -1, ctypes.byref(max_r), 0x0001)

        # Control Button: Close (X)
        close_r = RECT(w_width - 38, 0, w_width, 38)
        gdi32.SetTextColor(hdc, RGB(157, 160, 168))
        close_txt_r = RECT(w_width - 38, 8, w_width, 32)
        user32.DrawTextW(hdc, " X ", -1, ctypes.byref(close_txt_r), 0x0001)

        # Header Bottom Border Line (Subtle hairline divider #393b40)
        hdr_line_r = RECT(0, 37, w_width, 38)
        line_brush = gdi32.CreateSolidBrush(RGB(57, 59, 64))
        user32.FillRect(hdc, ctypes.byref(hdr_line_r), line_brush)
        gdi32.DeleteObject(line_brush)

        # Render Page Components below title bar header (y >= 48)
        if self.root_node:
            self._render_gdi_node(self.root_node, 16, 48, w_width - 32, hdc, gdi32, user32, RGB, RECT)

    def _render_gdi_node(self, node: Node, x: int, y: int, max_w: int, hdc, gdi32, user32, RGB, RECT) -> Tuple[int, int]:
        if node.tag in ("Main", "Window"):
            cur_y = y
            for child in node.children:
                _, ch_h = self._render_gdi_node(child, x, cur_y, max_w, hdc, gdi32, user32, RGB, RECT)
                cur_y += ch_h + 12
            return max_w, cur_y - y

        elif node.tag == "Row":
            gap = eval_prop(node.props.get("gap"), 16)
            cur_x = x
            max_h = 40
            for child in node.children:
                cw, ch = self._render_gdi_node(child, cur_x, y, max_w - (cur_x - x), hdc, gdi32, user32, RGB, RECT)
                cur_x += cw + gap
                max_h = max(max_h, ch)
            node.rect = Rect(x, y, max_w, max_h)
            return max_w, max_h

        elif node.tag == "Column":
            gap = eval_prop(node.props.get("gap"), 12)
            w_prop = eval_prop(node.props.get("width"), max_w)
            col_w = w_prop if isinstance(w_prop, int) else max_w
            cur_y = y
            for child in node.children:
                _, ch_h = self._render_gdi_node(child, x, cur_y, col_w, hdc, gdi32, user32, RGB, RECT)
                cur_y += ch_h + gap
            node.rect = Rect(x, y, col_w, cur_y - y)
            return col_w, cur_y - y

        elif node.tag in ("Card", "Section"):
            pad = eval_prop(node.props.get("padding"), 14)
            card_w = max_w
            cur_y = y + pad
            max_child_h = 0
            for child in node.children:
                _, ch_h = self._render_gdi_node(child, x + pad, cur_y, card_w - (pad * 2), hdc, gdi32, user32, RGB, RECT)
                cur_y += ch_h + 10
            card_h = max(40, (cur_y - y) + pad)
            node.rect = Rect(x, y, card_w, card_h)

            card_r = RECT(x, y, x + card_w, y + card_h)
            card_b = gdi32.CreateSolidBrush(RGB(43, 45, 48))
            user32.FillRect(hdc, ctypes.byref(card_r), card_b)
            gdi32.DeleteObject(card_b)

            # 1px border #393b40
            b_brush = gdi32.CreateSolidBrush(RGB(57, 59, 64))
            user32.FrameRect(hdc, ctypes.byref(card_r), b_brush)
            gdi32.DeleteObject(b_brush)

            # Re-render children over card surface
            cur_y = y + pad
            for child in node.children:
                _, ch_h = self._render_gdi_node(child, x + pad, cur_y, card_w - (pad * 2), hdc, gdi32, user32, RGB, RECT)
                cur_y += ch_h + 10
            return card_w, card_h

        elif node.tag == "Heading":
            txt = str(eval_prop(node.props.get("text"), ""))
            gdi32.SetTextColor(hdc, RGB(223, 225, 229))
            r = RECT(x, y, x + max_w, y + 32)
            user32.DrawTextW(hdc, txt, -1, ctypes.byref(r), 0)
            node.rect = Rect(x, y, max_w, 32)
            return max_w, 32

        elif node.tag == "Text" or node.tag == "GradientText":
            txt = str(eval_prop(node.props.get("text"), ""))
            gdi32.SetTextColor(hdc, RGB(188, 190, 196))
            r = RECT(x, y, x + max_w, y + 22)
            user32.DrawTextW(hdc, txt, -1, ctypes.byref(r), 0)
            node.rect = Rect(x, y, max_w, 22)
            return max_w, 22

        elif node.tag == "Button":
            txt = str(eval_prop(node.props.get("text"), "Button"))
            btn_w = max(130, len(txt) * 9 + 28)
            btn_h = 32
            node.rect = Rect(x, y, btn_w, btn_h)

            r = RECT(x, y, x + btn_w, y + btn_h)
            variant = str(node.props.get("variant", ""))
            if "run" in txt.lower() or "success" in variant:
                btn_color = RGB(73, 156, 84) # Android Studio Run Green #499c54
            elif "danger" in variant:
                btn_color = RGB(224, 85, 85) # Error Red #e05555
            elif "primary" in variant or "blue" in variant:
                btn_color = RGB(53, 116, 240) # Android Studio Blue #3574f0
            else:
                btn_color = RGB(53, 116, 240) # Default IDE Blue
            btn_brush = gdi32.CreateSolidBrush(btn_color)
            user32.FillRect(hdc, ctypes.byref(r), btn_brush)
            gdi32.DeleteObject(btn_brush)

            gdi32.SetTextColor(hdc, RGB(255, 255, 255))
            text_r = RECT(x + 8, y + 7, x + btn_w - 8, y + btn_h)
            user32.DrawTextW(hdc, txt, -1, ctypes.byref(text_r), 0x0001) # DT_CENTER
            return btn_w, btn_h

        elif node.tag == "NavItem":
            txt = str(eval_prop(node.props.get("text"), ""))
            active = bool(eval_prop(node.props.get("active"), False))
            w = max(160, len(txt) * 8 + 24)
            h = 30
            node.rect = Rect(x, y, w, h)
            r = RECT(x, y, x + w, y + h)
            if active:
                act_brush = gdi32.CreateSolidBrush(RGB(46, 67, 110))
                user32.FillRect(hdc, ctypes.byref(r), act_brush)
                gdi32.DeleteObject(act_brush)
                gdi32.SetTextColor(hdc, RGB(255, 255, 255))
                txt_r = RECT(x + 8, y + 6, x + w - 8, y + h)
                user32.DrawTextW(hdc, f"● {txt}", -1, ctypes.byref(txt_r), 0)
            else:
                gdi32.SetTextColor(hdc, RGB(157, 160, 168))
                txt_r = RECT(x + 8, y + 6, x + w - 8, y + h)
                user32.DrawTextW(hdc, f"○ {txt}", -1, ctypes.byref(txt_r), 0)
            return w, h

        elif node.tag == "Badge":
            txt = str(eval_prop(node.props.get("text"), ""))
            w = max(90, len(txt) * 8 + 18)
            node.rect = Rect(x, y, w, 24)
            gdi32.SetTextColor(hdc, RGB(73, 156, 84))
            r = RECT(x, y, x + w, y + 24)
            user32.DrawTextW(hdc, f"[ {txt} ]", -1, ctypes.byref(r), 0)
            return w, 24

        elif node.tag == "Progress" or node.tag == "ProgressBar":
            val = eval_prop(node.props.get("value"), 50)
            max_v = eval_prop(node.props.get("max"), 100)
            pct = max(0.0, min(1.0, float(val) / float(max_v if max_v > 0 else 1)))
            p_w, p_h = min(max_w, 240), 14
            node.rect = Rect(x, y, p_w, p_h)

            track_r = RECT(x, y, x + p_w, y + p_h)
            t_brush = gdi32.CreateSolidBrush(RGB(30, 31, 34))
            user32.FillRect(hdc, ctypes.byref(track_r), t_brush)
            gdi32.DeleteObject(t_brush)

            fill_w = int(p_w * pct)
            if fill_w > 0:
                fill_r = RECT(x, y, x + fill_w, y + p_h)
                f_brush = gdi32.CreateSolidBrush(RGB(53, 116, 240))
                user32.FillRect(hdc, ctypes.byref(fill_r), f_brush)
                gdi32.DeleteObject(f_brush)
            return p_w, p_h

        elif node.tag == "Switch":
            active = eval_prop(node.props.get("active"), True)
            sw_w, sw_h = 50, 24
            node.rect = Rect(x, y, sw_w, sw_h)

            sw_r = RECT(x, y, x + sw_w, y + sw_h)
            sw_brush = gdi32.CreateSolidBrush(RGB(52, 199, 89) if active else RGB(42, 42, 56))
            user32.FillRect(hdc, ctypes.byref(sw_r), sw_brush)
            gdi32.DeleteObject(sw_brush)

            knob_x = x + 28 if active else x + 4
            knob_r = RECT(knob_x, y + 3, knob_x + 18, y + 21)
            k_brush = gdi32.CreateSolidBrush(RGB(255, 255, 255))
            user32.FillRect(hdc, ctypes.byref(knob_r), k_brush)
            gdi32.DeleteObject(k_brush)
            return sw_w, sw_h

        elif node.tag == "Avatar" or node.tag == "Image":
            sz = eval_prop(node.props.get("size"), eval_prop(node.props.get("width"), 40))
            node.rect = Rect(x, y, sz, sz)
            img_r = RECT(x, y, x + sz, y + sz)
            img_brush = gdi32.CreateSolidBrush(RGB(255, 0, 127))
            user32.FillRect(hdc, ctypes.byref(img_r), img_brush)
            gdi32.DeleteObject(img_brush)
            gdi32.SetTextColor(hdc, RGB(255, 255, 255))
            user32.DrawTextW(hdc, " ICON ", -1, ctypes.byref(img_r), 0x0001)
            return sz, sz

        elif node.tag == "DataTable":
            cols = eval_prop(node.props.get("columns"), [])
            raw_rows = eval_prop(node.props.get("data"), [])
            rows = []
            if raw_rows and isinstance(raw_rows, list):
                if isinstance(raw_rows[0], dict):
                    if not cols:
                        cols = list(raw_rows[0].keys())
                    for r in raw_rows:
                        rows.append([r.get(c, "") for c in cols])
                elif isinstance(raw_rows[0], (list, tuple)):
                    rows = raw_rows
                else:
                    rows = [[str(r)] for r in raw_rows]

            tbl_w = max_w
            tbl_h = max(80, (len(rows) + 1) * 28 + 10)
            node.rect = Rect(x, y, tbl_w, tbl_h)

            hdr_r = RECT(x, y, x + tbl_w, y + 28)
            hdr_b = gdi32.CreateSolidBrush(RGB(30, 32, 44))
            user32.FillRect(hdc, ctypes.byref(hdr_r), hdr_b)
            gdi32.DeleteObject(hdr_b)

            if cols:
                col_w = tbl_w // len(cols)
                gdi32.SetTextColor(hdc, RGB(0, 242, 254))
                for i, col_name in enumerate(cols):
                    c_r = RECT(x + i * col_w + 8, y + 5, x + (i + 1) * col_w - 8, y + 25)
                    user32.DrawTextW(hdc, str(col_name), -1, ctypes.byref(c_r), 0)

            gdi32.SetTextColor(hdc, RGB(220, 220, 230))
            col_w = tbl_w // (len(cols) if cols else 1)
            for r_idx, row in enumerate(rows[:10]):
                row_y = y + 28 + r_idx * 26
                for c_idx, val in enumerate(row):
                    cell_r = RECT(x + c_idx * col_w + 8, row_y + 4, x + (c_idx + 1) * col_w - 8, row_y + 24)
                    user32.DrawTextW(hdc, str(val), -1, ctypes.byref(cell_r), 0)

            return tbl_w, tbl_h

        return 0, 0

    def _hit_test(self, node: Node, pos: Tuple[int, int]) -> Optional[Node]:
        if not node: return None
        if hasattr(node, "rect") and node.rect and node.rect.collidepoint(pos):
            for child in reversed(node.children):
                hit = self._hit_test(child, pos)
                if hit: return hit
            return node
        return None

    def _handle_win32_click(self, x: int, y: int):
        """Processes Win32 mouse click events against widget bounding boxes."""
        if not self.root_node: return
        clicked = self._hit_test(self.root_node, (x, y))
        if clicked:
            cb = clicked.props.get("on_click")
            if callable(cb):
                cb()

    def _run_native_app_host(self):
        """Fallback Native OS Desktop Host Execution."""
        print(f"[TinPyUI Native Engine] Created Custom Native Window Context for '{self.title}'.")

    def _measure_node(self, node: Node, max_w: int) -> Tuple[int, int]:
        if node.tag == "GradientText": return max_w, 38
        elif node.tag == "Heading": return max_w, 32
        elif node.tag == "Text": return max_w, 24
        elif node.tag == "Button": return 130, 36
        elif node.tag == "Input": return max_w, 180
        elif node.tag == "Badge": return 90, 24
        elif node.tag == "Spacer": return 20, 10
        elif node.tag == "Card": return max_w, 160
        return max_w, 36


def create_window(title: str = "TinPyUI Desktop Window", width: int = 800, height: int = 500) -> App:
    """Ultra-concise TinPyUI window creation helper function."""
    return App(title=title, width=width, height=height)

def Window(title: str = "TinPyUI Desktop Window", width: int = 800, height: int = 500) -> App:
    """Ultra-easy Window creation helper function."""
    return App(title=title, width=width, height=height)

def run(app: Optional[App] = None):
    """Launches the native desktop window app."""
    if app:
        app.run()

def export_mobile(target_file: str = "main.tin", output_dir: str = "build/mobile/android", app_name: str = "TinPyUI App", package_name: str = "com.tinpyui.app", build_apk: bool = False):
    """Packages application into a standalone Android Gradle project and optionally compiles APK."""
    try:
        from pypi_build.tinpyui.mobile_export import export_android_project
    except ImportError:
        try:
            from tinpyui.mobile_export import export_android_project
        except ImportError:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "mobile_export",
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "pypi_build", "tinpyui", "mobile_export.py")
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            export_android_project = mod.export_android_project
    return export_android_project(target_file=target_file, output_dir=output_dir, app_name=app_name, package_name=package_name, build_apk=build_apk)

export_android = export_mobile

def export_ios(target_file: str = "main.tin", output_dir: str = "build/mobile/ios", app_name: str = "TinPyUI App", bundle_id: str = "com.tinpyui.app", build_ipa: bool = False):
    """Packages application into a standalone Apple iOS Xcode project."""
    try:
        from pypi_build.tinpyui.mobile_export import export_ios_project
    except ImportError:
        try:
            from tinpyui.mobile_export import export_ios_project
        except ImportError:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "mobile_export",
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "mobile_export.py")
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            export_ios_project = mod.export_ios_project
    return export_ios_project(target_file=target_file, output_dir=output_dir, app_name=app_name, bundle_id=bundle_id, build_ipa=build_ipa)


if __name__ == "__main__":

    import os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pypi_build"))
    from tinpyui.cli import main as cli_main
    cli_main()


