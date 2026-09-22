## 🚀 Pull Request Description

### Summary of Changes
<!-- Provide a clear, concise overview of what this PR accomplishes. -->

### Related Issue(s)
<!-- Fixes #123, Closes #456 -->
- Fixes: #

---

## 🏷️ Type of Change

- [ ] 🐛 **Bug fix** (non-breaking change fixing an issue)
- [ ] ✨ **New feature** (non-breaking change adding functionality or component)
- [ ] ⚡ **Performance improvement** (optimizing runtime, compile time, or memory)
- [ ] 💥 **Breaking change** (fix or feature that causes existing code to not work as expected)
- [ ] 📝 **Documentation update** (typos, guides, new tutorials)
- [ ] 🧪 **Tests / CI** (adding missing tests, updating GitHub Actions)
- [ ] 🧹 **Refactor** (code cleanup, formatting, no functional changes)

---

## 🧩 Affected Subsystems

- [ ] Python Runtime (`tinpyui.py`)
- [ ] Go Compiler / Lexer / Parser (`compiler/`, `main.go`)
- [ ] WebAssembly / WebGPU Kernel (`wasm_engine/`)
- [ ] Native C++ Shell (`native/engine_core.cc`)
- [ ] Database Layer (`tin.connect`, PostgreSQL/Mongo/SQLite/RAM)
- [ ] CLI & Scaffolding (`cli/`)
- [ ] VS Code Extension (`tinui-syntax/`)
- [ ] NPM Package (`tinui-npm/`)

---

## 🧪 Testing & Verification

Please describe the tests you ran to verify your changes:

- [ ] Python test suite passed (`python -m unittest discover tests`)
- [ ] Go tests passed (`go test ./...`)
- [ ] Go static analysis clean (`go vet ./...`)
- [ ] WebAssembly compilation verified (`GOOS=js GOARCH=wasm go build ./wasm_engine`)
- [ ] Manual verification in browser / desktop window

---

## 📋 Contributor Checklist

- [ ] My code follows the code style and guidelines described in [CONTRIBUTING.md](CONTRIBUTING.md).
- [ ] I have performed a self-review of my own code.
- [ ] I have commented my code, particularly in hard-to-understand areas.
- [ ] I have updated relevant documentation (or docstrings) where necessary.
- [ ] If adding new public APIs, I have updated `tinpyui.pyi`.
- [ ] My changes generate no new warnings or lint errors.
- [ ] New and existing unit tests pass locally with my changes.
