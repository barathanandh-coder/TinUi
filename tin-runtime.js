// tin-runtime.js — TinPyUI v1.6.0 Runtime
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
