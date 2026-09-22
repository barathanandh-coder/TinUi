import os
import json
import subprocess
from pathlib import Path

SHOWCASE_DIR = Path(r"C:\Users\barat\Portfolio_Projects\Showcase")
TINUI_DIR = Path(r"C:\Users\barat\Portfolio_Projects\TinUi")

print(f"Showcase directory exists: {SHOWCASE_DIR.exists()}")

# 1. Perfected showcase.tin
SHOWCASE_TIN = '''component Main():
    AnimatedBackground(effect = "pillars-of-creation", primaryColor = "neon-cyan", secondaryColor = "neon-purple", speed = "1"):
        
        # Navigation
        Navbar(class_ = "w-full fixed top-0 z-50 bg-[#03050c]/85 backdrop-blur-xl border-b border-amber-500/20 flex"):
            Row(justify = "space-between", align = "center", width = "full", class_ = "max-w-max-width mx-auto px-margin-desktop py-4 flex-1"):
                Link(href = "#", class_ = "font-display-lg font-bold tracking-tighter flex items-center gap-3 no-underline"):
                    Text(text = "TinPyUI", class_ = "text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-200 to-cyan-300 font-extrabold text-2xl tracking-tight")
                    Text(text = "PILLARS OF CREATION", class_ = "text-amber-300/80 font-mono text-[10px] tracking-widest uppercase px-2.5 py-1 rounded-full border border-amber-400/30 bg-amber-950/50")
                Row(gap = 32, class_ = "hidden md:flex items-center"):
                    Link(text = "Overview", href = "#", class_ = "text-sm font-semibold text-amber-300 hover:text-white transition-colors no-underline")
                    Link(text = "Features", href = "#features", class_ = "text-sm font-medium text-slate-300 hover:text-amber-300 transition-colors no-underline")
                    Link(text = "Performance", href = "#performance", class_ = "text-sm font-medium text-slate-300 hover:text-amber-300 transition-colors no-underline")
                    Link(text = "Components", href = "#components", class_ = "text-sm font-medium text-slate-300 hover:text-amber-300 transition-colors no-underline")
                    Link(text = "Documentation", href = "https://github.com/barathanandh-coder/TinUi", class_ = "text-sm font-medium text-slate-300 hover:text-amber-300 transition-colors no-underline")
                Row(gap = 16, align = "center"):
                    Link(text = "GitHub ★", href = "https://github.com/barathanandh-coder/TinUi", class_ = "text-xs font-mono font-bold px-3 py-1.5 rounded-lg border border-amber-400/40 text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 transition-all no-underline")

        # Hero Section
        Section(class_ = "relative min-h-[92vh] flex items-center overflow-hidden bg-transparent"):
            Grid(cols = "2", gap = 48, class_ = "container mx-auto px-margin-desktop items-center relative z-10 pt-20"):
                Container(class_ = "space-y-6"):
                    Row(gap = 8, align = "center", class_ = "inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-amber-400/30 bg-amber-500/10 backdrop-blur-md mb-2"):
                        Container(class_ = "w-2 h-2 rounded-full bg-amber-400 animate-ping")
                        Text(text = "M16 EAGLE NEBULA ENGINE ONLINE", class_ = "font-label-mono text-xs tracking-widest text-amber-300 font-semibold")
                    Heading(text = "Pillars of Creation.", size = "hero", class_ = "font-display-lg text-6xl md:text-7xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-white via-amber-100 to-amber-500 leading-[1.08] tracking-tight drop-shadow-[0_4px_24px_rgba(245,158,11,0.4)]")
                    Text(text = "The Celestial Limit of Zero-DOM Web Performance.", class_ = "font-label-mono text-xl md:text-2xl text-cyan-300 drop-shadow-[0_0_12px_rgba(34,211,238,0.4)] font-semibold")
                    Text(text = "Forged in the heart of the digital cosmos. TinPyUI bypasses virtual DOM tree recalculations, compiling Pythonic declarative syntax straight into raw WebGPU/WebGL instructions and 120 FPS WebAssembly kernels.", class_ = "font-body-lg text-slate-300 max-w-lg leading-relaxed text-base md:text-lg")
                    Row(gap = 16, class_ = "pt-4"):
                        Link(text = "Explore Features", href = "#features", onClick = "window.location.href='#features'", class_ = "bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-extrabold px-8 py-4 rounded-xl shadow-[0_0_30px_rgba(245,158,11,0.5)] hover:scale-105 hover:shadow-[0_0_40px_rgba(245,158,11,0.8)] transition-all inline-block cursor-pointer border border-amber-300/40 no-underline")
                        Link(text = "Get Started", href = "https://www.npmjs.com/package/tinpyui?activeTab=versions", class_ = "border border-cyan-400/60 text-cyan-300 px-8 py-4 font-bold rounded-xl hover:bg-cyan-500/10 hover:border-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.2)] transition-all inline-block cursor-pointer backdrop-blur-sm no-underline")
                Container():
                    # Empty column to frame towering background pillars

        # Live Features Gallery
        Section(id = "features", class_ = "py-28 relative px-margin-desktop max-w-max-width mx-auto bg-transparent"):
            Container(class_ = "mb-16 text-center md:text-left"):
                Text(text = "STELLAR FRAMEWORK CORE", class_ = "font-label-caps text-amber-400 tracking-widest block mb-4 font-mono font-bold")
                Heading(text = "Cosmic Performance Architecture", class_ = "font-display-lg text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-yellow-100 to-cyan-300 drop-shadow-[0_0_15px_rgba(245,158,11,0.4)]")
            
            Grid(cols = "3", gap = 32):
                # Feature 1
                Card(class_ = "bg-[rgba(8,12,28,0.65)] backdrop-blur-[20px] shadow-[0_8px_32px_rgba(0,0,0,0.5)] border border-[rgba(245,158,11,0.25)] p-0 group hover:-translate-y-2 hover:border-amber-400/60 hover:shadow-[0_0_30px_rgba(245,158,11,0.3)] transition-all duration-500 cursor-pointer overflow-hidden flex flex-col min-h-[420px] rounded-2xl"):
                    Container(class_ = "h-48 relative overflow-hidden bg-slate-950/70 border-b border-amber-500/20"):
                        ShaderLayer(effect = "cyber-grid")
                    Container(class_ = "p-8 flex-1 flex flex-col"):
                        Heading(text = "Zero-DOM Hardware Pipeline", class_ = "font-headline-md text-amber-200 text-xl font-bold mb-3")
                        Text(text = "Eliminates Document Object Model overhead entirely. Components compile to GPU vector bytecode painted at native hardware refresh rates.", class_ = "font-body-md text-slate-300 mb-8 flex-1 leading-relaxed text-sm")
                        Button(text = "Inspect Pipeline", onClick = "window.open('https://github.com/barathanandh-coder/TinUi/blob/main/README.md', '_blank')", class_ = "w-full py-3 bg-amber-500/15 border border-amber-400/30 text-amber-300 font-bold rounded-xl group-hover:bg-amber-500 group-hover:text-slate-950 transition-colors")

                # Feature 2
                Card(class_ = "bg-[rgba(8,12,28,0.65)] backdrop-blur-[20px] shadow-[0_8px_32px_rgba(0,0,0,0.5)] border border-[rgba(34,211,238,0.25)] p-0 group hover:-translate-y-2 hover:border-cyan-400/60 hover:shadow-[0_0_30px_rgba(34,211,238,0.3)] transition-all duration-500 cursor-pointer overflow-hidden flex flex-col min-h-[420px] rounded-2xl"):
                    Container(class_ = "h-48 relative overflow-hidden bg-slate-950/70 border-b border-cyan-500/20"):
                        ShaderLayer(effect = "fluid-sim")
                    Container(class_ = "p-8 flex-1 flex flex-col"):
                        Heading(text = "Pythonic Constellation Syntax", class_ = "font-headline-md text-cyan-200 text-xl font-bold mb-3")
                        Text(text = "Author reactive layouts with pristine Pythonic simplicity. Clean declarative semantics eliminate HTML boilerplate, CSS spaghetti, and JSX runtime tax.", class_ = "font-body-md text-slate-300 mb-8 flex-1 leading-relaxed text-sm")
                        Button(text = "View Syntax Guide", onClick = "window.open('https://github.com/barathanandh-coder/TinUi/blob/main/README.md', '_blank')", class_ = "w-full py-3 bg-cyan-500/15 border border-cyan-400/30 text-cyan-300 font-bold rounded-xl group-hover:bg-cyan-400 group-hover:text-slate-950 transition-colors")

                # Feature 3
                Card(class_ = "bg-[rgba(8,12,28,0.65)] backdrop-blur-[20px] shadow-[0_8px_32px_rgba(0,0,0,0.5)] border border-[rgba(168,85,247,0.25)] p-0 group hover:-translate-y-2 hover:border-purple-400/60 hover:shadow-[0_0_30px_rgba(168,85,247,0.3)] transition-all duration-500 cursor-pointer overflow-hidden flex flex-col min-h-[420px] rounded-2xl"):
                    Container(class_ = "h-48 relative overflow-hidden bg-slate-950/70 border-b border-purple-500/20"):
                        ShaderLayer(effect = "particles")
                    Container(class_ = "p-8 flex-1 flex flex-col"):
                        Heading(text = "Wasm & WebGPU Stellar Nursery", class_ = "font-headline-md text-purple-200 text-xl font-bold mb-3")
                        Text(text = "Unified WebAssembly compute kernel pushing 50,000+ spatial nodes with instant hydration fallback and sub-millisecond reactive signal propagation.", class_ = "font-body-md text-slate-300 mb-8 flex-1 leading-relaxed text-sm")
                        Button(text = "Benchmark Wasm", onClick = "window.open('https://github.com/barathanandh-coder/TinUi/blob/main/README.md', '_blank')", class_ = "w-full py-3 bg-purple-500/15 border border-purple-400/30 text-purple-300 font-bold rounded-xl group-hover:bg-purple-500 group-hover:text-slate-950 transition-colors")

        # Performance Lab
        Section(id = "performance", class_ = "py-28 bg-[#02040a]/60 backdrop-blur-md border-y border-amber-500/15"):
            Container(class_ = "max-w-max-width mx-auto px-margin-desktop"):
                Container(class_ = "text-center mb-16"):
                    Text(text = "ASTROPHYSICAL BENCHMARKS", class_ = "font-label-caps text-amber-400 tracking-widest block mb-4 font-mono font-bold")
                    Heading(text = "Performance Lab", class_ = "font-display-lg text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-amber-200 to-amber-400 drop-shadow-[0_0_12px_rgba(34,211,238,0.5)]")
                
                Grid(cols = "2", gap = 48):
                    Card(class_ = "bg-[rgba(10,14,28,0.65)] backdrop-blur-[16px] border border-red-500/30 p-10 relative rounded-3xl shadow-xl"):
                        Text(text = "STATUS: BOTTLENECKED", class_ = "absolute top-5 right-6 font-label-mono text-red-400 text-xs font-bold tracking-wider")
                        Heading(text = "Legacy Virtual DOM", class_ = "font-headline-md text-red-400 text-2xl font-bold mb-8")
                        Container(class_ = "space-y-6"):
                            Row(align = "end", gap = 16):
                                Text(text = "14", class_ = "font-display-lg text-7xl font-extrabold text-red-400 leading-none")
                                Text(text = "FPS", class_ = "font-label-mono text-slate-400 pb-2 font-bold")
                            Container(class_ = "h-3 w-full bg-red-500/15 rounded-full overflow-hidden"):
                                Container(class_ = "h-full bg-red-500 w-[14%]")
                            Text(text = "Reflow and tree-diffing overhead stalling the browser main thread during complex animation cycles.", class_ = "text-slate-400 text-sm font-body-md")

                    Card(class_ = "bg-[rgba(10,14,28,0.65)] backdrop-blur-[16px] border border-amber-400/40 p-10 relative rounded-3xl shadow-[0_0_35px_rgba(245,158,11,0.18)]"):
                        Row(align = "center", gap = 8, class_ = "absolute top-5 right-6"):
                            Container(class_ = "w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping")
                            Text(text = "STELLAR 120 FPS", class_ = "font-label-mono text-amber-300 text-xs font-bold tracking-wider")
                        Heading(text = "TinPyUI Wasm Core", class_ = "font-headline-md text-amber-300 text-2xl font-bold mb-8")
                        Container(class_ = "space-y-6"):
                            Row(align = "end", gap = 16):
                                Text(text = "120", class_ = "font-display-lg text-7xl font-extrabold text-amber-300 leading-none")
                                Text(text = "FPS", class_ = "font-label-mono text-slate-300 pb-2 font-bold")
                            Container(class_ = "h-3 w-full bg-amber-400/15 rounded-full overflow-hidden"):
                                Container(class_ = "h-full bg-gradient-to-r from-amber-400 to-cyan-400 w-full shadow-[0_0_20px_rgba(245,158,11,0.6)]")
                            Text(text = "Direct GPU pipeline via WebAssembly. Zero DOM interaction, 100% efficient vector pushing at native refresh rate.", class_ = "text-slate-300 text-sm font-body-md")

        # The Component Lab
        Section(id = "components", class_ = "py-28 bg-transparent"):
            Container(class_ = "max-w-max-width mx-auto px-margin-desktop text-center mb-16"):
                Heading(text = "The Component Lab", class_ = "font-display-lg text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-200 to-cyan-300 drop-shadow-[0_0_12px_rgba(245,158,11,0.5)]")
                Text(text = "Interactive primitives pulsing with reactive signals in the digital nebula.", class_ = "text-slate-300 mt-4 font-body-lg text-lg")
            
            Row(justify = "center", align = "center", gap = 48, class_ = "flex-wrap"):
                Container(class_ = "group flex flex-col items-center gap-4"):
                    Card(class_ = "w-48 h-48 rounded-3xl bg-[rgba(8,12,28,0.65)] backdrop-blur-[16px] border border-amber-400/25 flex items-center justify-center hover:scale-110 hover:border-amber-400 transition-all cursor-pointer relative overflow-hidden shadow-lg"):
                        Button(text = "Button()", class_ = "px-6 py-3 border-2 border-amber-400 text-amber-300 font-bold rounded-full animate-pulse shadow-[0_0_15px_rgba(245,158,11,0.35)]")
                    Text(text = "Interactive State", class_ = "font-label-mono text-amber-300 text-sm font-semibold")
                
                Container(class_ = "group flex flex-col items-center gap-4"):
                    Card(class_ = "w-48 h-48 rounded-3xl bg-[rgba(8,12,28,0.65)] backdrop-blur-[16px] border border-cyan-400/25 flex items-center justify-center hover:scale-110 hover:border-cyan-400 transition-all cursor-pointer relative overflow-hidden shadow-lg"):
                        GradientText(text = "STELLAR", class_ = "font-display-lg tracking-widest bg-clip-text text-transparent bg-gradient-to-r from-amber-300 via-yellow-100 to-cyan-300 font-extrabold text-2xl animate-pulse")
                    Text(text = "GradientText()", class_ = "font-label-mono text-cyan-300 text-sm font-semibold")

                Container(class_ = "group flex flex-col items-center gap-4"):
                    Card(class_ = "w-48 h-48 rounded-3xl bg-[rgba(8,12,28,0.65)] backdrop-blur-[16px] border border-purple-400/25 flex items-center justify-center hover:scale-110 hover:border-purple-400 transition-all cursor-pointer relative overflow-hidden group shadow-lg"):
                        Container(class_ = "w-24 h-24 border-2 border-dashed border-amber-400/50 rounded-full animate-spin flex items-center justify-center group-hover:border-amber-400 transition-colors"):
                            Icon(name = "flare", class_ = "text-amber-400 text-4xl drop-shadow-[0_0_12px_rgba(245,158,11,0.9)]")
                    Text(text = "PulsarLoader()", class_ = "font-label-mono text-amber-300 text-sm font-semibold")

        # Engine Blueprint Section
        Section(class_ = "py-28 bg-transparent"):
            Container(class_ = "max-w-max-width mx-auto px-margin-desktop"):
                Container(class_ = "mb-12"):
                    Text(text = "BLUEPRINT", class_ = "font-label-caps text-amber-400 tracking-widest block mb-4 font-mono font-bold")
                    Heading(text = "The Stellar Blueprint", class_ = "font-display-lg text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-white to-cyan-300 drop-shadow-[0_0_10px_rgba(245,158,11,0.4)]")
                
                Grid(cols = "2", class_ = "gap-px bg-amber-500/20 rounded-3xl overflow-hidden shadow-2xl border border-amber-500/30"):
                    Container(class_ = "bg-[#040610] p-8 font-label-mono text-sm leading-relaxed overflow-x-auto min-h-[460px] text-[#c9d1d9]"):
                        Row(gap = 8, align = "center", class_ = "mb-6"):
                            Row(gap = 6):
                                Container(class_ = "w-3 h-3 rounded-full bg-[#ff5f56]")
                                Container(class_ = "w-3 h-3 rounded-full bg-[#ffbd2e]")
                                Container(class_ = "w-3 h-3 rounded-full bg-[#27c93f]")
                            Text(text = "pillars_of_creation.tin", class_ = "text-amber-300/80 ml-4 text-xs font-mono")
                        Text(text = "component NebulaDashboard():\\n    AnimatedBackground(effect='pillars-of-creation', speed='1'):\\n        Container(align='center', justify='center', width='full', padding=32):\\n            GradientText(text='Pillars of Creation', animation='stellar-glow')\\n            Card(title='Telemetry 120 FPS', glow=True):\\n                Button(text='Ignite Nursery', color='cosmic-gold')\\n\\n# Zero-DOM hardware execution on WebAssembly\\nmount(NebulaDashboard)", class_ = "whitespace-pre text-amber-100/90")

                    Container(class_ = "relative bg-black/50 backdrop-blur-md flex items-center justify-center p-8 overflow-hidden"):
                        Card(class_ = "relative z-10 w-full max-w-sm bg-[rgba(8,12,28,0.7)] backdrop-blur-[20px] border border-amber-400/40 shadow-[0_0_30px_rgba(245,158,11,0.3)] p-10 text-center rounded-3xl"):
                            Text(text = "NEBULA STREAM ACTIVE", class_ = "font-display-lg text-amber-300 tracking-widest mb-6 font-bold text-lg bg-clip-text text-transparent bg-gradient-to-r from-amber-300 to-cyan-300")
                            Container(class_ = "flex flex-col gap-4"):
                                Container(class_ = "h-2 w-full bg-slate-800 rounded-full overflow-hidden"):
                                    Container(class_ = "h-full bg-gradient-to-r from-amber-400 to-cyan-400 w-3/4 shadow-[0_0_12px_rgba(245,158,11,1)] animate-pulse")
                                Row(justify = "space-between", class_ = "font-label-mono text-xs text-slate-300 w-full font-bold"):
                                    Text(text = "VECTOR THROUGHPUT")
                                    Text(text = "12.6 GB/S")
                            Button(text = "IONIZE VECTOR FIELD", class_ = "mt-8 w-full py-3 border border-amber-400/60 text-amber-300 font-bold rounded-xl hover:bg-amber-400 hover:text-slate-950 transition-all shadow-[0_0_15px_rgba(245,158,11,0.25)]")

        # CTA
        Section(class_ = "py-32 relative"):
            Container(class_ = "max-w-4xl mx-auto px-margin-mobile text-center"):
                Card(class_ = "bg-[rgba(8,12,28,0.7)] backdrop-blur-[24px] border border-amber-400/35 p-16 relative overflow-hidden rounded-3xl shadow-[0_0_50px_rgba(0,0,0,0.7)]"):
                    Heading(text = "Ready to forge across the stars?", class_ = "font-display-lg text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-yellow-100 to-cyan-300 drop-shadow-[0_0_18px_rgba(245,158,11,0.5)] mb-6 relative z-10")
                    Text(text = "Join developers worldwide creating ultra-performance Zero-DOM applications with pure Pythonic syntax and native GPU acceleration.", class_ = "text-slate-300 mb-10 font-body-lg max-w-xl mx-auto relative z-10 leading-relaxed text-base md:text-lg")
                    Row(justify = "center", gap = 24, class_ = "relative z-10 flex-col sm:flex-row"):
                        Link(text = "Submit Your Constellation", href = "https://github.com/barathanandh-coder/TinUi/discussions", class_ = "bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 border border-amber-300/40 px-12 py-5 font-extrabold rounded-2xl hover:scale-105 hover:shadow-[0_0_35px_rgba(245,158,11,0.7)] transition-all text-lg cursor-pointer no-underline inline-block")

        # Footer
        Footer(class_ = "bg-[#02040a]/90 backdrop-blur-xl py-12 border-t border-amber-500/20 w-full"):
            Row(justify = "space-between", align = "center", class_ = "max-w-max-width mx-auto px-margin-desktop flex-col md:flex-row gap-8 w-full"):
                Row(align = "center", gap = 12):
                    Heading(text = "TinPyUI", class_ = "font-headline-md text-amber-300 text-xl font-bold")
                    Text(text = "• Pillars of Creation Edition", class_ = "text-slate-400 text-sm")
                Row(gap = 24, class_ = "font-label-mono text-sm flex-wrap justify-center"):
                    Link(text = "NPM", href = "https://www.npmjs.com/package/tinpyui?activeTab=versions", class_ = "text-slate-400 hover:text-amber-300 transition-colors no-underline")
                    Link(text = "PyPI", href = "https://pypi.org/project/tinpyui-ff/", class_ = "text-slate-400 hover:text-amber-300 transition-colors no-underline")
                    Link(text = "GitHub", href = "https://github.com/barathanandh-coder/TinUi", class_ = "text-slate-400 hover:text-amber-300 transition-colors no-underline")
                    Link(text = "Discussions", href = "https://github.com/barathanandh-coder/TinUi/discussions", class_ = "text-slate-400 hover:text-amber-300 transition-colors no-underline")
                Container(class_ = "font-label-mono text-slate-400 text-right text-xs"):
                    Text(text = "© 2026 TinPyUI Framework. Zero-DOM Architecture.")
'''

