import os
import json
import subprocess
from pathlib import Path

SHOWCASE_DIR = Path(r"C:\Users\barat\Portfolio_Projects\Showcase")
TINUI_DIR = Path(r"C:\Users\barat\Portfolio_Projects\TinUi")

print(f"Showcase directory exists: {SHOWCASE_DIR.exists()}")

# 1. New Pillars of Creation showcase.tin content
SHOWCASE_TIN = '''component Main():
    AnimatedBackground(effect = "pillars-of-creation", primaryColor = "neon-cyan", secondaryColor = "neon-purple", speed = "1"):
        
        # Navigation
        Navbar(class_ = "w-full fixed top-0 z-50 bg-[#060814]/85 backdrop-blur-md border-b border-amber-500/20 flex"):
            Row(justify = "space-between", align = "center", width = "full", class_ = "max-w-max-width mx-auto px-margin-desktop py-4 flex-1"):
                Link(href = "#", class_ = "font-display-lg-mobile text-display-lg-mobile font-bold tracking-tighter flex items-center gap-3"):
                    Text(text = "TinPyUI", class_ = "text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-200 to-cyan-300 font-extrabold text-2xl")
                    Text(text = "Pillars of Creation", class_ = "text-amber-200/80 font-mono text-xs tracking-widest uppercase px-2.5 py-1 rounded-full border border-amber-400/30 bg-amber-950/40")
                Row(gap = 32, class_ = "hidden md:flex items-center"):
                    Button(text = "Nebula Showcase", onClick = "window.location.href='#'", class_ = "font-body-md text-amber-300 border-b-2 border-amber-400 pb-1 bg-transparent hover:bg-white/5 px-3 py-1 rounded transition-colors")
                    Button(text = "Stellar Features", onClick = "window.location.href='#features'", class_ = "font-body-md text-slate-300 hover:text-amber-200 bg-transparent hover:bg-white/5 px-3 py-1 rounded transition-colors")
                    Button(text = "Cosmic Docs", onClick = "window.open('https://github.com/barathanandh-coder/TinUi', '_blank')", class_ = "font-body-md text-slate-300 hover:text-amber-200 bg-transparent hover:bg-white/5 px-3 py-1 rounded transition-colors")
                    Button(text = "Community", onClick = "window.open('https://github.com/barathanandh-coder/TinUi/discussions', '_blank')", class_ = "font-body-md text-slate-300 hover:text-amber-200 bg-transparent hover:bg-white/5 px-3 py-1 rounded transition-colors")
                Row(gap = 16, align = "center"):
                    Icon(name = "auto_awesome", class_ = "text-amber-400 cursor-pointer hover:scale-125 transition-transform drop-shadow-[0_0_8px_rgba(251,191,36,0.8)]")

        # Hero
        Section(class_ = "relative min-h-[92vh] flex items-center overflow-hidden bg-transparent"):
            Grid(cols = "2", gap = 48, class_ = "container mx-auto px-margin-desktop items-center relative z-10 pt-16"):
                Container(class_ = "space-y-8"):
                    Row(gap = 8, align = "center", class_ = "inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-amber-400/30 bg-amber-500/10 backdrop-blur-md mb-2"):
                        Container(class_ = "w-2 h-2 rounded-full bg-amber-400 animate-ping")
                        Text(text = "M16 EAGLE NEBULA ENGINE ONLINE", class_ = "font-label-mono text-xs tracking-widest text-amber-300 font-semibold")
                    Heading(text = "Pillars of \\nCreation.", size = "hero", class_ = "font-display-lg text-display-lg text-transparent bg-clip-text bg-gradient-to-br from-white via-amber-100 to-amber-500 leading-[1.05] tracking-tight whitespace-pre-line drop-shadow-[0_4px_24px_rgba(245,158,11,0.35)]")
                    Text(text = "The Celestial Limit of Zero-DOM Web Performance.", class_ = "font-label-mono text-headline-md text-cyan-300 drop-shadow-[0_0_12px_rgba(34,211,238,0.4)]")
                    Text(text = "Forged in the heart of the digital cosmos. TinPyUI bypasses virtual DOM tree recalculations, compiling Pythonic declarative syntax straight into raw WebGPU/WebGL instructions and 120 FPS WebAssembly kernels.", class_ = "font-body-lg text-slate-300 max-w-lg leading-relaxed")
                    Row(gap = 16, class_ = "pt-2"):
                        Link(text = "Explore the Pillars", href = "#features", onClick = "window.location.href='#features'", class_ = "bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 font-extrabold px-8 py-4 rounded-lg shadow-[0_0_30px_rgba(245,158,11,0.5)] hover:scale-105 hover:shadow-[0_0_40px_rgba(245,158,11,0.8)] transition-all inline-block cursor-pointer border border-amber-300/40")
                        Link(text = "Launch Wasm Core", href = "https://www.npmjs.com/package/tinpyui?activeTab=versions", class_ = "border border-cyan-400/60 text-cyan-300 px-8 py-4 font-bold rounded-lg hover:bg-cyan-500/10 hover:border-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.2)] transition-all inline-block cursor-pointer backdrop-blur-sm")
                Container():
                    # Empty Right Column showcasing towering background pillars

        # Live Features Gallery
        Section(id = "features", scrollReveal = "true", class_ = "py-24 relative px-margin-desktop max-w-max-width mx-auto bg-transparent"):
            Container(class_ = "mb-16"):
                Text(text = "STELLAR FRAMEWORK CORE", class_ = "font-label-caps text-amber-400 tracking-widest block mb-4")
                Heading(text = "Cosmic Performance Architecture", class_ = "font-display-lg text-display-lg-mobile text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-yellow-100 to-cyan-300 drop-shadow-[0_0_15px_rgba(245,158,11,0.4)]")
            
            Grid(cols = "3", gap = 32):
                # Feature 1
                Card(class_ = "bg-[rgba(10,14,28,0.55)] backdrop-blur-[20px] shadow-[0_8px_32px_rgba(0,0,0,0.5)] border border-[rgba(245,158,11,0.25)] p-0 group hover:-translate-y-2 hover:border-amber-400/60 hover:shadow-[0_0_30px_rgba(245,158,11,0.3)] transition-all duration-500 cursor-pointer overflow-hidden flex flex-col min-h-[420px] rounded-2xl"):
                    Container(class_ = "h-48 relative overflow-hidden bg-slate-950/60 border-b border-amber-500/20"):
                        ShaderLayer(effect = "cyber-grid")
                    Container(class_ = "p-8 flex-1 flex flex-col"):
                        Heading(text = "Zero-DOM Hardware Pipeline", class_ = "font-headline-md text-amber-200 mb-2")
                        Text(text = "Eliminates Document Object Model overhead entirely. Components compile to GPU vector bytecode painted at native hardware refresh rates.", class_ = "font-body-md text-slate-300 mb-8 flex-1 leading-relaxed")
                        Button(text = "Inspect Pipeline", onClick = "window.open('https://github.com/barathanandh-coder/TinUi/blob/main/README.md', '_blank')", class_ = "w-full py-3 bg-amber-500/15 border border-amber-400/30 text-amber-300 font-bold rounded-lg group-hover:bg-amber-500 group-hover:text-slate-950 transition-colors")

                # Feature 2
                Card(class_ = "bg-[rgba(10,14,28,0.55)] backdrop-blur-[20px] shadow-[0_8px_32px_rgba(0,0,0,0.5)] border border-[rgba(34,211,238,0.25)] p-0 group hover:-translate-y-2 hover:border-cyan-400/60 hover:shadow-[0_0_30px_rgba(34,211,238,0.3)] transition-all duration-500 cursor-pointer overflow-hidden flex flex-col min-h-[420px] rounded-2xl"):
                    Container(class_ = "h-48 relative overflow-hidden bg-slate-950/60 border-b border-cyan-500/20"):
                        ShaderLayer(effect = "fluid-sim")
                    Container(class_ = "p-8 flex-1 flex flex-col"):
                        Heading(text = "Pythonic Constellation Syntax", class_ = "font-headline-md text-cyan-200 mb-2")
                        Text(text = "Author reactive layouts with pristine Pythonic simplicity. Clean declarative semantics eliminate HTML boilerplate, CSS spaghetti, and JSX runtime tax.", class_ = "font-body-md text-slate-300 mb-8 flex-1 leading-relaxed")
                        Button(text = "View Syntax Guide", onClick = "window.open('https://github.com/barathanandh-coder/TinUi/blob/main/README.md', '_blank')", class_ = "w-full py-3 bg-cyan-500/15 border border-cyan-400/30 text-cyan-300 font-bold rounded-lg group-hover:bg-cyan-400 group-hover:text-slate-950 transition-colors")

                # Feature 3
                Card(class_ = "bg-[rgba(10,14,28,0.55)] backdrop-blur-[20px] shadow-[0_8px_32px_rgba(0,0,0,0.5)] border border-[rgba(168,85,247,0.25)] p-0 group hover:-translate-y-2 hover:border-purple-400/60 hover:shadow-[0_0_30px_rgba(168,85,247,0.3)] transition-all duration-500 cursor-pointer overflow-hidden flex flex-col min-h-[420px] rounded-2xl"):
                    Container(class_ = "h-48 relative overflow-hidden bg-slate-950/60 border-b border-purple-500/20"):
                        ShaderLayer(effect = "particles")
                    Container(class_ = "p-8 flex-1 flex flex-col"):
                        Heading(text = "Wasm & WebGPU Stellar Nursery", class_ = "font-headline-md text-purple-200 mb-2")
                        Text(text = "Unified WebAssembly compute kernel pushing 50,000+ spatial nodes with instant hydration fallback and sub-millisecond reactive signal propagation.", class_ = "font-body-md text-slate-300 mb-8 flex-1 leading-relaxed")
                        Button(text = "Benchmark Wasm", onClick = "window.open('https://github.com/barathanandh-coder/TinUi/blob/main/README.md', '_blank')", class_ = "w-full py-3 bg-purple-500/15 border border-purple-400/30 text-purple-300 font-bold rounded-lg group-hover:bg-purple-500 group-hover:text-slate-950 transition-colors")

        # Performance Lab
        Section(scrollReveal = "true", class_ = "py-24 bg-[#030614]/40 backdrop-blur-sm border-y border-amber-500/10"):
            Container(class_ = "max-w-max-width mx-auto px-margin-desktop"):
                Container(class_ = "text-center mb-16"):
                    Text(text = "ASTROPHYSICAL BENCHMARKS", class_ = "font-label-caps text-amber-400 tracking-widest block mb-4")
                    Heading(text = "Performance Lab", class_ = "font-display-lg text-display-lg-mobile text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-amber-200 to-amber-400 drop-shadow-[0_0_12px_rgba(34,211,238,0.5)]")
                
                Grid(cols = "2", gap = 48):
                    Card(class_ = "bg-[rgba(10,14,28,0.5)] backdrop-blur-[16px] border border-red-500/30 p-10 relative rounded-2xl"):
                        Text(text = "STATUS: BOTTLENECKED", class_ = "absolute top-4 right-6 font-label-mono text-red-400 text-xs font-bold")
                        Heading(text = "Legacy Virtual DOM", class_ = "font-headline-md text-red-400 mb-8")
                        Container(class_ = "space-y-8"):
                            Row(align = "end", gap = 16):
                                Text(text = "14", class_ = "font-display-lg text-[80px] text-red-400 leading-none font-extrabold")
                                Text(text = "FPS", class_ = "font-label-mono text-slate-400 pb-2")
                            Container(class_ = "h-2 w-full bg-red-500/10 rounded-full"):
                                Container(class_ = "h-full bg-red-500 w-[15%]")
                            Text(text = "Reflow and tree-diffing overhead stalling the main thread during complex animation cycles.", class_ = "text-slate-400 text-sm font-body-md")

                    Card(class_ = "bg-[rgba(10,14,28,0.5)] backdrop-blur-[16px] border border-amber-400/40 p-10 relative rounded-2xl shadow-[0_0_30px_rgba(245,158,11,0.15)]"):
                        Row(align = "center", gap = 8, class_ = "absolute top-4 right-6"):
                            Container(class_ = "w-2 h-2 rounded-full bg-amber-400 animate-ping")
                            Text(text = "STELLAR 120 FPS", class_ = "font-label-mono text-amber-300 text-xs font-bold")
                        Heading(text = "TinPyUI Wasm Core", class_ = "font-headline-md text-amber-300 mb-8")
                        Container(class_ = "space-y-8"):
                            Row(align = "end", gap = 16):
                                Text(text = "120", class_ = "font-display-lg text-[80px] text-amber-300 leading-none font-extrabold")
                                Text(text = "FPS", class_ = "font-label-mono text-slate-300 pb-2")
                            Container(class_ = "h-2 w-full bg-amber-400/10 rounded-full"):
                                Container(class_ = "h-full bg-gradient-to-r from-amber-400 to-cyan-400 w-full shadow-[0_0_20px_rgba(245,158,11,0.6)]")
                            Text(text = "Direct GPU pipeline via WebAssembly. Zero DOM interaction, 100% efficient vector pushing.", class_ = "text-slate-300 text-sm font-body-md")

        # The Component Lab
        Section(scrollReveal = "true", class_ = "py-24 bg-transparent"):
            Container(class_ = "max-w-max-width mx-auto px-margin-desktop text-center mb-16"):
                Heading(text = "The Component Lab", class_ = "font-display-lg text-display-lg-mobile text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-200 to-cyan-300 drop-shadow-[0_0_12px_rgba(245,158,11,0.5)]")
                Text(text = "Interactive primitives pulsing with reactive signals in the digital nebula.", class_ = "text-slate-300 mt-4 font-body-lg")
            
            Row(justify = "center", align = "center", gap = 48, class_ = "flex-wrap"):
                Container(class_ = "group flex flex-col items-center gap-4"):
                    Card(class_ = "w-44 h-44 rounded-2xl bg-[rgba(10,14,28,0.5)] backdrop-blur-[16px] border border-amber-400/20 flex items-center justify-center hover:scale-110 hover:border-amber-400 transition-all cursor-pointer relative overflow-hidden"):
                        Button(text = "Button()", class_ = "px-6 py-3 border-2 border-amber-400 text-amber-300 font-bold rounded-full animate-pulse shadow-[0_0_15px_rgba(245,158,11,0.3)]")
                    Text(text = "Interactive State", class_ = "font-label-mono text-amber-300 text-sm")
                
                Container(class_ = "group flex flex-col items-center gap-4"):
                    Card(class_ = "w-44 h-44 rounded-2xl bg-[rgba(10,14,28,0.5)] backdrop-blur-[16px] border border-cyan-400/20 flex items-center justify-center hover:scale-110 hover:border-cyan-400 transition-all cursor-pointer relative overflow-hidden"):
                        GradientText(text = "STELLAR", class_ = "font-display-lg-mobile tracking-widest bg-clip-text text-transparent bg-gradient-to-r from-amber-300 via-yellow-100 to-cyan-300 font-bold animate-pulse")
                    Text(text = "GradientText()", class_ = "font-label-mono text-cyan-300 text-sm")

                Container(class_ = "group flex flex-col items-center gap-4"):
                    Card(class_ = "w-44 h-44 rounded-2xl bg-[rgba(10,14,28,0.5)] backdrop-blur-[16px] border border-purple-400/20 flex items-center justify-center hover:scale-110 hover:border-purple-400 transition-all cursor-pointer relative overflow-hidden group"):
                        Container(class_ = "w-24 h-24 border-2 border-dashed border-amber-400/50 rounded-full animate-spin flex items-center justify-center group-hover:border-amber-400 transition-colors"):
                            Icon(name = "flare", class_ = "text-amber-400 text-4xl drop-shadow-[0_0_10px_rgba(245,158,11,0.8)]")
                    Text(text = "PulsarLoader()", class_ = "font-label-mono text-amber-300 text-sm")

        # Engine Blueprint Section
        Section(scrollReveal = "true", class_ = "py-24 bg-transparent"):
            Container(class_ = "max-w-max-width mx-auto px-margin-desktop"):
                Container(class_ = "mb-12"):
                    Text(text = "BLUEPRINT", class_ = "font-label-caps text-amber-400 tracking-widest block mb-4")
                    Heading(text = "The Stellar Blueprint", class_ = "font-display-lg text-display-lg-mobile text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-white to-cyan-300 drop-shadow-[0_0_10px_rgba(245,158,11,0.4)]")
                
                Grid(cols = "2", class_ = "gap-px bg-amber-500/20 rounded-2xl overflow-hidden shadow-2xl border border-amber-500/30"):
                    Container(class_ = "bg-[#060814] p-8 font-label-mono text-sm leading-relaxed overflow-x-auto min-h-[500px] text-[#c9d1d9]"):
                        Row(gap = 8, align = "center", class_ = "mb-6"):
                            Row(gap = 6):
                                Container(class_ = "w-3 h-3 rounded-full bg-[#ff5f56]")
                                Container(class_ = "w-3 h-3 rounded-full bg-[#ffbd2e]")
                                Container(class_ = "w-3 h-3 rounded-full bg-[#27c93f]")
                            Text(text = "pillars_of_creation.tin", class_ = "text-amber-300/80 ml-4 text-xs font-mono")
                        Text(text = "component NebulaDashboard():\\n    AnimatedBackground(effect='pillars-of-creation', speed='1'):\\n        Container(align='center', justify='center', width='full', padding=32):\\n            GradientText(text='Pillars of Creation', animation='stellar-glow')\\n            Card(title='Telemetry 120 FPS', glow=True):\\n                Button(text='Ignite Nursery', color='cosmic-gold')\\n\\n# Zero-DOM hardware execution on WebAssembly\\nmount(NebulaDashboard)", class_ = "whitespace-pre")

                    Container(class_ = "relative bg-black/40 backdrop-blur-md flex items-center justify-center overflow-hidden"):
                        Card(class_ = "relative z-10 bg-[rgba(10,14,28,0.6)] backdrop-blur-[16px] border border-amber-400/40 shadow-[0_0_25px_rgba(245,158,11,0.25)] p-10 text-center rounded-2xl"):
                            Text(text = "NEBULA STREAM ACTIVE", class_ = "font-display-lg-mobile text-amber-300 tracking-widest mb-6 font-bold bg-clip-text text-transparent bg-gradient-to-r from-amber-300 to-cyan-300")
                            Container(class_ = "flex flex-col gap-4"):
                                Container(class_ = "h-1.5 w-full bg-slate-800 rounded-full overflow-hidden"):
                                    Container(class_ = "h-full bg-gradient-to-r from-amber-400 to-cyan-400 w-3/4 shadow-[0_0_12px_rgba(245,158,11,1)] animate-pulse")
                                Row(justify = "space-between", class_ = "font-label-mono text-xs text-slate-300 w-full"):
                                    Text(text = "VECTOR THROUGHPUT")
                                    Text(text = "12.6 GB/S")
                            Button(text = "IONIZE VECTOR FIELD", class_ = "mt-8 px-8 py-2.5 border border-amber-400/60 text-amber-300 font-bold rounded-lg hover:bg-amber-400 hover:text-slate-950 transition-all shadow-[0_0_15px_rgba(245,158,11,0.2)]")

        # CTA
        Section(scrollReveal = "true", class_ = "py-32 relative"):
            Container(class_ = "max-w-4xl mx-auto px-margin-mobile text-center"):
                Card(class_ = "bg-[rgba(10,14,28,0.6)] backdrop-blur-[20px] border border-amber-400/30 p-16 relative overflow-hidden rounded-3xl shadow-[0_0_40px_rgba(0,0,0,0.6)]"):
                    Heading(text = "Ready to forge across the stars?", class_ = "font-display-lg text-display-lg-mobile text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-yellow-100 to-cyan-300 drop-shadow-[0_0_18px_rgba(245,158,11,0.5)] mb-8 relative z-10")
                    Text(text = "Join developers worldwide creating ultra-performance Zero-DOM applications with pure Pythonic syntax and native GPU acceleration.", class_ = "text-slate-300 mb-12 font-body-lg max-w-xl mx-auto relative z-10 leading-relaxed")
                    Row(justify = "center", gap = 24, class_ = "relative z-10 flex-col sm:flex-row"):
                        Button(text = "Submit Your Constellation", onClick = "window.open('https://github.com/barathanandh-coder/TinUi/discussions', '_blank')", class_ = "bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 border border-amber-300/40 px-12 py-5 font-bold rounded-xl hover:scale-105 hover:shadow-[0_0_30px_rgba(245,158,11,0.6)] transition-all text-lg cursor-pointer")

        # Footer
        Footer(class_ = "bg-[#04060e]/80 backdrop-blur-md py-12 border-t border-amber-500/20 w-full"):
            Row(justify = "space-between", align = "center", class_ = "max-w-max-width mx-auto px-margin-desktop flex-col md:flex-row gap-8 w-full"):
                Heading(text = "TinPyUI", class_ = "font-headline-md text-amber-300")
                Row(gap = 24, class_ = "font-label-mono text-label-mono flex-wrap justify-center"):
                    Link(text = "NPM Package", href = "https://www.npmjs.com/package/tinpyui?activeTab=versions", class_ = "text-slate-400 hover:text-amber-300 transition-colors")
                    Link(text = "PyPI Distribution", href = "https://pypi.org/project/tinpyui-ff/", class_ = "text-slate-400 hover:text-amber-300 transition-colors")
                    Link(text = "GitHub Repository", href = "https://github.com/barathanandh-coder/TinUi", class_ = "text-slate-400 hover:text-amber-300 transition-colors")
                    Link(text = "Discussions", href = "https://github.com/barathanandh-coder/TinUi/discussions", class_ = "text-slate-400 hover:text-amber-300 transition-colors")
                Container(class_ = "font-label-mono text-label-mono text-slate-400 text-right"):
                    Text(text = "© 2026 TinPyUI Framework.")
                    Text(text = "Showcase Portal — Pillars of Creation Edition. Zero-DOM Architecture.", class_ = "text-[11px] text-amber-300/70")
'''

