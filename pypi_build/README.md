# ⚡ TinPyUI (`tinpyui-ff`) v1.6.0
### *Hardware-Accelerated Omni-Platform UI Engine & Vector Graphics Pipeline*

[![pypi](https://img.shields.io/badge/pypi-tinpyui--ff-v1.6.0-9b51e0?style=for-the-badge&logo=pypi)](https://pypi.org/project/tinpyui-ff/)
[![license](https://img.shields.io/badge/license-MIT-00ff66?style=for-the-badge)](https://github.com/barathanandh-coder/tinui)
[![platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20macOS%20%7C%20Linux%20%7C%20Web%20%7C%20Mobile-blueviolet?style=for-the-badge)](https://github.com/barathanandh-coder/tinui)

Official zero-dependency Python distribution for **TinPyUI v1.6.0** — the memory-safe, hardware-accelerated UI application framework.

---

## 🚀 Key Highlights

- 🪶 **100% Zero PIP Dependencies**: Built using pure Python standard library + native C-FFI (`user32.dll`/`gdi32.dll` on Win32, AppKit on macOS, GTK on Linux). Zero external wheels required.
- ⚡ **120 FPS Reactive UI Engine**: Sub-millisecond vector rendering and O(1) state signal cells (`tin.Signal`, `tin.State`).
- 🗄️ **Universal Reactive Database Suite**: Unified `tin.connect()` factory for **PostgreSQL**, **MongoDB**, **SQLite**, and **In-Memory RAM** with automatic reactive UI updates at 120 FPS.
- 🪄 **Low-Code Components**: 1-line full-stack components (`tin.AutoCRUD`, `tin.LiveDataTable`) auto-wired to live database queries.
- 🌊 **Symplectic Spring Physics**: Hooke's Law differential solver ($F = -kx - cv$) for physics-based gestures and inertia.
- 📜 **100k Row Spatial Virtualization**: `tin.VirtualList` and `tin.VirtualStack` with sub-millisecond scrolling latency.
- 📡 **Real-Time Streams**: First-class reactive WebSockets (`tin.use_socket`) and Server-Sent Events (`tin.use_sse`).
- 🌉 **Native OS Hardware Bridge**: Zero-copy C-FFI dialogs, desktop toast alerts, haptic vibration, and clipboard sync (`tin.PlatformBridge`).
- 🧠 **Dynamic WASM IR Export**: `app.export_ir("public/app.ir.json")` compiles pure Python UI trees directly into static WebAssembly IR.

---

## 📦 Installation

```bash
pip install tinpyui-ff
```

Launch the package CLI test:
```bash
python -m tinpyui
```

---

## ⚡ Quickstart: Pure Python Declarative UI

```python
import tinpyui as tin

class CyberApp(tin.App):
    def __init__(self):
        super().__init__(title="TinPyUI Native Desktop", width=1100, height=750)
        self.count = tin.Signal(0)

    def increment(self):
        self.count.update(lambda c: c + 1)

    def build(self):
        with tin.Window(title="TinPyUI Native Desktop App"):
            with tin.Section(padding=24, align="center"):
                tin.GradientText("Hardware-Accelerated TinPyUI Desktop Engine", gradient=["#00f2fe", "#9b51e0"], size="hero")
                tin.Spacer(height=16)
                
                with tin.Card(bg="#141218", radius=16, shadow="cyan", padding=24):
                    tin.Heading("Reactive Counter Signal", size="h2")
                    tin.Text(text=lambda: f"Counter Value: {self.count.value}", color="#ffffff", size="large")
                    tin.Spacer(height=12)
                    with tin.Row(gap=12):
                        tin.Button("⚡ Increment Signal", on_click=self.increment, variant="primary")
                        tin.Button("📳 Haptic Pulse", on_click=lambda: tin.haptics.vibrate(50), variant="outline")

if __name__ == "__main__":
    CyberApp().run()
```

---

## 🗄️ Universal Database & Live Low-Code CRUD

```python
import tinpyui as tin

# 1. Connect to PostgreSQL, MongoDB, SQLite, or In-Memory RAM
db = tin.connect("sqlite:///production.db")
devices = db.table("devices")

# 2. 1-Line Reactive Live Data Table or Full AutoCRUD Dashboard
app = tin.Window(title="Fleet Management Console", width=1280, height=800)
with app:
    tin.AutoCRUD(devices, title="Live Fleet Device Manager")

if __name__ == "__main__":
    tin.run(app)
```

---

## 📡 Real-Time WebSockets & Native OS Channels

```python
import tinpyui as tin

# Reactive WebSocket Stream
ws = tin.use_socket("wss://echo.websocket.events")

with tin.Window(title="Real-Time Stream"):
    tin.Text(text=lambda: f"Status: {ws.status.value.upper()}")
    tin.Text(text=lambda: f"Payload: {ws.message.value}")
    tin.Button("Send Ping", on_click=lambda: ws.send("PING"))
    
    # Native OS File Dialog & Toast Alerts
    tin.Button("Save File", on_click=lambda: tin.PlatformBridge.save_file_dialog())
```

---

## 🌐 Dynamic WebAssembly IR Compilation (`app.export_ir`)

```python
import tinpyui as tin

app = tin.Window(title="WASM Edge App", width=1280, height=800)
with app:
    tin.GradientText("Hardware-Accelerated WebAssembly", gradient=["#00f2fe", "#9b51e0"])
    tin.Button("Launch Cluster", variant="primary")

# Exports deterministic IR blueprint for static CDN / Wasm hosting
app.export_ir("public/app.ir.json")
```

---

## 📄 Repository & Documentation
For full documentation, `.tin` grammar specs, WebAssembly engine architecture, and production guides, visit the main GitHub repository:
👉 [https://github.com/barathanandh-coder/TinUi](https://github.com/barathanandh-coder/TinUi)
