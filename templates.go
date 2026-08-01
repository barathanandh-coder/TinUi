package main

const DefaultIndexHTML = `<!DOCTYPE html><html lang="en"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Showcase - TinPyUI</title>
    <style>
        body { margin: 0; padding: 0; background: #000; overflow: hidden; color: white; font-family: sans-serif; }
        #tinui-root { width: 100vw; height: 100vh; position: relative; }
    <script id="tailwind-config">
    window.tailwind = window.tailwind || {};
    window.tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            "colors": {
                    "on-tertiary-container": "#503d00",
                    "surface-variant": "#36343a",
                    "secondary-fixed-dim": "#cdc0e9",
                    "on-error-container": "#ffdad6",
                    "tertiary-container": "#c9a74d",
                    "surface-tint": "#cfbcff",
                    "primary": "#cfbcff",
                    "outline-variant": "#494551",
                    "secondary": "#cdc0e9",
                    "on-surface": "#e6e0e9",
                    "on-background": "#e6e0e9",
                    "surface": "#141218",
                    "on-secondary-fixed": "#1f1635",
                    "background": "transparent",
                    "on-tertiary-fixed": "#241a00",
                    "on-tertiary": "#3e2e00",
                    "on-primary-fixed-variant": "#4f378a",
                    "surface-container-high": "#2b292f",
                    "primary-container": "#6750a4",
                    "inverse-surface": "#e6e0e9",
                    "on-secondary-fixed-variant": "#4b4263",
                    "surface-container-low": "#1d1b20",
                    "on-error": "#690005",
                    "tertiary-fixed-dim": "#e7c365",
                    "outline": "#948e9c",
                    "surface-dim": "#141218",
                    "secondary-container": "#4d4465",
                    "primary-fixed": "#e9ddff",
                    "error": "#ffb4ab",
                    "inverse-primary": "#6750a4",
                    "on-primary-container": "#e0d2ff",
                    "on-primary-fixed": "#22005d",
                    "inverse-on-surface": "#322f35",
                    "tertiary-fixed": "#ffdf93",
                    "surface-container": "#211f24",
                    "on-surface-variant": "#cbc4d2",
                    "primary-fixed-dim": "#cfbcff",
                    "on-primary": "#381e72",
                    "surface-container-lowest": "#0f0d13",
                    "on-tertiary-fixed-variant": "#594400",
                    "error-container": "#93000a",
                    "surface-bright": "#3b383e",
                    "secondary-fixed": "#e9ddff",
                    "surface-container-highest": "#36343a",
                    "on-secondary-container": "#bfb2da",
                    "on-secondary": "#342b4b",
                    "tertiary": "#e7c365"
            },
            "borderRadius": {
                    "DEFAULT": "0.125rem",
                    "lg": "0.25rem",
                    "xl": "0.5rem",
                    "full": "0.75rem"
            },
            "spacing": {
                    "margin-desktop": "2.5rem",
                    "unit": "4px",
                    "margin-mobile": "1rem",
                    "max-width": "1440px",
                    "gutter": "1.5rem"
            },
            "fontFamily": {
                    "label-mono": ["JetBrains Mono"],
                    "label-caps": ["JetBrains Mono"],
                    "body-lg": ["Plus Jakarta Sans"],
                    "body-md": ["Plus Jakarta Sans"],
                    "headline-md": ["Sora"],
                    "display-lg-mobile": ["Sora"],
                    "display-lg": ["Sora"]
            },
            "fontSize": {
                    "label-mono": ["14px", {"lineHeight": "1.4", "letterSpacing": "0.05em", "fontWeight": "500"}],
                    "label-caps": ["12px", {"lineHeight": "1", "letterSpacing": "0.1em", "fontWeight": "700"}],
                    "body-lg": ["18px", {"lineHeight": "1.6", "fontWeight": "400"}],
                    "body-md": ["16px", {"lineHeight": "1.6", "fontWeight": "400"}],
                    "headline-md": ["24px", {"lineHeight": "1.3", "fontWeight": "600"}],
                    "display-lg-mobile": ["32px", {"lineHeight": "1.2", "fontWeight": "700"}],
                    "display-lg": ["48px", {"lineHeight": "1.1", "letterSpacing": "-0.02em", "fontWeight": "700"}]
            }
          },
        },
      }
    </script><style>
        body { background-color: #030712; scroll-behavior: smooth; cursor: none; overflow-x: hidden; }
        .cursor-trail { position: fixed; width: 20px; height: 20px; border-radius: 50%; pointer-events: none; z-index: 9999; background: radial-gradient(circle, rgba(207,188,255,0.8) 0%, transparent 70%); transition: transform 0.1s ease-out; }
        .glass-card { background: rgba(20, 18, 24, 0.2); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .neon-border-cyan { box-shadow: 0 0 15px rgba(0, 255, 255, 0.2); border-color: rgba(0, 255, 255, 0.3); }
        .neon-border-primary { box-shadow: 0 0 15px rgba(207,188,255,0.2); border-color: rgba(207,188,255,0.3); }
        .reveal-section { transition: all 1s cubic-bezier(0.4, 0, 0.2, 1); opacity: 0; transform: perspective(1000px) translateZ(-100px); filter: blur(10px); }
        .reveal-section.active { opacity: 1; transform: perspective(1000px) translateZ(0); filter: blur(0); }
        .marquee { animation: marquee 30s linear infinite; }
        @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        .glitch-hover:hover { animation: glitch 0.3s cubic-bezier(.25,.46,.45,.94) both infinite; }
        @keyframes glitch { 0% { transform: translate(0); } 20% { transform: translate(-2px, 2px); } 40% { transform: translate(-2px, -2px); } 60% { transform: translate(2px, 2px); } 80% { transform: translate(2px, -2px); } 100% { transform: translate(0); } }
        .terminal-shadow { box-shadow: 0 0 40px rgba(231, 195, 101, 0.1); }
        .pulse-glitch { animation: pulse-glitch 2s infinite; }
        @keyframes pulse-glitch { 0%, 100% { opacity: 1; filter: hue-rotate(0deg); } 50% { opacity: 0.8; filter: hue-rotate(90deg) brightness(1.2); } }
    </style></head>
<body>
    <div id="tinui-root">
        <!-- The Wasm Engine mounts here -->
    </div>
    
    <script src="wasm_exec.js"></script>
    <script src="tin-runtime.js"></script>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&amp;family=Sora:wght@400;600;700;800&amp;family=JetBrains+Mono:wght@400;500;700&amp;display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet">
</body></html>`

