# TinPyUI v1.8.0 Python Compiler Migration Audit

## Executive Summary
This document provides a comprehensive read-only audit of the Python AOT compiler dependencies (`aot_compiler.py` and `binary_ir.py`). Its purpose is to map out execution paths, APIs, and legacy workflows before selecting a deprecation or migration strategy.

## Dependency Trace & Execution Map

### Who Imports and Executes Them?
- **`src/tinpyui/cli.py`**: Imports `AOTCompiler` and `build_aot_static_bundle`.
- **`src/tinpyui/core/__init__.py`**: Explicitly imports and exposes `encode_binary_ir` and `decode_binary_ir` via `__all__`.
- **`tests/test_aot_hmr_lsp.py`**: Executes the AOT compiler and decodes the binary IR matrix to verify node attributes.
- **`tests/test_optimizations.py`**: Deeply tests `binary_ir.py` for roundtrip serialization and payload efficiency.

### CLI Command Invocation
- `python -m tinpyui.cli build`: **Yes.** Invokes `build_aot_static_bundle` to generate `index.html`, `app.ir.bin`, and `app.ir.json`.
- `python -m tinpyui.cli check`: **Yes.** Invokes `AOTCompiler.compile_tin_source()` to validate syntax.
- `python main.py`: **No.** Immediate-mode UI execution relies on the Python `tinpyui.App` runtime, bypassing static AOT compilation entirely.

### Runtime Consumption
- **Does any runtime consume `app.ir.bin`?** **Yes.** The primary Zero-DOM WebAssembly frontend loader (`tin-runtime.js`) maintains an array of binary endpoints (e.g., `app.ir.bin`) and explicitly fetches and parses this payload if present before falling back to `app.ir.json`.

### Public API Exposure
- Are they exposed through the Python API? **Yes.** `encode_binary_ir` and `decode_binary_ir` are public API members of `tinpyui.core`.
- Are there documented programmatic APIs? **Yes.** `build_aot_static_bundle` serves as a programmatic API for custom build scripts.

## Workflow Impact Analysis

If the Python regex compiler (`aot_compiler.py`) and binary serializer (`binary_ir.py`) were immediately deleted, the following v1.7.1 workflows would catastrophically break:
1. **Python Build Pipelines:** Users relying on `tinpyui build` to generate static `.bin` sites would experience hard crashes.
2. **Syntax Validation:** `tinpyui check` via Python would fail.
3. **Optimized Loaders:** `tin-runtime.js` might encounter 404s fetching `app.ir.bin` (though it falls back to JSON, performance-critical apps relying on binary sizes would be degraded).
4. **Test Suites:** `test_aot_hmr_lsp.py` and `test_optimizations.py` would instantly fail.
5. **Custom Scripts:** Any user-space Python script calling `tinpyui.core.encode_binary_ir` for custom binary payloads would crash.

## Dependency Classification

- `src/tinpyui/core/aot_compiler.py` (AOTCompiler): **LEGACY / PUBLIC API**
- `src/tinpyui/core/aot_compiler.py` (build_aot_static_bundle): **LEGACY / PUBLIC API**
- `src/tinpyui/core/binary_ir.py` (encode/decode): **RUNTIME-CRITICAL / PUBLIC API**
- `src/tinpyui/cli.py` (check/build commands): **PUBLIC API**
- `tests/test_aot_hmr_lsp.py`: **TEST-ONLY**
- `tests/test_optimizations.py`: **TEST-ONLY**

---

## Potential Migration Strategies

### A. Go Subprocess/IPC Bridge
- **Concept:** Deprecate the Python AST parsing logic completely. `aot_compiler.py` remains in the Python API but becomes a thin wrapper that executes the Go `tinui.exe compile` via `subprocess`.
- **Pros:** Guarantees 100% AST schema conformance; removes regex constraints; minimal Python maintenance.
- **Cons:** Requires the Go binary to be distributed inside the PyPI package or assumes the user has installed `tinui` globally. Cross-platform execution (Windows `.exe` vs Linux) complicates packaging.

### B. Go Compiler Exposed as a Library/API (C-FFI / WebAssembly)
- **Concept:** Compile the Go parser to a C shared library (`.so`/`.dll`) or WebAssembly module and embed it directly into the Python package using `ctypes` or `wasmtime`.
- **Pros:** Perfect conformance; no subprocess overhead; self-contained PyPI package.
- **Cons:** Extremely high build complexity; requires cross-compiling Go CGO for Win/Mac/Linux and maintaining complex build wheels.

### C. Maintain Python Compiler Temporarily with Explicit Deprecation
- **Concept:** Leave `aot_compiler.py` as is, but inject loud `DeprecationWarning`s. Direct users to switch to the Go `tinui build` binary. Phase it out in v1.9.0.
- **Pros:** Zero breakage; zero engineering effort; smooth transition for users.
- **Cons:** We continue shipping a fundamentally broken, non-conforming regex compiler that fails on complex `.tin` files. Confusion remains regarding the "correct" build pipeline.
