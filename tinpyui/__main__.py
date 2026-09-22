"""
TinPyUI CLI Entrypoint
Enables 'python -m tinpyui' to launch the Native Desktop Application Runner or scaffold new projects.
"""

import sys
import os
import shutil
import json
import tinpyui as tin

def scaffold_project_interactive(target_dir_arg: str = ""):
    """Interactively asks for project name, target device architecture, and confirmation before scaffolding."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
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
    DIM = "\033[90m"

    print(f"\n{CYAN}+==============================================================================+{RESET}")
    print(f"{CYAN}|   {WHITE}[*] Welcome to TinPyUI! Let's create your new app{CYAN}                          |{RESET}")
    print(f"{CYAN}+==============================================================================+{RESET}\n")

    # 1. Project Directory / Name
    default_name = target_dir_arg.strip() if target_dir_arg.strip() else "my_app"
    if not target_dir_arg.strip():
        try:
            proj_name = input(f"{CYAN}>> What would you like to name your project? {WHITE}[default: {default_name}]{RESET}: {YELLOW}").strip()
            print(f"{RESET}", end="")
        except Exception:
            proj_name = default_name
    else:
        proj_name = target_dir_arg.strip()
    if not proj_name:
        proj_name = default_name

    # 2. Target Device Architecture Selection
    print(f"\n{WHITE}Where do you want your app to run?{RESET}")
    print(f"  {CYAN}[1]{RESET} {WHITE}Universal App{RESET}    {CYAN_DIM}(Runs everywhere: Browser, Desktop & Mobile){RESET} {GREEN}[Recommended]{RESET}")
    print(f"  {GREEN}[2]{RESET} {WHITE}Desktop App{RESET}      {GREEN_DIM}(Windows, Mac & Linux desktop window){RESET}")
    print(f"  {BLUE}[3]{RESET} {WHITE}Mobile / Web App{RESET} {BLUE_DIM}(Phones, Tablets & Browsers){RESET}\n")

    try:
        dev_choice = input(f"{CYAN}>> Choose an option {WHITE}(1-3){RESET} {DIM}[default: 1]{RESET}: {YELLOW}").strip()
        print(f"{RESET}", end="")
    except Exception:
        dev_choice = "1"

    dev_modes = {
        "1": ("Universal (Web, Desktop & Mobile)", "universal"),
        "2": ("Desktop App", "desktop"),
        "3": ("Mobile & Web App", "mobile"),
    }
    dev_title, dev_slug = dev_modes.get(dev_choice, ("Universal (Web, Desktop & Mobile)", "universal"))

    print(f"\n{GREEN}[+] Creating project in: {proj_name}...{RESET}")

    # Create directory tree
    dirs = ["public", "scenes", "shaders", "database", "backend"]
    for d in dirs:
        os.makedirs(os.path.join(proj_name, d), exist_ok=True)

    # 1. Config JSON
    config_data = {
        "name": os.path.basename(os.path.abspath(proj_name)),
        "version": "1.0.0",
        "targetDevice": dev_slug,
        "compilerSettings": {
            "entry": "main.tin",
            "output": "public/app.ir.json"
        }
    }
    with open(os.path.join(proj_name, "tinpyui.config.json"), "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)

    # 2. tinpy.toml
    toml_content = f"""[project]
name = "{proj_name}"
version = "1.0.0"
target_device = "{dev_slug}"

[dev]
port = 8080
watch = true
"""
    with open(os.path.join(proj_name, "tinpy.toml"), "w", encoding="utf-8") as f:
        f.write(toml_content)

    # 3. index.tin & main.tin
    starter_tin_content = f"""component Main():
    AnimatedBackground(effect="quantum-vortex", primaryColor="neon-purple", secondaryColor="neon-cyan"):
        Navbar(padding=20, blur=true):
            Row(align="center", justify="space-between", width="full"):
                Row(align="center", gap=10):
                    Text(text="{proj_name} ({dev_title})", color="neon-cyan", weight="bold")
                Row(gap=30, color="white"):
                    NavLink(text="Dashboard", href="/")
                    NavLink(text="Documentation", href="/docs")
        Section(align="center", paddingY=80, maxWidth=800, justify="center"):
            GradientText(text="{proj_name}", gradient=["neon-cyan", "neon-purple"], size="hero")
            Text(text="Target: {dev_title}", size="large", color="white", weight="bold", marginTop=20)
            Text(text="Hardware-Accelerated UI Engine with Pythonic Indentation DSL.", color="muted", marginTop=10)
            Row(gap=20, align="center", justify="center", marginTop=40):
                Button(text="Get Started", variant="solid", glow="neon-cyan", radius="pill")
                Button(text="⚡ Spring Physics", variant="outline", glow="neon-purple", radius="pill")
