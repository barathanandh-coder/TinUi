import os
import shutil
import subprocess

SHOWCASE_DIR = r"C:\Users\barat\Portfolio_Projects\Showcase"
PUBLIC_DIR = os.path.join(SHOWCASE_DIR, "public")
TINUI_DIR = r"c:\Users\barat\Portfolio_Projects\TinUi"

# 1. Update public/index.html with all styling, morphisms, reveal animations, and redirect overlay
index_html = """<!DOCTYPE html>
<html class="dark" lang="en">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>TinPyUI v1.7.0 | High-Performance Python UI Engine</title>
    <meta name="description" content="TinPyUI is a zero-pip-dependency Python UI framework with Go AOT compilation, WebAssembly reactive DOM, hardware-accelerated WebGL shaders, dynamic scroll speed control, and live morphism sandboxes."/>
    <!-- Google Fonts: Space Grotesk, Outfit, Plus Jakarta Sans, Inter, JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <script id="tailwind-config">
      tailwind.config = {
        darkMode: 'class',
        theme: {
          extend: {
            colors: {
              background: '#07090e',
              surface: '#0d1117',
              'surface-card': '#131924',
              'surface-border': '#1e293b',
              brand: '#6366f1',
              'brand-light': '#818cf8',
              cyan: { 400: '#22d3ee', 500: '#06b6d4' },
              emerald: { 400: '#34d399', 500: '#10b981' },
              amber: { 400: '#fbbf24', 500: '#f59e0b' }
            },
            fontFamily: {
              sans: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
              display: ['Space Grotesk', 'Outfit', 'sans-serif'],
              mono: ['JetBrains Mono', 'monospace']
            }
          }
        }
      };
    </script>
    <style>
      /* Standardized Global Typography */
      body {
        background-color: #07090e;
        color: #f1f5f9;
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
        overflow-x: hidden;
        letter-spacing: -0.01em;
      }
      h1, h2, h3, h4, h5, h6, .font-display {
        font-family: 'Space Grotesk', 'Outfit', sans-serif !important;
        letter-spacing: -0.025em !important;
      }
      p, .font-sans {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
        letter-spacing: -0.01em;
        line-height: 1.6;
      }
      code, pre, .font-mono, input, .badge-mono {
        font-family: 'JetBrains Mono', monospace !important;
        letter-spacing: -0.02em;
      }
      #shader-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 0;
        pointer-events: none;
        opacity: 0.70;
        transition: opacity 0.5s ease;
      }
      #tinui-root {
        position: relative;
        z-index: 10;
        min-height: 100vh;
      }
      .glass-panel {
        background: rgba(13, 17, 23, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
      }
      .glass-card {
        background: rgba(19, 25, 36, 0.78);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.07);
      }
      .neon-border-cyan {
        border: 1px solid rgba(34, 211, 238, 0.35);
        box-shadow: 0 0 25px -5px rgba(6, 182, 212, 0.18);
      }
      .neon-border-purple {
        border: 1px solid rgba(168, 85, 247, 0.35);
        box-shadow: 0 0 25px -5px rgba(147, 51, 234, 0.18);
      }
      .neon-border-emerald {
        border: 1px solid rgba(52, 211, 153, 0.35);
        box-shadow: 0 0 25px -5px rgba(16, 185, 129, 0.18);
      }
      .code-preview {
        background: #090d14;
        border: 1px solid #1a2333;
        font-family: 'JetBrains Mono', monospace;
      }

      /* 1) Dynamic Morphism Classes */
      .glass-morphism {
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
      }
      .neu-morphism {
        background: #0d131f !important;
        box-shadow: 8px 8px 20px #04060a, -8px -8px 20px #162034 !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
      }
      .clay-morphism {
        background: #182234 !important;
        border-radius: 24px !important;
        box-shadow: inset 4px 4px 8px rgba(255, 255, 255, 0.12), inset -4px -4px 8px rgba(0, 0, 0, 0.6), 12px 12px 24px rgba(0, 0, 0, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
      }
      .holo-morphism {
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.15), rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.15)) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.28) !important;
        box-shadow: 0 0 30px rgba(34, 211, 238, 0.3), inset 0 0 20px rgba(168, 85, 247, 0.25) !important;
      }

      /* 2) While Scrolling Animation of Appearing Components */
      .reveal-on-scroll {
        opacity: 0;
        transform: translateY(36px);
        transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        will-change: opacity, transform;
      }
      .reveal-on-scroll.is-visible {
        opacity: 1 !important;
        transform: translateY(0) !important;
      }

      /* 5) Redirecting Animation to Next Page Overlay */
      #page-redirect-overlay {
        position: fixed;
        inset: 0;
        z-index: 99999;
        pointer-events: none;
        opacity: 0;
        backdrop-filter: blur(0px);
        background: radial-gradient(circle at center, rgba(14, 165, 233, 0.2), #07090e 80%);
        transition: opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1), backdrop-filter 0.4s ease;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      #page-redirect-overlay.active {
        pointer-events: auto;
        opacity: 1;
        backdrop-filter: blur(24px);
      }
      #page-redirect-overlay .shutter-left,
      #page-redirect-overlay .shutter-right {
        position: absolute;
        top: 0;
        bottom: 0;
        width: 50%;
        background: #07090e;
        transition: transform 0.5s cubic-bezier(0.77, 0, 0.175, 1);
      }
      #page-redirect-overlay .shutter-left {
        left: 0;
        transform: translateX(-100%);
      }
      #page-redirect-overlay .shutter-right {
        right: 0;
        transform: translateX(100%);
      }
      #page-redirect-overlay.active .shutter-left {
        transform: translateX(0);
      }
      #page-redirect-overlay.active .shutter-right {
        transform: translateX(0);
      }

      /* Grid Stage Background */
      .grid-stage {
        background-size: 24px 24px;
        background-image: 
          linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
      }

      ::-webkit-scrollbar { width: 8px; height: 8px; }
      ::-webkit-scrollbar-track { background: #07090e; }
      ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
      ::-webkit-scrollbar-thumb:hover { background: #334155; }
    </style>
</head>
<body class="min-h-screen relative antialiased selection:bg-cyan-500 selection:text-black">
    <!-- Cinematic Redirect Animation Overlay -->
    <div id="page-redirect-overlay">
      <div class="shutter-left"></div>
      <div class="shutter-right"></div>
      <div class="relative z-10 text-center space-y-5 max-w-md px-6">
        <div class="w-16 h-16 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto shadow-[0_0_25px_rgba(34,211,238,0.6)]"></div>
        <div>
          <div id="redirect-style-desc" class="text-xs font-mono text-cyan-400 tracking-widest uppercase mb-1">Engaging Quantum Warp Routing...</div>
          <div id="redirect-dest-title" class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">TRANSITIONING</div>
        </div>
        <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden border border-slate-700">
          <div id="redirect-progress-bar" class="bg-gradient-to-r from-cyan-400 via-indigo-500 to-purple-500 h-full w-0 transition-all duration-700 ease-out"></div>
        </div>
      </div>
    </div>

    <!-- TinPyUI Native Engine Mount Root -->
    <div id="tinui-root">
      <div class="flex items-center justify-center min-h-screen">
        <div class="text-center space-y-4">
          <div class="w-12 h-12 border-4 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p class="font-mono text-cyan-400 text-sm tracking-wider uppercase">Mounting TinPyUI Engine v1.7.0...</p>
        </div>
      </div>
    </div>

    <!-- WebAssembly & TinPyUI Runtime -->
    <script src="wasm_exec.js"></script>
    <script src="tin-runtime.js"></script>
</body>
</html>
"""