# 2. Updated index.html with full Tailwind configuration and font preloads
INDEX_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TinPyUI Showcase — Pillars of Creation</title>
    <meta name="description" content="TinPyUI Universal Omni-Platform Zero-DOM WebAssembly & WebGL Showcase — Pillars of Creation Theme.">
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    <!-- Tailwind CSS Engine -->
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <script>
      tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            colors: {
              primary: "#f59e0b",
              secondary: "#06b6d4",
              tertiary: "#fbbf24",
              "surface-container-high": "rgba(15, 23, 42, 0.6)",
              "on-surface": "#f8fafc",
              "on-surface-variant": "#94a3b8"
            },
            spacing: {
              "margin-desktop": "2.5rem",
              "margin-mobile": "1rem",
              "max-width": "1440px"
            },
            fontFamily: {
              "label-mono": ["JetBrains Mono", "monospace"],
              "display-lg": ["Sora", "sans-serif"],
              "display-lg-mobile": ["Sora", "sans-serif"],
              "headline-md": ["Sora", "sans-serif"],
              "body-lg": ["Plus Jakarta Sans", "sans-serif"],
              "body-md": ["Plus Jakarta Sans", "sans-serif"]
            }
          }
        }
      };
    </script>
    <style>
      * { box-sizing: border-box; }
      html { scroll-behavior: smooth; }
      body {
        margin: 0;
        padding: 0;
        background-color: #03050c;
        color: #f8fafc;
        font-family: 'Plus Jakarta Sans', sans-serif;
        overflow-x: hidden;
      }
      [data-scroll-reveal] {
        opacity: 1;
      }
    </style>
