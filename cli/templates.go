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

const DefaultTinRuntimeJS = `// tin-runtime.js — TinPyUI v1.6.0 Runtime
const go = new Go();
const _tinWasmSources = ["tinui_engine.wasm", "app.wasm", "/tinui_engine.wasm", "/app.wasm"];
let _tinWasmPromise = null;
for (const src of _tinWasmSources) {
    if (!_tinWasmPromise) {
        _tinWasmPromise = fetch(src).then(res => {
            if (!res.ok) throw new Error("Status " + res.status);
            return res;
        });
    } else {
        _tinWasmPromise = _tinWasmPromise.catch(() => fetch(src).then(res => {
            if (!res.ok) throw new Error("Status " + res.status);
            return res;
        }));
    }
}
_tinWasmPromise.then(res => WebAssembly.instantiateStreaming(res, go.importObject))
.then((result) => {
    go.run(result.instance);
    fetch('app.ir.json').then(r => r.text()).then(json => {
        if (typeof BootTinUI === 'function') {
            BootTinUI(json);
        }
    });
}).catch(err => {
    console.error('[TinPyUI Runtime] Failed to initialize WebAssembly engine:', err);
});
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