with open(os.path.join(PUBLIC_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
print("Updated public/index.html")

# 2. Copy showcase_tin_runtime.js to public/tin-runtime.js
shutil.copyfile("showcase_tin_runtime.js", os.path.join(PUBLIC_DIR, "tin-runtime.js"))
print("Copied showcase_tin_runtime.js to public/tin-runtime.js")

# 3. Write showcase.tin completely from scratch with all 5 features
showcase_tin = """component Main():
    Container(class_="selection:bg-cyan-500 selection:text-black min-h-screen relative"):
        # 1. Fullscreen WebGL Shader Background Canvas
        WebGLCanvas(id="shader-canvas", class_="fixed inset-0 w-full h-full pointer-events-none -z-10 block")
        Container(class_="fixed inset-0 pointer-events-none -z-[5] bg-gradient-to-b from-[#07090e]/80 via-[#07090e]/35 to-[#07090e]/95")
        Container(id="toast-container", class_="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none")

        # 2. Top Sticky Navigation Bar
        Navbar(class_="fixed top-0 w-full z-50 bg-[#0d1117]/90 backdrop-blur-xl border-b border-slate-800/80 shadow-2xl"):
            Container(class_="max-w-7xl mx-auto px-4 md:px-8 py-3.5 flex items-center justify-between"):
                # Brand
                Row(gap=12, align="center", class_="flex items-center gap-3"):
                    Link(href="#", class_="flex items-center gap-2.5 group no-underline"):
                        Container(class_="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 via-indigo-500 to-purple-600 flex items-center justify-center shadow-[0_0_16px_rgba(34,211,238,0.4)] group-hover:scale-105 transition-transform"):
                            Icon(name="terminal", class_="text-black text-xl font-bold")
                        Text(text="TinPyUI", class_="text-xl md:text-2xl font-extrabold tracking-tight text-white")
                    Badge(text="v1.7.0 WebAssembly & WebGL", class_="hidden sm:inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-mono font-semibold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30")

                # Center Nav Links
                Row(gap=20, class_="hidden xl:flex items-center gap-5 text-xs font-mono text-slate-400"):
                    Link(text="Scroll Speed", href="#scroll-hud", class_="hover:text-cyan-400 transition-colors no-underline")
                    Link(text="Adjuster Studio", href="#component-mover-studio", class_="hover:text-cyan-400 transition-colors no-underline")
                    Link(text="Morphisms", href="#morphisms", class_="hover:text-purple-400 transition-colors no-underline")
                    Link(text="Shaders", href="#shader-studio", class_="hover:text-indigo-400 transition-colors no-underline")
                    Link(text="Redirects", href="#redirects", class_="hover:text-emerald-400 transition-colors no-underline")
                    Link(text="Connectors", href="#connectors", class_="hover:text-slate-200 transition-colors no-underline")
                    Link(text="Benchmarks", href="#benchmarks", class_="hover:text-slate-200 transition-colors no-underline")

                # Trailing Actions
                Row(gap=12, align="center", class_="flex items-center gap-3 font-mono text-xs"):
                    Button(id="pip-install-btn", onClick="copyInstallCmd()", class_="hidden sm:flex items-center gap-2 bg-slate-900 border border-cyan-500/40 hover:border-cyan-400 text-cyan-300 px-3 py-1.5 rounded-lg shadow-[0_0_12px_rgba(6,182,212,0.15)] active:scale-95 transition-all"):
                        Icon(name="terminal", class_="text-sm")
                        Text(text="pip install tinpyui-ff")
                        Icon(name="content_copy", class_="text-sm")
                    Link(href="https://github.com/barathanandh-coder/TinUi", target="_blank", class_="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white transition-all no-underline"):
                        Icon(name="code", class_="text-sm text-cyan-400")
                        Text(text="GitHub", class_="font-bold text-xs")

        # 3. Hero Section
        Section(class_="pt-32 pb-14 px-4 md:px-8 max-w-7xl mx-auto relative"):
            Container(class_="text-center max-w-4xl mx-auto space-y-6"):
                # Release Tag
                Container(class_="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-mono font-medium shadow-[0_0_20px_rgba(6,182,212,0.15)]"):
                    Icon(name="verified", class_="text-sm text-cyan-400")
                    Text(text="v1.7.0 RELEASED - ZERO PIP DEPENDENCIES - GO AOT COMPILER - WEBGL SHADERS")

                # Main Headline
                Container(class_="space-y-2"):
                    Heading(text="Next-Gen Python UI Engine", class_="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white")
                    Heading(text="Powered by WebAssembly & Hardware Shaders", class_="text-3xl sm:text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent")

                # Subtitle
                Text(text="Build ultra-fast, modern reactive applications in pure Python. Compile declarative .tin templates to optimized IR via Go AOT, render via WebAssembly at 60+ FPS, and leverage native database connectors with zero external pip dependencies.", class_="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto font-normal leading-relaxed")

                # CTA Buttons
                Row(gap=16, justify="center", class_="flex flex-wrap items-center justify-center gap-4 pt-2"):
                    Link(href="#component-mover-studio", class_="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-black font-bold text-sm shadow-[0_0_25px_rgba(6,182,212,0.4)] hover:scale-105 active:scale-95 transition-all no-underline flex items-center gap-2"):
                        Icon(name="tune", class_="text-lg")
                        Text(text="Component Sandbox")
                    Link(href="#morphisms", class_="px-6 py-3 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-white font-semibold text-sm border border-slate-700 hover:border-slate-500 hover:scale-105 active:scale-95 transition-all no-underline flex items-center gap-2"):
                        Icon(name="auto_awesome", class_="text-lg text-purple-400")
                        Text(text="Explore Morphisms")

                # FEATURE 1: DYNAMIC SCROLLING SPEED CONTROL HUD
                Card(id="scroll-hud", class_="reveal-on-scroll mt-8 p-5 rounded-2xl glass-card neon-border-cyan max-w-3xl mx-auto text-left"):
                    Row(gap=8, justify="space-between", align="center", class_="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800"):
                        Row(gap=8, align="center", class_="flex items-center gap-2"):
                            Icon(name="speed", class_="text-cyan-400 text-xl")
                            Heading(text="Feature 1: Dynamic Scrolling Speed & Inertia Control", class_="text-base font-bold text-white")
                        Text(text="SCROLL VELOCITY: 1.0x", id="scroll-speed-label", class_="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30")

                    Container(class_="grid grid-cols-1 md:grid-cols-12 gap-4 pt-3 items-center"):
                        Container(class_="md:col-span-7 space-y-2"):
                            Text(text="ADJUST MOUSE WHEEL INERTIA / SPEED MULTIPLIER:", class_="text-[11px] font-mono text-slate-400 uppercase tracking-wider block")
                            Input(type="range", min="0.2", max="4.0", step="0.1", value="1.0", id="scroll-speed-slider", oninput="setScrollSpeedMultiplier(this.value)", class_="w-full accent-cyan-400 cursor-pointer")
                            Row(gap=6, class_="flex flex-wrap gap-2 text-xs font-mono pt-1"):
                                Button(text="0.5x Glide", onClick="setScrollSpeedMultiplier(0.5, this)", class_="scroll-speed-btn px-2.5 py-1 rounded bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white transition-all")
                                Button(text="1.0x Standard", onClick="setScrollSpeedMultiplier(1.0, this)", class_="scroll-speed-btn px-2.5 py-1 rounded bg-cyan-500/20 border border-cyan-400 text-cyan-300 font-bold transition-all")
                                Button(text="2.0x Turbo", onClick="setScrollSpeedMultiplier(2.0, this)", class_="scroll-speed-btn px-2.5 py-1 rounded bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white transition-all")
                                Button(text="3.5x Hyper", onClick="setScrollSpeedMultiplier(3.5, this)", class_="scroll-speed-btn px-2.5 py-1 rounded bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white transition-all")

                        Container(class_="md:col-span-5 flex flex-col gap-2 font-mono text-xs"):
                            Button(text="▶ Auto-Scroll Tour", id="auto-scroll-btn", onClick="toggleAutoScroll()", class_="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 border border-cyan-500/50 hover:border-cyan-400 text-cyan-300 font-bold flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(6,182,212,0.2)] transition-all")
                            Text(text="Experience smooth auto-flight through all UI sections at the selected velocity multiplier.", class_="text-[10px] text-slate-400 text-center")

                # FEATURE 2: WHILE SCROLLING ANIMATION OF APPEARING COMPONENTS (Metrics Cards)
                Grid(cols="4", gap=16, class_="grid grid-cols-2 lg:grid-cols-4 gap-4 pt-8 text-left font-mono"):
                    Card(class_="reveal-on-scroll glass-card p-4 rounded-xl border border-slate-800"):
                        Text(text="0 Pip Deps", class_="text-2xl font-bold text-cyan-400 block")
                        Text(text="Pure Python stdlib (ctypes, mmap, json)", class_="text-xs text-slate-400 mt-1 block")
                    Card(class_="reveal-on-scroll glass-card p-4 rounded-xl border border-slate-800"):
                        Text(text="46 / 46 Tests", class_="text-2xl font-bold text-emerald-400 block")
                        Text(text="100% automated test coverage passing", class_="text-xs text-slate-400 mt-1 block")
                    Card(class_="reveal-on-scroll glass-card p-4 rounded-xl border border-slate-800"):
                        Text(text="< 0.1 ms IPC", class_="text-2xl font-bold text-indigo-400 block")
                        Text(text="Zero-copy OS shared memory buffers", class_="text-xs text-slate-400 mt-1 block")
                    Card(class_="reveal-on-scroll glass-card p-4 rounded-xl border border-slate-800"):
                        Text(text="60+ FPS", class_="text-2xl font-bold text-purple-400 block")
                        Text(text="Hardware WebGL 2.0 fragment shaders", class_="text-xs text-slate-400 mt-1 block")

        # FEATURE 3: COMPONENT ADJUSTING AND MOVING COMPONENT SANDBOX
        Section(id="component-mover-studio", class_="reveal-on-scroll px-4 md:px-8 max-w-7xl mx-auto mb-24"):
            Card(class_="glass-card neon-border-cyan rounded-2xl p-6 md:p-8 shadow-2xl relative overflow-hidden"):
                Container(class_="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 border-b border-slate-800"):
                    Container():
                        Row(gap=8, align="center", class_="flex items-center gap-2"):
                            Icon(name="drag_pan", class_="text-cyan-400 text-2xl")
                            Heading(text="Feature 3: Component Adjusting & Moving Sandbox", class_="text-xl md:text-2xl font-bold text-white")
                        Text(text="Manipulate component coordinates, scale, padding, border radius, glow, and morphism live:", class_="text-sm text-slate-400 mt-1")
                    Container(class_="px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-[11px] font-mono text-cyan-400 font-bold uppercase"):
                        Text(text="Zero-DOM Live Transforms")

                Container(class_="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-6"):
                    # Controls Column
                    Container(class_="lg:col-span-5 space-y-4 font-mono text-xs"):
                        Text(text="COMPONENT PARAMETER ADJUSTERS:", class_="text-xs font-bold text-slate-300 uppercase tracking-wider block")
                        
                        Container(class_="bg-slate-900/90 p-3 rounded-xl border border-slate-800"):
                            Row(justify="space-between", class_="flex justify-between text-slate-400 mb-1"):
                                Text(text="OFFSET X: 0px", id="move-x-label", class_="text-cyan-400 font-bold")
                            Input(type="range", min="-100", max="100", step="2", value="0", id="x-slider", oninput="updateMovableComponent('x', this.value)", class_="w-full accent-cyan-400 cursor-pointer")

                        Container(class_="bg-slate-900/90 p-3 rounded-xl border border-slate-800"):
                            Row(justify="space-between", class_="flex justify-between text-slate-400 mb-1"):
                                Text(text="OFFSET Y: 0px", id="move-y-label", class_="text-cyan-400 font-bold")
                            Input(type="range", min="-60", max="60", step="2", value="0", id="y-slider", oninput="updateMovableComponent('y', this.value)", class_="w-full accent-cyan-400 cursor-pointer")

                        Container(class_="bg-slate-900/90 p-3 rounded-xl border border-slate-800"):
                            Row(justify="space-between", class_="flex justify-between text-slate-400 mb-1"):
                                Text(text="SCALE: 1.00x", id="scale-label", class_="text-indigo-400 font-bold")
                            Input(type="range", min="0.6", max="1.5", step="0.05", value="1.0", id="scale-slider", oninput="updateMovableComponent('scale', this.value)", class_="w-full accent-indigo-400 cursor-pointer")

                        Container(class_="bg-slate-900/90 p-3 rounded-xl border border-slate-800"):
                            Row(justify="space-between", class_="flex justify-between text-slate-400 mb-1"):
                                Text(text="CORNER RADIUS: 16px", id="radius-label", class_="text-purple-400 font-bold")
                            Input(type="range", min="0", max="48", step="2", value="16", id="radius-slider", oninput="updateMovableComponent('radius', this.value)", class_="w-full accent-purple-400 cursor-pointer")

                        Container(class_="bg-slate-900/90 p-3 rounded-xl border border-slate-800"):
                            Row(justify="space-between", class_="flex justify-between text-slate-400 mb-1"):
                                Text(text="GLOW HALO: 50%", id="glow-label", class_="text-emerald-400 font-bold")
                            Input(type="range", min="0", max="100", step="5", value="50", id="glow-slider", oninput="updateMovableComponent('glow', this.value)", class_="w-full accent-emerald-400 cursor-pointer")

                        Container(class_="pt-2 space-y-2"):
                            Text(text="APPLY MORPHISM STYLE:", class_="text-[11px] text-slate-400 uppercase tracking-wider block")
                            Row(gap=6, class_="flex flex-wrap gap-2"):
                                Button(text="Glass", onClick="setComponentMorphism('glass-morphism', this)", class_="morphism-choice-btn active px-3 py-1.5 rounded-lg bg-cyan-500/20 border border-cyan-400 text-cyan-300 font-bold transition-all")
                                Button(text="Neumorphic", onClick="setComponentMorphism('neu-morphism', this)", class_="morphism-choice-btn px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white transition-all")
                                Button(text="Claymorphic", onClick="setComponentMorphism('clay-morphism', this)", class_="morphism-choice-btn px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white transition-all")
                                Button(text="Holomorphic", onClick="setComponentMorphism('holo-morphism', this)", class_="morphism-choice-btn px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white transition-all")

                        Button(text="↺ Reset Component Transforms", onClick="resetMovableComponent()", class_="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white transition-all")

                    # Live Stage Column
                    Container(class_="lg:col-span-7 space-y-4"):
                        # Interactive Stage
                        Container(class_="grid-stage w-full min-h-[300px] rounded-2xl border border-slate-800 bg-[#07090e]/90 flex items-center justify-center p-6 relative overflow-hidden shadow-inner"):
                            # Movable Target Card
                            Card(id="movable-target-card", class_="transition-all duration-200 border relative overflow-hidden glass-morphism p-6 rounded-2xl max-w-sm w-full space-y-3 shadow-2xl"):
                                Row(gap=10, align="center", class_="flex items-center gap-3"):
                                    Container(class_="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-indigo-600 flex items-center justify-center text-black shadow-lg"):
                                        Icon(name="widgets", class_="text-xl font-bold")
                                    Container():
                                        Heading(text="Dynamic Movable Widget", class_="text-sm font-bold text-white")
                                        Badge(text="Reactive Transform Stream", class_="text-[10px] font-mono text-cyan-300")
                                Text(text="This component transforms smoothly in 2D space without re-rendering the DOM tree.", class_="text-xs text-slate-300 leading-relaxed")
                                Row(gap=8, class_="flex items-center justify-between pt-2 border-t border-slate-700/60 text-[11px] font-mono text-slate-400"):
                                    Text(text="Status: Active • 60 FPS")
                                    Text(text="TinPyUI Native")

                        # Live Code Preview
                        Container(class_="code-preview p-4 rounded-xl border border-slate-800 font-mono text-xs space-y-2"):
                            Text(text="Live Declarative .tin Code Output:", class_="text-cyan-400 font-bold block pb-1 border-b border-slate-800")
                            Text(text="Card(class_='glass-morphism rounded-[16px] p-[24px]', style='transform: translate(0px, 0px) scale(1.00)'):\\n    Text('Dynamic Movable UI Widget', color='cyan')\\n    Badge('Reactive State Stream', variant='neon-cyan')", id="component-live-code", class_="text-slate-300 block whitespace-pre")

        # FEATURE 4: TYPES OF MORPHISM GALLERY
        Section(id="morphisms", class_="reveal-on-scroll px-4 md:px-8 max-w-7xl mx-auto mb-24"):
            Container(class_="text-center max-w-2xl mx-auto mb-12"):
                Text(text="FEATURE 4: TYPES OF MORPHISM", class_="text-purple-400 text-xs font-mono font-bold tracking-widest uppercase block mb-2")
                Heading(text="The 4 Types of Modern UI Morphism", class_="text-3xl sm:text-4xl font-extrabold text-white")
                Text(text="Explore authentic visual aesthetics engineered for extreme clarity and modern contrast.", class_="text-slate-400 text-sm mt-2")

            Grid(cols="4", gap=24, class_="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"):
                # 1. Glassmorphism
                Card(class_="reveal-on-scroll glass-morphism p-6 rounded-2xl transition-transform hover:-translate-y-1 space-y-3"):
                    Badge(text="GLASSMORPHISM", class_="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/40")
                    Heading(text="Frosted Glass", class_="text-lg font-bold text-white")
                    Text(text="Features backdrop-filter blur, multi-layered translucency, luminous rim borders, and depth stacking.", class_="text-xs text-slate-300 leading-relaxed")
                    Container(class_="p-2.5 rounded-lg bg-black/30 font-mono text-[11px] text-cyan-300 border border-white/10"):
                        Text(text="backdrop-filter: blur(16px); background: rgba(15,23,42,0.65);")

                # 2. Neumorphism
                Card(class_="reveal-on-scroll neu-morphism p-6 rounded-2xl transition-transform hover:-translate-y-1 space-y-3"):
                    Badge(text="NEUMORPHISM", class_="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-slate-700/40 text-slate-300 border border-slate-600")
                    Heading(text="Soft Emboss", class_="text-lg font-bold text-white")
                    Text(text="Dual shadow balance simulating soft extruded physical material on a unified dark surface plane.", class_="text-xs text-slate-300 leading-relaxed")
                    Container(class_="p-2.5 rounded-lg bg-black/30 font-mono text-[11px] text-slate-300 border border-white/5"):
                        Text(text="box-shadow: 8px 8px 20px #04060a, -8px -8px 20px #162034;")

                # 3. Claymorphism
                Card(class_="reveal-on-scroll clay-morphism p-6 rounded-3xl transition-transform hover:-translate-y-1 space-y-3"):
                    Badge(text="CLAYMORPHISM", class_="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40")
                    Heading(text="3D Pillowed Clay", class_="text-lg font-bold text-white")
                    Text(text="Tactile 3D inflated pillowed depth using inner highlights and soft ambient floating cast shadows.", class_="text-xs text-slate-300 leading-relaxed")
                    Container(class_="p-2.5 rounded-lg bg-black/30 font-mono text-[11px] text-indigo-300 border border-white/10"):
                        Text(text="border-radius: 24px; box-shadow: inset 4px 4px 8px ...")

                # 4. Holomorphism
                Card(class_="reveal-on-scroll holo-morphism p-6 rounded-2xl transition-transform hover:-translate-y-1 space-y-3"):
                    Badge(text="HOLOMORPHISM", class_="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-pink-500/20 text-pink-300 border border-pink-500/40")
                    Heading(text="Prismatic Glow", class_="text-lg font-bold text-white")
                    Text(text="Chromatic dispersion with iridescent gradients, hyper-luminous border halos, and cosmic sheen.", class_="text-xs text-slate-300 leading-relaxed")
                    Container(class_="p-2.5 rounded-lg bg-black/30 font-mono text-[11px] text-pink-300 border border-white/10"):
                        Text(text="linear-gradient(135deg, cyan, purple); box-shadow: 0 0 30px rgba(...)")

        # FEATURE 4 (CONT): UNIQUE BACKGROUND HARDWARE SHADERS
        Section(id="shader-studio", class_="reveal-on-scroll px-4 md:px-8 max-w-7xl mx-auto mb-24"):
            Card(class_="glass-card neon-border-purple rounded-2xl p-6 md:p-8 shadow-2xl relative overflow-hidden backdrop-blur-xl"):
                Container(class_="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 border-b border-slate-800"):
                    Container():
                        Row(gap=8, align="center", class_="flex items-center gap-2"):
                            Icon(name="blur_on", class_="text-purple-400 text-2xl")
                            Heading(text="Unique Background Animations: WebGL 2.0 Shader Studio", class_="text-xl md:text-2xl font-bold text-white")
                        Text(text="Real-time GPU fragment shaders generating reactive background particle meshes and auroras:", class_="text-sm text-slate-400 mt-1")
                    Container(class_="px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-[11px] font-mono text-purple-400 font-bold uppercase"):
                        Text(text="WebGL 2.0 Active")

                Container(class_="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-6"):
                    # Preset selector buttons
                    Container(class_="lg:col-span-7 space-y-4"):
                        Text(text="SELECT GLSL FRAGMENT SHADER PRESET:", class_="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider block")
                        Row(gap=8, id="preset-buttons", class_="flex flex-wrap gap-2 text-xs font-mono"):
                            Button(text="black_hole", onClick="switchShaderPreset(this, 'black_hole')", class_="preset-btn active px-4 py-2.5 rounded-lg bg-cyan-500/20 border border-cyan-400 text-cyan-300 font-bold shadow-[0_0_15px_rgba(6,182,212,0.3)] transition-all")
                            Button(text="pillars_of_creation", onClick="switchShaderPreset(this, 'pillars_of_creation')", class_="preset-btn px-4 py-2.5 rounded-lg bg-slate-800/80 border border-slate-700 hover:border-amber-400 text-slate-300 hover:text-white transition-all")
                            Button(text="supernova_nebula", onClick="switchShaderPreset(this, 'supernova_nebula')", class_="preset-btn px-4 py-2.5 rounded-lg bg-slate-800/80 border border-slate-700 hover:border-purple-400 text-slate-300 hover:text-white transition-all")
                            Button(text="cyber_mesh", onClick="switchShaderPreset(this, 'cyber_mesh')", class_="preset-btn px-4 py-2.5 rounded-lg bg-slate-800/80 border border-slate-700 hover:border-cyan-400 text-slate-300 hover:text-white transition-all")
                            Button(text="aurora_flux", onClick="switchShaderPreset(this, 'aurora_flux')", class_="preset-btn px-4 py-2.5 rounded-lg bg-slate-800/80 border border-slate-700 hover:border-teal-400 text-slate-300 hover:text-white transition-all")
                            Button(text="off", onClick="switchShaderPreset(this, 'off')", class_="preset-btn px-4 py-2.5 rounded-lg bg-slate-800/80 border border-slate-700 hover:border-slate-500 text-slate-400 hover:text-white transition-all")

                        Container(id="shader-description", class_="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs font-mono text-slate-300"):
                            Text(text="Active: black_hole.frag - Relativistic Schwarzschild black hole with Doppler-beamed accretion disk & gravitational lensing.", id="shader-desc-text")

                        Container(class_="pt-2 space-y-2"):
                            Text(text="GPU PERFORMANCE MODE / LOAD CONTROL:", class_="text-[11px] font-mono text-slate-400 uppercase tracking-wider block")
                            Row(gap=6, class_="flex flex-wrap gap-2 text-xs font-mono"):
                                Button(text="Ultra-Eco (0.25x)", onClick="setGpuPerformanceMode(0.25, this)", class_="gpu-mode-btn px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white transition-all")
                                Button(text="Eco Mode (0.40x)", onClick="setGpuPerformanceMode(0.40, this)", class_="gpu-mode-btn active px-3 py-1.5 rounded-lg bg-cyan-500/20 border border-cyan-400 text-cyan-300 font-bold transition-all")
                                Button(text="Balanced (0.60x)", onClick="setGpuPerformanceMode(0.60, this)", class_="gpu-mode-btn px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white transition-all")
                                Button(text="Native (1.0x)", onClick="setGpuPerformanceMode(1.0, this)", class_="gpu-mode-btn px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white transition-all")

                    # Live Uniform Controls
                    Container(class_="lg:col-span-5 grid grid-cols-1 sm:grid-cols-2 gap-4 font-mono text-xs"):
                        Container(class_="bg-slate-900/90 p-4 rounded-xl border border-slate-800"):
                            Text(text="ANIM SPEED: 1.0x", id="speed-label", class_="text-cyan-400 font-bold mb-2 block")
                            Input(type="range", min="0.2", max="3.0", step="0.1", value="1.0", oninput="updateShaderSpeed(this.value)", class_="w-full accent-cyan-400 cursor-pointer")
                        Container(class_="bg-slate-900/90 p-4 rounded-xl border border-slate-800"):
                            Text(text="INTENSITY: 100%", id="intensity-label", class_="text-purple-400 font-bold mb-2 block")
                            Input(type="range", min="0.2", max="2.0", step="0.1", value="1.0", oninput="updateShaderIntensity(this.value)", class_="w-full accent-purple-400 cursor-pointer")

        # FEATURE 5: REDIRECTING ANIMATION TO NEXT PAGE
        Section(id="redirects", class_="reveal-on-scroll px-4 md:px-8 max-w-7xl mx-auto mb-24"):
            Card(class_="glass-card neon-border-emerald rounded-2xl p-6 md:p-8 shadow-2xl"):
                Container(class_="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 border-b border-slate-800"):
                    Container():
                        Row(gap=8, align="center", class_="flex items-center gap-2"):
                            Icon(name="near_me", class_="text-emerald-400 text-2xl")
                            Heading(text="Feature 5: Cinematic Redirecting Animations to Next Page", class_="text-xl md:text-2xl font-bold text-white")
                        Text(text="Engage cinematic shutter routing transitions between views with full progress pacing:", class_="text-sm text-slate-400 mt-1")
                    Container(class_="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[11px] font-mono text-emerald-400 font-bold uppercase"):
                        Text(text="Seamless Routing Engine")

                Container(class_="pt-6 space-y-4 font-mono text-xs"):
                    Text(text="TRIGGER CINEMATIC ROUTING TRANSITIONS (CLICK TO TEST):", class_="text-slate-400 uppercase tracking-wider block")
                    Row(gap=12, class_="flex flex-wrap gap-3"):
                        Button(text="🚀 Quantum Warp -> Features", onClick="triggerPageRedirect('Core Architectural Foundations', '#features', 'Quantum Warp')", class_="px-4 py-3 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-400 text-cyan-300 font-bold transition-all active:scale-95")
                        Button(text="⚡ Shutter -> Component Studio", onClick="triggerPageRedirect('Component Adjuster Studio', '#component-mover-studio', 'Hyper-Speed Shutter')", class_="px-4 py-3 rounded-xl bg-indigo-500/20 hover:bg-indigo-500/30 border border-indigo-400 text-indigo-300 font-bold transition-all active:scale-95")
                        Button(text="🌈 Prismatic -> Morphism Gallery", onClick="triggerPageRedirect('Morphism Showcase Gallery', '#morphisms', 'Prismatic Blur')", class_="px-4 py-3 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 border border-purple-400 text-purple-300 font-bold transition-all active:scale-95")
                        Button(text="🌐 Gateway -> PyPI Package", onClick="triggerPageRedirect('PyPI Official Repository', 'https://pypi.org/project/tinpyui-ff/', 'Gateway Tunnel')", class_="px-4 py-3 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-400 text-emerald-300 font-bold transition-all active:scale-95")
                        Button(text="📂 Quantum Portal -> GitHub", onClick="triggerPageRedirect('GitHub Source Repository', 'https://github.com/barathanandh-coder/TinUi', 'Quantum Portal')", class_="px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white font-bold transition-all active:scale-95")

        # 6. Core Architectural Foundations
        Section(id="features", class_="reveal-on-scroll px-4 md:px-8 max-w-7xl mx-auto mb-24"):
            Container(class_="text-center max-w-2xl mx-auto mb-12"):
                Text(text="CORE ARCHITECTURE", class_="text-cyan-400 text-xs font-mono font-bold tracking-widest uppercase block mb-2")
                Heading(text="The 4 Architectural Foundations of TinPyUI", class_="text-3xl sm:text-4xl font-extrabold text-white")
                Text(text="Engineered from scratch for speed, lightness, and developer joy.", class_="text-slate-400 text-sm mt-2")

            Grid(cols="4", gap=24, class_="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"):
                Card(class_="reveal-on-scroll glass-card p-6 rounded-2xl border border-slate-800 hover:border-cyan-500/50 transition-all"):
                    Container(class_="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-5"):
                        Icon(name="feather", class_="text-2xl")
                    Heading(text="Zero Pip Dependencies", class_="text-lg font-bold text-white mb-2")
                    Text(text="Pure Python using only standard library modules: ctypes, mmap, and json. No heavy wheels, no PyQt, no PySide, no Electron overhead.", class_="text-xs text-slate-400 leading-relaxed")

                Card(class_="reveal-on-scroll glass-card p-6 rounded-2xl border border-slate-800 hover:border-indigo-500/50 transition-all"):
                    Container(class_="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-5"):
                        Icon(name="bolt", class_="text-2xl")
                    Heading(text="Go AOT Compiler", class_="text-lg font-bold text-white mb-2")
                    Text(text="High-performance native Go binary compiles declarative .tin template syntax into compact, optimized JSON intermediate representation in single-digit milliseconds.", class_="text-xs text-slate-400 leading-relaxed")

                Card(class_="reveal-on-scroll glass-card p-6 rounded-2xl border border-slate-800 hover:border-purple-500/50 transition-all"):
                    Container(class_="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-5"):
                        Icon(name="integration_instructions", class_="text-2xl")
                    Heading(text="WebAssembly Core", class_="text-lg font-bold text-white mb-2")
                    Text(text="Compiled WebAssembly engine (tinui_engine.wasm) handles instant reactive reconciliation and DOM mounting with microsecond event routing.", class_="text-xs text-slate-400 leading-relaxed")

                Card(class_="reveal-on-scroll glass-card p-6 rounded-2xl border border-slate-800 hover:border-emerald-500/50 transition-all"):
                    Container(class_="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-5"):
                        Icon(name="sync_alt", class_="text-2xl")
                    Heading(text="Zero-Copy IPC", class_="text-lg font-bold text-white mb-2")
                    Text(text="Ultra-low-latency bidirectional IPC utilizing OS shared memory and memory-mapped files, delivering under 0.1ms frame transfers between Python and UI.", class_="text-xs text-slate-400 leading-relaxed")

        # 7. Native Database Connectors (tin.connect)
        Section(id="connectors", class_="reveal-on-scroll px-4 md:px-8 max-w-7xl mx-auto mb-24"):
            Card(class_="glass-card neon-border-emerald rounded-2xl p-6 md:p-8 shadow-2xl"):
                Container(class_="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-6 border-b border-slate-800"):
                    Container():
                        Row(gap=8, align="center", class_="flex items-center gap-2"):
                            Icon(name="database", class_="text-emerald-400 text-xl")
                            Heading(text="Native Database Connectors (tin.connect)", class_="text-xl md:text-2xl font-bold text-white")
                        Text(text="Built-in zero-boilerplate connectors for modern high-performance databases:", class_="text-sm text-slate-400 mt-1")
                    Container(class_="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[11px] font-mono text-emerald-400 font-bold uppercase"):
                        Text(text="tin.connect API")

                Container(class_="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-6"):
                    # Connector tabs
                    Container(class_="lg:col-span-4 space-y-2 font-mono text-xs"):
                        Button(text="DuckDB (Vectorized Analytics)", id="conn-duckdb-btn", onClick="runConnectorDemo('duckdb')", class_="w-full text-left px-4 py-3 rounded-xl bg-emerald-500/20 border border-emerald-500 text-emerald-300 font-bold transition-all")
                        Button(text="Redis (In-Memory Cache & PubSub)", id="conn-redis-btn", onClick="runConnectorDemo('redis')", class_="w-full text-left px-4 py-3 rounded-xl bg-slate-800/80 border border-slate-700 hover:border-emerald-400 text-slate-300 hover:text-white transition-all")
                        Button(text="ClickHouse (Columnar Telemetry)", id="conn-clickhouse-btn", onClick="runConnectorDemo('clickhouse')", class_="w-full text-left px-4 py-3 rounded-xl bg-slate-800/80 border border-slate-700 hover:border-emerald-400 text-slate-300 hover:text-white transition-all")
                        Button(text="SQLite (Embedded ACID Store)", id="conn-sqlite-btn", onClick="runConnectorDemo('sqlite')", class_="w-full text-left px-4 py-3 rounded-xl bg-slate-800/80 border border-slate-700 hover:border-emerald-400 text-slate-300 hover:text-white transition-all")

                    # Live Query Preview
                    Container(class_="lg:col-span-8 code-preview p-4 rounded-xl border border-slate-800 space-y-3 font-mono text-xs"):
                        Row(justify="space-between", align="center", class_="flex items-center justify-between pb-2 border-b border-slate-800"):
                            Text(text="Interactive Query Simulator", id="conn-demo-title", class_="text-emerald-400 font-bold")
                            Button(text="Execute Query", onClick="executeCurrentQuery()", class_="px-3 py-1 rounded bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 font-bold transition-all")
                        Text(text="from tinpyui import connect  # DuckDB vectorized analytics", id="conn-code-display", class_="text-slate-300 block whitespace-pre")
                        Container(class_="pt-2 border-t border-slate-800"):
                            Text(text="Query Result (simulated 0.04ms execution):", class_="text-[11px] text-slate-400 block mb-1")
                            Text(text="[ { 'region': 'us-east-1', 'avg_latency': 0.042 }, { 'region': 'eu-west-1', 'avg_latency': 0.051 } ]", id="conn-result-display", class_="text-emerald-400 font-bold block")

        # 8. Interactive Reactive State Playground
        Section(class_="reveal-on-scroll px-4 md:px-8 max-w-7xl mx-auto mb-24"):
            Grid(cols="2", gap=24, class_="grid grid-cols-1 md:grid-cols-2 gap-6"):
                # Widget 1: State Counter
                Card(class_="glass-card neon-border-purple p-6 rounded-2xl"):
                    Row(gap=8, align="center", class_="flex items-center gap-2 mb-4"):
                        Icon(name="tune", class_="text-purple-400 text-xl")
                        Heading(text="Reactive Signal Counter", class_="text-lg font-bold text-white")
                    Text(text="Direct signal reactivity without virtual DOM diffing. Mutate state with sub-millisecond updates:", class_="text-xs text-slate-400 mb-6")
                    Container(class_="flex items-center justify-center gap-6 py-4 bg-slate-900/80 rounded-xl border border-slate-800"):
                        Button(text="- Decrement", onClick="updateCounter(-1)", class_="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-mono text-sm border border-slate-700 active:scale-95 transition-all")
                        Text(text="42", id="reactive-counter-value", class_="text-4xl font-bold font-mono text-purple-400")
                        Button(text="+ Increment", onClick="updateCounter(1)", class_="px-4 py-2 rounded-lg bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 font-mono text-sm border border-purple-500/40 active:scale-95 transition-all")

                # Widget 2: Test Suite Verifier
                Card(class_="glass-card neon-border-cyan p-6 rounded-2xl"):
                    Row(gap=8, align="center", class_="flex items-center gap-2 mb-4"):
                        Icon(name="fact_check", class_="text-cyan-400 text-xl")
                        Heading(text="Test Suite Status (v1.7.0)", class_="text-lg font-bold text-white")
                    Text(text="46 automated unit tests validating compiler, IPC, connectors, and reactive core:", class_="text-xs text-slate-400 mb-4")
                    Container(class_="space-y-2 font-mono text-xs"):
                        Container(class_="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800"):
                            Text(text="tests/test_cli.py (14 tests)", class_="text-slate-300")
                            Badge(text="PASSED", class_="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold")
                        Container(class_="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800"):
                            Text(text="tests/test_v16_sample_project.py (18 tests)", class_="text-slate-300")
                            Badge(text="PASSED", class_="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold")
                        Container(class_="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800"):
                            Text(text="tests/test_duckdb.py (14 tests)", class_="text-slate-300")
                            Badge(text="PASSED", class_="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold")

        # 9. Real Performance Benchmarks
        Section(id="benchmarks", class_="reveal-on-scroll px-4 md:px-8 max-w-7xl mx-auto mb-24"):
            Container(class_="text-center max-w-2xl mx-auto mb-12"):
                Text(text="VERIFIED BENCHMARKS", class_="text-cyan-400 text-xs font-mono font-bold tracking-widest uppercase block mb-2")
                Heading(text="Engineered for Extreme Efficiency", class_="text-3xl sm:text-4xl font-extrabold text-white")
                Text(text="Measured on standard developer hardware against modern desktop and web frameworks.", class_="text-slate-400 text-sm mt-2")

            Grid(cols="3", gap=24, class_="grid grid-cols-1 md:grid-cols-3 gap-6 font-mono text-xs"):
                Card(class_="reveal-on-scroll glass-card p-6 rounded-2xl border border-slate-800 space-y-3"):
                    Text(text="Cold Boot Time", class_="text-slate-400 font-bold block text-sm")
                    Container(class_="space-y-2 pt-2"):
                        Container(class_="flex justify-between items-center"):
                            Text(text="TinPyUI", class_="text-cyan-400 font-bold")
                            Text(text="8 ms", class_="text-cyan-400 font-bold")
                        Container(class_="w-full h-2 rounded-full bg-slate-800 overflow-hidden"):
                            Container(class_="h-full bg-cyan-400 rounded-full w-[6%]")
                        Container(class_="flex justify-between items-center text-slate-400 pt-1"):
                            Text(text="PyQt6")
                            Text(text="450 ms")
                        Container(class_="flex justify-between items-center text-slate-400"):
                            Text(text="Electron")
                            Text(text="1,200 ms")

                Card(class_="reveal-on-scroll glass-card p-6 rounded-2xl border border-slate-800 space-y-3"):
                    Text(text="Baseline Memory", class_="text-slate-400 font-bold block text-sm")
                    Container(class_="space-y-2 pt-2"):
                        Container(class_="flex justify-between items-center"):
                            Text(text="TinPyUI", class_="text-emerald-400 font-bold")
                            Text(text="14 MB", class_="text-emerald-400 font-bold")
                        Container(class_="w-full h-2 rounded-full bg-slate-800 overflow-hidden"):
                            Container(class_="h-full bg-emerald-400 rounded-full w-[10%]")
                        Container(class_="flex justify-between items-center text-slate-400 pt-1"):
                            Text(text="PyQt6")
                            Text(text="65 MB")
                        Container(class_="flex justify-between items-center text-slate-400"):
                            Text(text="Electron")
                            Text(text="180 MB")

                Card(class_="reveal-on-scroll glass-card p-6 rounded-2xl border border-slate-800 space-y-3"):
                    Text(text="External Pip Deps", class_="text-slate-400 font-bold block text-sm")
                    Container(class_="space-y-2 pt-2"):
                        Container(class_="flex justify-between items-center"):
                            Text(text="TinPyUI", class_="text-indigo-400 font-bold")
                            Text(text="0 packages", class_="text-indigo-400 font-bold")
                        Container(class_="w-full h-2 rounded-full bg-slate-800 overflow-hidden"):
                            Container(class_="h-full bg-indigo-400 rounded-full w-[2%]")
                        Container(class_="flex justify-between items-center text-slate-400 pt-1"):
                            Text(text="PyQt6")
                            Text(text="80 MB+ binaries")
                        Container(class_="flex justify-between items-center text-slate-400"):
                            Text(text="Flet / Streamlit")
                            Text(text="15+ dependencies")

        # 10. Quick Start CLI Guide
        Section(id="quick-start", class_="reveal-on-scroll px-4 md:px-8 max-w-7xl mx-auto mb-28"):
            Card(class_="glass-card rounded-2xl p-6 md:p-8 shadow-2xl border border-slate-800"):
                Row(gap=8, align="center", class_="flex items-center gap-2 mb-2"):
                    Icon(name="terminal", class_="text-cyan-400 text-xl")
                    Heading(text="Quick Start Guide", class_="text-2xl font-bold text-white")
                Text(text="Get up and running with TinPyUI in three simple commands:", class_="text-sm text-slate-400 mb-6")

                Container(class_="space-y-4 font-mono text-xs"):
                    # Step 1
                    Container(class_="code-preview p-4 rounded-xl flex items-center justify-between"):
                        Container():
                            Text(text="# 1. Install from PyPI", class_="text-slate-500 block mb-1")
                            Text(text="pip install tinpyui-ff", class_="text-cyan-300 text-sm font-bold")
                        Button(text="Copy", onClick="copyToClipboard('pip install tinpyui-ff', 'Copied pip command!')", class_="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700")

                    # Step 2
                    Container(class_="code-preview p-4 rounded-xl flex items-center justify-between"):
                        Container():
                            Text(text="# 2. Create a new project", class_="text-slate-500 block mb-1")
                            Text(text="tinpyui create my-dashboard", class_="text-cyan-300 text-sm font-bold")
                        Button(text="Copy", onClick="copyToClipboard('tinpyui create my-dashboard', 'Copied create command!')", class_="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700")

                    # Step 3
                    Container(class_="code-preview p-4 rounded-xl flex items-center justify-between"):
                        Container():
                            Text(text="# 3. Compile and launch local dev server", class_="text-slate-500 block mb-1")
                            Text(text="cd my-dashboard && tinpyui serve", class_="text-cyan-300 text-sm font-bold")
                        Button(text="Copy", onClick="copyToClipboard('cd my-dashboard && tinpyui serve', 'Copied serve command!')", class_="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700")

        # 11. Clean Genuine Footer
        Navbar(class_="w-full border-t border-slate-800/80 bg-[#07090e] py-10"):
            Container(class_="max-w-7xl mx-auto px-4 md:px-8 flex flex-col md:flex-row items-center justify-between gap-6 font-mono text-xs text-slate-500"):
                Row(gap=8, align="center", class_="flex items-center gap-2"):
                    Text(text="TinPyUI v1.7.0")
                    Text(text="•")
                    Text(text="Open Source under MIT License")
                    Text(text="•")
                    Text(text="Created by Barathanandh")

                Row(gap=16, class_="flex items-center gap-4 text-slate-400"):
                    Link(text="GitHub", href="https://github.com/barathanandh-coder/TinUi", target="_blank", class_="hover:text-cyan-400 transition-colors no-underline")
                    Link(text="PyPI Package", href="https://pypi.org/project/tinpyui-ff/", target="_blank", class_="hover:text-cyan-400 transition-colors no-underline")
                    Link(text="npm Package", href="https://www.npmjs.com/package/tinpyui", target="_blank", class_="hover:text-cyan-400 transition-colors no-underline")
"""

# Write to Showcase/showcase.tin
with open(os.path.join(SHOWCASE_DIR, "showcase.tin"), "w", encoding="utf-8") as f:
    f.write(showcase_tin)
print("Updated Showcase/showcase.tin")

# Write also to TinUi/index.tin and TinUi/main.tin
with open(os.path.join(TINUI_DIR, "index.tin"), "w", encoding="utf-8") as f:
    f.write(showcase_tin)
with open(os.path.join(TINUI_DIR, "main.tin"), "w", encoding="utf-8") as f:
    f.write(showcase_tin)
print("Synchronized TinUi/index.tin and TinUi/main.tin")

# 4. Compile showcase.tin
print("Compiling showcase.tin via npm run compile...")
comp = subprocess.run(["npm.cmd", "run", "compile"], cwd=SHOWCASE_DIR, capture_output=True, text=True, encoding="utf-8")
print(comp.stdout.encode("ascii", errors="replace").decode("ascii"))
if comp.stderr:
    print("Stderr:", comp.stderr.encode("ascii", errors="replace").decode("ascii"))

# 5. Copy IR files
shutil.copyfile(os.path.join(SHOWCASE_DIR, "showcase.ir.json"), os.path.join(PUBLIC_DIR, "app.ir.json"))
shutil.copyfile(os.path.join(SHOWCASE_DIR, "showcase.ir.json"), os.path.join(PUBLIC_DIR, "showcase.ir.json"))
print("Successfully copied showcase.ir.json to public/app.ir.json and public/showcase.ir.json")