"""
    with open(os.path.join(proj_name, "index.tin"), "w", encoding="utf-8") as f:
        f.write(starter_tin_content)

    os.makedirs(os.path.join(proj_name, "src"), exist_ok=True)
    with open(os.path.join(proj_name, "src", "index.tin"), "w", encoding="utf-8") as f:
        f.write(starter_tin_content)

    with open(os.path.join(proj_name, "main.tin"), "w", encoding="utf-8") as f:
        f.write(starter_tin_content)

    # 4. scenes/dashboard.tin
    dash_tin_content = f"""component Dashboard():
    Container(align="center", justify="center", width="full", padding=40):
        GradientText(text="Welcome to {proj_name}", size="hero")
        Spacer(height=20)
        Text(text="Configured Architecture: {dev_title}", size="large", color="white", weight="bold")
        Spacer(height=15)
        Text(text="Hardware-Accelerated UI Engine with Pythonic Indentation DSL.", color="muted")
        Spacer(height=30)
        Row(gap=20, align="center", justify="center"):
            Button(text="📳 Haptic Pulse", variant="solid", glow="neon-cyan", radius="pill")
            Button(text="⚡ Spring Physics", variant="outline", glow="neon-purple", radius="pill")
"""
    with open(os.path.join(proj_name, "scenes", "dashboard.tin"), "w", encoding="utf-8") as f:
        f.write(dash_tin_content)

    # 5. shaders/background.frag
    bg_frag_content = """precision highp float;