</head>
<body>
    <div id="tinui-root">
        <!-- Wasm Engine / Instant Fallback mounts here -->
    </div>
    <script src="wasm_exec.js"></script>
    <script src="tin-runtime.js"></script>
</body>
</html>
'''

# 3. WebGL Runtime with majestic sculpted Pillars of Creation shader
TIN_RUNTIME_JS = '''// tin-runtime.js — TinPyUI v1.6.1 Runtime (Pillars of Creation Edition)
const go = new Go();

function _tinResolvePaletteColor(name) {
  const palette = {
    'neon-cyan': '#00f2fe', 'neon-purple': '#9b51e0', 'neon-pink': '#ff007f',
    'stellar-gold': '#f59e0b', 'cosmic-teal': '#06b6d4',
    'dark-core': '#03050c', 'white': '#ffffff', 'muted': '#94a3b8'
  };
  return palette[name] || name;
}

// --- WebGL Shader Utilities ---
function _tinCreateShaderProgram(gl, vs, fs) {
  function compile(type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.error('[TinPyUI WebGL] Shader compile error:', gl.getShaderInfoLog(s));
    }
    return s;
  }
  const prog = gl.createProgram();
  gl.attachShader(prog, compile(gl.VERTEX_SHADER, vs));
  gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    console.error('[TinPyUI WebGL] Program link error:', gl.getProgramInfoLog(prog));
  }
  return prog;
}

