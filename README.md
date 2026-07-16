TinUI 

TinUI is a memory-safe, blazing-fast, and entirely custom UI framework. It completely bypasses Virtual DOM diffing by leveraging a custom Go WebAssembly linear memory engine mapped to a declarative Python-like syntax.

This is not a React clone. This is a ground-up systems engineering project featuring its own Lexer, Parser, Intermediate Representation (IR) Compiler, and Wasm runtime.

## Installation

### 1. The TinUI Compiler (CLI)
The core TinUI compiler is distributed as a universal WebAssembly binary via NPM. To install it globally, run:

```bash
npm install -g tinpyui
```
*Note: Requires Node.js installed on your machine.*

### 2. VS Code Syntax Highlighting
To enable official syntax highlighting for `.tin` files in your editor:

1. Download the latest `.vsix` file from the Releases page.
2. Open VS Code and navigate to the Extensions panel (`Ctrl+Shift+X`).
3. Click the `...` menu in the top right corner of the panel.
4. Select **Install from VSIX...** and choose the downloaded file.

## 🧠 Architecture Overview

# TinPyUI Framework

TinPyUI is a modern, Pythonically structured layout framework that compiles directly into native WebAssembly UI nodes. In v1.3, TinPyUI eliminates all external CSS and HTML dependencies, letting developers write elegant interface code that maps dynamically to hardcoded browser primitives with rich design features out of the box.

## 🚀 The v1.3 Developer Workflow

### Step 1: Install Globally
Install the unified CLI:
```bash
npm install -g tinpyui
```

### Step 2: Initialize a New Workspace
```bash
tinpyui init my-cyber-app
cd my-cyber-app
```
This scaffolds your `src/index.tin` configuration layout, `tinpyui.config.json`, and the essential `public/` web assembly bootloader files automatically.

### Step 3: Write Your UI
Edit `src/index.tin` using strict Pythonic indentation rules, invoking rich components like `AnimatedBackground`, `Marquee`, or `GradientText`. Zero CSS overhead.

### Step 4: Compile the Layout
```bash
tinpyui compile src/index.tin
```
The internal style compiler traverses your configuration, executes dynamic translation, maps explicit color palettes, validates indentation precisely, and outputs a native `public/app.ir.json` payload.

### Step 5: Launch the Dev Server
```bash
tinpyui serve
```
Spin up the local node driver hosting your fully formed WebAssembly target instantly on port 3000.

## 🧠 Architecture Overview

3. The Zero-Cost Wasm Runtime
When the Go WebAssembly runtime boots in the browser:
- It hydrates a `StateRegistry` tracking every variable.
- It allocates a 64-bit **Dirty Bitmap**. 
- When an event occurs (e.g., clicking a button or typing in an input), a JavaScript bridge triggers `TinUIDispatch` or `TinUIMutateState`.
- The Wasm engine mutates memory, flips a bit on the dirty bitmap, and runs `flushPatches()`.
- **The Result**: The DOM is patched surgically in $O(1)$ time. No tree walking. No diffing. Just microsecond pointer swaps.

Getting Started

### Prerequisites
- [Go](https://go.dev/) (1.21+)

### Building the Project
Run the included build script to compile the CLI and the Wasm engine.

bat
.\build.bat

*(This will generate `tinui.exe` and `tinui_engine.wasm`)*

Running an Application
1. Compile your `.tin` file:
   bash
   .\tinui.exe compile task_manager.tin
   
   This generates `task_manager.ir.json`.

2. To view the app, ensure `app.ir.json` in your server directory is symbolically linked to (or copied from) `task_manager.ir.json`. (Update `index.html`'s fetch target if needed).

3. Serve the directory to bypass CORS:
   bash
   python -m http.server 8080
   
4. Open `http://localhost:8080` in your browser.

Example: Task Manager
See `task_manager.tin` for an example of:
- Complex Deterministic Control Flow (Conditionals)
- Two-Way Data Binding
- Tailwind CSS Integration

Enjoy building at the speed of memory.
