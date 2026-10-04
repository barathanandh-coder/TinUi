# Compiler Architecture (TinPyUI v1.8)

TinPyUI ships with **two distinct compilers**, each tailored for specific workflows. They produce highly compatible Intermediate Representation (IR), but they differ in purpose and authority.

### 1. The Go Compiler (`tinui` CLI) - *AUTHORITATIVE*
The Go compiler is written entirely in Go (`src/compiler/`) and handles `.tin` source files.
- **Authority:** It is the **primary, authoritative compiler** for TinPyUI syntax. It implements the zero-DOM architecture rules strictly.
- **Speed:** Compiles projects in < 2ms.
- **Output:** Transforms `.tin` DSL into `app.ir.json`.
- **Usage:** Run `tinui compile main.tin` or `tinui check main.tin`.

### 2. The Python AOT Compiler - *BRIDGE*
The Python compiler is written in Python (`src/tinpyui/core/aot_compiler.py`) and handles `.py` files using the `tinpyui` module.
- **Authority:** It acts as a bridge for developers who prefer pure Python instead of `.tin` files.
- **Output:** Transforms Python `tinpyui` class instantiations into an identical `app.ir.json`.
- **Usage:** Run `python -m src.tinpyui.cli build main.py`.

### Compatibility & Guardrails
Both compilers inject an `IRMetadata` header (`_tinpyui`) into the generated `app.ir.json`. This metadata explicitly marks the output as generated and tags it with a `runtime_abi` version (currently v4). If the generated JSON is loaded by a mismatched runtime engine, the engine will halt and request a rebuild.
