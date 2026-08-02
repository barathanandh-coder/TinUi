# TinPyUI Framework

TinPyUI is a memory-safe, blazing-fast, and entirely custom UI framework. It completely bypasses Virtual DOM diffing by leveraging a custom Go WebAssembly linear memory engine mapped to a declarative Python-like syntax (`.tin`).

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

---

## 🚀 The Developer Workflow

### Step 1: Initialize a New Workspace
```bash
tinpyui init my-cyber-app
cd my-cyber-app
```
This scaffolds your `main.tin` configuration layout, `tinpy.toml`, and the essential `public/` web assembly bootloader files automatically.

### Step 2: Write Your UI
Edit `main.tin` using strict Pythonic and declarative rules, invoking rich components like `AnimatedBackground`, `Row`, or `GradientText`. Zero CSS overhead.

### Step 3: Compile the Layout
```bash
tinpyui compile main.tin
```
The internal style compiler traverses your configuration, executes dynamic translation, maps explicit color palettes, validates indentation precisely, and outputs a native `app.ir.json` payload.

### Step 4: Launch the Dev Server
```bash
tinpyui dev main.tin
```
Spin up the local dev server hosting your fully formed WebAssembly target instantly.

---

## 🧠 Architecture Overview: The Zero-Cost Wasm Runtime

When the Go WebAssembly runtime boots in the browser:
- It hydrates a `StateRegistry` tracking every variable.
- It allocates a 64-bit **Dirty Bitmap**. 
- When an event occurs (e.g., clicking a button or typing in an input), a JavaScript bridge triggers `TinUIDispatch` or `TinUIMutateState`.
- The Wasm engine mutates memory, flips a bit on the dirty bitmap, and runs `flushPatches()`.
- **The Result**: The DOM is patched surgically in $O(1)$ time. No tree walking. No diffing. Just microsecond pointer swaps.

---

## 📖 Detailed `.tin` Syntax and Usage Guide

TinPyUI uses a hierarchical, block-based grammar designed for rapid structural compilation. You do **not** write HTML, CSS, or JS. You strictly use `.tin` syntax.

### Grammar & Syntax Rules
1. **Root Block**: Every UI must be wrapped inside a `main { ... }` block (or `component ComponentName():` depending on engine version, but `main { ... }` is standard).
2. **Components**: All component names must be strictly PascalCase (e.g., `Section`, `GradientText`, `Button`).
3. **Properties (Props)**: Passed inside parentheses as `key: value` pairs, separated by commas.
   - Strings: `"Submit"`
   - Numbers: `42`
   - Booleans: `true`, `false`
   - Arrays: `["neon-cyan", "neon-purple"]`
4. **Nesting**: Child components are placed inside curly braces `{ ... }` immediately following the parent's properties.

#### Example Syntax:
```text
main {
    Section(paddingY: 40) {
        Heading(text: "Dashboard", color: "white")
        Text(text: "Welcome back.", size: "large")
    }
}
```

### Strict Layout Constraints (100% Width Rule)
By default, block-level interactive components (like `Form`, `Input`, and `Button`) will aggressively expand to consume **100% of the available width**.

**Constraint Rules to Prevent Visual Bugs:**
- **Never leave forms unconstrained**: Do not place inputs or buttons directly inside `main` without a wrapper, or they will stretch across the entire screen.
- **Use `maxWidth`**: Wrap interactive clusters inside a container (`Section` or `Card`) and explicitly define a `maxWidth`.
- **Horizontal Grouping**: To place buttons side-by-side, wrap them in a `Row` component.

#### Correct Constraint Example:
```text
Section(align: "center", justify: "center") {
    // The Card traps the inputs, preventing infinite stretching
    Card(maxWidth: 600, padding: 30) {
        Form(gap: 15) {
            Input(placeholder: "Email Address", width: "full")
            Input(placeholder: "Password", width: "full")
            Button(text: "Login", width: "full", variant: "primary")
        }
    }
}
```

---

## 🧩 Component API Reference

