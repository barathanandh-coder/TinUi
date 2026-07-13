TinUI 

TinUI is a memory-safe, blazing-fast, and entirely custom UI framework. It completely bypasses Virtual DOM diffing by leveraging a custom Go WebAssembly linear memory engine mapped to a declarative Python-like syntax.

This is not a React clone. This is a ground-up systems engineering project featuring its own Lexer, Parser, Intermediate Representation (IR) Compiler, and Wasm runtime.

 Architecture Overview

1. The Pythonic Grammar
TinUI uses strict indentation logic (similar to Python). It removes the clutter of JSX and `useState` hooks. 
- You declare `state` natively.
- UI elements nest organically via indentation.
- Two-way binding is natively understood via the `bind` keyword.

2. AST & IR Generation
The Go compiler parses your `.tin` file and generates a flat JSON array of OpCodes (Intermediate Representation). 
Instead of sending a heavy AST to the browser, the IR strips away logic and emits simple machine-like instructions (`DECLARE_STATE`, `CREATE_CONDITIONAL`, `BIND_INPUT`).

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
