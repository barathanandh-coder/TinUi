# TinPyUI Framework v1.6.0

[![npm](https://img.shields.io/badge/npm-tinpyui-v1.6.0-cyan)](https://www.npmjs.com/package/tinpyui)
[![pypi](https://img.shields.io/badge/pypi-tinpyui--ff-v1.6.0-blue)](https://pypi.org/project/tinpyui-ff/)
[![license](https://img.shields.io/badge/license-MIT-green)](#license)
[![engine](https://img.shields.io/badge/engine-Hybrid--DOM--WebGL--GPU-purple)](#architecture)
[![docs](https://img.shields.io/badge/manual-tinpyui--docs.md-orange)](tinpyui-docs.md)

TinPyUI is a memory-safe, zero-dependency, hardware-accelerated UI application engine. It combines a **Native C-FFI Vector Surface Engine** for Desktop (Windows, macOS, Linux) with a **Hybrid DOM UI Layout + WebGL GPU Shader Layer** compiled via Go to WebAssembly (`tinui_engine.wasm`).

> 📖 **Complete Technical Handbook**: For the comprehensive, book-like architecture and reference guide, read [tinpyui-docs.md](tinpyui-docs.md).

---

## 🏛️ The Architectural Reality: How TinPyUI Differs

TinPyUI is **not** a raw canvas blitter (which breaks browser accessibility, copy-paste, and SEO). Instead, it uses **Direct IR DOM Generation** for layout and typography coupled with **Hardware-Accelerated WebGL Canvases** for background shaders and particles:

| Feature / Metric | **TinPyUI v1.6** | **React / Next.js** | **Flutter Web (CanvasKit)** | **PyScript / Pyodide** | **Streamlit / Flet** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Language DSL** | Pythonic Indentation (`.tin`) | JSX / XML | Dart Widgets | CPython in Wasm | Python Backend |
| **Execution** | Go WebAssembly + IR Engine | JS V-DOM Diffing | Raw Canvas Blit | 25MB CPython runtime | Server WebSocket IPC |
| **DOM Model** | Direct Semantic DOM + WebGL | Virtual DOM | Canvas Only (No DOM) | JS Proxy DOM | Server-driven DOM |
| **Accessibility & SEO** | Native DOM + SEO Shell | Native DOM | ❌ None (Raw pixels) | Partial | ❌ None (Dynamic) |
| **Client Latency** | 0 ms (Local WASM) | 0 ms (Local JS) | 0 ms (Local WASM) | High startup lag | 50-200 ms network lag |
| **GPU Shaders** | Built-in GLSL & WebGL | Requires Three.js | Canvas drawing API | Canvas library required | Not supported |

---

## 📦 Installation

### 1. NPM Package (Universal CLI)
The core TinPyUI compiler CLI is distributed globally via NPM. Install it with:

```bash
npm install -g tinpyui
```
*Note: Requires Node.js (>= 18.0.0).*

### 2. PyPI Package (Python Ecosystem -- 0 Third-Party Dependencies)
For Python developers (Requires 0 external pip packages):

```bash
pip install tinpyui-ff
```

---

## ⚡ TinPyUI Flagship Native Desktop Application Framework

**TinPyUI** (`import tinpyui as tin`) is a flagship universal Python desktop GUI application framework built to surpass Tkinter in speed, modern cyber aesthetics (linear gradients, glassmorphism, glowing neon borders, pill-rounded buttons), and cross-platform portability (**Windows, macOS, Linux**).

### Key Features
- 🚀 **Hardware-Accelerated Surface**: Sub-millisecond vector graphics rendering engine using native C-FFI.
- 🎨 **Modern Cyber Aesthetics**: Linear gradients, glassmorphism blur, neon glow borders, pill-rounded buttons, animated shader backgrounds.
- ⚡ **O(1) Reactive Signal System**: Automatic UI binding with `tin.State(value)` / `tin.Signal(value)`.
- 💻 **100% Zero PIP Dependencies**: Uses pure Python stdlib + C-FFI (`user32.dll`/`gdi32.dll` on Win32, AppKit on macOS, GTK on Linux).
- 🔒 **Enterprise Security Suite**: `SessionBindingGuard` (HMAC signatures), `RAMMaskedState` (in-memory string masking), and `CSRFGuard`.
- 📈 **Live Telemetry Monitoring**: Dynamic FPS and render latency sampling via `tin.PerformanceMonitor`.

### Quickstart Example
```python
import tinpyui as tin

class MyApp(tin.App):
    def __init__(self):
        super().__init__(title="TinPyUI Native Desktop App", width=1100, height=750)
        self.count = tin.Signal(0)

    def build(self):
        with tin.Window(title="TinPyUI Native Desktop App"):
            with tin.Card(bg="#141218", radius=16, shadow="cyan"):
                tin.GradientText("Hardware-Accelerated TinPyUI Desktop Engine", gradient=["#00ffff", "#cfbcff"])
                tin.Text(text=lambda: f"Counter Signal Value: {self.count.value}", color="#ffffff")
                tin.Button("Increment Counter", on_click=self.increment, variant="primary")

    def increment(self):
        self.count.value += 1

if __name__ == "__main__":
    MyApp().run()
```

### Launching Desktop Applications
Run the native desktop application launcher:

```bash
python main.py
```
Or launch via the package CLI:
```bash
python -m tinpyui
```

---

## 🌐 Universal Cross-Platform C++ Core (`engine_core.cc`)

TinPyUI achieves cross-platform desktop native packaging using a **C/C++ Abstraction Layer** (`webview.h`). This compiles down into a microscopic **2 MB to 3 MB** native desktop executable without bundling bulky browser runtimes.

### Native OS GPU Engine Mapping
- 🍎 **macOS (Apple Silicon & Intel)**: Cocoa API + **WKWebView** (Apple **Metal** GPU rendering engine).
- 🐧 **Linux (Ubuntu, Fedora, Arch)**: GTK3/GTK4 + **WebKitGTK** (X11 / Wayland native window integration).
- 🪟 **Windows (10 & 11)**: Win32 API (`HWND`) + Microsoft **Edge WebView2** (**DirectX 12** hardware acceleration at 120 FPS).

### Zero-Bloat Cross-Platform Compiler Pipeline
```bash
# macOS (Clang)
c++ engine_core.cc -std=c++11 -framework WebKit -framework Cocoa -o tinui_mac

# Linux (GCC)
g++ engine_core.cc `pkg-config --cflags --libs gtk+-3.0 webkit2gtk-4.0` -o tinui_linux

# Windows (MinGW/GCC)
g++ engine_core.cc -mwindows -ladvapi32 -lole32 -lshell32 -lshlwapi -luser32 -lversion -o tinui_win.exe
```

---

## 🚀 Developer Workflow

### Step 1: Initialize a New Workspace
```bash
tinpyui init my-cyber-app
cd my-cyber-app
```
This scaffolds your `src/index.tin` configuration layout, `tinpyui.config.json`, static Wasm bootloader files, and an optional Flask `app.py` server.

### Step 2: Write Your UI
Edit `src/index.tin` using Pythonic indentation rules (`component Main():`), invoking components like `AnimatedBackground`, `Navbar`, `Row`, `GradientText`, and `Button`.

### Step 3: Compile the Layout
```bash
tinpyui compile src/index.tin
```
The internal compiler parses your `.tin` file, validates indentation and token schemas, converts component hierarchies into optimized IR, and outputs `public/app.ir.json`.

### Step 4: Launch the Dev Server
```bash
tinpyui serve
```
Or start the dev server directly with hot reloading:
```bash
tinpyui dev src/index.tin
```

---

## 🧠 Architecture: The Zero-DOM Wasm Engine

When the TinPyUI WebAssembly runtime initializes in the browser:
- **State Hydration**: Hydrates a `StateRegistry` tracking reactive variables in Wasm linear memory.
- **Dirty Bitmaps**: Allocates a 64-bit Dirty Bitmap tracking modified layout nodes.
- **Event Dispatching**: When user interactions occur (clicks, inputs), the JS bridge invokes `TinUIDispatch` or `TinUIMutateState` directly in Wasm.
- **Microsecond Pointer Swaps**: The Wasm engine updates memory and flushes surgical patches (`flushPatches()`) in $O(1)$ time without traversing virtual DOM trees.

---

## 📖 Detailed `.tin` Pythonic Syntax Guide

TinPyUI uses an indentation-based, Pythonic grammar ending with colons (`:`). **Do not use curly braces `{}` for UI structure.**

### Grammar & Syntax Rules
1. **Root Block**: Every file **must** begin with a `component Main():` block.
2. **Components**: Component names must strictly use PascalCase (e.g. `Section`, `GradientText`, `Button`).
3. **Properties (Props)**: Passed inside parentheses using `key="value"` or `key=value` pairs separated by commas.
   - **Strings**: `"Submit"`, `"neon-cyan"`
   - **Numbers**: `20`, `600`, `120`
   - **Booleans**: `true`, `false`
   - **Arrays**: `["neon-cyan", "neon-purple"]`
4. **Nesting & Indentation**: Child components are placed on new lines, indented 4 spaces under parent components that end with a colon (`:`).

#### Official Syntax Blueprint:
```text
component Main():
    Section(paddingY=40, align="center"):
        Heading(text="Dashboard", color="white", size="h1")
        Text(text="Welcome back to your workspace.", size="large")
```

---

## 📐 Strict Layout Constraints (100% Width Rule)

By default, block-level interactive components (like `Form`, `Input`, and `Button`) aggressively consume **100% of available container width**.

### Layout Rules to Avoid Visual Stretching:
- **Wrap in Containers**: Never place inputs or buttons directly under `Main()` without a wrapper.
- **Use `Card` & `maxWidth`**: Place forms and interactive elements inside a `Card` or `Section` with an explicit `maxWidth` (e.g. `maxWidth=600`).
- **Horizontal Grouping**: Wrap side-by-side elements inside a `Row` component.

#### Correct Constraint Blueprint:
```text
component Main():
    Section(align="center", justify="center"):
        Card(maxWidth=600, padding=30):
            Form(gap=15):
                Input(placeholder="Email Address", width="full")
                Input(placeholder="Password", width="full")
                Button(text="Login", width="full", variant="primary")
```

---

## 🧩 Component API Reference

### 1. Structural Containers
- **`Section(align: string, justify: string, paddingY: number, paddingBottom: number, maxWidth: number)`**  
  Primary layout wrapper isolating horizontal content blocks.
- **`Card(maxWidth: number, padding: number, background: string, border: string, radius: number, shadow: string)`**  
  Glassmorphism / solid container for forms, features, and cards.
- **`Row(gap: number, align: string, justify: string, width: string, marginTop: number)`**  
  Aligns child components horizontally using flex mechanics.
- **`Form(gap: number)`**  
  Vertical layout stack for form inputs and action buttons.

### 2. Typography
- **`Text(text: string, size: string, color: string, weight: string, marginTop: number, marginBottom: number)`**  
  Standard text element. Sizes: `"small"`, `"normal"`, `"large"`.
- **`Heading(text: string, color: string, size: string)`**  
  Heading typography. Sizes: `"h1"`, `"h2"`, `"h3"`.
- **`GradientText(text: string, gradient: ["string", "string"], size: string)`**  
  Displays vibrant linear gradient text for headers and hero sections.

### 3. Interactive Elements
- **`Button(text: string, variant: string, glow: string, radius: string | number, width: string, link: string)`**  
  Variants: `"solid"`, `"outline"`, `"primary"`. Radius: number (`8`) or string (`"pill"`).
- **`Input(value: string, placeholder: string, width: string, border: string)`**  
  Interactive data entry field.
- **`NavLink(text: string, target: string)`**  
  Navigation link anchoring to target sections.

### 4. Advanced Visual & Animated Components
- **`AnimatedBackground(effect: string, primaryColor: string, secondaryColor: string, speed: string)`**  
  Full-viewport canvas effects (`"cyber-wave"`, `"cyber-grid"`, `"particles"`).
- **`Navbar(padding: number, blur: boolean, borderBottom: string)`**  
  Fixed header bar supporting background blur glassmorphism (`blur=true`).
- **`Icon(name: string, color: string)`**  
  Renders native SVG icons directly inside the component graph.

---

## 🎨 Cyberpunk Design System & Color Tokens

TinPyUI ships with an ultra-modern dark-mode-first aesthetic:

- **Backgrounds**: `"dark-core"` (`#0a0b10`), `"dark-glass"` (`rgba(18,19,28,0.7)`).
- **Neon Accents**: `"neon-cyan"` (`#00f2fe`), `"neon-purple"` (`#9b51e0`), `"neon-pink"` (`#ff007f`).
- **Typography Tokens**: `"white"`, `"muted"`.

---

## 🚀 Complete Blueprint Example

Below is the production-ready reference blueprint for TinPyUI v1.6.0 applications:

```text
component Main():
    AnimatedBackground(effect="cyber-wave", primaryColor="neon-purple", secondaryColor="neon-cyan"):
        
        Navbar(padding=20, blur=true):
            Row(align="center", justify="space-between", width="full"):
                Text(text="TinPyUI App", color="neon-cyan", weight="bold")
                Row(gap=30, color="white"):
                    NavLink(text="Features")
                    NavLink(text="Docs")

        Section(align="center", paddingY=100, maxWidth=800, justify="center"):
            GradientText(text="The Zero-DOM Wasm Engine", gradient=["neon-cyan", "neon-purple"], size="hero")
            Text(text="Build high-performance web applications with Pythonic DSL.", size="large", color="white", marginTop=20)
            
            Row(gap=20, align="center", justify="center", marginTop=40):
                Button(text="Get Started", variant="solid", glow="neon-cyan", radius="pill")
                Button(text="Documentation", variant="outline", radius="pill")
```

---

## 📄 License
MIT License © Barathanandh
