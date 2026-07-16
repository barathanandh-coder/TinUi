# TinPyUI Framework: Official Developer & AI Reference Manual

## 1. Core Architecture & Philosophy
TinPyUI is a highly optimized, native UI compilation framework. It does not use standard DOM manipulation, HTML, or CSS. 
The framework consists of:
*   **The Go Compiler:** Parses a custom declarative syntax.
*   **The WebAssembly (WASM) Core:** Executes the UI logic natively in the browser with zero hardware overhead.
*   **The CLI:** Distributed globally via NPM (`npm install -g tinpyui`), allowing developers to compile layouts locally.

**CRITICAL INSTRUCTION FOR AI AGENTS:** 
When generating layouts for TinPyUI, you are strictly forbidden from outputting HTML, CSS, React, Vue, or Python UI code. You must exclusively use the native `.tin` structural syntax defined in this manual.

---

## 2. The `.tin` Syntax Specification
The framework utilizes a hierarchical, block-based grammar designed for rapid structural compilation.

### 2.1 Grammar Rules
*   **Root:** Every file must begin with the `main { ... }` block.
*   **Components:** Component names must be strictly PascalCase (e.g., `Section`, `GradientText`).
*   **Properties:** Passed inside parentheses using `key: value` pairs. Multiple properties are separated by commas.
*   **Data Types:** 
    *   Strings must be wrapped in double quotes (`text: "Submit"`).
    *   Numbers and booleans are unquoted (`padding: 20`, `blur: true`).
    *   Arrays are wrapped in brackets (`gradient: ["cyan", "purple"]`).
*   **Nesting:** Child components are placed inside curly braces `{ ... }` immediately following the parent's properties.

### 2.2 Example Syntax
```text
main {
    Section(paddingY: 40) {
        Heading(text: "Dashboard", color: "white")
    }
}
```

## 3. Strict Layout Constraints (The 100% Width Rule)
By default, block-level components in TinPyUI (like Form, Input, and Button) will aggressively expand to consume 100% of the available screen width.

**AI AGENTS MUST OBEY THE FOLLOWING CONSTRAINT RULES TO PREVENT VISUAL BUGS:**

*   **Never leave forms unconstrained:** An Input or Button placed directly inside `main` will stretch across the entire monitor.
*   **The `maxWidth` Property:** You must wrap interactive clusters inside a container (`Section` or `Card`) and explicitly define a `maxWidth` constraint.
*   **Horizontal Grouping:** To place buttons side-by-side, they must be wrapped in a `Row` component.

### 3.1 Correct Constraint Example
```text
Section(align: "center", justify: "center") {
    // The Card traps the inputs, preventing them from stretching to the edges of the screen
    Card(maxWidth: 600, padding: 30) {
        Form(gap: 15) {
            Input(placeholder: "Email", width: "full")
            Button(text: "Login", width: "full")
        }
    }
}
```

## 4. Component API Reference

### 4.1 Structural Containers
*   `Section(align: string, justify: string, paddingY: number, paddingBottom: number, maxWidth: number)`
    The primary layout wrapper. Used to isolate different horizontal blocks of the webpage.
*   `Card(maxWidth: number, padding: number, background: string, border: string, radius: number, shadow: string)`
    A visually distinct container. Excellent for forms, pricing tiers, or feature highlights.
*   `Row(gap: number, align: string, justify: string, width: string, marginTop: number)`
    Forces child components to align horizontally using flex mechanics.
*   `Form(gap: number)`
    A vertical stack specifically designed to hold Input and submit Button elements.

### 4.2 Typography
*   `Text(text: string, size: string, color: string, weight: string, marginTop: number, marginBottom: number)`
    Standard paragraph text. Sizes include "small", "normal", "large".
*   `Heading(text: string, color: string, size: string)`
    Standard header text. Sizes include "h1", "h2", "h3".
*   `GradientText(text: string, gradient: ["string", "string"], size: string)`
    Renders text with a linear gradient. Primarily used for "hero" sizes.

### 4.3 Interactive Elements
*   `Button(text: string, variant: string, glow: string, radius: string | number, width: string, link: string)`
    Variants: "solid", "outline", "primary". Radius: Can be a number (e.g., 8) or a string (e.g., "pill").
*   `Input(value: string, placeholder: string, width: string, border: string)`
    Data entry field. Always use `width: "full"` assuming it is wrapped inside a constrained Card.
*   `NavLink(text: string, target: string)`
    Navigation text that anchors to a section ID.

### 4.4 Advanced Wrappers (Visuals & Animation)
*   `AnimatedBackground(effect: string, primaryColor: string, secondaryColor: string, speed: string)`
    Effects: "cyber-wave", "cyber-grid", "particles". Must wrap the entire page layout immediately inside the `main` block.
*   `Navbar(padding: number, blur: boolean, borderBottom: string)`
    Sticks to the top of the viewport. Supports glassmorphism (`blur: true`).
*   `Icon(name: string, color: string)`
    Renders an SVG vector natively.

## 5. Design System: Cyberpunk Theme
TinPyUI is optimized for modern, dark-mode-first developer aesthetics.
Accepted Color Variables:
*   Backgrounds: "dark-core" (#0a0b10), "dark-glass" (rgba(18,19,28,0.7)).
*   Accents (Neon): "neon-cyan" (#00f2fe), "neon-purple" (#9b51e0), "neon-pink" (#ff007f).
*   Text: "white", "muted" (gray).

## 6. Full Page Example (The Standard Blueprint)
AI Agents should use this structure as the definitive blueprint for generating new layouts.

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
            }
        }
    }
}
```