const _TIN_VERT_SHADER = `
  attribute vec2 a_position;
  varying vec2 v_uv;
  void main() {
    v_uv = a_position * 0.5 + 0.5;
    gl_Position = vec4(a_position, 0.0, 1.0);
  }
`;

// Built-in effect shaders
const _TIN_SHADERS = {
  'pillars-of-creation': `
    precision highp float;
    uniform float u_time;
    uniform vec2 u_resolution;
    uniform vec2 u_mouse;
    varying vec2 v_uv;

    float hash(vec2 p) {
      p = fract(p * vec2(123.34, 456.21));
      p += dot(p, p + 45.32);
      return fract(p.x * p.y);
    }

    float noise(vec2 p) {
      vec2 i = floor(p);
      vec2 f = fract(p);
      f = f * f * (3.0 - 2.0 * f);
      float a = hash(i);
      float b = hash(i + vec2(1.0, 0.0));
      float c = hash(i + vec2(0.0, 1.0));
      float d = hash(i + vec2(1.0, 1.0));
      return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
    }

    float fbm(vec2 p) {
      float v = 0.0;
      float a = 0.5;
      mat2 rot = mat2(0.8, 0.6, -0.6, 0.8);
      for (int i = 0; i < 5; i++) {
        v += a * noise(p);
        p = rot * p * 2.02 + vec2(42.1, 17.4);
        a *= 0.5;
      }
      return v;
    }

    // 6-Point JWST / Hubble Diffraction Spike Star
    float jwstStar(vec2 uv, vec2 pos, float size, float brightness) {
      vec2 d = uv - pos;
      float dist = length(d);
      if (dist > size * 5.0) return 0.0;
      float core = (size * 0.035) / (dist + 0.0005);
      core = smoothstep(0.0, 1.2, core);
      float spikes = 0.0;
      for (int i = 0; i < 3; i++) {
        float ang = float(i) * 1.04719755;
        vec2 dir = vec2(cos(ang), sin(ang));
        float proj = abs(dot(d, vec2(-dir.y, dir.x)));
        spikes += smoothstep(size * 0.025, 0.0, proj) * smoothstep(size * 4.5, 0.0, dist);
      }
      return (core + spikes * 0.8) * brightness;
    }

    void main() {
      vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
      float t = u_time * 0.03;
      vec2 m = (u_mouse - 0.5) * 0.1;
      vec2 p = uv - m;

      // 1. Cosmic Background Nebula (O III Cyan & H-alpha Deep Violet)
      float nebFbm1 = fbm(p * 1.5 + vec2(t * 0.15, -t * 0.08));
      float nebFbm2 = fbm(p * 2.8 - vec2(t * 0.1, t * 0.2));
      
      vec3 voidBlack  = vec3(0.015, 0.02, 0.045);
      vec3 deepTeal   = vec3(0.01, 0.42, 0.58);   // [O III] doubly ionized oxygen
      vec3 brightCyan = vec3(0.1, 0.82, 0.95);    // High excitation core
      vec3 cosmicPurp = vec3(0.35, 0.12, 0.48);   // Ionized hydrogen / sulfur

      float nebMask = smoothstep(0.28, 0.85, nebFbm1 * 0.7 + nebFbm2 * 0.5);
      vec3 sky = mix(voidBlack, deepTeal, nebMask * 0.85);
      sky = mix(sky, cosmicPurp, smoothstep(0.4, 0.9, nebFbm2) * 0.55);
      sky += brightCyan * pow(nebMask, 2.5) * 0.4;
      sky += vec3(0.04, 0.35, 0.55) * smoothstep(-0.8, 1.2, p.y) * 0.4;

      // 2. The Three Majestic Pillars of Creation (Towering Gas & Dust Columns)
      // Column 1 (Left Pillar): Center x around -0.48, rises to y ~ 0.32
      float c1_turb = fbm(vec2(p.x * 3.5, p.y * 2.2) + t * 0.06);
      float c1_x = -0.48 + sin(p.y * 2.0 + 1.0) * 0.08 + (c1_turb - 0.5) * 0.16;
      float c1_width = 0.22 - p.y * 0.06;
      float c1_dist = abs(p.x - c1_x);
      float c1_top = 0.32 + sin(p.x * 12.0) * 0.05;
      float c1_body = smoothstep(c1_width, c1_width * 0.6, c1_dist) * smoothstep(c1_top + 0.15, c1_top - 0.1, p.y);

      // Column 2 (Center Pillar - The Tallest): Center x around 0.12, rises to y ~ 0.72
      float c2_turb = fbm(vec2(p.x * 3.2, p.y * 1.8) - t * 0.05);
      float c2_x = 0.12 + sin(p.y * 1.5 - 0.2) * 0.1 + (c2_turb - 0.5) * 0.18;
      float c2_width = 0.20 - p.y * 0.05;
      float c2_dist = abs(p.x - c2_x);
      float c2_top = 0.72 + sin(p.x * 10.0) * 0.06;
      float c2_body = smoothstep(c2_width, c2_width * 0.6, c2_dist) * smoothstep(c2_top + 0.15, c2_top - 0.1, p.y);

      // Column 3 (Right Pillar - Slender Column): Center x around 0.70, rises to y ~ 0.12
      float c3_turb = fbm(vec2(p.x * 4.0, p.y * 2.8) + t * 0.08);
      float c3_x = 0.70 + sin(p.y * 2.5 + 0.5) * 0.06 + (c3_turb - 0.5) * 0.14;
      float c3_width = 0.16 - p.y * 0.05;
      float c3_dist = abs(p.x - c3_x);
      float c3_top = 0.12 + sin(p.x * 14.0) * 0.04;
      float c3_body = smoothstep(c3_width, c3_width * 0.6, c3_dist) * smoothstep(c3_top + 0.15, c3_top - 0.1, p.y);

      float totalPillar = clamp(c1_body + c2_body + c3_body, 0.0, 1.0);

      // 3. Dense Molecular Dust & Amber/Gold Photoevaporation Rims
      float dustNoise = fbm(p * 6.0 + vec2(-t * 0.2, t * 0.1));
      vec3 darkCarbonDust = vec3(0.025, 0.015, 0.01);
      vec3 deepBronzeDust = vec3(0.25, 0.12, 0.04);
      vec3 pillarInterior = mix(darkCarbonDust, deepBronzeDust, dustNoise * 0.85);

      float rim1 = smoothstep(c1_width + 0.04, c1_width - 0.06, c1_dist) * smoothstep(c1_width * 0.3, c1_width, c1_dist) * smoothstep(c1_top + 0.18, c1_top - 0.15, p.y);
      float rim2 = smoothstep(c2_width + 0.04, c2_width - 0.06, c2_dist) * smoothstep(c2_width * 0.3, c2_width, c2_dist) * smoothstep(c2_top + 0.18, c2_top - 0.15, p.y);
      float rim3 = smoothstep(c3_width + 0.04, c3_width - 0.06, c3_dist) * smoothstep(c3_width * 0.3, c3_width, c3_dist) * smoothstep(c3_top + 0.18, c3_top - 0.15, p.y);
      float rimTotal = clamp(rim1 + rim2 + rim3, 0.0, 1.0);

      vec3 goldIonization = vec3(1.0, 0.74, 0.25);
      vec3 peachShockFront = vec3(1.0, 0.94, 0.72);
      vec3 rimColor = mix(goldIonization, peachShockFront, dustNoise) * (rimTotal * 2.4);

      vec3 scene = mix(sky, pillarInterior, totalPillar * 0.94);
      scene += rimColor;

      // 4. Stellar Nursery Stars with JWST 6-Point Diffraction Spikes
      float starHash = hash(floor(gl_FragCoord.xy * 0.4));
      if (starHash > 0.992) {
        float starTwinkle = sin(starHash * 400.0 + u_time * 2.5) * 0.5 + 0.5;
        float starBright = pow(hash(gl_FragCoord.xy), 3.0) * (0.35 + starTwinkle * 0.65);
        vec3 sCol = mix(vec3(0.5, 0.85, 1.0), vec3(1.0, 0.88, 0.65), hash(vec2(starHash, 2.1)));
        scene += sCol * starBright * (1.0 - totalPillar * 0.7);
      }

      scene += vec3(0.4, 0.85, 1.0) * jwstStar(uv, vec2(0.24, 0.68) + m * 0.4, 0.13, 1.8);
      scene += vec3(1.0, 0.82, 0.4) * jwstStar(uv, vec2(-0.40, 0.32) + m * 0.4, 0.11, 1.5);
      scene += vec3(0.65, 0.9, 1.0) * jwstStar(uv, vec2(0.68, 0.18) + m * 0.4, 0.09, 1.3);
      scene += vec3(1.0, 0.95, 0.8) * jwstStar(uv, vec2(-0.12, -0.25) + m * 0.4, 0.08, 1.0);
      scene += vec3(0.3, 0.95, 0.9) * jwstStar(uv, vec2(0.02, 0.88) + m * 0.4, 0.07, 1.2);

      float vig = smoothstep(1.9, 0.35, length(uv));
      scene *= vig;

      gl_FragColor = vec4(scene, 1.0);
    }
  `,
  'fluid-sim': `
    precision mediump float;
    uniform float u_time;
    uniform vec2 u_resolution;
    varying vec2 v_uv;
    void main() {
      vec2 uv = v_uv * 3.5;
      float t = u_time * 0.5;
      for (float i = 1.0; i < 4.0; i++) {
        uv.x += 0.3 / i * sin(i * 3.0 * uv.y + t) + 0.5;
        uv.y += 0.3 / i * cos(i * 3.0 * uv.x + t) + 0.5;
      }
      float g = sin(uv.x + uv.y) * 0.5 + 0.5;
      vec3 gold = vec3(0.96, 0.74, 0.26);
      vec3 teal = vec3(0.04, 0.78, 0.88);
      vec3 col = mix(teal, gold, g);
      gl_FragColor = vec4(col * 0.9, 0.95);
    }
  `,
  'cyber-grid': `
    precision mediump float;
    uniform float u_time;
    uniform vec2 u_resolution;
    varying vec2 v_uv;
    void main() {
      vec2 uv = v_uv * 18.0;
      vec2 grid = abs(fract(uv - 0.5) - 0.5);
      float line = min(grid.x, grid.y);
      float g = smoothstep(0.06, 0.0, line);
      float pulse = 0.6 + 0.4 * sin(u_time * 1.2 + v_uv.y * 6.0);
      vec3 gold = vec3(0.96, 0.72, 0.25);
      vec3 teal = vec3(0.0, 0.95, 0.99);
      vec3 col = mix(gold, teal, v_uv.x) * g * pulse;
      gl_FragColor = vec4(col, g * 0.8);
    }
  `,
  'cyber-wave': `
    precision mediump float;
    uniform float u_time;
    uniform vec2 u_resolution;
    varying vec2 v_uv;
    void main() {
      vec2 uv = v_uv;
      float wave = sin(uv.x * 12.0 + u_time * 1.5) * 0.04;
      float wave2 = sin(uv.x * 8.0 - u_time * 2.0 + 1.5) * 0.03;
      float y = uv.y + wave + wave2;
      float glow = smoothstep(0.5 + 0.1, 0.5, abs(y - 0.5)) * 0.6;
      vec3 cyan = vec3(0.0, 0.95, 0.99);
      vec3 purple = vec3(0.61, 0.32, 0.88);
      vec3 col = mix(cyan, purple, uv.x + sin(u_time * 0.4) * 0.3);
      gl_FragColor = vec4(col * glow, glow * 0.4);
    }
  `,
  'particles': `
    precision mediump float;
    uniform float u_time;
    uniform vec2 u_resolution;
    varying vec2 v_uv;
    float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    void main() {
      vec2 uv = v_uv;
      float glow = 0.0;
      for (float i = 0.0; i < 14.0; i++) {
        vec2 seed = vec2(i * 1.618, i * 2.39);
        vec2 pos = vec2(hash(seed + 0.1), hash(seed + 0.2));
        float t = fract(u_time * (0.04 + hash(seed) * 0.04) + hash(seed + 0.5));
        pos.y = 1.0 - t;
        pos.x = fract(pos.x + sin(t * 6.28 + i) * 0.1);
        float d = length(uv - pos);
        glow += 0.00035 / (d * d + 0.0001);
      }
      vec3 col = mix(vec3(0.96, 0.74, 0.26), vec3(0.0, 0.95, 0.99), uv.x);
      gl_FragColor = vec4(col * clamp(glow, 0.0, 1.0), clamp(glow, 0.0, 0.75));
    }
  `,
  'black-hole': `
    precision highp float;
    uniform float u_time;
    uniform vec2 u_resolution;
    uniform vec2 u_mouse;
    varying vec2 v_uv;
    void main() {
      vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / min(u_resolution.x, u_resolution.y);
      float dist = length(uv);
      float angle = atan(uv.y, uv.x);
      float core = smoothstep(0.42, 0.38, dist);
      float ringWidth = 0.08;
      float ringBase = smoothstep(0.55 + ringWidth, 0.45, dist) * smoothstep(0.38 - ringWidth, 0.42, dist);
      float noise = sin(angle * 8.0 + u_time * 1.5) * 0.03;
      float glow = 0.15 / abs(dist - (0.46 + noise));
      vec3 colorCyan = vec3(0.0, 1.0, 1.0);
      vec3 colorPink = vec3(1.0, 0.0, 1.0);
      vec3 ringColor = mix(colorCyan, colorPink, sin(angle + u_time * 0.4) * 0.5 + 0.5);
      vec3 finalColor = ringColor * (ringBase + glow * 0.8);
      float stars = pow(fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453), 150.0) * 0.4;
      finalColor += stars * colorCyan;
      finalColor *= (1.0 - core);
      gl_FragColor = vec4(finalColor, 1.0);
    }
  `
};

