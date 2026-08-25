# The TinPyUI Architecture & Developer Manual (v1.6.0)
*The Definitive Guide to Building Hardware-Accelerated WebAssembly Applications with Pythonic Syntax*

---

## Table of Contents
1. [Chapter 1: The Architectural Reality & Core Philosophy](#chapter-1-the-architectural-reality--core-philosophy)
2. [Chapter 2: Deep Architectural Comparison (How TinPyUI Differs from Others)](#chapter-2-deep-architectural-comparison)
3. [Chapter 3: The Intermediate Representation (IR) Compilation Pipeline](#chapter-3-the-intermediate-representation-ir-compilation-pipeline)
4. [Chapter 4: The Declarative `.tin` Syntax Specification](#chapter-4-the-declarative-tin-syntax-specification)
5. [Chapter 5: Multi-Scene Routing & State Management](#chapter-5-multi-scene-routing--state-management)
6. [Chapter 6: The Hardware Layer: WebGL GPU Shaders & Particles](#chapter-6-the-hardware-layer-webgl-gpu-shaders--particles)
7. [Chapter 7: Complete Component API Catalog](#chapter-7-complete-component-api-catalog)
8. [Chapter 8: CLI, Development Workflows & Dev Server](#chapter-8-cli-development-workflows--dev-server)
9. [Chapter 9: Native Desktop Shells & Cross-Platform Packaging](#chapter-9-native-desktop-shells--cross-platform-packaging)
10. [Chapter 10: Security Architecture & Memory Safety](#chapter-10-security-architecture--memory-safety)
11. [Chapter 11: Production Deployment & Backend Integration](#chapter-11-production-deployment--backend-integration)
12. [Chapter 12: High-Volume Scalability & Advanced Subsystems (v1.6)](#chapter-12-high-volume-scalability--advanced-subsystems-v16)
13. [Chapter 13: Universal Reactive Database & Low-Code Suite](#chapter-13-universal-reactive-database--low-code-suite)
14. [Chapter 14: Real-Time Sockets, Native OS Dialogs & Dynamic IR Export](#chapter-14-real-time-sockets-native-os-dialogs--dynamic-ir-export)
15. [Chapter 15: Full-Stack Architecture & Production Recipes](#chapter-15-full-stack-architecture--production-recipes)

---

## Chapter 1: The Architectural Reality & Core Philosophy

### 1.1 Dispelling the "Zero-DOM" Myth: What TinPyUI Actually Is
In modern web development, "Zero-DOM" is frequently used as a buzzword. To be technically precise and honest: **TinPyUI is NOT a raw Canvas-only blitter (like Flutter Web CanvasKit) that discards the browser DOM completely.** 

Rendering everything to a raw `<canvas>` causes severe web usability failures:
- Broken browser text selection and native copy-paste.
- Zero accessibility (a11y) support for screen readers.
- Broken search engine indexing (SEO).
- Inability to use native browser password managers and autocomplete.

Instead, TinPyUI operates on a **Hybrid DOM Layout + WebGL Hardware Acceleration Architecture**:

```
+-------------------------------------------------------------------------+
|                         TINPYUI DUAL-ENGINE ARCHITECTURE                 |
+-------------------------------------------------------------------------+
|  [ .tin Source Code ] -> [ Go AOT Compiler ] -> [ Intermediate Rep (IR) ]|
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  WASM RUNTIME ENGINE (tinui_engine.wasm)                 |
+------------------------------------+------------------------------------+
|         LAYER A: DOM ENGINE        |      LAYER B: HARDWARE GPU SHADER  |
|  - Semantic HTML5 Elements         |  - WebGL 2.0 Canvas Surfaces       |
|  - Flexbox & Grid CSS Tokens       |  - Custom Fragment Shaders (GLSL)  |
|  - Reactive State & Input Bindings |  - 120 FPS Particles & Cyber Waves |
|  - Native A11y & SEO Hydration     |  - Zero CPU Layout Interruption    |
+------------------------------------+------------------------------------+
```

### 1.2 Core Pillars of the Engine
1. **Pythonic, Indentation-Based Syntax (`.tin`)**: Write clean, declarative UI hierarchies without JSX brackets, closing tags, or XML clutter.
2. **Ahead-of-Time (AOT) Go Compiler**: Translates `.tin` ASTs directly into an ultra-compact deterministic Intermediate Representation JSON (`app.ir.json`).
3. **High-Performance WebAssembly Kernel**: Written in Go and compiled to `tinui_engine.wasm`, the kernel executes state mutation machines, event routing, and DOM lifecycle dispatch without JS virtual-DOM diffing loops.
4. **Isolated WebGL GPU Shaders**: Background effects (cyber-waves, quantum vortexes, interactive particle fields) run entirely on the GPU via dedicated WebGL canvases, ensuring 60/120 FPS animations without stalling the UI thread.

---

## Chapter 2: Deep Architectural Comparison

Understanding how TinPyUI differs fundamentally from existing web and UI frameworks is critical for engineering decisions:

| Architectural Metric | **TinPyUI v1.6** | **React / Vue / Next.js** | **Flutter Web (CanvasKit)** | **PyScript / Pyodide** | **Flet / Streamlit** | **Tauri / Electron** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Language DSL** | Pythonic Indentation (`.tin`) | JSX / Template XML | Dart Widgets | Pure Python (CPython) | Pure Python DSL | JS / TS / HTML |
| **Execution Model** | Go WebAssembly + IR Engine | JS V-DOM Diffing Loop | Skia/Impeller Canvas Blit | Full 25MB CPython Wasm | Server-side WebSocket IPC | Native Webview / Node |
| **DOM Strategy** | Direct IR DOM + WebGL | Virtual DOM Reconciliation | Canvas Only (No DOM) | Direct DOM via JS Proxy | DOM via React/Flutter wrapper | Native Webview DOM |
| **Bundle Size** | ~11 MB (Engine + Shaders) | 100 KB - 5 MB (JS bundle) | 20 MB - 35 MB | 25 MB - 40 MB | Full server runtime | 2 MB (Tauri) / 150 MB (Electron) |
| **SEO & Accessibility** | Full SEO Hydration Shell | Native DOM / SSR | None (Raw pixels on Canvas) | Limited | None (Dynamic client only) | Desktop Only |
| **Client-side Latency** | 0 ms (Local WASM) | 0 ms (Local JS) | 0 ms (Local WASM) | High startup overhead | 50-200 ms (Server roundtrip) | 0 ms (Local IPC) |
| **GPU Shader Layer** | Built-in GLSL & Shaders | Requires Three.js / R3F | Canvas drawing API | Canvas library required | Not supported | WebGL library required |

### Why TinPyUI Outperforms Alternatives:
- **Over React/Next.js**: Eliminates npm dependency bloat (`node_modules`), package version mismatches, and expensive recursive virtual-DOM tree diffs.
- **Over Flutter Web**: Maintains real browser DOM accessibility, text selection, link routing, and SEO while retaining hardware-accelerated animations.
- **Over PyScript**: Avoids bundling the entire 30MB Python CPython runtime into the browser. TinPyUI compiles UI logic into lightweight IR instructions ahead of time.
- **Over Streamlit/Flet**: UI interactions do NOT require a continuous WebSocket connection back to a server. All clicks, mutations, and transitions execute instantly in the client browser.

---

## Chapter 3: The Intermediate Representation (IR) Compilation Pipeline

The TinPyUI compiler transforms declarative code into executable instructions through a multi-stage deterministic compiler:

```
[ .tin Source Code ]
        |
        v
[ Lexer (lexer.go) ] ----------> Token Stream (INDENT, DEDENT, COMPONENT, IDENT, STRING...)
        |
        v
[ Parser (parser.go) ] --------> Abstract Syntax Tree (AST Nodes, DefNodes, Keyframes...)
        |
        v
[ Generator (generator.go) ] --> IR Blueprint (Nodes Instructions + Mutations Map)
        |
        +---------------------> [ public/app.ir.json ] (Consumed by Wasm Engine)
        |
        +---------------------> [ public/index.html ] (SEO Static Hydration Shell)
```

### The Instruction Set (`Instruction`)
Every DOM node and mutation is represented as an atomic instruction:
- `CREATE_NODE`: Instantiates a DOM node with mapped semantic tag (`section`, `div`, `h2`, `button`, etc.).
- `APPEND_CHILD`: Establishes parent-child tree hierarchy (`Parent -> Child`).
- `SET_ATTRIBUTE`: Sets HTML attributes, data-attributes, and compiled inline CSS tokens.
- `SET_TEXT`: Assigns static inner text.
- `BIND_TEXT`: Dynamically interpolates reactive state keys into template text (`"Count: {}"`).
- `DECLARE_STATE`: Registers reactive state variable with initial typed value.
- `ADD_EVENT`: Attaches DOM event listener (`click`, `input`) to internal mutation dispatcher.
- `BIND_INPUT`: Establishes two-way state binding for text and number inputs.
- `BIND_LOADING`: Attaches dynamic skeleton loader or spinner state to elements.

---

## Chapter 4: The Declarative `.tin` Syntax Specification

### 4.1 Grammar Rules
1. **Component Roots**: Every `.tin` file defines components via `component <Name>(<args>):`. The main entry point must be named `Main` or `App`.
2. **Indentation Blocks**: Child elements are indented with 4 spaces (or consistent tabs) following a colon (`:`).
3. **Properties (`key=value`)**:
   - Strings: Double quotes `text="Dashboard"`, `color="neon-cyan"`.
   - Numbers: `padding=20`, `maxWidth=800`.
   - Booleans: Case-insensitive Python/JS values `blur=True`, `blur=true`, `wrap=True`.
   - Lists: `gradient=["neon-cyan", "neon-purple"]`.

### 4.2 Code Example
```tin
component Main():
    AnimatedBackground(effect="cyber-wave", primaryColor="neon-purple", secondaryColor="neon-cyan"):
        Navbar(padding=20, blur=True):
            Row(align="center", justify="space-between", width="full"):
                Text(text="TinPyUI Portal", color="neon-cyan", weight="bold")
                Row(gap=30, color="white"):
                    NavLink(text="Features", href="/features")
                    NavLink(text="Dashboard", href="/dashboard")

        Section(align="center", paddingY=100, maxWidth=800, justify="center"):
            GradientText(text="Engineered for Precision", size="hero")
            Text(text="Pure Pythonic syntax compiled directly to WebAssembly.", color="muted", marginTop=20)
            Spacer(height=30)
            Row(gap=20, align="center"):
                Button(text="Get Started", variant="solid", glow="neon-cyan", radius="pill")
                Button(text="View Documentation", variant="outline", radius="pill")
```

---

## Chapter 5: Multi-Scene Routing & State Management

TinPyUI v1.6 features a **Cinematic Scene Router** that enables multi-file page architectures without client-side page reloads.

### 5.1 Project Layout for Multi-Scene Apps
```
my_tinpy_app/
├── main.tin               # Entry router configuration
├── scenes/
│   ├── dashboard.tin      # Scene component 1
│   ├── settings.tin       # Scene component 2
│   └── profile.tin        # Scene component 3
├── shaders/
│   └── custom.frag        # Custom GLSL fragment shaders
└── tinpy.toml             # Configuration manifest
```

### 5.2 Router & Scene Definition
In `main.tin`:
```tin
component Main():
    Router(transition="cinematic", duration="smooth"):
        Route(path="/", scene="Dashboard", default_route="true")
        Route(path="/settings", scene="Settings")
```

In `scenes/dashboard.tin`:
```tin
component Dashboard():
    Container(align="center", justify="center", width="full", padding=50):
        GradientText(text="Welcome to Dashboard", size="hero")
        Spacer(height=20)
        Text(text="Your application is running smoothly.", color="muted")
```

### 5.3 Reactive State & Mutations
State variables and mutation functions can be declared directly inside components:
```tin
component Counter():
    state count = 0

    def increment():
        count += 1

    def decrement():
        count -= 1

    Row(gap=20, align="center"):
        Button(text="-", on_click="decrement")
        Text(text="Current Count: {count}", color="white")
        Button(text="+", on_click="increment")
```

---

## Chapter 6: The Hardware Layer: WebGL GPU Shaders & Particles

TinPyUI embeds an automated WebGL shader pipeline. You can add background effects or standalone GPU canvases with zero boilerplate.

### 6.1 Built-in Shader Effects
- `effect="cyber-wave"`: Glowing dual-sine wave distortion grid in cyberpunk colors.
- `effect="particles"`: Interactive ambient floating particle dust with mouse repulsion.
- `effect="quantum-vortex"`: Multi-octave radial plasma vortex.

### 6.2 Custom GLSL Fragment Shaders
You can write custom GLSL code in `shaders/background.frag` or inline it via `CustomShader`:
```tin
component Hero():
    Surface(width="full", height=500):
        WebGLCanvas(fragmentCode="""
            precision mediump float;
            uniform float u_time;
            uniform vec2 u_resolution;
            void main() {
                vec2 uv = gl_FragCoord.xy / u_resolution.xy;
                gl_FragColor = vec4(uv.x, uv.y, sin(u_time), 1.0);
            }
        """)
```

The Go compiler automatically validates GLSL shaders at compile time (`glsl_validator.go`), catching syntax errors before browser execution.

---

## Chapter 7: Complete Component API Catalog

### 7.1 Structural & Layout Containers
| Component | Primary Properties | Description |
| :--- | :--- | :--- |
| `Section` | `align`, `justify`, `paddingY`, `maxWidth`, `minHeight` | Full-width vertical segment container |
| `Container` | `align`, `justify`, `width`, `padding`, `gap` | General-purpose flexbox container |
| `Row` | `align`, `justify`, `gap`, `width`, `wrap`, `marginTop` | Horizontal flex row |
| `Card` | `maxWidth`, `padding`, `background`, `border`, `radius`, `shadow` | Visually distinct glass/solid card |
| `Grid` | `cols`, `gap`, `width`, `padding` | Multi-column CSS grid container |
| `Spacer` | `height`, `width` | Explicit layout spacing block |
| `Divider` | `color`, `margin` | Horizontal rule divider line |

### 7.2 Typography
| Component | Primary Properties | Description |
| :--- | :--- | :--- |
| `Heading` | `text`, `size` (`"h1"`, `"h2"`, `"h3"`), `color` | Semantic heading element |
| `Text` | `text`, `size` (`"small"`, `"normal"`, `"large"`), `color`, `weight` | Paragraph text with reactive `{key}` interpolation |
| `GradientText`| `text`, `gradient` (`["cyan", "purple"]`), `size` (`"hero"`, `"h1"`) | Hardware-styled text gradient |
| `Badge` | `text`, `color`, `variant` | Compact label or status indicator |

### 7.3 Interactive & Inputs
| Component | Primary Properties | Description |
| :--- | :--- | :--- |
| `Button` | `text`, `variant` (`"solid"`, `"outline"`), `glow`, `radius`, `on_click` | Interactive button |
| `Input` | `placeholder`, `value`, `bind`, `width`, `type` | Two-way data bound input field |
| `Textarea` | `placeholder`, `value`, `bind`, `rows`, `width` | Multiline text entry |
| `NavLink` | `text`, `href`, `target` | Route transition navigation link |

---

## Chapter 8: CLI, Development Workflows & Dev Server

### 8.1 Global CLI Installation
Via NPM:
```bash
npm install -g tinpyui
```
Via Python PyPI:
```bash
pip install tinpyui-ff
```

### 8.2 Cross-Platform Compilation Guide (OS-by-OS)

#### 🪟 Windows (10 & 11)
```powershell
# Option A: Standalone Compiler Binary
.\tinui.exe compile src/index.tin
.\tinui.exe compile src/index.tin --hydrate   # With SEO HTML hydration

# Option B: Run from Go source
go run main.go compile src/index.tin
go run main.go compile src/index.tin --hydrate

# Option C: Global NPM CLI
tinpyui compile src/index.tin
tinpyui compile src/index.tin --hydrate

# Dev Server (Hot GLSL Reloading on http://localhost:8080)
.\tinui.exe dev src/index.tin
```

#### 🍎 macOS (Apple Silicon M1/M2/M3/M4 & Intel)
```bash
# Option A: Standalone Compiler Binary
chmod +x ./tinui
./tinui compile src/index.tin
./tinui compile src/index.tin --hydrate

# Option B: Run from Go source
go run main.go compile src/index.tin
go run main.go compile src/index.tin --hydrate

# Option C: Global NPM CLI
tinpyui compile src/index.tin
tinpyui compile src/index.tin --hydrate

# Dev Server (Hot GLSL Reloading on http://localhost:8080)
./tinui dev src/index.tin
```

#### 🐧 Linux (Ubuntu, Debian, Fedora, Arch, Alpine)
```bash
# Option A: Standalone Compiler Binary
chmod +x ./tinui
./tinui compile src/index.tin
./tinui compile src/index.tin --hydrate

# Option B: Run from Go source
go run main.go compile src/index.tin
go run main.go compile src/index.tin --hydrate

# Option C: Global NPM CLI
tinpyui compile src/index.tin
tinpyui compile src/index.tin --hydrate

# Dev Server (Hot GLSL Reloading on http://localhost:8080)
./tinui dev src/index.tin
```

#### 🌐 WebAssembly Engine Compilation (`tinui_engine.wasm`)
```bash
# Windows (PowerShell)
$env:GOOS="js"; $env:GOARCH="wasm"; go build -ldflags="-s -w" -o tinui_engine.wasm ./wasm_engine

# macOS / Linux (Bash / Zsh)
GOOS=js GOARCH=wasm go build -ldflags="-s -w" -o tinui_engine.wasm ./wasm_engine
```

### 8.3 Common CLI Commands
- `tinpy create <project_name>` / `tinpyui init`: Scaffold a complete starter project with `main.tin`, `scenes/dashboard.tin`, and shaders.
- `tinpy dev <file.tin>` / `tinui dev <file.tin>`: Start the live development server with Hot GLSL Reloading (HGR) on `http://localhost:8080`.
- `tinpy compile <file.tin>` / `tinui compile <file.tin>`: Compile `.tin` source code to `public/app.ir.json`.
- `tinpy compile <file.tin> --hydrate` / `tinui compile <file.tin> --hydrate`: Compile IR and generate static SEO `index.html` hydration shell.
- `tinpy desktop <file.tin>` / `tinui desktop <file.tin>`: Launch the native desktop window.

---

## Chapter 9: Native Desktop Shells & Cross-Platform Packaging

TinPyUI includes lightweight C++ host window bindings via `webview.h` and native platform graphics APIs:
- **Windows**: Win32 HWND + Microsoft Edge WebView2 (DirectX 12 acceleration).
- **macOS**: Cocoa + WKWebView (Apple Metal hardware acceleration).
- **Linux**: GTK3/GTK4 + WebKitGTK (X11 and Wayland acceleration).

Standalone desktop binaries compile to under **2 MB** without shipping the heavy overhead of Chromium.

---

## Chapter 10: Security Architecture & Memory Safety

TinPyUI enforces strict security defaults across the compilation and runtime pipeline:
1. **Adversarial Input Sanitization**: Strings and attributes are length-capped and HTML-entity escaped to prevent Cross-Site Scripting (XSS).
2. **GLSL Static Validator**: Shader code is scanned at compile-time to prevent GPU memory crashes and infinite loops.
3. **Session Binding Shield**: High-entropy HMAC session signatures protect against session replay attacks.
4. **Panic-Proof WASM Execution**: The WebAssembly engine wraps render updates in panic-recovery middleware, guaranteeing that runtime errors never crash the host web page.

---

## Chapter 11: Production Deployment & Backend Integration

### 11.1 Python Flask / FastAPI Integration
TinPyUI apps compile into static files (`index.html`, `tin-runtime.js`, `wasm_exec.js`, `tinui_engine.wasm`, `app.ir.json`) that can be hosted on any web server or Python backend:

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

### 11.2 Static Hosting (Vercel, Netlify, Cloudflare Pages, S3)
Deploy the contents of the `public/` directory directly to any static web host. Ensure that your web server serves `.wasm` files with the `Content-Type: application/wasm` MIME type header.

---

## Chapter 12: High-Volume Scalability & Advanced Subsystems (v1.6)

### 12.1 `VirtualStack` High-Volume Windowing
TinPyUI v1.6 introduces `VirtualStack` (`wasm_engine/virtual_stack.go`), capable of virtualizing 100,000+ items with sub-millisecond scrolling latency and zero GC allocations:
```tin
component LargeDatasetView():
    Container(padding=20):
        Heading(text="High-Volume Virtual Feed (100k Rows)", size="h2")
        VirtualStack(itemHeight=50, totalCount=100000):
            Card(padding=12, background="dark-core", border="neon-cyan"):
                Text(text="Dynamic Virtual Row Item", color="white")
```

### 12.2 Symplectic Euler Spring Physics
The animation subsystem integrates Hooke's Law differential solver ($F = -kx - cv$) for interactive gestures and inertia fling:
```python
import tinpyui as tin

spring = tin.Spring(tension=180.0, friction=22.0)
spring.target = 300.0  # Set target pixel position
next_pos = spring.step(1.0 / 120.0)
```

### 12.3 Zero-Copy Platform Channel Bridge
Native hardware access is decoupled through `PlatformBridge`:
- `tin.haptics.vibrate(50)`: Haptic feedback pulse.
- `tin.PlatformBridge.copy_clipboard(text)`: Native clipboard synchronization.
- Automatic light/dark system theme query (`GetSystemTheme`).

---

## Chapter 13: Universal Reactive Database & Low-Code Suite

TinPyUI provides a unified, zero-boilerplate **Universal Database & Low-Code Suite** with built-in multi-driver support for **PostgreSQL**, **MongoDB**, and **SQLite / In-Memory**, all sharing the same reactive 120 FPS UI synchronization pipeline.

```
+-----------------------------------------------------------------------------------+
|                        TINPYUI REACTIVE DATA PIPELINE                             |
+-----------------------------------------------------------------------------------+
|  [ Database Mutation ]  --->  [ Table / Collection Listener ]                     |
|  (insert / update / delete)                  │                                    |
|                                              ▼                                    |
|  [ UI Render (120 FPS) ] <--- [ LiveQuery / Reactive Signal ] <--- [ O(1) Graph ] |
+-----------------------------------------------------------------------------------+
```

---

### 13.1 Universal Connection Factory (`tin.connect` & `tin.Database`)

The `tin.connect()` factory dynamically inspects the URI protocol and instantiates the optimal database driver. It operates with zero crash probability across desktop, web, and mobile by providing automatic embedded fallbacks if external native drivers are not installed.

#### Syntax & Signatures:
```python
tin.connect(uri_or_path: str = ":memory:", **kwargs) -> Union[Database, PostgresDatabase, MongoDatabase]
tin.Database(path: str = ":memory:", auto_commit: bool = True) -> Database
tin.PostgresDB(uri: str, auto_commit: bool = True, **kwargs) -> PostgresDatabase
tin.MongoDB(uri: str, **kwargs) -> MongoDatabase
```

#### Connection String Protocols:
| Engine | URI Format Examples | Driver / Fallback Strategy |
| :--- | :--- | :--- |
| **PostgreSQL** | `postgres://user:pass@host:5432/dbname`<br>`postgresql://user:pass@host:5432/dbname` | Uses `psycopg2` or `psycopg3`. Falls back to in-memory Postgres dialect engine. |
| **MongoDB** | `mongodb://user:pass@host:27017/dbname`<br>`mongodb+srv://user:pass@cluster0.mongodb.net/dbname` | Uses `pymongo`. Falls back to high-performance embedded document store. |
| **SQLite (Disk)** | `sqlite:///app_data.db`<br>`./database.sqlite` | Native `sqlite3` driver with auto-reconnect and dynamic schema generation. |
| **In-Memory** | `:memory:`<br>`sqlite:///:memory:` | Zero-disk RAM database for testing, ephemeral sessions, and WASM runtime. |

---

### 13.2 PostgreSQL & Relational SQL Operations (`PostgresTable` & `Table`)

Tables represent schema-agnostic relational stores with dynamic schema evolution (automatic column addition upon `insert` without migration scripts).

#### Complete Method Reference:

##### 1. Insertion & Upsert
```python
# Single Insert with dynamic schema creation
row_id: int = table.insert(name="Alice", role="Admin", age=30, is_active=True)

# Bulk Insert in a single ACID transaction
ids: List[int] = table.insert_many([
    {"name": "Bob", "role": "Developer", "age": 25},
    {"name": "Charlie", "role": "Designer", "age": 28}
])

# Upsert (Updates if matching 'where' exists; otherwise inserts)
row_id: int = table.upsert(where={"name": "Alice"}, role="SuperAdmin", age=31)
```

##### 2. Fluent Query Building (`QueryBuilder`)
```python
# Chained query builder
query = (table.where(role="Developer")
              .gt("age", 22)
              .like("name", "B%")
              .order_by("age", desc=True)
              .limit(10)
              .offset(0))

# Execute query
results: List[Dict[str, Any]] = query.all()
first_match: Optional[Dict[str, Any]] = query.first()
total_matching: int = query.count()
```

##### 3. Updates & Deletions
```python
# Update matching records (returns affected row count)
updated_rows: int = table.update(where={"role": "Developer"}, is_active=False)

# Delete matching records (returns deleted row count)
deleted_rows: int = table.delete(where={"is_active": False})
```

##### 4. Raw Parameterized SQL Execution
```python
# Safe parameterized query execution
users = pg_db.query("SELECT * FROM users WHERE age >= ? AND role = ?", [21, "Admin"])
affected = pg_db.execute("UPDATE users SET status = ? WHERE last_login < ?", ["inactive", "2026-01-01"])
```

---

### 13.3 MongoDB & Document NoSQL Operations (`MongoCollection`)

`MongoCollection` provides full document database capabilities supporting nested dictionaries, dot-notation field navigation, and standard Mongo query operators.

#### Complete Method Reference:

##### 1. Document Insertion
```python
products = mongo_db.collection("products")

# Insert single document (auto-generates 12-char hex '_id' if omitted)
result = products.insert_one({
    "title": "Quantum GPU Server",
    "category": "Hardware",
    "price": 12000,
    "specs": {"cores": 128, "ram": "512GB", "storage": "8TB NVMe"}
})
inserted_id: str = result["inserted_id"]

# Bulk insert
products.insert_many([
    {"title": "Cyber Keyboard", "category": "Peripherals", "price": 150},
    {"title": "Holographic Display", "category": "Hardware", "price": 3500}
])
```

##### 2. Nested Dot-Notation & Operator Queries
```python
# Query with Mongo operators: $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin
heavy_hw = products.find({
    "category": "Hardware",
    "price": {"$gte": 3000, "$lte": 15000},
    "specs.ram": "512GB" # Nested dot notation
})

# Find first matching document
item = products.find_one({"title": "Cyber Keyboard"})
```

##### 3. Document Updates & Deletions
```python
# Update first match (supports $set syntax or raw dictionary)
products.update_one({"title": "Cyber Keyboard"}, {"$set": {"price": 129}})

# Update all matches
products.update_many({"category": "Hardware"}, {"$set": {"warranty": "3 Years"}})

# Delete single / multiple documents
products.delete_one({"title": "Cyber Keyboard"})
products.delete_many({"category": "Obsolete"})
```

---

### 13.4 Reactive Live Queries (`LiveQuery`)

`LiveQuery` bridges database tables and document collections directly to the TinPyUI reactive signal graph. Whenever any mutation (`insert`, `update`, `delete`, `upsert`) occurs on the target table/collection, the `LiveQuery` instantly re-evaluates and notifies all UI subscribers at 120 FPS without requiring manual event handlers.

#### Syntax & Live Binding Example:
```python
import tinpyui as tin

db = tin.connect("postgres://user:pass@localhost:5432/production")
tasks = db.table("tasks")

# 1. Instantiate LiveQuery Signal
active_tasks = tasks.live_query(status="pending")

# 2. Bind directly to UI elements (Updates automatically on DB mutation!)
with tin.Window(title="Real-Time Task Stream"):
    with tin.Section():
        tin.Heading(text="Live Task Queue")
        
        # VirtualList automatically scrolls and updates when new tasks are inserted
        tin.VirtualList(items=active_tasks, item_height=48.0)
        
        tin.Button(
            text="Add Rapid Task",
            on_click=lambda: tasks.insert(title="New Live Task", status="pending")
        )
```

---

### 13.5 Low-Code Declarative UI Components (`LiveDataTable` & `AutoCRUD`)

TinPyUI provides 1-line declarative components that reflect schemas and wire themselves to database collections automatically.

#### 1. `tin.LiveDataTable`
A high-performance reactive data grid that auto-discovers table headers and binds to live query updates:
```python
# Binds directly to a Table, MongoCollection, LiveQuery, or table name string
tin.LiveDataTable(db.table("users"))
tin.LiveDataTable(mongo_db.collection("products"), columns=["title", "price", "category"])
```

#### 2. `tin.AutoCRUD`
Generates a complete administrative CRUD interface (Header, Form Inputs, Data Grid, and Delete Triggers) with a single line of code:
```python
# Instantly renders complete CRUD Dashboard
tin.AutoCRUD(db.table("inventory"), title="Warehouse Inventory Manager")
```

---

### 13.6 Persistent Key-Value Store (`tin.use_store`)

`tin.use_store` provides a thread-safe, disk-persisted key-value storage engine with reactive signal binding for settings, tokens, and theme configurations.

```python
store = tin.use_store("app_settings.db", table="preferences")

# Direct Get / Set
store.set("theme", "cyber-dark")
store.set("audio_volume", 85)
current_theme = store.get("theme", default="cyber-dark")

# Disk-backed Reactive Signal (Mutating the signal automatically writes to disk!)
theme_signal = store.signal("theme", default="cyber-dark")
theme_signal.value = "neon-matrix"  # Automatically persists to disk
```

---

### 13.7 Declarative Active Record Models (`@tin.model`)

Use Python class syntax with type annotations to define Active Record models:

```python
@tin.model
class Customer:
    name: str
    email: str
    tier: str = "Standard"
    loyalty_points: int = 0

# Active Record CRUD
c = Customer.create(name="Alice", email="alice@test.com", tier="VIP")
all_vips = Customer.where(tier="VIP").order_by("loyalty_points", desc=True).all()
live_customers = Customer.live_query(tier="VIP")
Customer.delete(where={"loyalty_points": 0})
```

---

### 13.8 Data Portability (1-Line JSON & CSV Migration)

```python
# Full database backup & restore via JSON
db.export_json("backup.json")
db.import_json("backup.json")

# Single table CSV export & import
db.export_csv("users", "users_backup.csv")
db.import_csv("users", "users_backup.csv")
```

---

## Chapter 14: Real-Time Sockets, Native OS Dialogs & Dynamic IR Export

```
+-----------------------------------------------------------------------------------+
|                        REAL-TIME & HARDWARE OS IPC BRIDGES                        |
+-----------------------------------------------------------------------------------+
|  [ WebSocket / SSE Stream ] ---> [ Reactive Signal ] ---> [ UI Components ]       |
|  [ Native File Pickers ]   ---> [ PlatformBridge ]  ---> [ Win32 / Cocoa Dialogs ]|
|  [ Dynamic Python Tree ]   ---> [ app.export_ir ]   ---> [ Go WebAssembly Kernel ]|
+-----------------------------------------------------------------------------------+
```

---

### 14.1 Reactive WebSockets (`tin.use_socket`)

`tin.use_socket` creates a thread-safe bi-directional socket client that exposes reactive `Signal` instances for connection state and message streams.

#### Class Definition & API:
```python
class WebSocketConnection:
    url: str
    status: Signal  # "connecting" | "open" | "closed" | "error"
    message: Signal # Last received string/payload
    
    def send(self, data: str) -> None
    def close(self) -> None
```

#### Real-Time Chat & Telemetry Example:
```python
import tinpyui as tin

socket = tin.use_socket("wss://echo.websocket.events")

with tin.Window(title="Real-Time Telemetry"):
    with tin.Column(padding=20, gap=12):
        # Status indicator with dynamic color
        tin.Text(
            text=lambda: f"● Connection: {socket.status.value.upper()}",
            color=lambda: "#00f2fe" if socket.status.value == "open" else "#ff3b30"
        )
        
        # Message Display
        tin.Card(padding=16):
            tin.Text(text=lambda: f"Incoming Stream: {socket.message.value}")
        
        # Control Buttons
        with tin.Row(gap=10):
            tin.Button("Send Ping", on_click=lambda: socket.send("PING_TELEMETRY"))
            tin.Button("Disconnect", on_click=lambda: socket.close())
```

---

### 14.2 Server-Sent Events Stream (`tin.use_sse`)

Connect to HTTP text/event-stream endpoints with automated background thread streaming:

```python
live_feed = tin.use_sse("https://stream.wikimedia.org/v2/stream/recentchange")

# UI element auto-refreshes whenever an SSE packet arrives
tin.Text(text=live_feed, color="neon-cyan")
```

---

### 14.3 Native OS Platform Channel (`PlatformBridge`)

`tin.PlatformBridge` provides zero-copy C-FFI and native OS shell integrations across Windows (Win32), macOS (Cocoa), and Linux (GTK).

#### Method Specifications:

```python
# 1. Native File Dialog (Open File)
# Returns absolute filepath string or None if cancelled
selected_path: Optional[str] = tin.PlatformBridge.open_file_dialog()

# 2. Native File Dialog (Save File)
# Returns destination filepath string or None if cancelled
save_path: Optional[str] = tin.PlatformBridge.save_file_dialog()

# 3. Native Desktop Toast / Alert Notification
tin.PlatformBridge.show_notification(title="Build Success", message="Packaging complete!")

# 4. Haptic Feedback Pulse (Mobile / Touch Devices)
tin.PlatformBridge.vibrate(pattern_ms=50)

# 5. OS Clipboard Synchronization
tin.PlatformBridge.copy_clipboard("Data to Clipboard")
```

---

### 14.4 Dynamic Intermediate Representation Export (`app.export_ir`)

The `export_ir()` method on `tin.App` serializes the current Python component hierarchy into a deterministic Intermediate Representation JSON (`app.ir.json`). This JSON is directly consumed by `tinui_engine.wasm` for static deployment on CDNs without a Python backend.

#### Python to WebAssembly Pipeline:
```python
import tinpyui as tin

# 1. Compose UI in pure Python
app = tin.Window(title="Compiled WASM App", width=1280, height=800)
with app:
    with tin.Section():
        tin.Heading(text="High-Performance Edge App", size="hero")
        tin.GradientText("Hardware-Accelerated WebAssembly", gradient=["#00f2fe", "#9b51e0"])
        tin.Button(text="Launch Pipeline", variant="neon-cyan")

# 2. Export IR blueprint directly to public/ distribution folder
app.export_ir("public/app.ir.json")
```

The exported `app.ir.json` file contains the complete declarative blueprint:
```json
{
  "title": "Compiled WASM App",
  "width": 1280,
  "height": 800,
  "bg_color": "#0D0D10",
  "root": {
    "tag": "Window",
    "props": {"title": "Compiled WASM App"},
    "children": [
      {
        "tag": "Section",
        "props": {},
        "children": [
          {"tag": "Heading", "props": {"text": "High-Performance Edge App", "size": "hero"}, "children": []},
          {"tag": "GradientText", "props": {"text": "Hardware-Accelerated WebAssembly"}, "children": []},
          {"tag": "Button", "props": {"text": "Launch Pipeline", "variant": "neon-cyan"}, "children": []}
        ]
      }
    ]
  }
}
```

---

## Chapter 15: Full-Stack Architecture & Production Recipes

### 15.1 Real-World 50-Line Full-Stack Enterprise Application
The following complete application demonstrates **PostgreSQL/MongoDB Database connection**, **WebSocket live streaming**, **Reactive LiveQuery**, and **1-Line CRUD Generation**:

```python
import tinpyui as tin

# 1. Connect to PostgreSQL or MongoDB with fallback
db = tin.connect("postgres://admin:secret@localhost:5432/enterprise_db")
orders = db.table("orders")

# 2. Real-time WebSocket connection for market events
market_ws = tin.use_socket("wss://api.marketdata.com/stream")

# 3. Persistent user preferences
settings = tin.use_store("app_settings.db")
theme = settings.signal("theme", default="cyber-dark")

# 4. Live Reactive Queries
active_orders = orders.live_query(status="processing")

# 5. Declarative UI Tree
app = tin.Window(title="Enterprise Command Console", width=1400, height=900)
with app:
    with tin.Row(padding=20, gap=20):
        # Left Panel: Live Stream & Controls
        with tin.Column(width=400, gap=16):
            tin.Heading("MARKET FEED", size="md", color="#00f2fe")
            tin.Card(padding=16):
                tin.Text(text=lambda: f"Socket: {market_ws.status.value}")
                tin.Text(text=lambda: f"Ticker: {market_ws.message.value}")
            
            tin.Button(
                "Create Sample Order", 
                on_click=lambda: orders.insert(customer="Client Alpha", amount=2450.0, status="processing")
            )
            tin.Button(
                "Export Database to CSV",
                on_click=lambda: orders.export_csv("orders", tin.PlatformBridge.save_file_dialog() or "orders.csv")
            )

        # Right Panel: 1-Line Live Data Table & AutoCRUD
        with tin.Column(width="flex", gap=16):
            tin.AutoCRUD(orders, title="Live Order Processing Pipeline")

if __name__ == "__main__":
    tin.run(app)
```

---
*(End of Official Manual — TinPyUI Engine v1.6.0)*