const DefaultTinRuntimeJS = `// tin-runtime.js
const go = new Go();

WebAssembly.instantiateStreaming(fetch("app.wasm"), go.importObject).then((result) => {
    go.run(result.instance);
    
    fetch('app.ir.json').then(r => r.text()).then(json => {
        if (typeof BootTinUI === 'function') {
            BootTinUI(json);
setTimeout(() => {
// --- USER SCRIPTS INJECTED AFTER WASM BOOT ---

    (function() {
      const canvas = document.getElementById('shader-canvas-ANIMATION_13');
      function syncSize() {
        const w = window.innerWidth;
        const h = window.innerHeight;
        if (canvas.width !== w || canvas.height !== h) {
          canvas.width  = w;
          canvas.height = h;
        }
      }
      window.addEventListener('resize', syncSize);
      syncSize();

      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (!gl) return;
      const vs = ` + "`" + `attribute vec2 a_position;
    varying vec2 v_texCoord;
    void main() {
      v_texCoord = a_position * 0.5 + 0.5;
      gl_Position = vec4(a_position, 0.0, 1.0);
    }` + "`" + `;
      const fs = ` + "`" + `precision highp float;
    uniform float u_time;
    uniform vec2 u_resolution;
    uniform vec2 u_mouse;
    varying vec2 v_texCoord;
    void main() {
        vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / min(u_resolution.x, u_resolution.y);
        vec2 mouse = (u_mouse.xy / u_resolution.xy) * 2.0 - 1.0;
        float dist = length(uv);
        float angle = atan(uv.y, uv.x);
        
        // Pitch black center
        float core = smoothstep(0.42, 0.38, dist);
        
        float ringWidth = 0.08;
        float ringBase = smoothstep(0.55 + ringWidth, 0.45, dist) * smoothstep(0.38 - ringWidth, 0.42, dist);
        float noise = sin(angle * 8.0 + u_time * 1.5) * 0.03;
        float glow = 0.15 / abs(dist - (0.46 + noise));
        
        vec3 colorCyan = vec3(0.0, 1.0, 1.0); // Neon Cyan
        vec3 colorPink = vec3(1.0, 0.0, 1.0); // Neon Pink
        vec3 ringColor = mix(colorCyan, colorPink, sin(angle + u_time * 0.4) * 0.5 + 0.5);
        
        vec3 finalColor = ringColor * (ringBase + glow * 0.8);
        
        float particles = 0.0;
        for(float i = 0.0; i < 15.0; i++) {
            float t = u_time * (0.15 + i * 0.04);
            float r = 0.6 + i * 0.07;
            vec2 p = vec2(cos(t + i*1.3), sin(t + i*1.3)) * r;
            float pDist = length(uv - p);
            particles += 0.0008 / (pDist * pDist);
        }
        
        float stars = fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453);
        stars = pow(stars, 150.0) * 0.4;
        
        finalColor += (particles + stars) * colorCyan;
        
        // Ensure the core is absolutely black
        finalColor *= (1.0 - core);
        
        gl_FragColor = vec4(finalColor, 1.0);
    }` + "`" + `;
      function cs(type, src) {
        const s = gl.createShader(type);
        gl.shaderSource(s, src);
        gl.compileShader(s);
        return s;
      }
      const prog = gl.createProgram();
      gl.attachShader(prog, cs(gl.VERTEX_SHADER, vs));
      gl.attachShader(prog, cs(gl.FRAGMENT_SHADER, fs));
      gl.linkProgram(prog);
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
      let mouse = { x: canvas.width / 2, y: canvas.height / 2 };
      window.addEventListener('mousemove', (event) => {
        const rect = canvas.getBoundingClientRect();
        if (rect.width && rect.height) {
          const nx = (event.clientX - rect.left) / rect.width;
          const ny = 1.0 - (event.clientY - rect.top) / rect.height;
          mouse.x = nx * canvas.width;
          mouse.y = ny * canvas.height;
        }
      });
      function render(t) {
        gl.viewport(0, 0, canvas.width, canvas.height);
        if (uTime) gl.uniform1f(uTime, t * 0.001);
        if (uRes) gl.uniform2f(uRes, canvas.width, canvas.height);
        if (uMouse) gl.uniform2f(uMouse, mouse.x, mouse.y);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        requestAnimationFrame(render);
      }
      render(0);
    })();
    

        // Cursor Trail Logic
        const cursor = document.getElementById('cursor');
        document.addEventListener('mousemove', (e) => {
            cursor.style.transform = ` + "`" + `translate(${e.clientX - 10}px, ${e.clientY - 10}px)` + "`" + `;
        });

        // Scroll Reveal Observer
        const observerOptions = {
            threshold: 0.1
        };
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.reveal-section').forEach(section => {
            observer.observe(section);
        });

        // Benchmark Counters
        function animateValue(id, start, end, duration) {
            let obj = document.getElementById(id);
            if (!obj) return;
            let range = end - start;
            let current = start;
            let increment = end > start? 1 : -1;
            let stepTime = Math.abs(Math.floor(duration / range));
            let timer = setInterval(function() {
                current += increment;
                obj.textContent = current + (Math.random() > 0.8 ? (Math.random() > 0.5 ? 1 : -1) : 0); // Jitter for legacy
                if (current == end) {
                    clearInterval(timer);
                    // Add micro-fluctuation
                    setInterval(() => {
                        obj.textContent = end + Math.floor(Math.random() * 3) - 1;
                    }, 100);
                }
            }, stepTime);
        }

        setTimeout(() => {
            animateValue("legacy-fps", 0, 14, 2000);
            animateValue("wasm-fps", 0, 120, 1000);
        }, 1000);
        
        // Interaction micro-animations
        document.querySelectorAll('.glass-card').forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = (y - centerY) / 25;
                const rotateY = (centerX - x) / 25;
                card.style.transform = ` + "`" + `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.01)` + "`" + `;
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = ` + "`" + `perspective(1000px) rotateX(0) rotateY(0) scale(1)` + "`" + `;
            });
        });
    
}, 50);
        }
    });

    // Intercept standard link clicks to prevent full page reloads
    document.body.addEventListener('click', (e) => {
        const target = e.target.closest('[data-route-path]');
        if (target) {
            e.preventDefault();
            const route = target.getAttribute('href');
            if (route) {
                window.history.pushState({ route: route }, "", route);
                if (window.TinPyUI && window.TinPyUI.navigate) {
                    window.TinPyUI.navigate(route); 
                }
            }
        }
    });

    window.addEventListener('popstate', (e) => {
        const route = e.state ? e.state.route : "/"; 
        if (window.TinPyUI && window.TinPyUI.navigate) {
            window.TinPyUI.navigate(route, { reverse: true });
        }
    });
});
`

