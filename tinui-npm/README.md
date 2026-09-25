# TinPyUI

> The WebAssembly UI framework that compiles **Pythonic, indentation-based syntax** into blazing-fast native DOM, WebGL shaders, and multi-platform native apps.

[![npm](https://img.shields.io/badge/npm-tinpyui-v1.7.0-cyan)](https://www.npmjs.com/package/tinpyui)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/barathanandh-coder/TinUi/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/Docs-Full%20Manual-ff007f)](https://github.com/barathanandh-coder/TinUi/blob/main/tinpyui-docs.md)

> 📚 **Official Full Documentation & Architecture Manual**:
> Looking for the complete 16-chapter technical guide explaining TinPyUI from compiler internals to production deployment?
> 👉 Read the full guide: **[The TinPyUI Architecture & Developer Manual (tinpyui-docs.md)](https://github.com/barathanandh-coder/TinUi/blob/main/tinpyui-docs.md)**

---

## ✨ What Makes TinPyUI Special?

### Indentation-Based Syntax

No JSX brackets. No template soup. Just clean, Pythonic indentation:

```tin
component Main():
    Navbar(padding=20, blur=true, fixed=true):
        Row(align="center", justify="space-between"):
            Text(text="TinPyUI", color="neon-cyan", weight="bold")
            NavLink(text="GitHub", href="https://github.com/barathanandh-coder/tinui")

    Section(align="center", paddingY=120):
        Text(text="Hello World", size="hero", color="white")
        NeonButton(text="Get Started", color="neon-cyan")
```

### WebAssembly & Native Desktop Dual-Engine

A Go-compiled WASM engine executes your UI logic at near-native speed. On desktop, an anonymous 4MB shared memory C-FFI pipeline talks directly to native Windows (DirectX), macOS (Metal), and Linux (GTK) window hosts with sub-millisecond latency.

### 3D, Shaders & Animation Ready

Built-in components for 3D scenes, particle systems, GLSL fragment shaders (Bloom, Cyber Mesh, Volumetric Fog, Fluid Particles), scroll-triggered animations, and glassmorphism.

### Zero Virtual DOM & Hybrid Hardware Acceleration

Unlike React or Vue, TinPyUI has **zero Virtual DOM (Zero-VDOM) overhead**—reactive signals mutate nodes directly in $O(1)$ time without expensive tree diffing. Heavy visual effects (particles, GLSL shaders) run on an isolated WebGL 2.0 / WebGPU canvas without touching the DOM, while typography, inputs, and layout containers remain genuine semantic HTML5 elements for 100% native copy-paste, screen reader accessibility (a11y), and SEO.

### Omni-Platform Packaging

Package to **Web (WASM)**, **Apple iOS (Xcode / Swift / WKWebView)**, **Android (Gradle / APK)**, and **Desktop (standalone native binary)** with 1 command.

---

## 🚀 Quick Start

### Install

```bash
npm install -g tinpyui
```

### Create a Project

```bash
tinpyui init my-app
cd my-app
```

### Develop with Live Reload

```bash
tinpyui dev src/index.tin
```

---

## 🧱 Component Reference

### Layout
| Component | Purpose |
|-----------|---------|
| `Section` | Full-width container with padding & alignment |
| `Row` | Flexbox row with gap & alignment |
| `Column` | Flexbox column with gap & alignment |
| `Spacer` | Fixed vertical or horizontal space |
| `Divider` | Styled horizontal line |
| `Container` | Centered max-width content wrapper |

### Enterprise & Data (v1.7.0)
| Component | Purpose |
|-----------|---------|
| `DataGrid` | High-volume virtualized table with search, column sorting, pagination, and CSV/JSON export |
| `AIChat` | Streaming token LLM conversation container with Markdown and 1-click code copying |
| `ColorPicker` | Interactive Hex/RGB/HSL picker with opacity slider and palette swatches |
| `DatePicker` & `Calendar` | Interactive monthly calendar matrix and date selection dropdown |
| `LineChart`, `BarChart`, `DonutChart` | Declarative responsive vector SVG charts with gradients and tooltips |
| `TreeView` & `TreeNode` | Collapsible nested hierarchical tree view |
| `LiveDataTable` & `AutoCRUD` | 1-line reactive tables auto-wired to database models |

### Interactive Controls
| Component | Purpose |
|-----------|---------|
| `Button` | Interactive clickable button with glow states |
| `Input` | Two-way data-bound text input |
| `Slider` | Smooth numeric value slider |
| `Switch` | Animated toggle switch |
| `ProgressBar` | Progress indicator with gradient styling |

### 3D & Shaders
| Component | Purpose |
|-----------|---------|
| `Scene3D` | WebGL 3D scene container |
| `Mesh3D` | 3D mesh objects (box, sphere, torus) |
| `ParticleSystem3D` | GPU particle effects |
| `AnimatedBackground` | Fullscreen WebGL shader background (Bloom, Cyber Mesh, Fog) |

---

## 🛠️ CLI Commands

| Command | Description |
|---------|-------------|
| `tinpyui init [dir]` | Scaffold a new project |
| `tinpyui compile <file>` | Compile `.tin` to IR + static assets |
| `tinpyui dev <file>` | Dev server with file watching & live reload |
| `tinpyui repl` | Interactive Python REPL & State Inspector |
| `tinpyui build --web` | Compile production WebAssembly bundle |
| `tinpyui build --ios` | Generate standalone Apple iOS Xcode project |
| `tinpyui build --mobile` | Generate standalone Android Gradle project & APK |
| `tinpyui build --desktop` | Build standalone native desktop executable bundle |
| `tinpyui --version` | Show version (`v1.7.0`) |
| `tinpyui --help` | Show help |

---

## 🗄️ Universal Reactive Database Suite

Connect to any database in 1 line with automatic reactive UI updates:
```python
import tinpyui as tin

# PostgreSQL
pg = tin.connect("postgres://user:pass@localhost:5432/db")

# MongoDB
mongo = tin.connect("mongodb://localhost:27017/db")

# Redis (Pub/Sub signals + caching)
redis = tin.connect("redis://localhost:6379/0")

# DuckDB (Vectorized analytics)
analytics = tin.connect("duckdb://analytics.db")

# SQLite & In-Memory
db = tin.connect("sqlite:///app.db")
ram = tin.connect(":memory:")
```

---

## 📦 IDE Support

TinPyUI ships with Python type stub files (`tinpyui.pyi`) for full autocomplete and diagnostics in VS Code, Cursor, and PyCharm.

---

## 🔗 Links

| Resource | URL |
|----------|-----|
| npm Package | [https://www.npmjs.com/package/tinpyui](https://www.npmjs.com/package/tinpyui) |
| PyPI Package | [https://pypi.org/project/tinpyui-ff/](https://pypi.org/project/tinpyui-ff/) |
| GitHub Repo | [https://github.com/barathanandh-coder/tinui](https://github.com/barathanandh-coder/tinui) |
| Documentation | [https://github.com/barathanandh-coder/tinui/blob/main/tinpyui-docs.md](https://github.com/barathanandh-coder/tinui/blob/main/tinpyui-docs.md) |

---

## 📝 License

MIT © 2026 Barathanandh
