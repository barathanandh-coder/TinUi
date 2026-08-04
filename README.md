# TinPyUI Framework v1.5.2

[![npm](https://img.shields.io/badge/npm-tinpyui-v1.5.2-cyan)](https://www.npmjs.com/package/tinpyui)
[![pypi](https://img.shields.io/badge/pypi-tinpyui--ff-v1.5.2-blue)](https://pypi.org/project/tinpyui-ff/)
[![license](https://img.shields.io/badge/license-MIT-green)](#license)
[![architecture](https://img.shields.io/badge/engine-Zero--DOM--Wasm-purple)](#architecture)

TinPyUI is a memory-safe, blazing-fast, and custom UI compilation framework. It completely bypasses Virtual DOM diffing by leveraging a custom Go WebAssembly linear memory engine mapped to a declarative, Pythonic syntax (`.tin`).

This is not a React clone. TinPyUI is a ground-up systems engineering project featuring its own Lexer, Parser, Intermediate Representation (IR) Compiler, and Wasm runtime.

---

## 📦 Installation

### 1. NPM Package (Universal CLI)
The core TinPyUI compiler CLI is distributed globally via NPM. Install it with:

```bash
npm install -g tinpyui
```
*Note: Requires Node.js (>= 18.0.0).*

### 2. PyPI Package (Python Ecosystem)
For Python developers and Flask integration:

```bash
pip install tinpyui-ff
```

### 3. VS Code Syntax Highlighting
To enable official syntax highlighting for `.tin` files:
1. Download the latest `.vsix` from the [tinui-syntax](file:///c:/Users/barat/Portfolio_Projects/TinUi/tinui-syntax) directory or Releases.
2. Open VS Code and open Extensions (`Ctrl+Shift+X`).
3. Click `...` > **Install from VSIX...** and select the `.vsix` package.

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

Below is the production-ready reference blueprint for TinPyUI v1.5.2 applications:

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
