# ⚡ TinPyUI Framework v1.6.0
### *Hardware-Accelerated Omni-Platform UI Engine & Vector Graphics Pipeline*

[![npm](https://img.shields.io/badge/npm-tinpyui-v1.6.0-00f2fe?style=for-the-badge&logo=npm)](https://www.npmjs.com/package/tinpyui)
[![pypi](https://img.shields.io/badge/pypi-tinpyui--ff-v1.6.0-9b51e0?style=for-the-badge&logo=pypi)](https://pypi.org/project/tinpyui-ff/)
[![license](https://img.shields.io/badge/license-MIT-00ff66?style=for-the-badge)](#-license)
[![engine](https://img.shields.io/badge/engine-Hybrid--DOM--WebGL--WebGPU-ff007f?style=for-the-badge)](#-architectural-reality)
[![platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux%20%7C%20Web%20%7C%20Mobile-blueviolet?style=for-the-badge)](#-universal-cross-platform-native-runtime)

**TinPyUI** is an ultra-high-performance, memory-safe, zero-dependency, hardware-accelerated UI application framework. It unites a **Native C-FFI Sub-Millisecond Vector Surface Engine** for Desktop (**Windows DirectX 12, macOS Apple Metal, Linux GTK4/Wayland**) and Mobile (**Android Touch Haptics, iOS Retina**) with a **Hybrid Semantic DOM + WebGL 2.0 / WebGPU Shader Layer** compiled via Go to WebAssembly (`tinui_engine.wasm`).

> 📖 **Comprehensive Technical Manual**: For deep internal architecture, compiler AST specs, and memory diagrams, consult [tinpyui-docs.md](tinpyui-docs.md) and [DATABASE_AND_CONNECTIONS_GUIDE.md](DATABASE_AND_CONNECTIONS_GUIDE.md).

---

## 📑 Table of Contents

1. [✨ Key Highlights](#-key-highlights)
2. [🏛️ Architectural Reality](#-architectural-reality)
3. [📊 Deep Architectural Comparison](#-deep-architectural-comparison)
4. [📦 Installation](#-installation)
5. [💻 Universal Cross-Platform Native Runtime](#-universal-cross-platform-native-runtime)
6. [⚡ Pure Python Declarative UI Framework (`tinpyui`)](#-pure-python-declarative-ui-framework-tinpyui)
7. [📖 Declarative `.tin` Indentation-Based Syntax](#-declarative-tin-indentation-based-syntax)
8. [🧱 Complete Component API Catalog](#-complete-component-api-catalog)
9. [⚡ Reactive State Signals & Symplectic Spring Physics (120 FPS)](#-reactive-state-signals--symplectic-spring-physics-120-fps)
10. [📜 High-Volume Spatial Virtualization (`VirtualStack` & `VirtualList`)](#-high-volume-spatial-virtualization-virtualstack--virtuallist)
11. [🗄️ Universal Reactive Database Suite (`tin.connect`)](#-universal-reactive-database-suite-tinconnect)
    - [PostgreSQL Relational SQL](#1-postgresql-relational-sql)
    - [MongoDB Document NoSQL](#2-mongodb-document-nosql)
    - [SQLite & Ephemeral In-Memory Storage](#3-sqlite--ephemeral-in-memory-storage)
    - [Reactive Live Queries (`LiveQuery`)](#4-reactive-live-queries-livequery)
    - [Persistent Key-Value Store (`tin.use_store`)](#5-persistent-key-value-store-tinuse_store)
    - [Active Record Declarative Models (`@tin.model`)](#6-active-record-declarative-models-tinmodel)
12. [🪄 Low-Code Declarative UI Components (`LiveDataTable` & `AutoCRUD`)](#-low-code-declarative-ui-components-livedatatable--autocrud)
13. [📡 Real-Time Streams & Sockets (`use_socket` & `use_sse`)](#-real-time-streams--sockets-use_socket--use_sse)
14. [🌉 Native OS Platform Channels (`PlatformBridge`)](#-native-os-platform-channels-platformbridge)
15. [🔒 Enterprise Security & Hardware Telemetry Suite](#-enterprise-security--hardware-telemetry-suite)
16. [🧠 Intermediate Representation (IR) Compiler & Dynamic Export (`app.export_ir`)](#-intermediate-representation-ir-compiler--dynamic-export-appexport_ir)
17. [🖥️ How to Compile `.tin` Code on Every OS (Windows, macOS, Linux)](#-how-to-compile-tin-code-on-every-os-windows-macos-linux)
18. [🛠️ CLI Workflows & Dev Server (Hot GLSL Reloading)](#-cli-workflows--dev-server-hot-glsl-reloading)
19. [🚀 Production Deployment & Backend Integration](#-production-deployment--backend-integration)
20. [🌟 Full-Stack Production Master Blueprint](#-full-stack-production-master-blueprint)
21. [📄 License](#-license)

---

## ✨ Key Highlights

- 🚀 **120 FPS Hardware Acceleration**: Sub-millisecond vector graphics rendering via native C-FFI on desktop and dedicated WebGL/WebGPU shaders in browser runtimes.
- 🪶 **100% Zero PIP Dependencies**: Pure Python standard library implementation with native C-FFI (`user32.dll`/`gdi32.dll` on Win32, AppKit on macOS, GTK on Linux). Zero external wheels required.
- 📦 **Microscopic ~2 MB Native Executable**: Zero-bloat C++ shell (`engine_core.cc`) eliminates 150MB+ Electron runtime bloat while retaining modern web rendering capabilities.
- ⚡ **O(1) Reactive State Graph**: Granular signal cells (`tin.Signal`, `tin.State`) with automatic subscriber invalidation and zero virtual DOM tree diffing.
- 🌊 **Symplectic Euler Spring Physics**: True Hooke's Law differential solver ($F = -kx - cv$) for physics-based inertia, gestures, and fluid motion.
- 🗄️ **Universal Multi-Engine Database**: Unified connection factory (`tin.connect`) supporting **PostgreSQL**, **MongoDB**, **SQLite**, and **In-Memory RAM** with dynamic schema evolution and automatic fallback.
- ⚡ **Low-Code Live Components**: 1-line instant full-stack components (`tin.AutoCRUD`, `tin.LiveDataTable`) auto-wired to database mutations.
- 📜 **100,000+ Row Spatial Virtualization**: `tin.VirtualStack` and `tin.VirtualList` deliver sub-millisecond scrolling with zero garbage collection allocations.
- 🔒 **Enterprise-Grade Security Core**: Session binding shields (HMAC), in-memory RAM string masking (`RAMMaskedState`), CSRF guards, and Honeypot decoy generators.
- 📱 **Omni-Platform Topology**: Seamlessly adapts layouts between Desktop 3-Column, Tablet Split-View, and Mobile Single-Column Touch interfaces.

---

## 🏛️ Architectural Reality

TinPyUI rejects the raw canvas-only approach (e.g., Flutter Web CanvasKit) which destroys browser copy-paste, breaks accessibility (a11y), and impairs search engine indexing (SEO).

Instead, TinPyUI employs a **Hybrid Semantic DOM + WebGL Hardware Acceleration Architecture**:

```
+-----------------------------------------------------------------------------------+
|                        TINPYUI DUAL-ENGINE ARCHITECTURE                           |
+-----------------------------------------------------------------------------------+
|  [ .tin Source Code ]  ──▶  [ Go AOT Compiler ]  ──▶  [ Intermediate Rep (IR) ]   |
+-----------------------------------------------------------------------------------+
                                          │
                                          ▼
+-----------------------------------------------------------------------------------+
|                     WASM RUNTIME KERNEL (tinui_engine.wasm)                       |
+-----------------------------------------+-----------------------------------------+
|          LAYER A: DOM ENGINE            |       LAYER B: HARDWARE GPU SHADER      |
|  - Semantic HTML5 Elements              |  - WebGL 2.0 / WebGPU Surfaces          |
|  - Flexbox & Dynamic CSS Tokens         |  - Custom GLSL Fragment Shaders         |
|  - Reactive State & Input Bindings      |  - 120 FPS Cyber Waves & Particle Dust  |
|  - Native A11y & SEO Hydration Shell    |  - Zero CPU Layout Interruptions        |
+-----------------------------------------+-----------------------------------------+
```

---

## 📊 Deep Architectural Comparison

| Feature / Metric | **TinPyUI v1.6** | **React / Next.js** | **Flutter Web (CanvasKit)** | **PyScript / Pyodide** | **Streamlit / Flet** | **Tauri / Electron** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Language DSL** | Pythonic (`.tin`) & Pure Python | JSX / XML | Dart Widgets | Pure Python (CPython) | Python Backend | JS / TS / HTML |
| **Execution** | Go WebAssembly + IR Engine | JS V-DOM Diffing | Skia/Impeller Canvas | 25MB CPython Wasm | Server WebSocket IPC | Native Webview / Node |
| **DOM Strategy** | Direct Semantic DOM + WebGL | Virtual DOM Diffing | Canvas Only (No DOM) | JS Proxy DOM | Server-driven DOM | Native Webview DOM |
| **Accessibility & SEO** | Native DOM + SEO Shell | Native DOM | ❌ None (Raw pixels) | Partial | ❌ None (Dynamic) | Native Desktop |
| **Client Latency** | 0 ms (Local WASM) | 0 ms (Local JS) | 0 ms (Local WASM) | High startup lag | 50-200 ms network lag | 0 ms (Local IPC) |
| **GPU Shader Engine** | Built-in GLSL & WebGL | Requires Three.js | Canvas 2D API | Canvas library | Not supported | WebGL library |
| **Binary Size** | ~2 MB Native Shell | N/A (Web bundle) | 20 MB - 35 MB | 25 MB - 40 MB | Full Python Server | 2 MB (Tauri) / 150 MB (Electron) |
| **PIP Dependencies** | **0 External Packages** | N/A | N/A | Requires Pyodide | Heavy pip dependencies | Heavy npm packages |

---

## 📦 Installation

### 1. NPM Global Compiler CLI
The core ahead-of-time compiler and dev server is distributed globally via NPM:
```bash
npm install -g tinpyui
```
*(Requires Node.js >= 18.0.0)*

### 2. PyPI Python Package (Zero 3rd-Party Dependencies)
For Python developers across Windows, macOS, and Linux:
```bash
pip install tinpyui-ff
```
*Verification*:
```bash
python -m tinpyui
```

---

## 💻 Universal Cross-Platform Native Runtime

TinPyUI embeds lightweight C/C++ host window bindings (`engine_core.cc`) compiling down to a **~2 MB standalone native desktop binary** without bundling Chromium:

```
+-----------------------------------------------------------------------------------+
|                         NATIVE HARDWARE OS ACCELERATION                           |
+-----------------------------------------------------------------------------------+
|  🍎 macOS (Apple Silicon & Intel)  ──▶  Cocoa API + WKWebView (Apple Metal GPU)   |
|  🐧 Linux (Ubuntu, Fedora, Arch)   ──▶  GTK3/GTK4 + WebKitGTK (Wayland / X11)     |
|  🪟 Windows (10 & 11)              ──▶  Win32 HWND + Edge WebView2 (DirectX 12)   |
|  📱 Mobile (Android & iOS)         ──▶  Touch Engine + Haptic Hardware Channels   |
+-----------------------------------------------------------------------------------+
```

### Zero-Bloat Native Compilation Pipeline:
```bash
# macOS (Clang / Metal)
c++ native/engine_core.cc -std=c++11 -framework WebKit -framework Cocoa -o tinui_mac

# Linux (GCC / GTK)
g++ native/engine_core.cc `pkg-config --cflags --libs gtk+-3.0 webkit2gtk-4.0` -o tinui_linux

# Windows (MinGW / DirectX)
g++ native/engine_core.cc -mwindows -ladvapi32 -lole32 -lshell32 -lshlwapi -luser32 -lversion -o tinui_win.exe
```

---

## ⚡ Pure Python Declarative UI Framework (`tinpyui`)

You can build full desktop and web applications directly in pure Python using declarative context managers:

```python
import tinpyui as tin

class CyberDashboard(tin.App):
    def __init__(self):
        super().__init__(title="TinPyUI Cyber Hub", width=1200, height=800)
        self.counter = tin.Signal(0)
        self.status = tin.Signal("Hardware Online (120 FPS)")

    def increment(self):
        self.counter.update(lambda c: c + 1)
        self.status.set(f"Signal mutated to {self.counter.value}")

    def build(self):
        with tin.Window(title="TinPyUI Native Desktop App"):
            with tin.Section(padding=24, align="center"):
                tin.GradientText("Hardware-Accelerated TinPyUI Engine", gradient=["#00f2fe", "#9b51e0"], size="hero")
                tin.Text(text=lambda: f"● {self.status.value}", color="muted")
                tin.Spacer(height=20)
                
                with tin.Card(bg="#141218", radius=16, shadow="cyan", padding=24):
                    tin.Heading("Reactive Telemetry", size="h2")
                    tin.Text(text=lambda: f"Counter Signal: {self.counter.value}", color="#ffffff", size="large")
                    tin.Spacer(height=12)
                    with tin.Row(gap=12):
                        tin.Button("⚡ Increment Signal", on_click=self.increment, variant="primary")
                        tin.Button("📳 Haptic Pulse", on_click=lambda: tin.haptics.vibrate(50), variant="outline")

if __name__ == "__main__":
    CyberDashboard().run()
```

---

## 📖 Declarative `.tin` Indentation-Based Syntax

TinPyUI provides an indentation-based DSL that compiles directly to WebAssembly IR:

### Syntax Rules:
1. **Component Root**: Every file begins with `component Main():` or custom component definitions.
2. **Indentation**: 4 spaces following a colon (`:`). No curly braces `{}` or closing tags.
3. **Typed Props**: Key-value pairs (`key="string"`, `number=20`, `flag=true`, `list=["a", "b"]`).
4. **Data Binding**: Interpolate reactive variables via `{variable_name}` inside strings.

```tin
component Main():
    AnimatedBackground(effect="cyber-wave", primaryColor="neon-purple", secondaryColor="neon-cyan"):
        
        Navbar(padding=20, blur=true):
            Row(align="center", justify="space-between", width="full"):
                Text(text="TinPyUI Cloud Console", color="neon-cyan", weight="bold")
                Row(gap=30, color="white"):
                    NavLink(text="Dashboard", route="/")
                    NavLink(text="Telemetry", route="/telemetry")

        Section(align="center", paddingY=80, maxWidth=900, justify="center"):
            GradientText(text="The Zero-DOM WebAssembly Engine", gradient=["neon-cyan", "neon-purple"], size="hero")
            Text(text="Build high-performance native & web applications with pure Pythonic syntax.", size="large", color="white", marginTop=20)
            
            Spacer(height=30)
            Row(gap=20, align="center", justify="center"):
                Button(text="Launch Cluster", variant="solid", glow="neon-cyan", radius="pill")
                Button(text="System Documentation", variant="outline", radius="pill")
```

---

## 🧱 Complete Component API Catalog

### 1. Structural & Layout Containers
| Component | Primary Properties | Description |
| :--- | :--- | :--- |
| `Section` | `align`, `justify`, `padding`, `paddingY`, `maxWidth`, `minHeight`, `bg`, `radius` | Primary layout block isolating horizontal regions |
| `Container` | `align`, `justify`, `width`, `padding`, `gap`, `animation`, `duration` | General-purpose flexbox container with animation triggers |
| `Row` | `align`, `justify`, `gap`, `width`, `wrap`, `marginTop`, `color` | Horizontal flex row aligning children |
| `Column` | `align`, `justify`, `gap`, `padding`, `bg`, `border`, `radius`, `minWidth`, `maxWidth` | Vertical layout column stack |
| `Card` | `maxWidth`, `padding`, `bg`/`background`, `border`, `radius`, `shadow` | Glassmorphism or solid container card |
| `Grid` | `cols`, `gap`, `width`, `padding` | Multi-column responsive grid layout |
| `Spacer` | `height`, `width` | Fixed dimensional spacing element |
| `Divider` | `color`, `margin` | Visual horizontal rule separator |
| `Surface` | `width`, `height`, `background` | Canvas drawing / shader surface |

### 2. Typography & Visual Badges
| Component | Primary Properties | Description |
| :--- | :--- | :--- |
| `Heading` | `text`, `size` (`"hero"`, `"h1"`, `"h2"`, `"h3"`, `"small"`), `color`, `weight` | Semantic heading element |
| `Text` | `text`, `size` (`"small"`, `"normal"`, `"large"`), `color`, `weight`, `align`, `dataBind` | Paragraph text with dynamic `{state}` interpolation or lambda bindings |
| `GradientText` | `text`, `gradient` (`["#00f2fe", "#9b51e0"]`), `size` | Vibrant linear gradient typography |
| `Badge` | `text`, `variant` (`"neon-cyan"`, `"neon-pink"`), `color` | Compact status tag or telemetry pill |
| `Span` | `text` | Inline text span element |

### 3. Interactive Controls & Forms
| Component | Primary Properties | Description |
| :--- | :--- | :--- |
| `Button` | `text`, `variant` (`"solid"`, `"outline"`, `"primary"`), `glow`, `radius` (`"pill"`, `8`), `on_click`, `action` | Interactive button supporting click animations & glow states |
| `Input` | `placeholder`, `value`, `dataBind`, `width`, `padding`, `bg`, `border`, `radius`, `color` | Two-way data-bound input field |
| `Textarea` | `placeholder`, `value`, `dataBind`, `rows`, `width` | Multiline text entry |
| `Form` | `gap` | Semantic form wrapper |
| `NavLink` | `text`, `route`/`target`, `href` | Cinematic scene transition link |

### 4. Advanced Hardware Shaders & Media
| Component | Primary Properties | Description |
| :--- | :--- | :--- |
| `AnimatedBackground` | `effect` (`"cyber-wave"`, `"particles"`, `"quantum-vortex"`), `primaryColor`, `secondaryColor`, `speed` | Full-screen hardware WebGL canvas effect |
| `Navbar` | `padding`, `blur` (bool), `fixed` (bool), `borderBottom` | Glassmorphic navigation header with backdrop blur |
| `CustomShader` | `fragment_code`, `uniforms` | Raw inline GLSL fragment shader with compile-time validation |
| `Marquee` | `direction`, `speed` | Continuous hardware-accelerated scrolling ticker |
| `Icon` | `name`, `color` | Native vector SVG icon element |
| `Image` | `src`, `url`, `assetPriority` | Optimized image element |

---

## ⚡ Reactive State Signals & Symplectic Spring Physics (120 FPS)

TinPyUI features an $O(1)$ reactive state graph coupled with a **Symplectic Euler differential solver** for physics animations:

```python
import tinpyui as tin

# 1. Reactive Signals (O(1) updates)
count = tin.Signal(0)
count.subscribe(lambda val: print(f"Counter changed: {val}"))
count.update(lambda c: c + 1)

# 2. Symplectic Euler Spring Physics (Hooke's Law: F = -kx - cv)
spring = tin.Spring(tension=180.0, friction=20.0)
spring.target = 250.0  # Set target displacement in pixels

# Step the differential solver (e.g. inside a 120 FPS frame loop)
current_pos = spring.step(delta_time=1.0 / 120.0)
print(f"Spring Position: {current_pos:.2f}px | Velocity: {spring.velocity:.2f}")
```

---

## 📜 High-Volume Spatial Virtualization (`VirtualStack` & `VirtualList`)

TinPyUI v1.6 introduces **Spatial Index Windowing** capable of rendering **100,000+ items** with sub-millisecond scrolling latency and zero garbage collection allocations:

### In `.tin` DSL:
```tin
component VirtualFeed():
    Section(padding=20):
        Heading(text="High-Volume Virtual Feed (100k Rows)", size="h2")
        VirtualStack(itemHeight=52, totalCount=100000):
            Card(padding=12, bg="rgba(20, 20, 30, 0.8)", border="neon-cyan"):
                Text(text="Dynamic Virtual Row Item", color="white")
```

### In Pure Python:
```python
import tinpyui as tin

items = [f"Server Node #{i} - Status: ACTIVE" for i in range(50000)]

with tin.Window(title="Virtualized Cluster View"):
    tin.Heading("50,000 Telemetry Nodes (120 FPS)", size="h1")
    # Only visible nodes within the viewport rect are rendered to the hardware surface
    tin.VirtualList(items=items, item_height=48.0)
```

---

## 🗄️ Universal Reactive Database Suite (`tin.connect`)

TinPyUI provides a unified multi-engine database layer that automatically binds mutations to the 120 FPS UI signal graph:

```
+-----------------------------------------------------------------------------------+
|                        TINPYUI REACTIVE DATA PIPELINE                             |
+-----------------------------------------------------------------------------------+
|  [ Database Mutation ]  ──▶  [ Table / Collection Listener ]                      |
|  (insert / update / delete)                 │                                     |
|                                             ▼                                     |
|  [ UI Render (120 FPS) ] ◀── [ LiveQuery / Reactive Signal ] ◀── [ O(1) Graph ]  |
+-----------------------------------------------------------------------------------+
```

### 1. PostgreSQL Relational SQL
```python
pg_db = tin.connect("postgres://admin:secret@localhost:5432/production_db")
events = pg_db.table("analytics_events")

# Single insert with auto-schema evolution (creates columns dynamically)
row_id = events.insert(event="user_login", user_id="usr_42", duration_ms=18.5, is_active=True)

# Bulk ACID transaction
events.insert_many([
    {"event": "page_view", "user_id": "usr_42", "duration_ms": 12.0},
    {"event": "checkout",  "user_id": "usr_43", "duration_ms": 190.0}
])

# Fluent query building
active_users = (events.where(user_id="usr_42")
                      .gt("duration_ms", 10.0)
                      .order_by("duration_ms", desc=True)
                      .limit(10)
                      .all())
```

### 2. MongoDB Document NoSQL
```python
mongo_db = tin.connect("mongodb://localhost:27017/fleet_db")
devices = mongo_db.collection("devices")

# Insert document
devices.insert_one({
    "name": "Edge-Gateway-01",
    "specs": {"cpu_cores": 16, "ram_gb": 64},
    "tags": ["edge", "gateway", "active"]
})

# Nested dot-notation and operator query
results = devices.find({
    "specs.ram_gb": {"$gte": 32},
    "tags": {"$in": ["gateway"]}
})
```

### 3. SQLite & Ephemeral In-Memory Storage
```python
# Disk SQLite
sqlite_db = tin.connect("sqlite:///fleet_data.db")

# Zero-disk Ephemeral RAM database (Ideal for unit tests & WASM runtime)
ram_db = tin.connect(":memory:")
```

### 4. Reactive Live Queries (`LiveQuery`)
Live queries re-evaluate automatically on any table mutation, updating subscribed UI widgets at 120 FPS with zero manual refresh loops:
```python
orders = pg_db.table("orders")

# Create LiveQuery Signal
active_orders = orders.live_query(status="pending")

# Bind directly to UI
with tin.Window(title="Live Order Queue"):
    tin.VirtualList(items=active_orders, item_height=50.0)
    tin.Button("Add Order", on_click=lambda: orders.insert(status="pending", item="Cyber Deck"))
```

### 5. Persistent Key-Value Store (`tin.use_store`)
Thread-safe disk-backed key-value store with reactive signal synchronization:
```python
store = tin.use_store("app_config.db", table="preferences")
store.set("theme", "cyber-dark")

# Mutating the signal automatically persists value to disk!
theme_signal = store.signal("theme", default="cyber-dark")
theme_signal.value = "neon-matrix"
```

### 6. Active Record Declarative Models (`@tin.model`)
```python
@tin.model
class DeviceNode:
    name: str
    platform: str
    fps_target: int = 120
    is_online: bool = True

node = DeviceNode.create(name="MacBook-Pro-M3", platform="macOS (Metal)")
all_online = DeviceNode.where(is_online=True).all()
live_nodes = DeviceNode.live_query(is_online=True)
```

---

## 🪄 Low-Code Declarative UI Components (`LiveDataTable` & `AutoCRUD`)

Instantly generate fully functional reactive data grids and complete administrative dashboards in a single line of code:

### 1. `tin.LiveDataTable`
Auto-discovers schema headers and binds to real-time table queries:
```python
tin.LiveDataTable(pg_db.table("analytics_events"))
tin.LiveDataTable(mongo_db.collection("devices"), columns=["name", "platform", "fps_target"])
```

### 2. `tin.AutoCRUD`
Generates a complete management interface with Search, Add Form, Interactive Table, and Delete Actions:
```python
tin.AutoCRUD(sqlite_db.table("devices"), title="Fleet Device Management Dashboard")
```

---

## 📡 Real-Time Streams & Sockets (`use_socket` & `use_sse`)

```python
import tinpyui as tin

# 1. Bi-directional WebSockets with reactive status & message signals
socket = tin.use_socket("wss://stream.telemetry.io/v1")

with tin.Window(title="Real-Time Stream"):
    tin.Text(text=lambda: f"Socket Status: {socket.status.value.upper()}")
    tin.Text(text=lambda: f"Telemetry Packet: {socket.message.value}", color="neon-cyan")
    tin.Button("Send Ping", on_click=lambda: socket.send("PING_HEARTBEAT"))

# 2. Server-Sent Events (SSE) Stream
stream_signal = tin.use_sse("https://events.example.com/live_feed")
tin.Text(text=stream_signal, color="neon-pink")
```

---

## 🌉 Native OS Platform Channels (`PlatformBridge`)

TinPyUI provides zero-copy C-FFI channels into native host OS dialogs, clipboard, and hardware haptics:

```python
import tinpyui as tin

# 1. Native File Dialogs
selected_file = tin.PlatformBridge.open_file_dialog()
save_destination = tin.PlatformBridge.save_file_dialog()

# 2. Desktop System Toast Notifications
tin.PlatformBridge.show_notification(title="Cluster Build", message="Compilation finished in 1.2ms")

# 3. Mobile / Touch Device Haptics
tin.PlatformBridge.vibrate(pattern_ms=60)
tin.haptics.vibrate(60)

# 4. OS Clipboard Sync
tin.PlatformBridge.copy_clipboard("tinpyui_v16_auth_token_8892")

# 5. System Theme Query
current_theme = tin.PlatformBridge.get_system_theme() # "dark" | "light"
```

---

## 🔒 Enterprise Security & Hardware Telemetry Suite

TinPyUI is engineered with security-first constraints:

1. **In-Memory RAM Masking**: `tin.RAMMaskedState` and `tin.EncryptedState` protect sensitive passwords and API tokens in RAM against memory scraping.
2. **Session Binding Guard**: High-entropy HMAC-SHA256 signatures validate session authenticity against replay attacks.
3. **Decoy Network Traffic**: `tin.HoneypotAPI.start_decoy_traffic()` generates synthetic background traffic to confound network inspection.
4. **Hardware Fingerprinting**: `tin.Security.get_device_fingerprint()` generates unique hardware identification hashes.
5. **Live Performance Telemetry**: `tin.PerformanceMonitor` measures 120 FPS frame latency, render bottlenecks, and memory usage.
6. **Compile-Time GLSL Validator**: `glsl_validator.go` scans shader ASTs ahead-of-time to prevent GPU memory crashes and infinite loops.
7. **Panic-Proof WASM Boundary**: The WebAssembly runtime wraps rendering in panic-recovery middleware, guaranteeing that runtime errors never crash the host web page.

---

## 🧠 Intermediate Representation (IR) Compiler & Dynamic Export (`app.export_ir`)

### Dynamic Python to WebAssembly Export
Compile pure Python UI trees directly into static Intermediate Representation JSON (`app.ir.json`) for serverless CDN hosting:

```python
import tinpyui as tin

app = tin.Window(title="WASM Edge Application", width=1280, height=800)
with app:
    with tin.Section(padding=24):
        tin.Heading("Compiled Edge App", size="hero")
        tin.GradientText("Hardware-Accelerated WebAssembly", gradient=["#00f2fe", "#9b51e0"])
        tin.Button("Launch Cluster", variant="primary")

# Exports deterministic IR blueprint to public/ distribution folder
app.export_ir("public/app.ir.json")
```

### Generated `app.ir.json` Schema:
```json
{
  "title": "WASM Edge Application",
  "width": 1280,
  "height": 800,
  "bg_color": "#0D0D10",
  "root": {
    "tag": "Window",
    "props": {"title": "WASM Edge Application"},
    "children": [
      {
        "tag": "Section",
        "props": {"padding": 24},
        "children": [
          {"tag": "Heading", "props": {"text": "Compiled Edge App", "size": "hero"}, "children": []},
          {"tag": "GradientText", "props": {"text": "Hardware-Accelerated WebAssembly"}, "children": []},
          {"tag": "Button", "props": {"text": "Launch Cluster", "variant": "primary"}, "children": []}
        ]
      }
    ]
  }
}
```

## 🖥️ How to Compile `.tin` Code on Every OS (Windows, macOS, Linux)

TinPyUI source files (`.tin`) compile into a deterministic Intermediate Representation (`.ir.json`) and optional pre-rendered static HTML hydration shells (`.html`).

```
+-----------------------------------------------------------------------------------+
|                        CROSS-PLATFORM COMPILATION PIPELINE                        |
+-----------------------------------------------------------------------------------+
|  [ index.tin Source ]                                                             |
|           │                                                                       |
|           ▼                                                                       |
|  [ TinPyUI Go / NPM Compiler ] ──(Windows / macOS / Linux)                        |
|           │                                                                       |
|           ├──▶ [ index.ir.json / app.ir.json ]  ──▶ Consumed by tinui_engine.wasm |
|           └──▶ [ index.html ] (with --hydrate) ──▶ SEO Static Pre-Rendered DOM    |
+-----------------------------------------------------------------------------------+
```

---

### 🪟 1. Compiling on Windows (10 & 11)

Open **PowerShell**, **Command Prompt (CMD)**, or **Windows Terminal**:

#### Option A: Using the Compiled Binary (`tinui.exe`)
```powershell
# Standard compilation -> outputs index.ir.json
.\tinui.exe compile index.tin

# Compilation with static SEO HTML hydration -> outputs index.ir.json & index.html
.\tinui.exe compile index.tin --hydrate

# Live Dev Server with Hot Reload on http://localhost:8080
.\tinui.exe dev index.tin
```

#### Option B: Using Go Directly from Source
```powershell
go run main.go compile index.tin
go run main.go compile index.tin --hydrate
go run main.go dev index.tin
```

#### Option C: Using the Global NPM CLI
```powershell
npm install -g tinpyui
tinpyui compile index.tin
tinpyui compile index.tin --hydrate
```

#### Building the Windows Compiler Binary from Source:
```powershell
go build -o tinui.exe .
```

---

### 🍎 2. Compiling on macOS (Apple Silicon M1/M2/M3/M4 & Intel)

Open **Terminal** (Zsh or Bash):

#### Option A: Using the Standalone Binary (`tinui`)
```bash
# Ensure execution permissions
chmod +x ./tinui

# Standard compilation -> outputs index.ir.json
./tinui compile index.tin

# Compilation with static SEO HTML hydration -> outputs index.ir.json & index.html
./tinui compile index.tin --hydrate

# Live Dev Server with Hot Reload on http://localhost:8080
./tinui dev index.tin
```

#### Option B: Using Go Directly from Source
```bash
go run main.go compile index.tin
go run main.go compile index.tin --hydrate
go run main.go dev index.tin
```

#### Option C: Using the Global NPM CLI
```bash
npm install -g tinpyui
tinpyui compile index.tin
tinpyui compile index.tin --hydrate
```

#### Building the macOS Compiler Binary from Source:
```bash
go build -o tinui .
chmod +x tinui
```

---

### 🐧 3. Compiling on Linux (Ubuntu, Debian, Fedora, Arch, Alpine)

Open your preferred Linux **terminal**:

#### Option A: Using the Standalone Binary (`tinui`)
```bash
# Ensure execution permissions
chmod +x ./tinui

# Standard compilation -> outputs index.ir.json
./tinui compile index.tin

# Compilation with static SEO HTML hydration -> outputs index.ir.json & index.html
./tinui compile index.tin --hydrate

# Live Dev Server with Hot Reload on http://localhost:8080
./tinui dev index.tin
```

#### Option B: Using Go Directly from Source
```bash
go run main.go compile index.tin
go run main.go compile index.tin --hydrate
go run main.go dev index.tin
```

#### Option C: Using the Global NPM CLI
```bash
npm install -g tinpyui
tinpyui compile index.tin
tinpyui compile index.tin --hydrate
```

#### Building the Linux Compiler Binary from Source:
```bash
go build -o tinui .
chmod +x tinui
```

---

### 🌐 4. Compiling the WebAssembly Engine (`tinui_engine.wasm`) on Any OS

To rebuild the core WebAssembly runtime from Go source:

#### On Windows (PowerShell):
```powershell
$env:GOOS="js"; $env:GOARCH="wasm"; go build -ldflags="-s -w" -o tinui_engine.wasm ./wasm_engine
```

#### On macOS & Linux (Bash / Zsh):
```bash
GOOS=js GOARCH=wasm go build -ldflags="-s -w" -o tinui_engine.wasm ./wasm_engine
```

---

### ⚙️ 5. Compiler Flags & Configuration Reference

| Flag / Setting | Command Syntax | Description |
| :--- | :--- | :--- |
| **Standard Compile** | `tinui compile <file.tin>` | Parses `.tin` and emits deterministic `.ir.json` AST. |
| **Static Hydration** | `tinui compile <file.tin> --hydrate` | Generates `.ir.json` plus pre-rendered static `index.html` SEO shell. |
| **Live Dev Server** | `tinui dev <file.tin>` | Starts hot-reloading dev server on `http://localhost:8080`. |
| **Native Desktop** | `tinui desktop <file.tin>` | Compiles and opens native desktop UI window. |
| **Project Init** | `tinui init` | Scaffolds standard workspace with `index.tin`, config, and Wasm files. |

#### Customizing Output Paths via `tinpyui.config.json`:
```json
{
  "compilerSettings": {
    "output": "public/app.ir.json",
    "enableHydration": true,
    "minify": true
  }
}
```

---

## 🛠️ CLI Workflows & Dev Server (Hot GLSL Reloading)

```bash
# 1. Scaffold a new cyber application
tinpy create my-cyber-app
cd my-cyber-app

# 2. Launch live development server with Hot GLSL Reloading (HGR) on http://localhost:8080
tinpy dev

# 3. Compile .tin source to Intermediate Representation
tinpy compile src/index.tin

# 4. Compile with static SEO HTML hydration shell
tinpy compile src/index.tin --hydrate

# 5. Launch native desktop window
tinpy desktop src/index.tin

# 6. Run security vulnerability scanner
python cli/security_scanner.py
```

---

## 🚀 Production Deployment & Backend Integration

### 1. Python Flask / FastAPI Integration
TinPyUI apps compile into static assets (`index.html`, `tin-runtime.js`, `wasm_exec.js`, `tinui_engine.wasm`, `app.ir.json`) that can be hosted on any web server:

```python
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='public')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    print("[TinPyUI] Serving on http://localhost:5000")
    app.run(port=5000)
```

### 2. Static CDN Hosting (Vercel, Cloudflare Pages, Netlify, AWS S3)
Deploy the `public/` directory directly to any static web host. Ensure that your web server serves `.wasm` files with the `Content-Type: application/wasm` MIME type header.

---

## 🌟 Full-Stack Production Master Blueprint

Below is an end-to-end production script combining **PostgreSQL/MongoDB connectivity**, **WebSocket streams**, **Spring physics**, **1-Line AutoCRUD**, and **Hardware Haptics**:

```python
import tinpyui as tin

# 1. Connect to Database with dynamic schema creation
db = tin.connect("sqlite:///production_fleet.db")
devices = db.table("devices")

# 2. Real-Time Telemetry Socket
telemetry_ws = tin.use_socket("wss://echo.websocket.events")

# 3. Persistent Settings Store
settings = tin.use_store("user_settings.db")
theme_signal = settings.signal("theme", default="cyber-dark")

# 4. Symplectic Euler Spring Solver (120 FPS)
spring = tin.Spring(tension=180.0, friction=20.0)
spring_pos = tin.Signal(0.0)

def step_physics():
    spring.target = 150.0 if spring.target == 0.0 else 0.0
    spring_pos.set(round(spring.step(1.0 / 120.0), 2))
    tin.PlatformBridge.vibrate(40)

# 5. Declarative UI Window
app = tin.Window(title="Omni-Platform Enterprise Console", width=1400, height=880)
with app:
    with tin.Row(padding=20, gap=20):
        # Left Panel: Telemetry & Controls
        with tin.Column(width=420, gap=16):
            tin.GradientText("CYBER TELEMETRY", gradient=["neon-cyan", "neon-purple"], size="h2")
            
            with tin.Card(padding=16, bg="rgba(18, 22, 34, 0.8)", radius=12):
                tin.Text(text=lambda: f"● Socket Status: {telemetry_ws.status.value.upper()}", color="neon-cyan")
                tin.Text(text=lambda: f"Feed: {telemetry_ws.message.value or 'Awaiting stream...'}")
                tin.Spacer(height=10)
                tin.Button("Send Heartbeat", on_click=lambda: telemetry_ws.send("PING_TELEMETRY"))

            with tin.Card(padding=16, bg="rgba(24, 20, 32, 0.8)", radius=12):
                tin.Heading("Spring Physics Simulator (120 FPS)", size="small")
                tin.Text(text=lambda: f"Displacement: {spring_pos.value} px", color="neon-pink")
                tin.Spacer(height=8)
                tin.Button("🚀 Trigger Spring Step", on_click=step_physics, variant="primary")

        # Right Panel: 1-Line Reactive AutoCRUD Dashboard
        with tin.Column(width="flex", gap=16):
            tin.AutoCRUD(devices, title="Live Fleet Device Management")

if __name__ == "__main__":
    tin.run(app)
```

---

## 📄 License

MIT License © 2026 Barathanandh
