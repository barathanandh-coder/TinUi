# Contributing to TinPyUI

Thank you for your interest in contributing to **TinPyUI**! 🎉

TinPyUI is an open-source, ultra-high-performance, hardware-accelerated UI application framework that unites a **Pure Python Declarative Runtime** with a **Go WebAssembly/WebGPU Kernel** and **Native C++ Desktop Shells**.

Whether you're fixing a bug, adding new declarative components, writing GLSL shaders, improving documentation, or adding database connectors, your contributions are welcome!

---

## 📑 Table of Contents

1. [Code of Conduct](#-code-of-conduct)
2. [Project Architecture Overview](#-project-architecture-overview)
3. [Development Environment Setup](#-development-environment-setup)
4. [Developer Tooling & Commands](#-developer-tooling--commands)
5. [Git Workflow & Branching Strategy](#-git-workflow--branching-strategy)
6. [Commit Message Guidelines](#-commit-message-guidelines)
7. [Code Style & Best Practices](#-code-style--best-practices)
8. [Testing Guide](#-testing-guide)
9. [Submitting a Pull Request](#-submitting-a-pull-request)
10. [Community & Help](#-community--help)

---

## 📜 Code of Conduct

All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating.

---

## 🏛️ Project Architecture Overview

TinPyUI is organized into modular subsystems across multiple languages:

```
TinUi/
├── tinpyui.py                  # Core Pure Python Runtime (Zero-PIP dependency, Signals, Spring Physics, DB Suite)
├── tinpyui.pyi                 # Complete Python Type Stub definitions for IDE autocomplete
├── main.go                     # TinUI CLI Engine entrypoint (compile, dev server, scaffold, build)
├── compiler/                   # Go Lexer, Parser, AST, GLSL Validator, and HTML Hydrator
│   ├── ast.go                  # Abstract Syntax Tree nodes
│   ├── generator.go            # IR code generator
│   ├── html_hydrator.go        # Semantic HTML5 hydration engine
│   ├── lexer.go                # Indentation-aware tokenizer
│   └── parser.go               # Recursive-descent parser for .tin syntax
├── wasm_engine/                # Go WebAssembly Kernel (compiled to tinui_engine.wasm)
│   ├── hal_webgpu.go           # Hardware Abstraction Layer (WebGPU / WebGL2 / WebGL1 fallback)
│   ├── platform_bridge.go      # Native platform channel bridge (Haptics, Clipboard, Sysinfo)
│   ├── v16_core.go             # Symplectic Euler spring solver & vertex buffers
│   └── virtual_stack.go        # Spatial windowing engine for 100k+ row virtualization
├── native/                     # Native C++ Desktop Shells
│   └── engine_core.cc          # Lightweight ~2MB shell (DirectX 12 / Apple Metal / WebKitGTK)
├── database/                   # Schema builders & database helpers
├── tests/                      # Python unit & adversarial security test suite
├── tinui-npm/                  # Node.js CLI & runtime npm distribution package
├── tinui-syntax/               # VS Code syntax highlighting extension for .tin files
└── .github/                    # CI/CD Workflows, Issue & PR templates, Codeowners
```

---

## 💻 Development Environment Setup

### Prerequisites

1. **Python**: 3.10 or higher (`python --version`)
2. **Go**: 1.21 or higher (`go version`)
3. **Git**: Latest version
4. *(Optional for C++ Native Shell)*: GCC/Clang or MSVC C++20 compiler
5. *(Optional for VS Code Extension)*: Node.js 18+ & npm

### Clone the Repository

```bash
git clone https://github.com/barathanandh-coder/TinUi.git
cd TinUi
```

### Verify Local Toolchains

Check that Python and Go run without issues:

```bash
# Verify Python
python -c "import tinpyui; print(f'TinPyUI v{tinpyui.__version__} loaded successfully!')"

# Verify Go compiler
go vet ./...
go test ./...
```

---

## 🛠️ Developer Tooling & Commands

We provide a `Makefile` (Linux/macOS/Git Bash) and `dev.bat` (Windows PowerShell/Command Prompt) for streamlined developer tasks:

### Using `dev.bat` (Windows):
```cmd
dev.bat help          :: Show all available commands
dev.bat test          :: Run all Python and Go tests
dev.bat test-py       :: Run only Python unit tests
dev.bat test-go       :: Run only Go tests
dev.bat vet           :: Run Go static analysis
dev.bat wasm          :: Compile Go WASM runtime kernel
dev.bat build         :: Build tinui CLI binary
dev.bat clean         :: Remove build artifacts and temporary databases
```

### Using `make` (Linux / macOS / Git Bash):
```bash
make help             # Display available targets
make test             # Run all Python and Go test suites
make test-py          # Run Python unit tests with verbose output
make test-go          # Run Go unit and generator tests
make wasm             # Compile wasm_engine into public/tinui_engine.wasm
make build            # Build the local tinui CLI executable
make lint             # Run go vet and static checks
make clean            # Remove caches and temporary build files
```

---

## 🌿 Git Workflow & Branching Strategy

1. **Fork** the repository to your own GitHub account.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/TinUi.git
   cd TinUi
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/barathanandh-coder/TinUi.git
   ```
4. **Create a topic branch** from `main`:
   ```bash
   git checkout -b feat/my-new-feature
   # or
   git checkout -b fix/issue-description
   ```

### Branch Naming Conventions
- `feat/<feature-name>`: New UI components, database adapters, compiler features
- `fix/<bug-summary>`: Bug fixes and security patches
- `docs/<doc-topic>`: Documentation updates, guides, or tutorials
- `perf/<optimization>`: Performance or memory improvements
- `refactor/<subsystem>`: Internal restructuring without external API change

---

## 📝 Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) standard. Structured commit messages enable automated changelogs and clear git history:

```
<type>(<scope>): <short summary>

[optional body explaining context, rationale, and breaking changes]

[optional issue reference: Fixes #123]
```

### Allowed Types:
- **`feat`**: A new feature (e.g. `feat(components): add tin.ColorPicker component`)
- **`fix`**: A bug fix (e.g. `fix(compiler): resolve line number offset in lexer`)
- **`docs`**: Documentation only changes (e.g. `docs(api): clarify ReactiveLiveQuery lifecycle`)
- **`perf`**: A code change that improves performance (e.g. `perf(wasm): optimize vertex buffer pool`)
- **`refactor`**: Code change that neither fixes a bug nor adds a feature
- **`test`**: Adding missing tests or correcting existing tests
- **`chore`**: Maintenance, CI workflow changes, dependency updates

---

## 🎨 Code Style & Best Practices

### Python (`tinpyui.py`, `tests/`)
- **Zero-PIP Standard Library Philosophy**: Core runtime features must remain 100% dependency-free using Python's standard library (`ctypes`, `sqlite3`, `urllib`, `socket`, `hmac`, `json`, `dataclasses`). Optional database engines (`psycopg2`, `pymongo`) should use dynamic imports with graceful fallback.
- Follow **PEP 8** style guidelines.
- Add complete type hints and update `tinpyui.pyi` when adding new public functions or classes.
- Write descriptive docstrings for public classes and methods.

### Go (`compiler/`, `wasm_engine/`, `main.go`)
- Format code strictly with `gofmt -s -w .`.
- Ensure `go vet ./...` passes with 0 warnings.
- Avoid trailing newlines inside `fmt.Println` arguments.
- Handle all returned errors explicitly; avoid unhandled errors or panics.

### C++ (`native/engine_core.cc`)
- Modern **C++20** standard.
- Use RAII principles for memory management.
- Preserve platform `#ifdef` isolation between Win32, Cocoa/macOS, and Linux WebKitGTK.

---

## 🧪 Testing Guide

Always run tests locally before opening a pull request:

### 1. Python Unit Tests & Adversarial Security Suite
```bash
python -m unittest discover tests -v
```

This runs all 35+ test cases, covering:
- Reactive State Signals & Symplectic Spring Physics
- Universal Database Connections (`tin.connect`, PostgreSQL, MongoDB, SQLite, RAM)
- Active Record Models (`@tin.model`) & Live Queries
- Spatial Virtualization (`VirtualStack`, `VirtualList`)
- Enterprise Security Core (HMAC session shields, RAMMaskedState, Honeypot generators)

### 2. Go Compiler & AST Tests
```bash
go test -v ./compiler/...
```

### 3. WebAssembly Compilation Test
```bash
# On Linux / macOS / Git Bash:
GOOS=js GOARCH=wasm go build -o public/tinui_engine.wasm ./wasm_engine

# On Windows PowerShell:
$env:GOOS="js"; $env:GOARCH="wasm"; go build -o public/tinui_engine.wasm ./wasm_engine
```

---

## 🚀 Submitting a Pull Request

1. **Rebase** your branch onto latest `upstream/main`:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```
2. **Run full tests and verification**:
   ```bash
   # All tests must pass
   python -m unittest discover tests
   go vet ./...
   go test ./...
   ```
3. **Push to your fork**:
   ```bash
   git push origin feat/my-new-feature
   ```
4. **Open a Pull Request** on GitHub against the `main` branch.
5. Fill out the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md) completely:
   - Link any related issues (`Closes #42`).
   - Describe what changed and the motivation.
   - Attach screenshots/recordings if modifying UI rendering.
6. A maintainer will review your PR, trigger the CI matrix, and provide feedback!

---

## 💬 Community & Help

- 💡 **Discussions & Ideas**: [GitHub Discussions](https://github.com/barathanandh-coder/TinUi/discussions)
- 🐛 **Bug Reports & Issues**: [GitHub Issues](https://github.com/barathanandh-coder/TinUi/issues)
- 🗺️ **Roadmap & Vision**: [ROADMAP.md](ROADMAP.md)
- 🛡️ **Security Inquiries**: [SECURITY.md](SECURITY.md)

Thank you for helping make TinPyUI faster, more versatile, and accessible to developers worldwide! 🚀