const DefaultMainTin = `component Main():
    div(class_="text-on-surface selection:bg-primary selection:text-on-primary"):
        div(class_="fixed inset-0 w-full h-full -z-50 overflow-hidden pointer-events-none", style="display:block;"):
            canvas(height="4576", id="shader-canvas-ANIMATION_13", style="display:block;width:100%;height:100%", width="1280")
        div(class_="cursor-trail", id="cursor", style="transform: translate(1264px, 3818px);")
        nav(class_="fixed top-0 w-full z-50 bg-surface-container-lowest/30 backdrop-blur-xl border-b border-outline-variant/10"):
            div(class_="flex justify-between items-center max-w-max-width mx-auto px-margin-desktop py-4"):
                div(class_="font-display-lg-mobile text-display-lg-mobile font-bold text-primary tracking-tighter"):
                    Span(text="TinPyUI")
                div(class_="hidden md:flex gap-8 items-center"):
                    a(class_="font-body-md text-body-md text-primary border-b-2 border-primary pb-1", href="#"):
                        Span(text="Showcase")
                    a(class_="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-colors", href="#"):
                        Span(text="Experiments")
                    a(class_="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-colors", href="#"):
                        Span(text="Docs")
                    a(class_="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-colors", href="#"):
                        Span(text="Community")
                div(class_="flex items-center gap-4"):
                    a(class_="material-symbols-outlined text-primary cursor-pointer hover:scale-110 transition-transform", href="https://github.com/barathanandh-coder/TinPyUI", target="_blank"):
                        Span(text="terminal")
                    button(class_="bg-primary text-on-primary px-6 py-2 font-body-md font-bold hover:scale-105 transition-transform active:scale-95"):
                        Span(text="Join the Beta")
        main(class_="relative bg-transparent"):
            section(class_="relative min-h-[90vh] flex items-center overflow-hidden bg-transparent"):
                div(class_="container mx-auto px-margin-desktop grid md:grid-cols-2 gap-12 items-center relative z-10"):
                    div(class_="space-y-8"):
                        h1(class_="font-display-lg text-display-lg text-on-surface leading-[1.05] tracking-tight"):
                            Span(text="The Wasm")
                            br()
                            span(class_="text-primary italic"):
                                Span(text="Showcase.")
                        div(class_="h-12 overflow-hidden"):
                            div(class_="transition-all duration-500 font-label-mono text-headline-md text-secondary", id="morph-subheadline"):
                                Span(text="Experience the limit of the Zero-DOM engine.")
                        p(class_="font-body-lg text-body-lg text-on-surface-variant max-w-lg"):
                            Span(text="Dive into the vanguard of web graphics. These experiments are rendered directly to WebGL via our specialized WebAssembly kernel, achieving performance previously impossible in a browser.")
                        div(class_="flex gap-4"):
                            a(class_="bg-tertiary text-on-tertiary-fixed px-8 py-4 font-bold rounded-lg shadow-[0_0_20px_rgba(231,195,101,0.4)] hover:scale-105 transition-all inline-block", href="#experiments"):
                                Span(text="Explore Experiments")
                            button(class_="border border-primary text-primary px-8 py-4 font-bold rounded-lg hover:bg-primary/10 transition-all"):
                                Span(text="Submit Your Experiment")
            section(class_="py-24 relative reveal-section px-margin-desktop max-w-max-width mx-auto bg-transparent active", id="experiments"):
                div(class_="mb-16"):
                    span(class_="font-label-caps text-primary tracking-widest block mb-4"):
                        Span(text="VANGUARD PROJECTS")
                    h2(class_="font-display-lg text-display-lg-mobile text-on-surface"):
                        Span(text="Live Experiments")
                div(class_="grid md:grid-cols-3 gap-8"):
                    div(class_="glass-card neon-border-primary p-0 group hover:-translate-y-2 transition-transform duration-500 cursor-pointer overflow-hidden flex flex-col min-h-[400px]"):
                        div(class_="h-48 bg-gradient-to-br from-primary/20 to-surface-container relative overflow-hidden"):
                            div(class_="absolute inset-0 opacity-40 group-hover:opacity-100 transition-opacity flex items-center justify-center"):
                                span(class_="material-symbols-outlined text-[80px] text-primary animate-pulse"):
                                    Span(text="waves")
                            div(class_="absolute top-3 left-3 flex gap-1.5"):
                                div(class_="w-2 h-2 rounded-full bg-[#ff5f56]")
                                div(class_="w-2 h-2 rounded-full bg-[#ffbd2e]")
                                div(class_="w-2 h-2 rounded-full bg-[#27c93f]")
                        div(class_="p-8 space-y-4 flex-1 flex flex-col"):
                            h3(class_="font-headline-md text-headline-md text-primary"):
                                Span(text="Real-time Fluid Dynamics")
                            p(class_="font-body-md text-on-surface-variant flex-1"):
                                Span(text="A Navier-Stokes simulation computed entirely in .tin syntax, pushing 2M particles at 120FPS.")
                            button(class_="w-full py-3 bg-primary/10 border border-primary text-primary font-bold hover:bg-primary hover:text-on-primary transition-all"):
                                Span(text="Launch Demo")
                    div(class_="glass-card neon-border-cyan p-0 group hover:-translate-y-2 transition-transform duration-500 cursor-pointer overflow-hidden flex flex-col min-h-[400px]"):
                        div(class_="h-48 bg-gradient-to-br from-secondary/20 to-surface-container relative overflow-hidden"):
                            div(class_="absolute inset-0 opacity-40 group-hover:opacity-100 transition-opacity flex items-center justify-center"):
                                span(class_="material-symbols-outlined text-[80px] text-secondary animate-spin", style="animation-duration: 8s;"):
                                    Span(text="hub")
                            div(class_="absolute top-3 left-3 flex gap-1.5"):
                                div(class_="w-2 h-2 rounded-full bg-outline")
                                div(class_="w-2 h-2 rounded-full bg-outline")
                        div(class_="p-8 space-y-4 flex-1 flex flex-col"):
                            h3(class_="font-headline-md text-headline-md text-secondary"):
                                Span(text="Neural Network Visualizer")
                            p(class_="font-body-md text-on-surface-variant flex-1"):
                                Span(text="Interactive weight mapping for a live Transformer model, rendered as a 3D topographic manifold.")
                            button(class_="w-full py-3 bg-secondary/10 border border-secondary text-secondary font-bold hover:bg-secondary hover:text-on-secondary transition-all"):
                                Span(text="Launch Demo")
                    div(class_="glass-card neon-border-primary p-0 group hover:-translate-y-2 transition-transform duration-500 cursor-pointer overflow-hidden flex flex-col min-h-[400px]"):
                        div(class_="h-48 bg-gradient-to-br from-tertiary/20 to-surface-container relative overflow-hidden"):
                            div(class_="absolute inset-0 opacity-40 group-hover:opacity-100 transition-opacity flex items-center justify-center"):
                                span(class_="material-symbols-outlined text-[80px] text-tertiary"):
                                    Span(text="blur_on")
                            div(class_="absolute top-3 left-3 flex gap-1.5"):
                                div(class_="w-2 h-2 rounded-full bg-outline")
                        div(class_="p-8 space-y-4 flex-1 flex flex-col"):
                            h3(class_="font-headline-md text-headline-md text-tertiary"):
                                Span(text="1M Particle Sim")
                            p(class_="font-body-md text-on-surface-variant flex-1"):
                                Span(text="Stress testing the Wasm kernel with massive point clouds responding to dynamic audio input.")
                            button(class_="w-full py-3 bg-tertiary/10 border border-tertiary text-tertiary font-bold hover:bg-tertiary hover:text-on-tertiary transition-all"):
                                Span(text="Launch Demo")
            section(class_="py-24 bg-surface-container-lowest/10 backdrop-blur-sm reveal-section active"):
                div(class_="max-w-max-width mx-auto px-margin-desktop"):
                    div(class_="text-center mb-16"):
                        span(class_="font-label-caps text-secondary tracking-widest block mb-4"):
                            Span(text="RAW BENCHMARKS")
                        h2(class_="font-display-lg text-display-lg-mobile text-on-surface"):
                            Span(text="Performance Lab")
                    div(class_="grid md:grid-cols-2 gap-12"):
                        div(class_="glass-card p-10 border-error/30 relative"):
                            div(class_="absolute top-4 right-6 font-label-mono text-error text-xs"):
                                Span(text="STATUS: BOTTLENECKED")
                            h4(class_="font-headline-md text-error mb-8"):
                                Span(text="Legacy DOM")
                            div(class_="space-y-8"):
                                div(class_="flex items-end gap-4"):
                                    span(class_="font-display-lg text-[80px] text-error leading-none", id="legacy-fps"):
                                        Span(text="14")
                                    span(class_="font-label-mono text-on-surface-variant pb-2"):
                                        Span(text="FPS")
                                div(class_="h-2 w-full bg-error/10 rounded-full"):
                                    div(class_="h-full bg-error w-[15%]")
                                p(class_="text-on-surface-variant text-sm font-body-md"):
                                    Span(text="Reflow/Repaint overhead stalling main thread during complex animation cycles.")
                        div(class_="glass-card p-10 border-primary/30 relative"):
                            div(class_="absolute top-4 right-6 font-label-mono text-primary text-xs flex items-center gap-2"):
                                span(class_="w-2 h-2 rounded-full bg-primary animate-ping")
                                Span(text="STABLE")
                            h4(class_="font-headline-md text-primary mb-8"):
                                Span(text="TinPyUI Wasm")
                            div(class_="space-y-8"):
                                div(class_="flex items-end gap-4"):
                                    span(class_="font-display-lg text-[80px] text-primary leading-none", id="wasm-fps"):
                                        Span(text="120")
                                    span(class_="font-label-mono text-on-surface-variant pb-2"):
                                        Span(text="FPS")
                                div(class_="h-2 w-full bg-primary/10 rounded-full"):
                                    div(class_="h-full bg-primary w-full shadow-[0_0_15px_rgba(207,188,255,0.5)]")
                                p(class_="text-on-surface-variant text-sm font-body-md"):
                                    Span(text="Direct GPU pipeline via WebAssembly. Zero DOM interaction, 100% efficient vector pushing.")
            section(class_="py-24 bg-transparent reveal-section active"):
                div(class_="max-w-max-width mx-auto px-margin-desktop text-center mb-16"):
                    h2(class_="font-display-lg text-display-lg-mobile text-on-surface"):
                        Span(text="The Component Lab")
                    p(class_="text-on-surface-variant mt-4 font-body-lg"):
                        Span(text="Interactive primitives pulsing with reactive neural signals.")
                div(class_="flex flex-wrap justify-center gap-12 items-center"):
                    div(class_="group flex flex-col items-center gap-4"):
                        div(class_="w-40 h-40 rounded-xl glass-card flex items-center justify-center hover:scale-110 transition-all cursor-pointer relative overflow-hidden group"):
                            div(class_="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity")
                            div(class_="px-6 py-3 border-2 border-primary text-primary font-bold rounded-full pulse-glitch"):
                                Span(text="Button()")
                        span(class_="font-label-mono text-primary"):
                            Span(text="Interactive State")
                    div(class_="group flex flex-col items-center gap-4"):
                        div(class_="w-40 h-40 rounded-xl glass-card flex items-center justify-center hover:scale-110 transition-all cursor-pointer relative"):
                            div(class_="absolute inset-0 bg-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity")
                            div(class_="font-display-lg-mobile text-primary tracking-widest bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-tertiary animate-pulse"):
                                Span(text="TEXT")
                        span(class_="font-label-mono text-secondary"):
                            Span(text="GradientText()")
                    div(class_="group flex flex-col items-center gap-4"):
                        div(class_="w-40 h-40 rounded-xl glass-card flex items-center justify-center hover:scale-110 transition-all cursor-pointer relative group"):
                            div(class_="w-24 h-24 border-2 border-dashed border-tertiary/50 rounded-full animate-spin-slow flex items-center justify-center group-hover:border-tertiary transition-colors", style="animation-duration: 10s;"):
                                span(class_="material-symbols-outlined text-tertiary text-4xl"):
                                    Span(text="settings_input_component")
                        span(class_="font-label-mono text-tertiary"):
                            Span(text="Loader()")
                    div(class_="group flex flex-col items-center gap-4"):
                        div(class_="w-40 h-40 rounded-xl glass-card flex flex-col gap-3 p-6 justify-center hover:scale-110 transition-all cursor-pointer group"):
                            div(class_="h-2 w-full bg-outline-variant/30 rounded")
                            div(class_="h-2 w-2/3 bg-primary rounded shadow-[0_0_8px_rgba(207,188,255,0.4)]")
                            div(class_="h-2 w-1/2 bg-outline-variant/30 rounded")
                        span(class_="font-label-mono text-primary"):
                            Span(text="ProgressBar()")
            section(class_="py-24 reveal-section bg-transparent active"):
                div(class_="max-w-max-width mx-auto px-margin-desktop"):
                    div(class_="mb-12"):
                        span(class_="font-label-caps text-primary tracking-widest block mb-4"):
                            Span(text="BLUEPRINT")
                        h2(class_="font-display-lg text-display-lg-mobile text-on-surface"):
                            Span(text="The Engine Blueprint")
                    div(class_="grid lg:grid-cols-2 gap-px bg-outline-variant/30 rounded-xl overflow-hidden shadow-2xl border border-outline-variant/50"):
                        div(class_="bg-[#0d1117] p-8 font-label-mono text-sm leading-relaxed overflow-x-auto min-h-[500px]"):
                            div(class_="flex items-center gap-2 mb-6"):
                                div(class_="flex gap-1.5"):
                                    div(class_="w-3 h-3 rounded-full bg-[#ff5f56]")
                                    div(class_="w-3 h-3 rounded-full bg-[#ffbd2e]")
                                    div(class_="w-3 h-3 rounded-full bg-[#27c93f]")
                                span(class_="text-on-surface-variant ml-4 text-xs"):
                                    Span(text="dashboard.tin")
                            code(class_="text-[#c9d1d9]"):
                                span(class_="text-[#ff7b72]"):
                                    Span(text="component")
                                span(class_="text-[#d2a8ff]"):
                                    Span(text="Dashboard")
                                Span(text="():")
                                br()
                                Span(text="Container(align=")
                                span(class_="text-[#a5d6ff]"):
                                    Span(text="'center'")
                                Span(text=", justify=")
                                span(class_="text-[#a5d6ff]"):
                                    Span(text="'center'")
                                Span(text=", width=")
                                span(class_="text-[#a5d6ff]"):
                                    Span(text="'full'")
                                Span(text=", padding=")
                                span(class_="text-[#79c0ff]"):
                                    Span(text="30")
                                Span(text="):")
                                br()
                                Span(text="GradientText(text=")
                                span(class_="text-[#a5d6ff]"):
                                    Span(text="'Active Metrics'")
                                Span(text=", animation=")
                                span(class_="text-[#a5d6ff]"):
                                    Span(text="'neon-pulse'")
                                Span(text=")")
                                br()
                                Span(text="Card(title=")
                                span(class_="text-[#a5d6ff]"):
                                    Span(text="'Real-time FPS'")
                                Span(text=", value=")
                                span(class_="text-[#79c0ff]"):
                                    Span(text="120")
                                Span(text=", glow=")
                                span(class_="text-[#ff7b72]"):
                                    Span(text="True")
                                Span(text="):")
                                br()
                                Span(text="Button(text=")
                                span(class_="text-[#a5d6ff]"):
                                    Span(text="'Interact'")
                                Span(text=", onClick=trigger_action, color=")
                                span(class_="text-[#a5d6ff]"):
                                    Span(text="'neon-cyan'")
                                Span(text=")")
                                br()
                                br()
                                span(class_="text-[#8b949e]"):
                                    Span(text="# .tin rendered execution on WebAssembly")
                                br()
                                span(class_="text-[#d2a8ff]"):
                                    Span(text="mount")
                                Span(text="(Dashboard)")
                        div(class_="relative bg-background/30 backdrop-blur-md flex items-center justify-center overflow-hidden"):
                            div(class_="absolute inset-0 opacity-20 pointer-events-none", style="background-image: radial-gradient(circle at 2px 2px, #cfbcff 1px, transparent 0); background-size: 24px 24px;")
                            div(class_="relative z-10 glass-card p-10 neon-border-primary text-center"):
                                h3(class_="font-display-lg-mobile text-primary tracking-widest mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-tertiary"):
                                    Span(text="NEON ACTIVE")
                                div(class_="flex flex-col gap-4"):
                                    div(class_="h-1 w-full bg-primary-container rounded-full overflow-hidden"):
                                        div(class_="h-full bg-primary w-2/3 shadow-[0_0_10px_rgba(207,188,255,1)] animate-pulse")
                                    div(class_="flex justify-between font-label-mono text-xs text-on-surface-variant"):
                                        span(class_=""):
                                            Span(text="THROUGHPUT")
                                        span(class_=""):
                                            Span(text="8.4 GB/S")
                                button(class_="mt-8 px-6 py-2 border border-primary/50 text-primary font-bold hover:bg-primary hover:text-on-primary transition-all"):
                                    Span(text="INTERACT")
                            div(class_="absolute bottom-4 right-4 flex items-center gap-2 text-xs font-label-mono text-on-surface-variant/50"):
                                span(class_="w-2 h-2 rounded-full bg-green-500 animate-ping")
                                Span(text="LIVE PREVIEW")
            section(class_="py-32 relative reveal-section active"):
                div(class_="max-w-4xl mx-auto px-margin-mobile text-center"):
                    div(class_="glass-card p-16 border-primary/20 relative overflow-hidden"):
                        div(class_="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent")
                        h2(class_="font-display-lg text-display-lg-mobile text-on-surface mb-8"):
                            Span(text="Ready to push the boundary?")
                        p(class_="text-on-surface-variant mb-12 font-body-lg max-w-xl mx-auto"):
                            Span(text="Join a community of developers rebuilding the web with pure Pythonic syntax and native performance.")
                        div(class_="flex flex-col sm:flex-row gap-6 justify-center"):
                            button(class_="bg-primary text-on-primary px-12 py-5 font-bold rounded-lg hover:scale-105 transition-transform text-lg shadow-[0_0_30px_rgba(207,188,255,0.3)]"):
                                Span(text="Join the Beta")
                            button(class_="glass-card text-on-surface border-outline-variant px-12 py-5 font-bold rounded-lg hover:bg-white/5 transition-all text-lg"):
                                Span(text="Submit Your Experiment")
        footer(class_="bg-surface-container-lowest/30 backdrop-blur-md py-12 border-t-2 border-tertiary"):
            div(class_="flex flex-col md:flex-row justify-between items-center max-w-max-width mx-auto px-margin-desktop gap-8"):
                div(class_="font-headline-md text-headline-md text-primary"):
                    Span(text="TinPyUI")
                div(class_="flex gap-12 font-label-mono text-label-mono"):
                    a(class_="text-outline hover:text-tertiary transition-colors hover:translate-x-1 transition-transform", href="#"):
                        Span(text="Docs")
                    a(class_="text-outline hover:text-tertiary transition-colors hover:translate-x-1 transition-transform", href="https://github.com/barathanandh-coder/TinPyUI", target="_blank"):
                        Span(text="GitHub")
                    a(class_="text-outline hover:text-tertiary transition-colors hover:translate-x-1 transition-transform", href="#"):
                        Span(text="Discord")
                    a(class_="text-outline hover:text-tertiary transition-colors hover:translate-x-1 transition-transform", href="#"):
                        Span(text="Status")
                div(class_="font-label-mono text-label-mono text-outline text-right"):
                    p(class_=""):
                        Span(text="© 2026 TinPyUI Framework.")
                    p(class_="text-[10px] opacity-50"):
                        Span(text="Showcase Portal v1.0. Zero-DOM Edition.")

`
