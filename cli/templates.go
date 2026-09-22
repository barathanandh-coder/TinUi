package main

const DefaultIndexHTML = `<!DOCTYPE html><html lang="en"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TinPyUI App</title>
</head>
<body>
    <div id="tinui-root">
        <!-- The Wasm Engine mounts here -->
    </div>
    <script src="wasm_exec.js"></script>
    <script src="tin-runtime.js"></script>
</body></html>`

const DefaultTinRuntimeJS = `// tin-runtime.js — TinPyUI v1.6.1 Runtime with Diagnostic Error Overlay & Boundary
(function() {
    function ensureDiagnosticOverlay() {
        if (!document.body) {
            document.addEventListener('DOMContentLoaded', ensureDiagnosticOverlay);
            return;
        }
        if (!document.getElementById('error-overlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'error-overlay';
            overlay.style.display = 'none';
            overlay.style.padding = '24px';
            overlay.style.color = '#ff4d4d';
            overlay.style.backgroundColor = '#0a0a0a';
            overlay.style.fontFamily = 'monospace';
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100vw';
            overlay.style.height = '100vh';
            overlay.style.zIndex = '999999';
            overlay.style.boxSizing = 'border-box';
            overlay.style.overflow = 'auto';

            const title = document.createElement('h2');
            title.style.margin = '0 0 16px 0';
            title.style.fontSize = '20px';
            title.style.borderBottom = '1px solid #ff4d4d';
            title.style.paddingBottom = '8px';
            title.innerText = '⚠️ TinPyUI Engine Panic';

            const log = document.createElement('pre');
            log.id = 'error-log';
            log.style.margin = '0';
            log.style.whiteSpace = 'pre-wrap';
            log.style.wordBreak = 'break-all';
            log.style.fontSize = '14px';
            log.style.lineHeight = '1.5';

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
        const errorDetails = error && error.stack ? error.stack : (msg + '\nLocation: ' + url + ':' + line + ':' + (col || 0));
        window.crash('Runtime Error: ' + errorDetails);
        return false;
    };

    window.addEventListener('unhandledrejection', function(event) {
        const reason = event.reason;
        const msg = reason && (reason.stack || reason.message) ? (reason.stack || reason.message) : String(reason);
        window.crash('Unhandled Rejection: ' + msg);
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
        }
    });

    const go = new Go();
    const _tinWasmSources = ["tinui_engine.wasm", "app.wasm", "/tinui_engine.wasm", "/app.wasm"];
    let _tinWasmPromise = null;
    for (const src of _tinWasmSources) {
        if (!_tinWasmPromise) {
            _tinWasmPromise = fetch(src).then(res => {
                if (!res.ok) throw new Error("HTTP " + res.status + " fetching " + src);
                return res;
            });
        } else {
            _tinWasmPromise = _tinWasmPromise.catch(() => fetch(src).then(res => {
                if (!res.ok) throw new Error("HTTP " + res.status + " fetching " + src);
                return res;
            }));
        }
    }

    async function _loadIR() {
        const irCandidates = ['app.ir.json', 'main.ir.json', 'index.ir.json', '/app.ir.json', '/main.ir.json', '/index.ir.json'];
        for (const path of irCandidates) {
            try {
                const res = await fetch(path);
                if (res.ok) {
                    const text = await res.text();
                    if (text && text.trim().startsWith('{')) {
                        const parsed = JSON.parse(text);
                        if (parsed.nodes && parsed.nodes.length > 0) return text;
                    }
                }
            } catch (e) {}
        }
        return null;
    }

    async function bootEngine() {
        try {
            ensureDiagnosticOverlay();
            const res = await _tinWasmPromise;
            if (!res) throw new Error("Could not load WebAssembly binary from candidate paths.");
            const result = await WebAssembly.instantiateStreaming(res, go.importObject);

            let canvas = document.getElementById('tin-canvas');
            if (!canvas && document.body) {
                canvas = document.createElement('canvas');
                canvas.id = 'tin-canvas';
                canvas.style.position = 'fixed';
                canvas.style.top = '0';
                canvas.style.left = '0';
                canvas.style.width = '100vw';
                canvas.style.height = '100vh';
                canvas.style.display = 'block';
                canvas.style.zIndex = '-1';
                document.body.prepend(canvas);
            }

            if (canvas) {
                const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
                if (gl) {
                    gl.clearColor(0.1, 0.1, 0.1, 1.0);
                    gl.clear(gl.COLOR_BUFFER_BIT);
                }
            }

            go.run(result.instance);
            const irJSON = await _loadIR();
            if (irJSON && typeof BootTinUI === 'function') {
                BootTinUI(irJSON);
            } else if (typeof BootTinUI !== 'function') {
                throw new Error("BootTinUI wasm symbol not found on global scope.");
            }
        } catch (err) {
            window.crash('Engine Boot Failure: ' + (err && (err.stack || err.message) ? (err.stack || err.message) : err));
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootEngine);
    } else {
        bootEngine();
    }
})();
`

const DefaultMainTin = `component Main():
    Router(transition="cinematic"):
        Route(path="/", scene="Dashboard")
`

const DefaultStarterTin = `component Main():
    Section(paddingY = 64, align = "center", justify = "center", minHeight = "screen"):
        Heading(text = "Hello from TinPyUI", color = "neon-cyan", size = "h1")
        Text(text = "Edit main.tin to get started.", color = "muted", marginTop = 24)
`