function _tinRunShader(canvas, effectOrCode, isCustom, uniforms) {
  if (!canvas) return;
  const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  if (!gl) { console.warn('[TinPyUI] WebGL not available'); return; }

  function sync() {
    const isFixed = canvas.style.position === 'fixed';
    const w = isFixed ? window.innerWidth : (canvas.parentElement ? canvas.parentElement.offsetWidth || window.innerWidth : window.innerWidth);
    const h = isFixed ? window.innerHeight : (canvas.parentElement ? canvas.parentElement.offsetHeight || window.innerHeight : window.innerHeight);
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
  }
  sync();
  window.addEventListener('resize', sync);

  const fragSrc = isCustom ? effectOrCode : _TIN_SHADERS[effectOrCode];
  if (!fragSrc) { console.warn('[TinPyUI] Unknown shader effect:', effectOrCode); return; }

  const prog = _tinCreateShaderProgram(gl, _TIN_VERT_SHADER, fragSrc);
  gl.useProgram(prog);
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  const pos = gl.getAttribLocation(prog, 'a_position');
  gl.enableVertexAttribArray(pos);
  gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);

  const uTime = gl.getUniformLocation(prog, 'u_time');
  const uRes = gl.getUniformLocation(prog, 'u_resolution');
  const uMouse = gl.getUniformLocation(prog, 'u_mouse');
  let mouse = { x: 0.5, y: 0.5 };
  window.addEventListener('mousemove', e => {
    const r = canvas.getBoundingClientRect();
    if (r.width && r.height) {
      mouse.x = (e.clientX - r.left) / r.width;
      mouse.y = 1.0 - (e.clientY - r.top) / r.height;
    }
  });

  let userUniforms = {};
  if (uniforms) {
    try { userUniforms = JSON.parse(uniforms); } catch(e) {}
  }

  function render(t) {
    sync();
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(0,0,0,0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    if (uTime) gl.uniform1f(uTime, t * 0.001);
    if (uRes) gl.uniform2f(uRes, canvas.width, canvas.height);
    if (uMouse) gl.uniform2f(uMouse, mouse.x * canvas.width, mouse.y * canvas.height);
    for (const [key, val] of Object.entries(userUniforms)) {
      const loc = gl.getUniformLocation(prog, key);
      if (loc && typeof val === 'number') gl.uniform1f(loc, val);
    }
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    requestAnimationFrame(render);
  }
  requestAnimationFrame(render);
}

