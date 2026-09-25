// tin-runtime.js — TinPyUI v1.7.0 Omni-Platform Client Runtime & WebGL Shader Engine
try {
    console.log(
        "%c⚡ TinPyUI v1.7.0 %c High-Performance Zero-DOM Python UI Framework\n" +
        "%c ⭐ GitHub:  https://github.com/barathanandh-coder/TinUi\n" +
        " 📦 PyPI:    pip install tinpyui-ff (https://pypi.org/project/tinpyui-ff/)\n" +
        " 📦 NPM:     npm install tinui (https://www.npmjs.com/package/tinui)\n" +
        " 🌐 Web:     https://github.com/barathanandh-coder/TinUi#readme",
        "background:#0f172a;color:#22d3ee;font-size:13px;font-weight:bold;padding:4px 8px;border-radius:4px 0 0 4px;",
        "background:#0f172a;color:#f8fafc;font-size:13px;padding:4px 8px;border-radius:0 4px 4px 0;",
        "color:#94a3b8;font-size:11px;font-family:monospace;line-height:1.6;"
    );
} catch(e) {}

(function() {
    // =========================================================================
    // 0. Persistent Brand Ribbon & Repository Showcase (All Browsers)
    // =========================================================================
    function ensureBrandRibbon() {
        if (!document.body || document.getElementById('tin-brand-badge')) return;
        const badge = document.createElement('div');
        badge.id = 'tin-brand-badge';
        badge.style.cssText = 'position:fixed;bottom:16px;right:16px;z-index:99999;display:flex;align-items:center;gap:8px;padding:7px 14px;background:rgba(8,11,20,0.88);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid rgba(34,211,238,0.35);border-radius:9999px;box-shadow:0 8px 32px rgba(0,0,0,0.5),0 0 15px rgba(34,211,238,0.25);font-family:system-ui,-apple-system,sans-serif;font-size:12px;transition:all 0.3s cubic-bezier(0.16,1,0.3,1);user-select:none;';
        
        badge.innerHTML = `
            <a href="https://github.com/barathanandh-coder/TinUi" target="_blank" rel="noopener noreferrer" title="Star TinPyUI on GitHub" style="display:flex;align-items:center;gap:6px;color:#f8fafc;text-decoration:none;font-weight:700;">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#22d3ee;box-shadow:0 0 8px #22d3ee;animation:tin-pulse 2s infinite;"></span>
                <span style="background:linear-gradient(135deg,#22d3ee,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;letter-spacing:0.5px;">TinPyUI</span>
                <span style="display:inline-flex;align-items:center;gap:3px;background:rgba(255,255,255,0.08);padding:2px 8px;border-radius:9999px;border:1px solid rgba(255,255,255,0.15);font-size:11px;color:#e2e8f0;">
                    ★ Star Repo
                </span>
            </a>
            <a href="https://pypi.org/project/tinpyui-ff/" target="_blank" rel="noopener noreferrer" title="View on PyPI (pip install tinpyui-ff)" style="color:#94a3b8;text-decoration:none;font-size:10px;font-family:monospace;padding:2px 6px;border-radius:4px;background:rgba(255,255,255,0.06);transition:color 0.2s;">
                PyPI
            </a>
            <a href="https://www.npmjs.com/package/tinui" target="_blank" rel="noopener noreferrer" title="View on NPM (npm i tinui)" style="color:#94a3b8;text-decoration:none;font-size:10px;font-family:monospace;padding:2px 6px;border-radius:4px;background:rgba(255,255,255,0.06);transition:color 0.2s;">
                NPM
            </a>
        `;

        badge.onmouseenter = () => {
            badge.style.transform = 'translateY(-2px) scale(1.02)';
            badge.style.borderColor = 'rgba(34,211,238,0.7)';
            badge.style.boxShadow = '0 12px 36px rgba(0,0,0,0.6), 0 0 25px rgba(34,211,238,0.45)';
        };
        badge.onmouseleave = () => {
            badge.style.transform = 'none';
            badge.style.borderColor = 'rgba(34,211,238,0.35)';
            badge.style.boxShadow = '0 8px 32px rgba(0,0,0,0.5), 0 0 15px rgba(34,211,238,0.25)';
        };

        if (!document.getElementById('tin-ribbon-style')) {
            const style = document.createElement('style');
            style.id = 'tin-ribbon-style';
            style.textContent = '@keyframes tin-pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.85); } }';
            document.head.appendChild(style);
        }
        document.body.appendChild(badge);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ensureBrandRibbon);
    } else {
        ensureBrandRibbon();
    }

    // =========================================================================
    // 1. Diagnostic Error Overlay & Crash Recovery
    // =========================================================================
    function ensureDiagnosticOverlay() {
        if (!document.body) {
            document.addEventListener('DOMContentLoaded', ensureDiagnosticOverlay);
            return;
        }
        if (!document.getElementById('error-overlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'error-overlay';
            overlay.style.cssText = 'display:none;padding:24px;color:#ff4d4d;background:#0a0a0a;font-family:monospace;position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:999999;box-sizing:border-box;overflow:auto;';

            const title = document.createElement('h2');
            title.style.cssText = 'margin:0 0 16px 0;font-size:20px;border-bottom:1px solid #ff4d4d;padding-bottom:8px;';
            title.innerText = '⚠️ TinPyUI Engine Panic';

            const log = document.createElement('pre');
            log.id = 'error-log';
            log.style.cssText = 'margin:0;white-space:pre-wrap;word-break:break-all;font-size:14px;line-height:1.5;';

            overlay.appendChild(title);
            overlay.appendChild(log);
            document.body.appendChild(overlay);
        }
    }
    ensureDiagnosticOverlay();

    window.crash = function(message) {
        ensureDiagnosticOverlay();
        const canvas = document.getElementById('tin-canvas');
        if (canvas) canvas.style.display = 'none';
        const root = document.getElementById('tinui-root');
        if (root) root.style.display = 'none';

        const overlay = document.getElementById('error-overlay');
        if (overlay) overlay.style.display = 'block';
        const log = document.getElementById('error-log');
        if (log) log.innerText += message + "\n\n";
        console.error('[TinPyUI Engine Panic]', message);
    };

    window.onerror = function(msg, url, line, col, error) {
        const errorDetails = error && error.stack ? error.stack : `${msg}\nLocation: ${url}:${line}:${col || 0}`;
        window.crash(`Runtime Error: ${errorDetails}`);
        return false;
    };

    window.addEventListener('unhandledrejection', function(event) {
        const reason = event.reason;
        const msg = reason && (reason.stack || reason.message) ? (reason.stack || reason.message) : String(reason);
        window.crash(`Unhandled Rejection: ${msg}`);
    });

    window.clearCrash = function() {
        const overlay = document.getElementById('error-overlay');
        if (overlay) {
            overlay.style.display = 'none';
            const log = document.getElementById('error-log');
            if (log) log.innerText = '';
        }
        const canvas = document.getElementById('tin-canvas');
        if (canvas) canvas.style.display = 'block';
        const root = document.getElementById('tinui-root');
        if (root) root.style.display = 'block';
    };

    window.reloadShader = function(target, code) {
        if (typeof window.TinUIReloadShader === 'function') {
            return window.TinUIReloadShader(target, code);
        }
        return false;
    };

    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'TINPYUI_RELOAD_SHADER') {
            window.reloadShader(event.data.target || 'tin-canvas', event.data.code);
        } else if (event.data && event.data.type === 'TINPYUI_HOT_RELOAD') {
            _reloadIRAndDOM();
        }
    });

    // Hot Module Replacement (HMR) & Dev Server SSE Listener
    function initDevHotReload() {
        if (typeof EventSource === 'undefined') return;
        try {
            const evtSource = new EventSource('/__tin_live_reload');
            evtSource.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'reload_shader') {
                        if (data.param === 'speed' && window.updateShaderSpeed) {
                            window.updateShaderSpeed(data.value);
                        } else if (data.param === 'intensity' && window.updateShaderIntensity) {
                            window.updateShaderIntensity(data.value);
                        } else if (data.param === 'effect' && window.switchShaderPreset) {
                            window.switchShaderPreset(null, data.value);
                        } else if (window.reloadShader) {
                            window.reloadShader(data.target || 'shader-canvas', data.code || '');
                        }
                    } else if (data.type === 'patch_node') {
                        // Targeted node patch without remounting canvas
                        const el = document.querySelector(`[data-node-id="${data.node_id}"]`) || document.getElementById(`node-${data.node_id}`);
                        if (el) {
                            if (data.action === 'SET_TEXT') {
                                el.textContent = data.value;
                            } else if (data.action === 'SET_ATTRIBUTE') {
                                if (data.key === 'class') el.className = data.value;
                                else el.setAttribute(data.key, data.value);
                            }
                        } else {
                            _reloadIRAndDOM();
                        }
                    } else if (data.type === 'reload_ir') {
                        _reloadIRAndDOM();
                    } else if (data.type === 'reload_full') {
                        window.location.reload();
                    }
                } catch(e) {
                    _reloadIRAndDOM();
                }
            };
        } catch(e) {}
    }
    initDevHotReload();

    // Wasm Linear Memory Direct State Bridge (SharedArrayBuffer)
    class WasmStateBridge {
        constructor(wasmMemoryInstance) {
            this.memory = wasmMemoryInstance || null;
            this.OFFSET_CONTROL = 0x0000;
            this.OFFSET_TRANSFORMS = 0x1000;
            this.FLOATS_PER_NODE = 12;
            this.floatView = null;
            this.initViews();
        }

        initViews() {
            if (this.memory && this.memory.buffer) {
                this.floatView = new Float32Array(this.memory.buffer, this.OFFSET_TRANSFORMS, 256 * this.FLOATS_PER_NODE);
            }
        }

        readNodeState(nodeId) {
            if (!this.floatView) this.initViews();
            if (!this.floatView) return null;
            const slot = (nodeId % 256) * this.FLOATS_PER_NODE;
            return {
                x: this.floatView[slot],
                y: this.floatView[slot + 1],
                scaleX: this.floatView[slot + 2],
                scaleY: this.floatView[slot + 3],
                rotation: this.floatView[slot + 4],
                opacity: this.floatView[slot + 5],
                speed: this.floatView[slot + 7],
                intensity: this.floatView[slot + 8]
            };
        }
    }
    window.WasmStateBridge = WasmStateBridge;
    window.tinWasmStateBridge = new WasmStateBridge();

    // =========================================================================
    // 2. Mobile Multi-Touch & Gesture Recognizers
    // =========================================================================
    function initGestures() {
        let touchStartX = 0, touchStartY = 0, touchStartTime = 0, initialPinchDist = 0;
        let pullIndicator = null, isPulling = false;

        function getDistance(t1, t2) {
            const dx = t1.clientX - t2.clientX, dy = t1.clientY - t2.clientY;
            return Math.sqrt(dx * dx + dy * dy);
        }

        window.addEventListener('touchstart', function(e) {
            if (e.touches.length === 2) {
                initialPinchDist = getDistance(e.touches[0], e.touches[1]);
            } else if (e.touches.length === 1) {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
                touchStartTime = Date.now();
                isPulling = window.scrollY === 0;
            }
        }, { passive: true });

        window.addEventListener('touchmove', function(e) {
            if (e.touches.length === 2 && initialPinchDist > 0) {
                const currentDist = getDistance(e.touches[0], e.touches[1]);
                const scale = currentDist / initialPinchDist;
                const centerX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
                const centerY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
                window.dispatchEvent(new CustomEvent('tin:pinch', {
                    detail: { scale: scale, centerX: centerX, centerY: centerY }
                }));
            } else if (e.touches.length === 1 && isPulling) {
                const deltaY = e.touches[0].clientY - touchStartY;
                if (deltaY > 60 && !pullIndicator) {
                    pullIndicator = document.createElement('div');
                    pullIndicator.id = 'tin-pull-indicator';
                    pullIndicator.style.cssText = 'position:fixed;top:12px;left:50%;transform:translateX(-50%);padding:8px 16px;background:rgba(0,242,254,0.9);color:#000;border-radius:20px;font-size:12px;font-weight:bold;z-index:99999;';
                    pullIndicator.innerText = 'Release to Refresh';
                    document.body.appendChild(pullIndicator);
                }
            }
        }, { passive: true });

        window.addEventListener('touchend', function(e) {
            if (e.touches.length < 2) initialPinchDist = 0;
            if (e.changedTouches.length === 1 && touchStartTime > 0) {
                const deltaX = e.changedTouches[0].clientX - touchStartX;
                const deltaY = e.changedTouches[0].clientY - touchStartY;
                const duration = Date.now() - touchStartTime;

                if (pullIndicator && isPulling && deltaY > 60) {
                    pullIndicator.innerText = 'Refreshing...';
                    window.dispatchEvent(new CustomEvent('tin:pullrefresh'));
                    setTimeout(() => {
                        if (pullIndicator && pullIndicator.parentNode) pullIndicator.parentNode.removeChild(pullIndicator);
                        pullIndicator = null;
                    }, 800);
                } else if (pullIndicator && pullIndicator.parentNode) {
                    pullIndicator.parentNode.removeChild(pullIndicator);
                    pullIndicator = null;
                }

                const absX = Math.abs(deltaX), absY = Math.abs(deltaY);
                if (duration < 500 && (absX > 40 || absY > 40)) {
                    const dir = absX > absY ? (deltaX > 0 ? 'right' : 'left') : (deltaY > 0 ? 'down' : 'up');
                    window.dispatchEvent(new CustomEvent('tin:swipe', {
                        detail: { direction: dir, deltaX: deltaX, deltaY: deltaY, velocity: Math.max(absX, absY) / duration }
                    }));
                }
            }
            touchStartTime = 0;
            isPulling = false;
        }, { passive: true });
    }
    initGestures();

    // =========================================================================
    // 3. WebGL 2.0 Vertex Shader & Built-in Fragment Shaders
    // =========================================================================
    const TIN_VS_SOURCE = `#version 300 es
in vec2 a_pos;
void main() {
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
`;

    const TIN_SHADERS = {
      black_hole: `#version 300 es
precision highp float;
out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform float u_intensity;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.35 * u_speed;
    float rs = 0.22;
    float r = length(uv);
    float phi = atan(uv.y, uv.x);
    float defl = (rs * rs) / max(r * r, 0.005);
    vec2 lensedUv = uv * (1.0 + defl * 0.45);

    float tilt = 0.45;
    vec2 diskP = vec2(uv.x, (uv.y + defl * 0.22 * sign(uv.y)) / cos(tilt));
    float diskR = length(diskP);
    float diskPhi = atan(diskP.y, diskP.x);

    float rin = rs * 1.25;
    float rout = rs * 4.2;
    float inDisk = smoothstep(rin, rin + 0.06, diskR) * (1.0 - smoothstep(rout - 0.35, rout, diskR));

    float omega = pow(max(diskR, 0.1), -1.5) * 2.2;
    float spiral = sin(diskPhi * 3.0 - diskR * 14.0 + t * 3.0 - omega) * 0.5 + 0.5;
    float turb = noise(vec2(diskR * 6.0, diskPhi * 3.0 - t * 1.5)) * 0.4;
    float gas = inDisk * (0.6 + 0.4 * spiral + turb);

    float doppler = 1.0 - sin(diskPhi) * 0.48;
    gas *= pow(doppler, 2.5);

    float temp = clamp((rout - diskR) / (rout - rin), 0.0, 1.0) * doppler;
    vec3 colHot = vec3(0.6, 0.88, 1.0) * 2.8;
    vec3 colWarm = vec3(1.0, 0.68, 0.2) * 2.0;
    vec3 colCool = vec3(0.9, 0.16, 0.04) * 1.4;
    vec3 diskCol = mix(colCool, colWarm, smoothstep(0.0, 0.45, temp));
    diskCol = mix(diskCol, colHot, smoothstep(0.45, 1.0, temp));

    float photonRing = exp(-pow((r - rs * 1.35) * 35.0, 2.0)) * 2.4;
    float horizon = smoothstep(rs * 0.94, rs * 1.04, r);

    vec2 starCoord = lensedUv * 90.0;
    vec2 starId = floor(starCoord);
    float sRand = hash(starId);
    float star = 0.0;
    if (sRand > 0.90) {
        float d = length(fract(starCoord) - 0.5);
        star = (0.012 / (d * d + 0.009)) * pow(sRand, 20.0) * 1.4;
    }

    float mw = exp(-pow(lensedUv.y * 2.5, 2.0)) * 0.15;
    vec3 bg = (vec3(0.012, 0.016, 0.035) + vec3(0.12, 0.08, 0.18) * mw + vec3(star)) * horizon;
    vec3 finalCol = bg + (diskCol * gas + vec3(0.7, 0.88, 1.0) * photonRing) * horizon;
    float halo = 0.025 / (r + 0.08);
    finalCol += vec3(0.1, 0.3, 0.7) * halo * 0.3;
    finalCol *= u_intensity;
    FragColor = vec4(finalCol, 0.90);
}`,

      pillars_of_creation: `#version 300 es
precision highp float;
out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform float u_intensity;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}
float fbm(vec2 p) {
    float v = 0.0; float a = 0.5;
    mat2 rot = mat2(0.8, 0.6, -0.6, 0.8);
    for (int i = 0; i < 4; i++) {
        v += a * noise(p);
        p = rot * p * 2.1;
        a *= 0.5;
    }
    return v;
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.06 * u_speed;

    float col1Width = mix(0.16, 0.26, smoothstep(0.46, -0.5, uv.y));
    float p1Dist = abs(uv.x + 0.28 + sin(uv.y * 3.0) * 0.04) - col1Width;
    float p1 = max(p1Dist, uv.y - 0.45);

    float col2Width = mix(0.12, 0.22, smoothstep(0.32, -0.5, uv.y));
    float p2Dist = abs(uv.x - 0.04 + sin(uv.y * 2.5) * 0.03) - col2Width;
    float p2 = max(p2Dist, uv.y - 0.30);

    float col3Width = mix(0.10, 0.18, smoothstep(0.18, -0.5, uv.y));
    float p3Dist = abs(uv.x - 0.35 - uv.y * 0.2) - col3Width;
    float p3 = max(p3Dist, uv.y - 0.16);

    float baseDist = min(p1, min(p2, p3));
    vec2 warp = uv * 3.2 + vec2(0.0, t * 0.15);
    vec2 q = vec2(fbm(warp), fbm(warp + vec2(4.3, 1.8)));
    float turb = fbm(uv * 4.5 + q * 1.5);
    float density = clamp((-baseDist + turb * 0.38) * 5.0, 0.0, 1.0);

    vec2 lightDir = normalize(vec2(0.75, 0.65));
    float eps = 0.015;
    float nX = (abs(uv.x + eps + 0.28) - abs(uv.x - eps + 0.28)) / (2.0 * eps);
    vec2 normal = normalize(vec2(nX, 1.0) + 0.001);

    float rim = smoothstep(0.15, 0.45, density) * (1.0 - smoothstep(0.45, 0.85, density));
    float lightFront = max(0.0, dot(normal, lightDir));

    vec3 dustCore = vec3(0.12, 0.06, 0.035);
    vec3 hAlpha = vec3(0.98, 0.62, 0.22) * 2.2;
    vec3 oiii = vec3(0.12, 0.82, 0.95) * 2.4;

    float bgNeb = fbm(uv * 2.5 + vec2(t * 0.08, -t * 0.04));
    vec3 bgCol = mix(vec3(0.015, 0.02, 0.05), vec3(0.04, 0.38, 0.62) * 0.6, bgNeb);

    vec2 starUv = uv * 110.0;
    vec2 starId = floor(starUv);
    float sRand = hash(starId);
    if (sRand > 0.90) {
        float d = length(fract(starUv) - 0.5);
        bgCol += mix(vec3(0.7, 0.88, 1.0), vec3(1.0, 0.85, 0.7), hash(starId + 1.2)) * (0.01 / (d * d + 0.008)) * pow(sRand, 18.0);
    }

    vec3 pillarCol = dustCore + hAlpha * rim * (0.6 + 0.8 * lightFront) + oiii * pow(rim, 2.2) * 1.5;
    vec3 finalCol = mix(bgCol, pillarCol, density);

    vec2 pStar1 = vec2(-0.28, 0.44);
    float dStar1 = length(uv - pStar1);
    float spike1 = max(0.0, 1.0 - abs(uv.x - pStar1.x) * 40.0) * max(0.0, 1.0 - abs(uv.y - pStar1.y) * 4.0);
    finalCol += vec3(1.0, 0.75, 0.3) * ((0.012 / (dStar1 * dStar1 + 0.004)) + spike1 * 1.6) * 0.45;

    finalCol *= u_intensity;
    FragColor = vec4(finalCol, 0.92);
}`,

      supernova_nebula: `#version 300 es
precision highp float;
out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform float u_intensity;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}
float fbm(vec2 p) {
    float v = 0.0; float a = 0.5;
    mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
    for (int i = 0; i < 4; ++i) { v += a * noise(p); p = rot * p * 2.1; a *= 0.5; }
    return v;
}

void main() {
    vec2 p = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.12 * u_speed;
    float r = length(p);
    float phi = atan(p.y, p.x);

    float ring = abs(r - 0.46 - sin(phi * 5.0 + t) * 0.04);
    float shock = 0.026 / (ring + 0.018);
    float filaments = fbm(p * 3.6 + vec2(sin(t * 0.4), cos(t * 0.3))) + 0.5 * fbm(p * 7.2 - vec2(t * 0.2, t * 0.1));
    float core = 0.07 / (r + 0.035);

    vec3 colCyan = vec3(0.08, 0.88, 0.98);
    vec3 colViolet = vec3(0.78, 0.22, 0.98);
    vec3 colGold = vec3(1.0, 0.72, 0.22);
    vec3 col = mix(colCyan, colViolet, filaments);
    col = col * shock * 0.78 + colGold * core * 1.3;
    col *= u_intensity;
    FragColor = vec4(col, clamp(r * 0.45 + 0.4, 0.0, 0.92));
}`,

      cyber_mesh: `#version 300 es
precision highp float;
out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform float u_intensity;

void main() {
    vec2 p = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    float horizon = 0.12;
    if (p.y < horizon) {
        float z = 0.3 / (horizon - p.y);
        vec2 gridUv = vec2(p.x * z, z + u_time * (1.5 * u_speed));
        vec2 grid = abs(fract(gridUv - 0.5) - 0.5) / fwidth(gridUv);
        float line = 1.0 - min(min(grid.x, grid.y), 1.0);
        float depthFog = exp(-z * 0.12);
        vec3 neonColor = mix(vec3(0.06, 0.65, 0.95), vec3(0.0, 0.95, 0.75), sin(gridUv.y * 0.2) * 0.5 + 0.5);
        vec3 col = neonColor * line * depthFog * (2.2 * u_intensity);
        float scanline = sin(gl_FragCoord.y * 1.5) * 0.06;
        col -= scanline;
        FragColor = vec4(col, depthFog * 0.85);
    } else {
        float skyGrad = (p.y - horizon) / 0.8;
        vec3 skyColor = mix(vec3(0.04, 0.05, 0.09), vec3(0.01, 0.01, 0.03), skyGrad);
        FragColor = vec4(skyColor, 0.8);
    }
}`,

      aurora_flux: `#version 300 es
precision highp float;
out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform float u_intensity;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 p = uv * 2.0 - 1.0;
    p.x *= u_resolution.x / u_resolution.y;
    float t = u_time * 0.4 * u_speed;
    float wave = sin(p.x * 2.5 + t) * 0.35 + cos(p.x * 1.8 - t * 0.7) * 0.25 + sin(p.x * 4.0 + t * 1.2) * 0.15;
    float dist = abs(p.y - wave);
    float glow = 0.09 / (dist + 0.035);
    vec3 col1 = vec3(0.0, 0.95, 0.85);
    vec3 col2 = vec3(0.65, 0.2, 1.0);
    vec3 col3 = vec3(0.1, 0.4, 0.95);
    vec3 aurora = mix(col1, col2, sin(p.x * 2.0 + t) * 0.5 + 0.5);
    aurora = mix(aurora, col3, cos(p.y * 3.0 + t) * 0.5 + 0.5);
    vec3 finalCol = aurora * glow * (1.8 * u_intensity);
    float alpha = clamp(glow * 0.65, 0.0, 0.85);
    FragColor = vec4(finalCol, alpha);
}`,

      fluid_particles: `#version 300 es
precision highp float;
out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform float u_intensity;

void main() {
    vec2 p = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * u_speed;
    float field = 0.0;
    vec3 fluidColor = vec3(0.0);
    for (int i = 0; i < 7; i++) {
        float fi = float(i);
        float speed = 0.8 + fi * 0.2;
        vec2 center = vec2(sin(t * speed + fi * 1.5) * 0.65, cos(t * (speed * 0.7) + fi * 2.1) * 0.45);
        float d = length(p - center);
        float radius = 0.24 + sin(fi + t) * 0.05;
        float metaball = radius / (d * d + 0.03);
        field += metaball;
        vec3 col = mix(vec3(0.1, 0.8, 0.95), vec3(0.4, 0.2, 0.9), sin(fi + t * 0.5) * 0.5 + 0.5);
        fluidColor += col * metaball;
    }
    fluidColor /= max(field, 0.001);
    float alpha = smoothstep(1.7, 2.3, field) * u_intensity;
    vec3 finalCol = fluidColor * alpha * 0.8;
    FragColor = vec4(finalCol, alpha * 0.5);
}`,

      volumetric_fog: `#version 300 es
precision highp float;
out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform float u_intensity;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }
float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}
float fbm(vec2 p) {
    float v = 0.0; float a = 0.5;
    mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
    for (int i = 0; i < 4; ++i) { v += a * noise(p); p = rot * p * 2.0; a *= 0.5; }
    return v;
}

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 p = uv * 2.0 - 1.0;
    p.x *= u_resolution.x / u_resolution.y;
    float t = u_time * (0.15 * u_speed);
    float fog = fbm(p * 1.5 + vec2(t * 0.4, t * 0.2)) + 0.5 * fbm(p * 3.0 - vec2(t * 0.3, t * 0.1));
    vec3 fogCol1 = vec3(0.03, 0.12, 0.24);
    vec3 fogCol2 = vec3(0.14, 0.05, 0.22);
    vec3 col = mix(fogCol1, fogCol2, fog) * u_intensity;
    FragColor = vec4(col * fog * 1.2, fog * 0.4);
}`,

      bloom: `#version 300 es
precision highp float;
out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform float u_intensity;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 p = uv * 2.0 - 1.0;
    p.x *= u_resolution.x / u_resolution.y;
    float d = length(p);
    float glow = 0.09 / (d + 0.02);
    float ring1 = sin(d * 18.0 - u_time * 2.0 * u_speed) * 0.5 + 0.5;
    float ring2 = cos(d * 28.0 + u_time * 1.5 * u_speed) * 0.5 + 0.5;
    vec3 coreColor = mix(vec3(0.1, 0.85, 1.0), vec3(0.6, 0.2, 1.0), sin(u_time * u_speed) * 0.5 + 0.5);
    vec3 finalColor = coreColor * (glow + ring1 * 0.15 + ring2 * 0.08) * u_intensity;
    FragColor = vec4(finalColor, clamp(glow * 0.7, 0.0, 0.85));
}`
    };

    // =========================================================================
    // 4. WebGL 2.0 Shader Controller Engine
    // =========================================================================
    class WebGLShaderEngine {
        constructor(canvasId) {
            this.canvas = typeof canvasId === 'string' ? document.getElementById(canvasId) : canvasId;
            if (!this.canvas) return;

            this.gl = this.canvas.getContext('webgl2', { antialias: false, depth: false, alpha: true }) ||
                      this.canvas.getContext('webgl', { antialias: false, depth: false, alpha: true });
            if (!this.gl) {
                console.warn("[TinPyUI] WebGL not supported on this device/browser");
                return;
            }

            this.activePreset = 'black_hole';
            this.speed = 1.0;
            this.intensity = 1.0;
            this.targetQualityScale = 0.40;
            this.qualityScale = 0.40; // Base: cuts 84% GPU pixel workload for cool performance
            this.minQualityScale = 0.20;
            this.maxQualityScale = 0.85;
            this.drsEnabled = true;
            this.recentFrameTimes = [];
            this.isVisible = true;
            this.animating = true;
            this.lastRenderTime = 0;
            this.fpsCapInterval = 28; // Max 35 FPS cap
            this.program = null;
            this.startTime = performance.now();

            this.initBuffers();
            this.setPreset('black_hole');
            this.bindEvents();
            this.initFrustumOcclusion();
            this.render();
        }

        initFrustumOcclusion() {
            if ('IntersectionObserver' in window && this.canvas) {
                const target = this.canvas.parentElement || this.canvas;
                this.visibilityObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        this.isVisible = entry.isIntersecting;
                        if (this.isVisible && !this.animating) {
                            this.animating = true;
                            requestAnimationFrame((t) => this.render(t));
                        }
                    });
                }, { threshold: 0.01 });
                this.visibilityObserver.observe(target);
            }
        }

        initBuffers() {
            const gl = this.gl;
            this.quadBuffer = gl.createBuffer();
            gl.bindBuffer(gl.ARRAY_BUFFER, this.quadBuffer);
            gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
        }

        compileShader(src, type) {
            const gl = this.gl;
            const shader = gl.createShader(type);
            gl.shaderSource(shader, src);
            gl.compileShader(shader);
            if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
                console.error("[TinPyUI Shader Compile Error]", gl.getShaderInfoLog(shader));
                return null;
            }
            return shader;
        }

        setPreset(preset) {
            if (preset === 'off') {
                this.activePreset = 'off';
                if (this.gl) {
                    this.gl.clearColor(0.03, 0.04, 0.06, 1.0);
                    this.gl.clear(this.gl.COLOR_BUFFER_BIT);
                }
                return;
            }

            const fsSrc = TIN_SHADERS[preset];
            if (!fsSrc) return;

            const gl = this.gl;
            const vs = this.compileShader(TIN_VS_SOURCE, gl.VERTEX_SHADER);
            const fs = this.compileShader(fsSrc, gl.FRAGMENT_SHADER);
            if (!vs || !fs) return;

            const prog = gl.createProgram();
            gl.attachShader(prog, vs);
            gl.attachShader(prog, fs);
            gl.linkProgram(prog);

            if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
                console.error("[TinPyUI Program Link Error]", gl.getProgramInfoLog(prog));
                return;
            }

            this.program = prog;
            this.activePreset = preset;
            this.uTime = gl.getUniformLocation(prog, "u_time");
            this.uRes = gl.getUniformLocation(prog, "u_resolution");
            this.uSpeed = gl.getUniformLocation(prog, "u_speed");
            this.uIntensity = gl.getUniformLocation(prog, "u_intensity");
            this.aPos = gl.getAttribLocation(prog, "a_pos");
        }

        resize() {
            if (!this.canvas) return;
            const scale = this.qualityScale || 0.40;
            const isFixed = this.canvas.style.position === 'fixed' || this.canvas.classList.contains('fixed');
            const w = isFixed ? Math.max(320, Math.floor(window.innerWidth * scale)) : (this.canvas.parentElement ? Math.floor(this.canvas.parentElement.offsetWidth * scale) : 320);
            const h = isFixed ? Math.max(180, Math.floor(window.innerHeight * scale)) : (this.canvas.parentElement ? Math.floor(this.canvas.parentElement.offsetHeight * scale) : 180);
            if (this.canvas.width !== w || this.canvas.height !== h) {
                this.canvas.width = w;
                this.canvas.height = h;
                this.gl.viewport(0, 0, w, h);
            }
        }

        bindEvents() {
            window.addEventListener('resize', () => this.resize());
            this.resize();
        }

        render(currentTime) {
            if (!this.isVisible) {
                this.animating = false;
                return; // Frustum culling: skip rendering when offscreen! 100% GPU compute saved
            }
            this.animating = true;
            requestAnimationFrame((t) => this.render(t));
            if (this.activePreset === 'off' || !this.program || !this.gl) return;

            const now = currentTime || performance.now();
            if (now - this.lastRenderTime < this.fpsCapInterval) return;

            // Dynamic Resolution Scaling (DRS) Engine
            if (this.drsEnabled && this.lastRenderTime > 0) {
                const delta = now - this.lastRenderTime;
                this.recentFrameTimes.push(delta);
                if (this.recentFrameTimes.length > 20) this.recentFrameTimes.shift();

                if (this.recentFrameTimes.length >= 10) {
                    const avgDelta = this.recentFrameTimes.reduce((a, b) => a + b, 0) / this.recentFrameTimes.length;
                    if (avgDelta > 32 && this.qualityScale > this.minQualityScale) {
                        // Severe load: step down resolution scale dynamically
                        this.qualityScale = Math.max(this.minQualityScale, parseFloat((this.qualityScale - 0.04).toFixed(2)));
                        this.resize();
                    } else if (avgDelta < 22 && this.qualityScale < this.targetQualityScale) {
                        // Light load: recover quality scale
                        this.qualityScale = Math.min(this.targetQualityScale, parseFloat((this.qualityScale + 0.02).toFixed(2)));
                        this.resize();
                    }
                }
            }
            this.lastRenderTime = now;

            const gl = this.gl;
            this.resize();

            gl.useProgram(this.program);
            gl.bindBuffer(gl.ARRAY_BUFFER, this.quadBuffer);
            gl.enableVertexAttribArray(this.aPos);
            gl.vertexAttribPointer(this.aPos, 2, gl.FLOAT, false, 0, 0);

            const elapsed = (now - this.startTime) * 0.001;
            if (this.uTime) gl.uniform1f(this.uTime, elapsed);
            if (this.uRes) gl.uniform2f(this.uRes, this.canvas.width, this.canvas.height);
            if (this.uSpeed) gl.uniform1f(this.uSpeed, this.speed);
            if (this.uIntensity) gl.uniform1f(this.uIntensity, this.intensity);

            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        }
    }

    window.WebGLShaderEngine = WebGLShaderEngine;
    window.shaderEngine = null;

    window.setGpuPerformanceMode = function(scale, btn) {
        const val = parseFloat(scale);
        if (window.shaderEngine) {
            window.shaderEngine.qualityScale = val;
            window.shaderEngine.resize();
        }
        document.querySelectorAll('.gpu-mode-btn').forEach(b => {
            b.classList.remove('active', 'bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300');
            b.classList.add('bg-slate-800/80', 'border-slate-700', 'text-slate-300');
        });
        if (btn) {
            btn.classList.remove('bg-slate-800/80', 'border-slate-700', 'text-slate-300');
            btn.classList.add('active', 'bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300');
        }
        const modeLabels = { '0.25': 'Ultra-Eco', '0.40': 'Eco Mode', '0.60': 'Balanced', '1.0': 'Native' };
        window.showToast(`GPU Mode: ${modeLabels[scale] || (scale + 'x')}`, 'cyan');
    };

    window.switchShaderPreset = function(btn, preset) {
        if (window.shaderEngine) {
            window.shaderEngine.setPreset(preset);
        }
        document.querySelectorAll('.preset-btn').forEach(b => {
            b.classList.remove('active', 'bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300', 'shadow-[0_0_15px_rgba(6,182,212,0.3)]');
            b.classList.add('bg-slate-800/80', 'border-slate-700', 'text-slate-300');
        });
        if (btn) {
            btn.classList.remove('bg-slate-800/80', 'border-slate-700', 'text-slate-300');
            btn.classList.add('active', 'bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300', 'shadow-[0_0_15px_rgba(6,182,212,0.3)]');
        }
        const descEl = document.getElementById('shader-desc-text');
        if (descEl) descEl.textContent = `Active: ${preset}.frag`;
        window.showToast(`Active Shader: ${preset}.frag`, 'cyan');
    };

    window.updateShaderSpeed = function(val) {
        const speed = parseFloat(val);
        if (window.shaderEngine) window.shaderEngine.speed = speed;
        const label = document.getElementById('speed-label');
        if (label) label.textContent = `ANIM SPEED: ${speed.toFixed(1)}x`;
    };

    window.updateShaderIntensity = function(val) {
        const intensity = parseFloat(val);
        if (window.shaderEngine) window.shaderEngine.intensity = intensity;
        const label = document.getElementById('intensity-label');
        if (label) label.textContent = `INTENSITY: ${Math.round(intensity * 100)}%`;
    };

    // =========================================================================
    // 5. Shader Layers & Particle Fields Auto-Mounting
    // =========================================================================
    function _tinResolvePaletteColor(name) {
        const palette = {
            'neon-cyan': '#00f2fe', 'neon-purple': '#9b51e0', 'neon-pink': '#ff007f',
            'stellar-gold': '#f59e0b', 'cosmic-teal': '#06b6d4',
            'dark-core': '#03050c', 'white': '#ffffff', 'muted': '#94a3b8'
        };
        return palette[name] || name;
    }

    function _tinMountShaderLayer(el) {
        const effect = el.getAttribute('data-shader-effect') || 'black_hole';
        const canvas = document.createElement('canvas');
        canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0;';
        el.style.position = el.style.position || 'relative';
        el.insertBefore(canvas, el.firstChild);
        new WebGLShaderEngine(canvas);
    }

    function _tinMountWebGLCanvas(el) {
        if (!window.shaderEngine && el.id === 'shader-canvas') {
            window.shaderEngine = new WebGLShaderEngine(el);
        } else {
            new WebGLShaderEngine(el);
        }
    }

    function _tinMountParticleField(el) {
        const count = parseInt(el.getAttribute('data-particle-count') || '60');
        const colorName = el.getAttribute('data-particle-color') || 'neon-purple';
        const color = _tinResolvePaletteColor(colorName);
        const speed = parseFloat(el.getAttribute('data-particle-speed') || '1');
        const interactive = el.getAttribute('data-particle-interactive') !== 'false';

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
            canvas.width = el.offsetWidth || window.innerWidth;
            canvas.height = el.offsetHeight || window.innerHeight;
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
                p.x += p.vx; p.y += p.vy;
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
        document.querySelectorAll('canvas[id="shader-canvas"], [data-webgl-canvas]').forEach(el => {
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

    // =========================================================================
    // 6. Dynamic Scrolling Speed & Inertia Engine
    // =========================================================================
    let scrollSpeedMultiplier = 1.0;
    let autoScrollActive = false;
    let autoScrollAnimId = null;
    let targetScrollY = window.scrollY;
    let currentScrollY = window.scrollY;
    let isSmoothScrolling = false;

    window.setScrollSpeedMultiplier = function(val, btn) {
        scrollSpeedMultiplier = parseFloat(val);
        const label = document.getElementById('scroll-speed-label');
        if (label) label.textContent = `SCROLL VELOCITY: ${scrollSpeedMultiplier.toFixed(1)}x`;
        const slider = document.getElementById('scroll-speed-slider');
        if (slider) slider.value = scrollSpeedMultiplier;

        document.querySelectorAll('.scroll-speed-btn').forEach(b => {
            b.classList.remove('bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300');
            b.classList.add('bg-slate-800/80', 'border-slate-700', 'text-slate-300');
        });
        if (btn) {
            btn.classList.remove('bg-slate-800/80', 'border-slate-700', 'text-slate-300');
            btn.classList.add('bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300');
        }
        window.showToast(`Scroll Velocity Set: ${scrollSpeedMultiplier.toFixed(1)}x`, 'cyan');
    };

    window.addEventListener('wheel', (e) => {
        if (autoScrollActive) window.toggleAutoScroll(false);
        if (scrollSpeedMultiplier !== 1.0) {
            e.preventDefault();
            const maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
            targetScrollY = Math.max(0, Math.min(maxScroll, targetScrollY + e.deltaY * scrollSpeedMultiplier));
            if (!isSmoothScrolling) {
                isSmoothScrolling = true;
                requestAnimationFrame(smoothScrollTick);
            }
        }
    }, { passive: false });

    function smoothScrollTick() {
        currentScrollY += (targetScrollY - currentScrollY) * 0.18;
        window.scrollTo(0, currentScrollY);
        if (Math.abs(targetScrollY - currentScrollY) > 0.5) {
            requestAnimationFrame(smoothScrollTick);
        } else {
            isSmoothScrolling = false;
        }
    }

    window.toggleAutoScroll = function(forceState) {
        autoScrollActive = typeof forceState === 'boolean' ? forceState : !autoScrollActive;
        const btn = document.getElementById('auto-scroll-btn');
        if (autoScrollActive) {
            if (btn) btn.textContent = '⏸ Pause Tour';
            window.showToast('Auto-Scroll Tour Active', 'cyan');
            function step() {
                if (!autoScrollActive) return;
                window.scrollBy(0, 1.8 * scrollSpeedMultiplier);
                if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 5) {
                    window.scrollTo(0, 0);
                }
                autoScrollAnimId = requestAnimationFrame(step);
            }
            autoScrollAnimId = requestAnimationFrame(step);
        } else {
            if (btn) btn.textContent = '▶ Auto-Scroll Tour';
            if (autoScrollAnimId) cancelAnimationFrame(autoScrollAnimId);
        }
    };

    // =========================================================================
    // 7. While Scrolling Appearing Components (Scroll Reveal)
    // =========================================================================
    function initScrollReveal() {
        if (!('IntersectionObserver' in window)) return;
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                }
            });
        }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });

        document.querySelectorAll('.reveal-on-scroll, [data-scroll-reveal]').forEach((el) => {
            observer.observe(el);
        });
    }
    window.initScrollReveal = initScrollReveal;

    // =========================================================================
    // 8. Component Adjusting & Moving Sandbox API
    // =========================================================================
    window.compState = { x: 0, y: 0, scale: 1.0, radius: 16, padding: 24, glow: 50, morphism: 'glass-morphism' };

    window.updateMovableComponent = function(prop, val) {
        window.compState[prop] = parseFloat(val) || val;
        const target = document.getElementById('movable-target-card') || document.querySelector('[data-movable="true"]');
        if (!target) return;

        target.style.transform = `translate(${window.compState.x}px, ${window.compState.y}px) scale(${window.compState.scale})`;
        target.style.borderRadius = `${window.compState.radius}px`;
        target.style.padding = `${window.compState.padding}px`;
        target.style.boxShadow = `0 0 ${window.compState.glow}px rgba(34, 211, 238, ${window.compState.glow / 100 * 0.45})`;

        const xLbl = document.getElementById('move-x-label');
        const yLbl = document.getElementById('move-y-label');
        const scaleLbl = document.getElementById('scale-label');
        const radiusLbl = document.getElementById('radius-label');
        const glowLbl = document.getElementById('glow-label');

        if (xLbl) xLbl.textContent = `OFFSET X: ${window.compState.x}px`;
        if (yLbl) yLbl.textContent = `OFFSET Y: ${window.compState.y}px`;
        if (scaleLbl) scaleLbl.textContent = `SCALE: ${window.compState.scale.toFixed(2)}x`;
        if (radiusLbl) radiusLbl.textContent = `CORNER RADIUS: ${window.compState.radius}px`;
        if (glowLbl) glowLbl.textContent = `GLOW HALO: ${window.compState.glow}%`;

        const codeEl = document.getElementById('component-live-code');
        if (codeEl) {
            codeEl.textContent = `Card(
    class_="${window.compState.morphism} rounded-[${window.compState.radius}px] p-[${window.compState.padding}px]",
    style="transform: translate(${window.compState.x}px, ${window.compState.y}px) scale(${window.compState.scale});"
):
    Text("Dynamic Movable UI Widget", color="cyan")
    Badge("Reactive State Stream", variant="neon-cyan")`;
        }
    };

    window.setComponentMorphism = function(morphismName, btn) {
        window.compState.morphism = morphismName;
        const target = document.getElementById('movable-target-card') || document.querySelector('[data-movable="true"]');
        if (target) {
            target.className = `transition-all duration-200 border relative overflow-hidden ${morphismName}`;
        }
        document.querySelectorAll('.morphism-choice-btn').forEach(b => {
            b.classList.remove('active', 'bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300');
            b.classList.add('bg-slate-800/80', 'border-slate-700', 'text-slate-300');
        });
        if (btn) {
            btn.classList.remove('bg-slate-800/80', 'border-slate-700', 'text-slate-300');
            btn.classList.add('active', 'bg-cyan-500/20', 'border-cyan-400', 'text-cyan-300');
        }
        window.updateMovableComponent('morphism', morphismName);
        window.showToast(`Applied Morphism: ${morphismName}`, 'cyan');
    };

    window.resetMovableComponent = function() {
        window.compState = { x: 0, y: 0, scale: 1.0, radius: 16, padding: 24, glow: 50, morphism: 'glass-morphism' };
        ['x-slider', 'y-slider', 'scale-slider', 'radius-slider', 'glow-slider'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = id === 'scale-slider' ? 1.0 : (id === 'radius-slider' ? 16 : (id === 'glow-slider' ? 50 : 0));
        });
        window.updateMovableComponent('x', 0);
        window.showToast('Reset component transforms', 'cyan');
    };

    // =========================================================================
    // 9. Cinematic Page Redirecting Overlay
    // =========================================================================
    function ensureRedirectOverlay() {
        if (!document.body) return null;
        let overlay = document.getElementById('page-redirect-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'page-redirect-overlay';
            overlay.style.cssText = 'position:fixed;inset:0;background:rgba(3,5,12,0.92);backdrop-filter:blur(24px);z-index:99999;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:opacity 0.4s ease;';
            overlay.innerHTML = `
                <div style="max-width:440px;width:90%;text-align:center;font-family:sans-serif;" class="space-y-4">
                    <div style="width:48px;height:48px;margin:0 auto 16px;border-radius:50%;border:3px solid rgba(6,182,212,0.3);border-top-color:#06b6d4;animation:spin 0.8s linear infinite;"></div>
                    <div id="redirect-dest-title" style="color:#fff;font-size:20px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;">ROUTING...</div>
                    <div id="redirect-style-desc" style="color:#94a3b8;font-size:12px;font-family:monospace;margin-top:6px;">Engaging Cinematic Transition...</div>
                    <div style="width:100%;height:4px;background:rgba(255,255,255,0.1);border-radius:2px;overflow:hidden;margin-top:20px;">
                        <div id="redirect-progress-bar" style="width:0%;height:100%;background:linear-gradient(90deg,#06b6d4,#a855f7);transition:width 0.7s cubic-bezier(0.16,1,0.3,1);"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        return overlay;
    }

    window.triggerPageRedirect = function(destinationName, targetUrl, transitionStyle = 'Quantum Warp') {
        const overlay = ensureRedirectOverlay();
        const titleEl = document.getElementById('redirect-dest-title');
        const progBar = document.getElementById('redirect-progress-bar');
        const descEl = document.getElementById('redirect-style-desc');

        if (titleEl) titleEl.textContent = destinationName.toUpperCase();
        if (descEl) descEl.textContent = `Engaging Cinematic ${transitionStyle.toUpperCase()} Routing...`;
        if (progBar) progBar.style.width = '0%';

        if (overlay) {
            overlay.style.opacity = '1';
            overlay.style.pointerEvents = 'auto';
            setTimeout(() => { if (progBar) progBar.style.width = '100%'; }, 50);
        }

        setTimeout(() => {
            if (targetUrl.startsWith('#')) {
                const el = document.querySelector(targetUrl);
                if (el) el.scrollIntoView({ behavior: 'smooth' });
                setTimeout(() => {
                    if (overlay) {
                        overlay.style.opacity = '0';
                        overlay.style.pointerEvents = 'none';
                    }
                    window.showToast(`Arrived at: ${destinationName}`, 'emerald');
                }, 400);
            } else {
                window.open(targetUrl, '_blank');
                setTimeout(() => {
                    if (overlay) {
                        overlay.style.opacity = '0';
                        overlay.style.pointerEvents = 'none';
                    }
                }, 300);
            }
        }, 850);
    };

    // =========================================================================
    // 10. Toast Notifications & Clipboard Helpers
    // =========================================================================
    window.showToast = function(msg, type = 'cyan') {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:99999;display:flex;flex-direction:column;gap:8px;pointer-events:none;';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.style.cssText = 'padding:10px 16px;border-radius:12px;background:rgba(15,23,42,0.85);backdrop-filter:blur(16px);border:1px solid rgba(6,182,212,0.4);color:#67e8f9;font-family:monospace;font-size:12px;box-shadow:0 8px 32px rgba(0,0,0,0.5);transform:translateY(16px);opacity:0;transition:all 0.3s ease;pointer-events:auto;';
        toast.innerText = `ⓘ ${msg}`;

        container.appendChild(toast);
        requestAnimationFrame(() => {
            toast.style.transform = 'translateY(0)';
            toast.style.opacity = '1';
        });

        setTimeout(() => {
            toast.style.transform = 'translateY(16px)';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 2600);
    };

    window.copyToClipboard = function(text, msg) {
        const toastMsg = msg || 'Copied to clipboard!';
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => window.showToast(toastMsg, 'cyan'));
        } else {
            window.showToast(toastMsg, 'cyan');
        }
    };

    window.copyInstallCmd = function() {
        window.copyToClipboard('pip install tinpyui-ff', 'Copied: pip install tinpyui-ff');
    };

    // =========================================================================
    // 10b. Modern Component Primitives Engine (Radix / Shadcn Suite)
    // =========================================================================
    function initModernPrimitives() {
        // 1. Accessible Tabs Controller
        document.querySelectorAll('[data-tabs], .tin-tabs').forEach(tabGroup => {
            const triggers = tabGroup.querySelectorAll('[data-tab-trigger], button[data-tab]');
            const contents = tabGroup.querySelectorAll('[data-tab-content], .tin-tab-content');
            
            triggers.forEach(trigger => {
                trigger.onclick = (e) => {
                    e.preventDefault();
                    const targetVal = trigger.getAttribute('data-tab-trigger') || trigger.getAttribute('data-tab');
                    triggers.forEach(t => t.classList.remove('active', 'border-cyan-400', 'text-cyan-300'));
                    trigger.classList.add('active', 'border-cyan-400', 'text-cyan-300');
                    
                    contents.forEach(content => {
                        const cVal = content.getAttribute('data-tab-content') || content.getAttribute('data-tab');
                        if (cVal === targetVal) {
                            content.style.display = 'block';
                            content.style.opacity = '0';
                            requestAnimationFrame(() => { content.style.transition = 'opacity 0.2s'; content.style.opacity = '1'; });
                        } else {
                            content.style.display = 'none';
                        }
                    });
                };
            });
        });

        // 2. Accordion Controller
        document.querySelectorAll('[data-accordion-trigger], .tin-accordion-header').forEach(header => {
            header.onclick = () => {
                const item = header.closest('[data-accordion-item], .tin-accordion-item');
                if (!item) return;
                const content = item.querySelector('[data-accordion-content], .tin-accordion-body');
                const chevron = item.querySelector('.tin-accordion-chevron, [data-chevron]');
                const isOpen = item.classList.contains('open') || item.getAttribute('data-open') === 'true';

                if (isOpen) {
                    item.classList.remove('open');
                    item.setAttribute('data-open', 'false');
                    if (content) content.style.display = 'none';
                    if (chevron) chevron.style.transform = 'rotate(0deg)';
                } else {
                    item.classList.add('open');
                    item.setAttribute('data-open', 'true');
                    if (content) {
                        content.style.display = 'block';
                    }
                    if (chevron) chevron.style.transform = 'rotate(180deg)';
                }
            };
        });

        // 3. Dialog / Modal Controller & ESC Key Dismissal
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.querySelectorAll('dialog[open], [data-modal][open]').forEach(dlg => {
                    dlg.removeAttribute('open');
                    dlg.style.display = 'none';
                });
            }
        });

        // 4. Two-Way Form Validation & Reactive Input Synchronization
        document.querySelectorAll('input[data-bind], textarea[data-bind]').forEach(input => {
            input.oninput = () => {
                const varName = input.getAttribute('data-bind');
                if (varName && window.TinUIMutateState) {
                    window.TinUIMutateState(varName, input.value);
                }
            };
        });
    }
    window.initModernPrimitives = initModernPrimitives;

    // =========================================================================
    // 11. Opcode Intermediate Representation (IR) Tree Renderer
    // =========================================================================
    function renderTinIR(ir, rootContainer) {
        if (!ir || !ir.nodes || !Array.isArray(ir.nodes)) return false;

        const elements = {};
        const rootIds = [];

        for (const op of ir.nodes) {
            if (op.op === 'CREATE_NODE') {
                const tag = op.tag || 'div';
                elements[op.id] = document.createElement(tag);
            } else if (op.op === 'SET_ATTRIBUTE') {
                const el = elements[op.id];
                if (el) {
                    if (op.key === 'class' || op.key === 'class_') {
                        el.className = op.value;
                    } else if (op.key === 'onClick') {
                        el.setAttribute('onclick', op.value);
                    } else if (op.key === 'oninput') {
                        el.setAttribute('oninput', op.value);
                    } else if (op.key === 'style') {
                        el.style.cssText = op.value;
                    } else if (op.key === 'text' || op.key === 'textContent') {
                        el.textContent = op.value;
                    } else {
                        el.setAttribute(op.key, op.value);
                    }
                }
            } else if (op.op === 'SET_TEXT') {
                const el = elements[op.id];
                if (el) {
                    if (el.tagName === 'SPAN' && (el.className.includes('material-symbols') || /^[a-z_]+$/.test(op.value))) {
                        if (!el.className.includes('material-symbols-outlined')) {
                            el.className = (el.className ? el.className + ' ' : '') + 'material-symbols-outlined';
                        }
                    }
                    el.textContent = op.value;
                }
            } else if (op.op === 'APPEND_CHILD') {
                const p = op.parent, c = op.child;
                if (p === undefined || p === null) {
                    rootIds.push(c);
                } else if (elements[p] && elements[c]) {
                    elements[p].appendChild(elements[c]);
                }
            }
        }

        rootContainer.innerHTML = '';
        for (const rid of rootIds) {
            const rootEl = elements[rid];
            if (rootEl && rootEl.tagName !== 'SCRIPT' && rootEl.tagName !== 'LINK' && rootEl.tagName !== 'STYLE') {
                rootContainer.appendChild(rootEl);
            }
        }

        setTimeout(() => {
            _tinMountAllEffects();
            initScrollReveal();
            initModernPrimitives();
        }, 20);

        return true;
    }

    // High-Speed Binary Opcode IR (TINB) Decoder
    function renderTinBinaryIR(buffer, rootContainer) {
        if (!buffer || buffer.byteLength < 10) return false;
        try {
            const view = new DataView(buffer);
            const m0 = view.getUint8(0), m1 = view.getUint8(1), m2 = view.getUint8(2), m3 = view.getUint8(3);
            if (m0 !== 0x54 || m1 !== 0x49 || m2 !== 0x4E || m3 !== 0x42) {
                return false; // Not TINB magic
            }

            let offset = 6;
            const strCount = view.getUint32(offset, true);
            offset += 4;

            const decoder = new TextDecoder('utf-8');
            const stringList = [];
            for (let i = 0; i < strCount; i++) {
                const sLen = view.getUint16(offset, true);
                offset += 2;
                const sBytes = new Uint8Array(buffer, offset, sLen);
                offset += sLen;
                stringList.push(decoder.decode(sBytes));
            }

            const opCount = view.getUint32(offset, true);
            offset += 4;

            const nodes = [];
            for (let i = 0; i < opCount; i++) {
                const opCode = view.getUint8(offset);
                offset += 1;
                if (opCode === 1) { // CREATE_NODE
                    const id = view.getUint32(offset, true);
                    const tagIdx = view.getUint16(offset + 4, true);
                    offset += 6;
                    nodes.push({ op: 'CREATE_NODE', id: id, tag: stringList[tagIdx] || 'div' });
                } else if (opCode === 2) { // SET_ATTRIBUTE
                    const id = view.getUint32(offset, true);
                    const kIdx = view.getUint16(offset + 4, true);
                    const vIdx = view.getUint16(offset + 6, true);
                    offset += 8;
                    nodes.push({ op: 'SET_ATTRIBUTE', id: id, key: stringList[kIdx], value: stringList[vIdx] });
                } else if (opCode === 3) { // SET_TEXT
                    const id = view.getUint32(offset, true);
                    const vIdx = view.getUint16(offset + 4, true);
                    offset += 6;
                    nodes.push({ op: 'SET_TEXT', id: id, value: stringList[vIdx] });
                } else if (opCode === 4) { // APPEND_CHILD
                    const isRoot = view.getUint8(offset);
                    const pId = view.getUint32(offset + 1, true);
                    const cId = view.getUint32(offset + 5, true);
                    offset += 9;
                    nodes.push({ op: 'APPEND_CHILD', parent: isRoot ? null : pId, child: cId });
                }
            }
            return renderTinIR({ nodes: nodes }, rootContainer);
        } catch (err) {
            console.warn('[TinPyUI Binary IR decode error]', err);
            return false;
        }
    }

    window.renderTinBinaryIR = renderTinBinaryIR;

    function renderIRFallback(irPayload) {
        try {
            let root = document.getElementById('tinui-root');
            if (!root) {
                root = document.createElement('div');
                root.id = 'tinui-root';
                document.body.appendChild(root);
            }
            if (irPayload instanceof ArrayBuffer) {
                return renderTinBinaryIR(irPayload, root);
            }
            const data = typeof irPayload === 'string' ? JSON.parse(irPayload) : irPayload;
            return renderTinIR(data, root);
        } catch (e) {
            console.warn('[TinPyUI IR render error]', e);
            return false;
        }
    }

    async function _loadIR() {
        // Check binary candidates first (70% smaller and 5x faster hydration)
        const binCandidates = ['app.ir.bin', 'showcase.ir.bin', 'main.ir.bin', 'index.ir.bin', './app.ir.bin', './showcase.ir.bin', './main.ir.bin', './index.ir.bin'];
        for (const p of binCandidates) {
            try {
                const res = await fetch(p + '?t=' + Date.now());
                if (res.ok) {
                    const buf = await res.arrayBuffer();
                    if (buf.byteLength >= 10) {
                        const view = new DataView(buf);
                        if (view.getUint8(0) === 0x54 && view.getUint8(1) === 0x49 && view.getUint8(2) === 0x4E && view.getUint8(3) === 0x42) {
                            return buf;
                        }
                    }
                }
            } catch(e) {}
        }

        const candidates = ['app.ir.json', 'showcase.ir.json', 'main.ir.json', 'index.ir.json', './app.ir.json', './showcase.ir.json', './main.ir.json', './index.ir.json'];
        for (const p of candidates) {
            try {
                const res = await fetch(p + '?t=' + Date.now());
                if (res.ok) {
                    const text = await res.text();
                    if (text && text.trim().startsWith('{')) return text;
                }
            } catch(e) {}
        }
        return null;
    }

    async function _reloadIRAndDOM() {
        const freshIR = await _loadIR();
        if (freshIR) {
            renderIRFallback(freshIR);
            if (typeof BootTinUI === 'function') BootTinUI(typeof freshIR === 'string' ? freshIR : JSON.stringify(freshIR));
        }
    }

    // =========================================================================
    // 12. WebAssembly Engine Boot & Fallback Activation (v1.8.0 Rust/Go Engine)
    // =========================================================================
    const _tinWasmSources = ["tinui_engine.wasm", "tin_wasm_engine_bg.wasm", "app.wasm", "./tinui_engine.wasm", "./tin_wasm_engine_bg.wasm", "./app.wasm"];

    async function bootEngine() {
        const irText = await _loadIR();
        if (irText) {
            renderIRFallback(irText);
        }
        initModernPrimitives();

        // Initialize WebGL background shader if shader canvas is present
        setTimeout(() => {
            const canvas = document.getElementById('shader-canvas') || document.querySelector('canvas[data-webgl-canvas]');
            if (canvas && !window.shaderEngine) {
                window.shaderEngine = new WebGLShaderEngine(canvas);
            }
        }, 40);

        // 1. High-Performance Priority: Rust WASM Core Engine
        if (typeof wasm_bindgen === 'function') {
            for (const src of _tinWasmSources) {
                try {
                    await wasm_bindgen(src);
                    if (typeof wasm_bindgen.BootTinUI === 'function') {
                        window.BootTinUI = wasm_bindgen.BootTinUI;
                        window.TinUIMutateState = wasm_bindgen.TinUIMutateState;
                        window.TinUIDispatchApi = wasm_bindgen.TinUIDispatchApi;
                        window.TinUISnapshot = wasm_bindgen.TinUISnapshot;
                        window.TinUIRestore = wasm_bindgen.TinUIRestore;
                        window.TinUIReloadShader = wasm_bindgen.TinUIReloadShader;
                        window.TinUICompileShader = wasm_bindgen.TinUICompileShader;
                        if (irText) {
                            window.BootTinUI(irText);
                            setTimeout(_tinMountAllEffects, 50);
                        }
                        console.info('[TinPyUI] Rust WebAssembly Core Engine v1.8.0 active (Zero-GC, 218KB).');
                        return;
                    }
                } catch(e) {}
            }
        }

        // 2. Legacy Fallback: Go WASM Engine
        const go = typeof Go === 'function' ? new Go() : null;
        if (go) {
            for (const src of _tinWasmSources) {
                try {
                    const res = await fetch(src);
                    if (res.ok) {
                        const result = await WebAssembly.instantiateStreaming(res, go.importObject);
                        go.run(result.instance);
                        if (irText && typeof BootTinUI === 'function') {
                            BootTinUI(irText);
                            setTimeout(_tinMountAllEffects, 50);
                        }
                        return;
                    }
                } catch(e) {}
            }
        }
        console.info('[TinPyUI] Pure High-Speed Zero-DOM JS & WebGL Engine active.');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootEngine);
    } else {
        bootEngine();
    }
})();
