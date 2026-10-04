# TinPyUI v1.8.0 Compiler Conformance Report

## Executive Summary
This report analyzes the parity between the Go AOT compiler (`src/compiler/`) and the Python AOT compiler bridge (`src/tinpyui/core/aot_compiler.py`).

The Go compiler is a fully-featured language parser (Lexer -> AST -> Semantic Analysis -> IR Generator) supporting reactive states, control flow (if/for), and event mutations. The Python compiler is a rudimentary regex-based scaffold generator capable only of static UI generation with hardcoded tag mappings.

## IR Schema Extraction

### Metadata Schema (Identical between Go and Python)
```json
{
  "generated": true,
  "do_not_edit": true,
  "source": "<filename>",
  "compiler_version": "1.8.0",
  "runtime_abi": 4,
  "timestamp": "<iso8601>"
}
```

### Supported IR Nodes (OpCodes)

| OpCode | Go Support | Python Support | Equivalent? | Notes |
| :--- | :---: | :---: | :---: | :--- |
| `CREATE_NODE` | ✅ | ✅ | IDENTICAL | Basic DOM creation |
| `APPEND_CHILD` | ✅ | ✅ | IDENTICAL | Tree building |
| `SET_TEXT` | ✅ | ✅ | IDENTICAL | Static text nodes |
| `SET_ATTRIBUTE` | ✅ | ✅ | IDENTICAL | Static attributes |
| `DECLARE_STATE` | ✅ | ❌ | GO-ONLY | Signal generation |
| `BIND_TEXT` | ✅ | ❌ | GO-ONLY | Reactive f-strings (`f"{state}"`) |
| `BIND_INPUT` | ✅ | ❌ | GO-ONLY | Two-way binding (`bind=state`) |
| `ADD_EVENT` | ✅ | ❌ | GO-ONLY | Click/hover triggers |
| `ASSIGN`, `INCREMENT`, `DECREMENT` | ✅ | ❌ | GO-ONLY | State mutations |
| `CREATE_CONDITIONAL` | ✅ | ❌ | GO-ONLY | `if/elif/else` branching |
| `RENDER_LIST` | ✅ | ❌ | GO-ONLY | `for item in state:` iteration |
| `BIND_LOADING` | ✅ | ❌ | GO-ONLY | Suspense boundaries |

## Feature Implementation Matrix

| Feature | Go Compiler | Python Compiler | IR Representation | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Parsing Engine** | Full Lexer/Parser AST | Single-pass regex | DIFFERENT | Go uses robust tokenization |
| **Type System** | Validated AST | String properties only | DIFFERENT | Python lacks type safety |
| **Event System** | Parses `def`, `on_click` | Ignored | GO-ONLY | Python bridge drops events |
| **Reactivity** | Parses `state`, binds | Static only | GO-ONLY | Python bridge is static |
| **Logic (if/for)** | AST Branching | Fails/Ignores syntax | GO-ONLY | Python regex misses blocks |
| **Tag Resolution** | Dynamic schema | `COMPONENT_TAG_MAP` | DIFFERENT | Python hardcodes HTML tags |
| **Component System**| Parses `component Main():` | Skips `component` lines | DIFFERENT | Python drops components |

## Detailed Divergence Analysis

### 1. Tag Mapping & Component Resolution
The Python compiler uses a hardcoded dictionary (`COMPONENT_TAG_MAP`) to map DSL tags to HTML elements (e.g., `"Row": "div"`). It dynamically injects special attributes (`data-tabs="true"` for `Tabs`). The Go compiler dynamically handles UI tags via AST, mapping them properly without hardcoded dictionaries.

### 2. Control Flow and State
The Python compiler completely fails to understand Pythonic control flow. A `.tin` file containing `if user.is_logged_in:` or `state counter = 0` will either be ignored or incorrectly parsed as a static component by the Python regex engine. The Go compiler correctly builds AST ConditionalNodes and StateDecls.

### 3. Binary Generation
The Python compiler generates both JSON and a custom `app.ir.bin` via `binary_ir.py`. The Go CLI outputs the standard JSON IR format that the frontend engine consumes.

## Conclusion

**Current Compiler Relationship:**
The Go compiler is the canonical, fully-featured authoritative compiler for the `.tin` language. The Python compiler is effectively a static scaffold generator incapable of understanding dynamic applications or state.

**Compatibility Risks:**
High. Any `.tin` file containing logic, state, or event bindings will silently fail to compile properly if routed through the Python AOT bridge. The Python implementation is severely outdated and rudimentary compared to the Go engine's capabilities.

**Recommended Next Audit Step:**
Formally document how to safely route Python compilation requests to the Go compiler executable (via IPC or `subprocess`), or define a mechanism to completely deprecate the `aot_compiler.py` parsing engine.