function _tinMountShaderLayer(el) {
  const effect = el.getAttribute('data-shader-effect');
  if (!effect) return;
  const isFixed = el.getAttribute('data-bg-fixed') === 'true';
  const canvas = document.createElement('canvas');
  if (isFixed) {
      canvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:-1;';
  } else {
      canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;';
  }
  el.style.position = el.style.position || 'relative';
  el.insertBefore(canvas, el.firstChild);
  const customCode = el.getAttribute('data-shader-code');
  const uniforms = el.getAttribute('data-shader-uniforms');
  _tinRunShader(canvas, customCode || effect, !!customCode, uniforms);
}

function _tinMountWebGLCanvas(el) {
  const code = el.getAttribute('data-shader-code');
  const uniforms = el.getAttribute('data-shader-uniforms');
  if (!code) return;
  _tinRunShader(el, code, true, uniforms);
}

function _tinMountParticleField(el) {
  const count = parseInt(el.getAttribute('data-particle-count') || '60');
  const colorName = el.getAttribute('data-particle-color') || 'neon-purple';
  const color = _tinResolvePaletteColor(colorName);
  const speed = parseFloat(el.getAttribute('data-particle-speed') || '1');
  const interactive = el.getAttribute('data-particle-interactive') === 'true';

  el.style.position = el.style.position || 'relative';
  const canvas = document.createElement('canvas');
  canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;';
  el.insertBefore(canvas, el.firstChild);

  let mouseX = 0, mouseY = 0;
  if (interactive) {
    el.addEventListener('mousemove', e => {
      const r = el.getBoundingClientRect();
      mouseX = e.clientX - r.left;
      mouseY = e.clientY - r.top;
    });
  }

  function resize() {
    canvas.width = el.offsetWidth;
    canvas.height = el.offsetHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const ctx = canvas.getContext('2d');
  const particles = Array.from({ length: count }, () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    vx: (Math.random() - 0.5) * speed,
    vy: (Math.random() - 0.5) * speed,
    r: Math.random() * 2 + 0.5,
    a: Math.random()
  }));

  function draw(t) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const p of particles) {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      if (interactive) {
        const dx = p.x - mouseX, dy = p.y - mouseY;
        const d = Math.sqrt(dx*dx + dy*dy);
        if (d < 80) { p.x += dx / d * 1.5; p.y += dy / d * 1.5; }
      }
      p.a = 0.4 + 0.6 * Math.abs(Math.sin(t * 0.001 + p.x));
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.globalAlpha = p.a;
      ctx.fill();
      ctx.globalAlpha = 1;
    }
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