# 2. Updated tin-runtime.js
TIN_RUNTIME_JS = '''// tin-runtime.js — TinPyUI v1.6.1 Runtime (Pillars of Creation Edition)
const go = new Go();

function _tinResolvePaletteColor(name) {
  const palette = {
    'neon-cyan': '#00f2fe', 'neon-purple': '#9b51e0', 'neon-pink': '#ff007f',
    'stellar-gold': '#f59e0b', 'cosmic-teal': '#06b6d4',
    'dark-core': '#04060e', 'white': '#ffffff', 'muted': '#747d8c'
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

    // Procedural Hash & Noise
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
        p = rot * p * 2.02 + vec2(100.0, 100.0);
        a *= 0.5;
      }
      return v;
    }

    // 6-Point JWST / Hubble Diffraction Spike Star
    float starWithSpikes(vec2 uv, vec2 pos, float size, float brightness) {
      vec2 d = uv - pos;
      float dist = length(d);
      if (dist > size * 4.0) return 0.0;
      float core = (size * 0.02) / (dist + 0.001);
      core = smoothstep(0.0, 1.0, core);
      float spikes = 0.0;
      for (int i = 0; i < 3; i++) {
        float ang = float(i) * 1.04719755; // PI / 3
        vec2 dir = vec2(cos(ang), sin(ang));
        float proj = abs(dot(d, vec2(-dir.y, dir.x)));
        spikes += smoothstep(size * 0.04, 0.0, proj) * smoothstep(size * 3.5, 0.0, dist);
      }
      return (core + spikes * 0.75) * brightness;
    }

    void main() {
      vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / min(u_resolution.x, u_resolution.y);
      float t = u_time * 0.04;
      vec2 m = (u_mouse - 0.5) * 0.12;
      vec2 p = uv - m;

      // 1. Cosmic Deep Space & Background Emission Nebula (O III / H-alpha)
      float nebNoise1 = fbm(p * 1.2 + vec2(t * 0.2, -t * 0.1));
      float nebNoise2 = fbm(p * 2.4 - vec2(t * 0.15, t * 0.25));

      vec3 deepSpace  = vec3(0.012, 0.02, 0.05);  // Deep cosmic void
      vec3 tealNebula = vec3(0.02, 0.48, 0.62);   // Ionized Oxygen [O III]
      vec3 cyanGlow   = vec3(0.12, 0.85, 0.95);   // High-energy cyan emission
      vec3 violetGas  = vec3(0.38, 0.14, 0.52);   // Sulfur / Hydrogen violet fringe

      float nebDensity = smoothstep(0.3, 0.8, nebNoise1 + nebNoise2 * 0.4);
      vec3 nebColor = mix(deepSpace, tealNebula, nebDensity * 0.7);
      nebColor = mix(nebColor, violetGas, smoothstep(0.4, 0.9, nebNoise2) * 0.5);
      nebColor += cyanGlow * pow(nebDensity, 3.0) * 0.35;

      float upperGlow = smoothstep(-0.8, 1.2, p.y) * 0.35;
      nebColor += vec3(0.05, 0.35, 0.5) * upperGlow;

      // 2. Towering Gas & Dust Pillars (The Pillars of Creation)
      // Column 1 (Left Pillar): Sculpted head
      float col1_x = -0.52 + sin(p.y * 1.8 + 1.2) * 0.08 + fbm(vec2(p.x * 3.0, p.y * 2.5) + t * 0.1) * 0.15;
      float col1_dist = abs(p.x - col1_x);
      float col1_height = 0.55 + noise(vec2(p.x * 8.0, 1.0)) * 0.1;
      float col1_mask = smoothstep(0.24, 0.08, col1_dist) * smoothstep(col1_height, col1_height - 0.25, p.y);

      // Column 2 (Center Pillar - Tallest)
      float col2_x = 0.04 + sin(p.y * 1.4) * 0.1 + fbm(vec2(p.x * 2.8, p.y * 2.0) - t * 0.08) * 0.18;
      float col2_dist = abs(p.x - col2_x);
      float col2_height = 0.82 + noise(vec2(p.x * 6.0, 4.0)) * 0.08;
      float col2_mask = smoothstep(0.22, 0.06, col2_dist) * smoothstep(col2_height, col2_height - 0.28, p.y);

      // Column 3 (Right Pillar - Slender)
      float col3_x = 0.56 + sin(p.y * 2.2 + 0.5) * 0.06 + fbm(vec2(p.x * 3.5, p.y * 3.0)) * 0.12;
      float col3_dist = abs(p.x - col3_x);
      float col3_height = 0.35 + noise(vec2(p.x * 7.0, 8.0)) * 0.08;
      float col3_mask = smoothstep(0.18, 0.05, col3_dist) * smoothstep(col3_height, col3_height - 0.2, p.y);

      float pillarMask = clamp(col1_mask + col2_mask + col3_mask, 0.0, 1.0);

      // Dense internal dust turbulence
      float dustTurbulence = fbm(p * 5.0 + vec2(-t * 0.3, t * 0.1));
      vec3 denseDustDark = vec3(0.035, 0.018, 0.012); // Opaque molecular dust
      vec3 warmDustAmber = vec3(0.35, 0.18, 0.06);     // Illuminated warm dust
      vec3 pillarBody = mix(denseDustDark, warmDustAmber, dustTurbulence);

      // 3. Ionization Rims & Evaporating Gaseous Globules
      float rim1 = smoothstep(0.20, 0.10, col1_dist) * smoothstep(0.09, 0.18, col1_dist) * smoothstep(col1_height + 0.05, col1_height - 0.2, p.y);
      float rim2 = smoothstep(0.18, 0.08, col2_dist) * smoothstep(0.07, 0.16, col2_dist) * smoothstep(col2_height + 0.05, col2_height - 0.2, p.y);
      float rim3 = smoothstep(0.15, 0.06, col3_dist) * smoothstep(0.05, 0.13, col3_dist) * smoothstep(col3_height + 0.05, col3_height - 0.18, p.y);
      float ionizationRim = clamp(rim1 + rim2 + rim3, 0.0, 1.0);

      vec3 goldIonization = vec3(1.0, 0.76, 0.28);     // Blazing ionization edge
      vec3 peachIncandescence = vec3(1.0, 0.92, 0.65);   // High temperature shock front
      vec3 rimGlow = mix(goldIonization, peachIncandescence, dustTurbulence) * (ionizationRim * 2.2);

      // Composite Pillars over Nebula
      vec3 compositeColor = mix(nebColor, pillarBody, pillarMask * 0.92);
      compositeColor += rimGlow;

      // 4. Stellar Nursery Stars & James Webb Spikes
      float starSeed = hash(floor(gl_FragCoord.xy * 0.35));
      float starBlink = sin(starSeed * 628.0 + u_time * 2.0) * 0.5 + 0.5;
      if (starSeed > 0.993) {
        float starGlow = pow(hash(gl_FragCoord.xy), 4.0) * (0.4 + starBlink * 0.6);
        vec3 starColor = mix(vec3(0.6, 0.85, 1.0), vec3(1.0, 0.9, 0.7), hash(vec2(starSeed, 1.2)));
        compositeColor += starColor * starGlow * (1.0 - pillarMask * 0.6);
      }

      // Major Protostars with 6-point diffraction spikes (Infant Stars)
      compositeColor += vec3(0.5, 0.85, 1.0) * starWithSpikes(uv, vec2(0.18, 0.68) + m * 0.5, 0.14, 1.6);
      compositeColor += vec3(1.0, 0.82, 0.45) * starWithSpikes(uv, vec2(-0.42, 0.45) + m * 0.5, 0.12, 1.4);
      compositeColor += vec3(0.7, 0.9, 1.0) * starWithSpikes(uv, vec2(0.62, 0.25) + m * 0.5, 0.10, 1.2);
      compositeColor += vec3(1.0, 0.95, 0.8) * starWithSpikes(uv, vec2(-0.15, -0.1) + m * 0.5, 0.08, 0.9);

      // Atmospheric Vignette
      float vignette = smoothstep(1.8, 0.4, length(uv));
      compositeColor *= vignette;

      gl_FragColor = vec4(compositeColor, 1.0);
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
      ctx.globalAlpha = p.a;
      ctx.fillStyle = color;
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
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('active'); });
  }, { threshold: 0.1 });
  document.querySelectorAll('[data-scroll-reveal]').forEach(el => observer.observe(el));
}

// High-speed instant IR hydration fallback
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
    setTimeout(_tinMountAllEffects, 20);
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

// Boot Engine: instant fallback first, then WebAssembly enhancement
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
    console.info('[TinPyUI] Running in High-Speed Zero-DOM JS engine mode:', wasmErr.message || wasmErr);
  }

  // Route navigation
  document.body.addEventListener('click', e => {
    const target = e.target.closest('[data-route-path]');
    if (target) {
      e.preventDefault();
      const route = target.getAttribute('href');
      if (route) {
        window.history.pushState({ route }, "", route);
        if (window.TinPyUI && window.TinPyUI.navigate) window.TinPyUI.navigate(route);
      }
    }
  });
  window.addEventListener('popstate', e => {
    const route = e.state ? e.state.route : "/";
    if (window.TinPyUI && window.TinPyUI.navigate) window.TinPyUI.navigate(route, { reverse: true });
  });
})();
'''