uniform float u_time;
uniform vec2 u_resolution;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    float color = 0.5 + 0.5 * sin(u_time + uv.x * 10.0);
    gl_FragColor = vec4(0.0, color, 1.0, 1.0);
}
"""
    with open(os.path.join(proj_name, "shaders", "background.frag"), "w", encoding="utf-8") as f:
        f.write(bg_frag_content)

    # 6. public/index.html Web & WASM Shell
    index_html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{proj_name} — {dev_title}</title>
    <script src="wasm_exec.js"></script>
    <script>
        const go = new Go();
        const _wasmSources = ["tinui_engine.wasm", "app.wasm", "/tinui_engine.wasm", "/app.wasm"];
        let _wasmPromise = null;
        for (const src of _wasmSources) {{
            if (!_wasmPromise) {{
                _wasmPromise = fetch(src).then(res => {{
                    if (!res.ok) throw new Error("Status " + res.status);
                    return res;
                }});
            }} else {{
                _wasmPromise = _wasmPromise.catch(() => fetch(src).then(res => {{
                    if (!res.ok) throw new Error("Status " + res.status);
                    return res;
                }}));
            }}
        }}

        _wasmPromise.then(res => WebAssembly.instantiateStreaming(res, go.importObject)).then((result) => {{
            go.run(result.instance);
            const bootApp = () => {{
                fetch("app.ir.json").then(res => res.text()).then(irString => {{
                    try {{
                        let ret = BootTinUI(irString);
                        if (ret) console.log(ret);
                    }} catch(e) {{
                        console.error("TinUI Boot Error:", e);
                    }}
                }}).catch(e => {{
                    console.error("Failed to fetch app.ir.json:", e);
                }});
            }};
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', bootApp);
            }} else {{
                bootApp();
            }}
        }}).catch((err) => {{
            console.error("WASM Boot Error:", err);
        }});
    </script>
</head>
<body style="margin: 0; padding: 0; background-color: #0a0b10; color: #ffffff; font-family: 'Inter', sans-serif;">
    <div id="tinui-root"></div>
</body>
</html>"""
    with open(os.path.join(proj_name, "public", "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html_content)

    # 7. Copy Wasm Assets if present in package or CWD
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    for asset in ["wasm_exec.js", "tinui_engine.wasm", "app.wasm", "tin-runtime.js"]:
        src_candidates = [
            asset,
            os.path.join(pkg_dir, asset),
            os.path.join(os.path.dirname(pkg_dir), asset)
        ]
        for src in src_candidates:
            if os.path.exists(src):
                try:
                    shutil.copyfile(src, os.path.join(proj_name, "public", asset))
                    break
                except Exception:
                    pass

    # 7. main.py Desktop/Simulator Entrypoint
    main_py_content = f"""import tinpyui as tin

class App(tin.App):
    def __init__(self):
        super().__init__(title="{proj_name} — {dev_title}", width=1280, height=820)
        self.count = tin.Signal(0)

    def build(self):
        with tin.LayoutWindow(title="{proj_name}") as root:
            with tin.Column(width="full", padding=24, gap=16):
                tin.GradientText("🚀 {proj_name}", gradient=["neon-cyan", "neon-purple"], size="hero")
                tin.Badge("Target: {dev_title}", variant="neon-cyan")
                tin.Text(text=lambda: f"Reactive Counter: {{self.count.value}}", color="white")
                with tin.Row(gap=12):
                    tin.Button("Increment Counter", on_click=lambda: self.count.set(self.count.value + 1))
                    tin.Button("📳 Haptic Pulse", on_click=lambda: tin.haptics.vibrate(60))
        return root

if __name__ == "__main__":
    app = App()
    app.run(prompt_target=True)
"""
    with open(os.path.join(proj_name, "main.py"), "w", encoding="utf-8") as f:
        f.write(main_py_content)

    # 8. backend/.gitkeep & database/.gitkeep
    with open(os.path.join(proj_name, "backend", ".gitkeep"), "w") as f: f.write("")
    with open(os.path.join(proj_name, "database", ".gitkeep"), "w") as f: f.write("")

    print(f"\n{GREEN}[+] All set! Your project '{proj_name}' is ready to rock.{RESET}\n")
    print(f"{WHITE}What was created:{RESET}")
    print(f"  - {CYAN}main.tin{RESET}               {DIM}# Your main screen layout & logic{RESET}")
    print(f"  - {CYAN}scenes/{RESET}                 {DIM}# Extra pages and views{RESET}")
    print(f"  - {CYAN}shaders/background.frag{RESET} {DIM}# Smooth hardware background animations{RESET}")
    print(f"  - {CYAN}public/{RESET}                  {DIM}# Web browser assets & icons{RESET}")
    print(f"  - {CYAN}tinpy.toml{RESET}              {DIM}# Project settings & window size{RESET}")
    print(f"\n{WHITE}Next steps:{RESET}")
    print(f"  {CYAN}cd {proj_name}{RESET}")
    print(f"  {CYAN}tinpyui run main.tin{RESET}         {DIM}# Starts your app window immediately{RESET}")
    print(f"  {CYAN}tinpyui run main.tin --web{RESET}   {DIM}# Live preview in your web browser with auto-reload{RESET}\n")


class DefaultDesktopApp(tin.App):
    def __init__(self):
        super().__init__(title="TinPyUI Native Desktop Engine v1.6", width=1280, height=820)
        self.counter = tin.Signal(0)
        self.status = tin.Signal("Native Desktop Hardware Surface Ready (120 FPS)")

    def build(self):
        with tin.LayoutWindow(title="TinPyUI Native Desktop Engine") as root:
            with tin.Row(width="full", padding=24, gap=24):
                with tin.Column(width=260, padding=16, bg="rgba(25, 22, 32, 0.6)", radius=16):
                    tin.Heading("DESKTOP NAVIGATION", size="xs", color="outline")
                    tin.NavItem("Dashboard", icon="dashboard", active=True, on_click=lambda: self.set_status("Dashboard Active"))
                    tin.NavItem("Hardware Telemetry", icon="bolt", on_click=lambda: self.set_status("120 FPS Symplectic Solver Active"))
                    tin.NavItem("Reactive Signals", icon="memory", on_click=lambda: self.set_status("O(1) Signal Cell Registry Verified"))
                    tin.NavItem("Packaging & Build", icon="grid_view", on_click=lambda: self.set_status("PyInstaller/C-FFI Packaging Host Ready"))

                with tin.Column(width="flex", gap=20):
                    tin.GradientText("TinPyUI Native Desktop Application", gradient=["neon-cyan", "neon-purple"], size="hero")
                    tin.Text("Hardware-accelerated native Python desktop GUI app running at sub-millisecond vector render speeds.", size="large")
                    
                    with tin.Row(gap=16):
                        tin.Button("Mutate Reactive Signal", on_click=self.increment)
                        tin.Badge("120 FPS GPU Surface", variant="neon-cyan")
                        tin.Badge("Zero DOM Overhead", variant="neon-purple")

                    tin.Text(text=lambda: f"Live Counter Signal Cell: {self.counter.value}", color="neon-cyan", size="medium")
                    tin.Text(text=lambda: f"● System Status: {self.status.value}", color="muted", size="small")
        return root

    def increment(self):
        self.counter.value += 1
        self.set_status(f"Signal cell mutated to {self.counter.value}")

    def set_status(self, msg: str):
        self.status.value = msg

def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ("init", "create", "new"):
            target_name = sys.argv[2] if len(sys.argv) > 2 else ""
            scaffold_project_interactive(target_name)
            return
        else:
            from .cli import main as cli_main
            cli_main()
            return

    CYAN = "\033[1;36m"
    PURPLE = "\033[1;35m"
    WHITE = "\033[1;97m"
    RESET = "\033[0m"
    print(f"{CYAN}=================================================================={RESET}")
    print(f" {PURPLE}* {WHITE}TinPyUI Flagship Native Desktop Application Launcher{RESET}")
    print(f" {CYAN}* {WHITE}Platform: Hardware-Accelerated Native OS Surface (120 FPS){RESET}")
    print(f"{CYAN}=================================================================={RESET}")
    
    app = DefaultDesktopApp()
    app.run(prompt_target=True)

if __name__ == "__main__":
    main()