function _tinMountAllEffects() {
  document.querySelectorAll('[data-shader-effect]').forEach(el => {
    if (!el.dataset.shaderMounted) {
      el.dataset.shaderMounted = 'true';
      _tinMountShaderLayer(el);
    }
  });
  document.querySelectorAll('[data-webgl-canvas]').forEach(el => {
    if (!el.dataset.webglMounted) {
      el.dataset.webglMounted = 'true';
      _tinMountWebGLCanvas(el);
    }
  });
  document.querySelectorAll('[data-particle-field]').forEach(el => {
    if (!el.dataset.particleMounted) {
      el.dataset.particleMounted = 'true';
      _tinMountParticleField(el);
    }
  });
}

// Instant high-speed IR hydration fallback
function renderIRFallback(irJSONText) {
  try {
    const data = typeof irJSONText === 'string' ? JSON.parse(irJSONText) : irJSONText;
    const nodes = data.nodes || [];
    if (!nodes.length) return false;

    let root = document.getElementById('tinui-root');
    if (!root) {
      root = document.createElement('div');
      root.id = 'tinui-root';
      document.body.appendChild(root);
    }
    root.innerHTML = '';

    const domNodes = {};
    for (const instr of nodes) {
      if (instr.op === 'CREATE_NODE') {
        const tag = instr.tag || 'div';
        domNodes[instr.id] = document.createElement(tag);
      } else if (instr.op === 'SET_ATTRIBUTE') {
        const el = domNodes[instr.id];
        if (el) {
          if (instr.key === 'textContent' || instr.key === 'text') {
            el.textContent = instr.value;
          } else if (instr.key === 'style') {
            el.style.cssText = instr.value;
          } else {
            el.setAttribute(instr.key, instr.value);
          }
        }
      } else if (instr.op === 'SET_TEXT') {
        const el = domNodes[instr.id];
        if (el) el.textContent = instr.value;
      } else if (instr.op === 'APPEND_CHILD') {
        const child = domNodes[instr.child];
        const parent = domNodes[instr.parent] || root;
        if (child && parent) {
          parent.appendChild(child);
        }
      }
    }
    setTimeout(_tinMountAllEffects, 25);
    return true;
  } catch (e) {
    console.warn('[TinPyUI Fallback notice]', e);
    return false;
  }
}