# 3. Updated index.html
INDEX_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TinPyUI Showcase — Pillars of Creation</title>
    <meta name="description" content="TinPyUI Universal Omni-Platform Zero-DOM WebAssembly & WebGL Showcase — Pillars of Creation Theme.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Sora:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    <style>
      body {
        margin: 0;
        padding: 0;
        background-color: #04060e;
        color: #f8fafc;
        font-family: 'Plus Jakarta Sans', sans-serif;
        overflow-x: hidden;
      }
      [data-scroll-reveal] {
        opacity: 0;
        transform: translateY(24px);
        transition: opacity 0.8s ease, transform 0.8s ease;
      }
      [data-scroll-reveal].active {
        opacity: 1;
        transform: translateY(0);
      }
    </style>
</head>
<body>
    <div id="tinui-root">
        <!-- The Wasm Engine / Instant Fallback mounts here -->
    </div>
    <script src="wasm_exec.js"></script>
    <script src="tin-runtime.js"></script>
</body>
</html>
'''

def update():
    # Write showcase.tin
    showcase_tin_path = SHOWCASE_DIR / "showcase.tin"
    showcase_tin_path.write_text(SHOWCASE_TIN, encoding="utf-8")
    print(f"Updated {showcase_tin_path}")

    # Write tin-runtime.js
    runtime_path = SHOWCASE_DIR / "public" / "tin-runtime.js"
    runtime_path.write_text(TIN_RUNTIME_JS, encoding="utf-8")
    print(f"Updated {runtime_path}")

    # Write index.html
    html_path = SHOWCASE_DIR / "public" / "index.html"
    html_path.write_text(INDEX_HTML, encoding="utf-8")
    print(f"Updated {html_path}")

    # Update package.json scripts
    pkg_path = SHOWCASE_DIR / "package.json"
    if pkg_path.exists():
        pkg_data = json.loads(pkg_path.read_text(encoding="utf-8"))
        pkg_data.setdefault("scripts", {})
        pkg_data["scripts"]["compile"] = "tinpyui compile showcase.tin"
        pkg_data["scripts"]["serve"] = "tinpyui serve"
        pkg_path.write_text(json.dumps(pkg_data, indent=2), encoding="utf-8")
        print(f"Updated {pkg_path}")

if __name__ == "__main__":
    update()
