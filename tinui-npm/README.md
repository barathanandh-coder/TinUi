# TinPyUI

> The WebAssembly UI framework that compiles **Pythonic, indentation-based syntax** into blazing-fast native DOM.

[![npm](https://img.shields.io/badge/npm-tinpyui-v1.5.2-cyan)](https://www.npmjs.com/package/tinpyui)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/barathanandh-coder/tinui/blob/main/LICENSE)

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

### WebAssembly Runtime

A Go-compiled WASM engine executes your UI logic at near-native speed. One install gives you a compiler, dev server, and runtime — zero external dependencies.

### 3D & Animation Ready

Built-in components for 3D scenes, particle systems, scroll-triggered animations, and glassmorphism — no external libraries needed.

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

Or manually:

```bash
tinpyui compile src/index.tin
tinpyui serve
```

Then open [http://localhost:3000](http://localhost:3000)

---

## 📝 Syntax Overview

### Components

```tin
# Self-closing
Text(text="Hello", color="white")

# With children (note the colon)
Section(align="center"):
    Text(text="Title")
    Text(text="Subtitle")
```

### State & Events

```tin
component Counter():
    state:
        count = 0

    Row(gap=12, align="center"):
        Button(text="-", onClick="decrement")
        Text(text="Count: " + count, size="large")
        Button(text="+", onClick="increment")

    function decrement():
        count = count - 1

    function increment():
        count = count + 1
```

### Two-Way Binding

```tin
Input(placeholder="Type here", dataBind="username")
Text(text="Hello, " + username)
```

### Conditionals

```tin
if isLoggedIn:
    Text(text="Welcome back!")
else:
    Button(text="Log In", action="login")
```

### Loops

```tin
for product in products:
    ProductCard(key=product.id, name=product.name, price=product.price)
```

### Custom Components

```tin
component Button(text, color="neon-cyan"):
    Text(
        text=text,
        color="black",
        bg=color,
        padding="12px 24px",
        radius=8,
        weight="bold"
    )

# Usage
Button(text="Click Me", color="neon-pink")
```

---

## 🎨 Built-in Components

### Layout
| Component | Purpose |
|-----------|---------|
| `Section` | Content section with id, padding, alignment |
| `Row` | Horizontal flex container |
| `Column` | Vertical flex container |
| `Grid` | CSS grid layout |
| `Spacer` | Empty space |

### UI
| Component | Purpose |
|-----------|---------|
| `Text` | Typography with color, size, weight |
| `Navbar` | Top navigation bar |
| `NavLink` | Navigation anchor link |
| `Footer` | Page footer |
| `Input` | Form input with data binding |
| `Button` | Clickable button |

### Visual
| Component | Purpose |
|-----------|---------|
| `AnimatedBackground` | Dynamic animated backgrounds |
| `GradientText` | Gradient-colored text |
| `NeonButton` | Glowing neon button |
| `BlackHoleLogo` | Animated black hole with accretion disk |
| `NeonBadge` | Glowing status badge |
| `NeonBox` | Glowing container box |

### Cards
| Component | Purpose |
|-----------|---------|
| `FeatureCard` | Icon + title + description card |
| `ReviewCard` | Avatar + stars + quote card |
| `DemoCard` | Titled demo container |
| `GlassCard` | Glassmorphism backdrop-blur card |
| `TiltCard` | 3D tilt-on-hover card |

### Animation
| Component | Purpose |
|-----------|---------|
| `ScrollTrigger` | Scroll-based animation triggers |
| `ParallaxLayer` | Multi-layer parallax scrolling |
| `TextReveal` | Character-by-character text reveal |
| `InfiniteMarquee` | Infinite scrolling text |
| `MorphShape` | SVG path morphing |

### 3D
| Component | Purpose |
|-----------|---------|
| `Scene3D` | WebGL 3D scene container |
| `Mesh3D` | 3D mesh objects (box, sphere, torus, etc.) |
| `Light3D` | 3D lighting (point, directional, spot) |
| `ParticleSystem3D` | GPU particle effects |
| `Model3D` | Load GLTF/GLB/OBJ models |

---

## 🛠️ CLI Commands

| Command | Description |
|---------|-------------|
| `tinpyui init [dir]` | Scaffold a new project |
| `tinpyui compile <file>` | Compile `.tin` to IR + assets |
| `tinpyui dev <file>` | Dev server with file watching & live reload |
| `tinpyui serve [dir]` | Start static file server on port 3000 |
| `tinpyui --version` | Show version |
| `tinpyui --help` | Show help |

---

## 🧩 Project Structure

```
my-app/
├── src/
│   └── index.tin          # Your app source (EDIT THIS)
├── public/                # Generated by compiler (DO NOT EDIT)
│   ├── index.html
│   ├── wasm_exec.js
│   ├── tinui_engine.wasm
│   └── app.ir.json
├── tinpyui.config.json    # Compiler config
└── app.py                 # Optional Flask server
```

> **Rule:** Only edit files in `src/`. Everything in `public/` is auto-generated by `tinpyui compile`.

---

## 📦 IDE Support

TinPyUI ships with a Python type stub file (`tinpyui.pyi`) for full autocomplete support in VS Code and PyCharm.

```bash
# VS Code will automatically pick up tinpyui.pyi
# Make sure your .tin files are associated with Python syntax
```

---

## 🔗 Links

| Resource | URL |
|----------|-----|
| npm Package | [https://www.npmjs.com/package/tinpyui](https://www.npmjs.com/package/tinpyui) |
| GitHub Repo | [https://github.com/barathanandh-coder/tinui](https://github.com/barathanandh-coder/tinui) |
| Issues | [https://github.com/barathanandh-coder/tinui/issues](https://github.com/barathanandh-coder/tinui/issues) |

---

## 📝 License

MIT © 2026 Barathanandh