async function _loadIR() {
  const irCandidates = ['app.ir.json', 'showcase.ir.json', '/app.ir.json', '/showcase.ir.json'];
  for (const p of irCandidates) {
    try {
      const res = await fetch(p);
      if (res.ok) {
        const text = await res.text();
        if (text && text.trim().startsWith('{')) return text;
      }
    } catch(e) {}
  }
  return null;
}

// Engine Boot
(async function boot() {
  const irText = await _loadIR();
  if (irText) {
    renderIRFallback(irText);
  }

  try {
    const res = await fetch("app.wasm");
    if (res.ok) {
      const result = await WebAssembly.instantiateStreaming(res, go.importObject);
      go.run(result.instance);
      if (irText && typeof BootTinUI === 'function') {
        BootTinUI(irText);
        setTimeout(_tinMountAllEffects, 50);
      }
    }
  } catch(wasmErr) {
    console.info('[TinPyUI] Zero-DOM High-Speed JS engine active.');
  }

  // Smooth local navigation
  document.body.addEventListener('click', e => {
    const link = e.target.closest('a[href^="#"]');
    if (link) {
      const targetId = link.getAttribute('href').slice(1);
      if (targetId) {
        const targetEl = document.getElementById(targetId);
        if (targetEl) {
          e.preventDefault();
          targetEl.scrollIntoView({ behavior: 'smooth' });
        }
      }
    }
  });
})();
'''

def apply_all():
    # 1. Update showcase.tin
    showcase_tin_path = SHOWCASE_DIR / "showcase.tin"
    showcase_tin_path.write_text(SHOWCASE_TIN, encoding="utf-8")
    print("Updated showcase.tin")

    # 2. Update index.html
    html_path = SHOWCASE_DIR / "public" / "index.html"
    html_path.write_text(INDEX_HTML, encoding="utf-8")
    print("Updated public/index.html")

    # 3. Update tin-runtime.js
    runtime_path = SHOWCASE_DIR / "public" / "tin-runtime.js"
    runtime_path.write_text(TIN_RUNTIME_JS, encoding="utf-8")
    print("Updated public/tin-runtime.js")

if __name__ == "__main__":
    apply_all()