### 1. Structural Containers
*   **`Section(align: string, justify: string, paddingY: number, paddingBottom: number, maxWidth: number)`**
    The primary layout wrapper. Used to isolate different horizontal blocks of the webpage.
*   **`Card(maxWidth: number, padding: number, background: string, border: string, radius: number, shadow: string)`**
    A visually distinct container (glassmorphism/solid). Excellent for forms, pricing tiers, or feature highlights.
*   **`Row(gap: number, align: string, justify: string, width: string, marginTop: number)`**
    Forces child components to align horizontally using flexbox mechanics.
*   **`Form(gap: number)`**
    A vertical stack specifically designed to hold `Input` and `Button` elements.

### 2. Typography
*   **`Text(text: string, size: string, color: string, weight: string, marginTop: number, marginBottom: number)`**
    Standard paragraph text. Sizes include `"small"`, `"normal"`, `"large"`.
*   **`Heading(text: string, color: string, size: string)`**
    Standard header text. Sizes include `"h1"`, `"h2"`, `"h3"`.
*   **`GradientText(text: string, gradient: ["string", "string"], size: string)`**
    Renders text with a linear gradient. Primarily used for `"hero"` sizes.

### 3. Interactive Elements
*   **`Button(text: string, variant: string, glow: string, radius: string | number, width: string, link: string)`**
    Variants: `"solid"`, `"outline"`, `"primary"`. Radius can be a number (`8`) or a string (`"pill"`).
*   **`Input(value: string, placeholder: string, width: string, border: string)`**
    Data entry field. Recommended to use `width: "full"` inside a constrained parent.
*   **`NavLink(text: string, target: string)`**
    Navigation text that anchors to a section ID.

### 4. Advanced Wrappers (Visuals & Animation)
*   **`AnimatedBackground(effect: string, primaryColor: string, secondaryColor: string, speed: string)`**
    Effects: `"cyber-wave"`, `"cyber-grid"`, `"particles"`. Must wrap the entire page layout immediately inside the `main` block.
*   **`Navbar(padding: number, blur: boolean, borderBottom: string)`**
    Sticks to the top of the viewport. Supports glassmorphism (`blur: true`).
*   **`Icon(name: string, color: string)`**
    Renders an SVG vector natively.

---

## 🎨 Design System: Cyberpunk Theme

TinPyUI is optimized for modern, dark-mode-first developer aesthetics out of the box.

**Accepted Color Variables:**
*   **Backgrounds:** `"dark-core"` (`#0a0b10`), `"dark-glass"` (`rgba(18,19,28,0.7)`).
*   **Accents (Neon):** `"neon-cyan"` (`#00f2fe`), `"neon-purple"` (`#9b51e0`), `"neon-pink"` (`#ff007f`).
*   **Text:** `"white"`, `"muted"` (gray).

---

## 🚀 Full Page Example (The Standard Blueprint)

Below is the definitive blueprint for generating new layouts. Use this as a starting point for complex applications.

```text
main {
    AnimatedBackground(effect: "cyber-wave", primaryColor: "neon-purple", secondaryColor: "neon-cyan") {
        
        Navbar(padding: 20, blur: true) {
            Row(align: "center", justify: "space-between", width: "full") {
                Text(text: "AppLogo", color: "neon-cyan", weight: "bold")
                Row(gap: 30, color: "white") {
                    NavLink(text: "Features")
                    NavLink(text: "Docs")
                }
            }
        }

        Section(align: "center", paddingY: 100, maxWidth: 800, justify: "center") {
            GradientText(text: "The WASM UI Engine", gradient: ["neon-cyan", "neon-purple"], size: "hero")
            Text(text: "Build faster.", size: "large", color: "white", marginTop: 20)
            
            Row(gap: 20, align: "center", justify: "center", marginTop: 40) {
                Button(text: "Get Started", variant: "solid", glow: "neon-cyan", radius: "pill")
                Button(text: "Documentation", variant: "outline", radius: "pill")
            }
        }
    }
}
```

Enjoy building at the speed of memory.
