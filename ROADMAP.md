# 🗺️ TinPyUI Project Roadmap

This document outlines the high-level roadmap, current milestones, and opportunities for open-source contributors to get involved.

---

## 🎯 Current Milestone: v1.6.x (Active Production & Stabilization)

- [x] **Universal Dual-Engine Architecture**: Go AOT Compiler + Pure Python Native Runtime.
- [x] **Symplectic Euler Spring Solver**: Real-time 120 FPS physics with Hooke's Law damping.
- [x] **High-Volume Spatial Virtualization**: `tin.VirtualStack` and `tin.VirtualList` for 100,000+ row rendering.
- [x] **Universal Reactive Multi-Engine Database Suite**: PostgreSQL, MongoDB, SQLite, and In-Memory RAM.
- [x] **Zero-DOM WebGL Shader Engine**: Custom GLSL fragment shader surfaces and particle layers.
- [x] **Enterprise Security Core**: HMAC session binding, RAMMaskedState string masking, decoy honeypots.
- [x] **Cross-Platform CI Matrix**: Automated testing on Windows, macOS, and Linux runners.
- [x] **Community Governance & Contributor Infrastructure**: RFC workflows, issue templates, dev tooling.

---

## 🚀 Upcoming Milestones

### 🌟 v1.7.0 — Ecosystem & High-Performance Extensions
- [x] **Extended WebGPU Shader Library**: Pre-built bloom, CRT cyber-mesh, volumetric fog, and fluid shaders.
- [x] **Redis, DuckDB & ClickHouse Reactive Connectors**: First-class support for `tin.connect("redis://...")`, `tin.connect("duckdb://...")`, and `tin.connect("clickhouse://...")`.
- [x] **Mobile Touch Gesture Enhancements**: Multi-touch pinch-to-zoom, directional swipe, and pull-to-refresh recognizers.
- [x] **Interactive REPL & Hot-Patching**: Python interactive debug shell (`tinpyui repl`) with SSE live-reload server.
- [x] **Advanced UI Component Suite**: Declarative `tin.DataGrid`, `tin.AIChat`, `tin.ColorPicker`, `tin.DatePicker`, `tin.Chart`, and `tin.TreeView`.
- [x] **iOS Native IPA Packaging Pipeline**: Standalone Apple iOS Xcode project generator (`tinpyui build --ios` / `tin.export_ios()`).
- [x] **Standalone Desktop Bundler**: Single-command desktop bundle creation (`tinpyui build --desktop`).
- [x] **Internationalization (i18n)**: Native RTL layout support and dynamic locale dictionary hydration.
- [x] **Direct Metal / DirectX 12 / Vulkan C++ Pipeline**: Direct GPU vector surface drawing bypassing OS webviews completely.
- [x] **TinPyUI Native Mobile Packages (Android)**: Standalone Android Gradle & APK export pipeline via CLI `tinui export mobile` / `tinpyui build --mobile`.
- [x] **Distributed Multi-Node State Sync**: Mesh networking state synchronization via WebRTC data channels and CRDTs.



---

## 💡 Good First Issues for New Contributors

Looking to make your first contribution? Here are great areas to start:

| Area | Description | Skills Required |
| :--- | :--- | :--- |
| **New UI Components** | Build new declarative components (e.g., `tin.ColorPicker`, `tin.Calendar`, `tin.AudioWaveform`) | Python / CSS |
| **GLSL Shaders** | Contribute new WebGL/WebGPU fragment shaders for UI backgrounds and cards | GLSL / WebGL |
| **Database Connectors** | Add support for DuckDB or MySQL in `tin.connect` | Python DB-API |
| **Compiler Optimizations** | Enhance `.tin` lexer error messages with line/column highlighting | Go |
| **VSCode Extension** | Add autocomplete snippets and syntax themes to `tinui-syntax` | TypeScript / JSON |
| **Tutorials & Examples** | Create complete sample apps (e.g., Financial Dashboard, IoT Monitor, Cyberpunk Chat) | Python / `.tin` |
| **Documentation & Translations** | Translate documentation into other languages or improve API guides | Markdown / Writing |

---

## 💬 How to Propose a Roadmap Item

Have an idea that isn't on the roadmap?
1. Check the [Open Issues](https://github.com/barathanandh-coder/TinUi/issues) to ensure it hasn't been proposed yet.
2. Submit a [Feature Request](.github/ISSUE_TEMPLATE/feature_request.yml) or [RFC Proposal](.github/ISSUE_TEMPLATE/rfc_proposal.yml).
3. Join the discussion and help design the solution!
