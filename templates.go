package main

const DefaultIndexHTML = `<!DOCTYPE html><html lang="en"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TinPyUI App</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Sora:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet">
	<script id="tailwind-config">
      tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            "colors": {
                    "on-tertiary-container": "#503d00", "surface-variant": "#36343a", "secondary-fixed-dim": "#cdc0e9",
                    "on-error-container": "#ffdad6", "tertiary-container": "#c9a74d", "surface-tint": "#cfbcff",
                    "primary": "#cfbcff", "outline-variant": "#494551", "secondary": "#cdc0e9", "on-surface": "#e6e0e9",
                    "on-background": "#e6e0e9", "surface": "#141218", "on-secondary-fixed": "#1f1635", "background": "transparent",
                    "on-tertiary-fixed": "#241a00", "on-tertiary": "#3e2e00", "on-primary-fixed-variant": "#4f378a",
                    "surface-container-high": "#2b292f", "primary-container": "#6750a4", "inverse-surface": "#e6e0e9",
                    "on-secondary-fixed-variant": "#4b4263", "surface-container-low": "#1d1b20", "on-error": "#690005",
                    "tertiary-fixed-dim": "#e7c365", "outline": "#948e9c", "surface-dim": "#141218", "secondary-container": "#4d4465",
                    "primary-fixed": "#e9ddff", "error": "#ffb4ab", "inverse-primary": "#6750a4", "on-primary-container": "#e0d2ff",
                    "on-primary-fixed": "#22005d", "inverse-on-surface": "#322f35", "tertiary-fixed": "#ffdf93",
                    "surface-container": "#211f24", "on-surface-variant": "#cbc4d2", "primary-fixed-dim": "#cfbcff",
                    "on-primary": "#381e72", "surface-container-lowest": "#0f0d13", "on-tertiary-fixed-variant": "#594400",
                    "error-container": "#93000a", "surface-bright": "#3b383e", "secondary-fixed": "#e9ddff",
                    "surface-container-highest": "#36343a", "on-secondary-container": "#bfb2da", "on-secondary": "#342b4b",
                    "tertiary": "#e7c365"
            },
            "spacing": { "margin-desktop": "2.5rem", "margin-mobile": "1rem", "max-width": "1440px" },
            "fontFamily": { "label-mono": ["JetBrains Mono"], "display-lg-mobile": ["Sora"], "display-lg": ["Sora"], "headline-md": ["Sora"], "body-lg": ["Plus Jakarta Sans"], "body-md": ["Plus Jakarta Sans"] }
          }
        }
      }
    </script>
</head>
<body>
    <div id="tinui-root">
        <!-- The Wasm Engine mounts here -->
    </div>
    <script src="wasm_exec.js"></script>
    <script src="tin-runtime.js"></script>
</body></html>`

const DefaultTinRuntimeJS = `// tin-runtime.js — TinPyUI v1.5 Runtime
const go = new Go();

function _tinResolvePaletteColor(name) {
  const palette = {
    'neon-cyan': '#00f2fe', 'neon-purple': '#9b51e0', 'neon-pink': '#ff007f',
    'dark-core': '#0a0b10', 'white': '#ffffff', 'muted': '#747d8c'
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

const _TIN_VERT_SHADER = ` + "`" + `
  attribute vec2 a_position;
  varying vec2 v_uv;
  void main() {
    v_uv = a_position * 0.5 + 0.5;
    gl_Position = vec4(a_position, 0.0, 1.0);
  }
` + "`" + `;

// Built-in effect shaders
const _TIN_SHADERS = {
  'cyber-wave': ` + "`" + `
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
  ` + "`" + `,
  'particles': ` + "`" + `
    precision mediump float;
    uniform float u_time;
    uniform vec2 u_resolution;
    varying vec2 v_uv;
    float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    void main() {
      vec2 uv = v_uv;
      float glow = 0.0;
      for (float i = 0.0; i < 12.0; i++) {
        vec2 seed = vec2(i * 1.618, i * 2.39);
        vec2 pos = vec2(hash(seed + 0.1), hash(seed + 0.2));
        float t = fract(u_time * (0.04 + hash(seed) * 0.04) + hash(seed + 0.5));
        pos.y = 1.0 - t;
        pos.x = fract(pos.x + sin(t * 6.28 + i) * 0.1);
        float d = length(uv - pos);
        glow += 0.0003 / (d * d + 0.0001);
      }
      vec3 col = mix(vec3(0.61, 0.32, 0.88), vec3(0.0, 0.95, 0.99), uv.x);
      gl_FragColor = vec4(col * clamp(glow, 0.0, 1.0), clamp(glow, 0.0, 0.7));
    }
  ` + "`" + `,
  'black-hole': ` + "`" + `
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
  ` + "`" + `,
  'cyber-grid': ` + "`" + `
    precision mediump float;
    uniform float u_time;
    uniform vec2 u_resolution;
    varying vec2 v_uv;
    void main() {
      vec2 uv = v_uv * 20.0;
      vec2 grid = abs(fract(uv - 0.5) - 0.5) / fwidth(uv);
      float line = min(grid.x, grid.y);
      float g = 1.0 - min(line, 1.0);
      float pulse = 0.5 + 0.5 * sin(u_time * 0.8 + v_uv.y * 5.0);
      vec3 col = mix(vec3(0.61, 0.32, 0.88), vec3(0.0, 0.95, 0.99), v_uv.x) * g * pulse;
      gl_FragColor = vec4(col, g * 0.5);
    }
  ` + "`" + `
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

  // Parse user uniforms if provided
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
      ctx.fillStyle = color.replace(')', ',' + p.a + ')').replace('rgb', 'rgba').replace('#', 'rgba(');
      // Fallback: just use hex with opacity via globalAlpha
      ctx.globalAlpha = p.a;
      ctx.fillStyle = color;
      ctx.fill();
      ctx.globalAlpha = 1;
    }
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
}

WebAssembly.instantiateStreaming(fetch("app.wasm"), go.importObject).then((result) => {
    go.run(result.instance);
    fetch('app.ir.json').then(r => r.text()).then(json => {
        if (typeof BootTinUI === 'function') {
            BootTinUI(json);
            setTimeout(() => {
                // Mount all shader layers
                document.querySelectorAll('[data-shader-effect]').forEach(el => {
                    _tinMountShaderLayer(el);
                });
                // Mount standalone WebGL canvases
                document.querySelectorAll('[data-webgl-canvas]').forEach(el => {
                    _tinMountWebGLCanvas(el);
                });
                // Mount particle fields
                document.querySelectorAll('[data-particle-field]').forEach(el => {
                    _tinMountParticleField(el);
                });
                // Scroll reveal
                const observer = new IntersectionObserver(entries => {
                    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('active'); });
                }, { threshold: 0.1 });
                document.querySelectorAll('[data-scroll-reveal]').forEach(el => observer.observe(el));
            }, 50);
        }
    });

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
});
`

const DefaultStarterTin = `component Main():
    Section(paddingY = 64, align = "center", justify = "center", minHeight = "screen"):
        Heading(text = "Hello from TinPyUI", color = "neon-cyan", size = "h1")
        Text(text = "Edit main.tin to get started.", color = "muted", marginTop = 24)
`
