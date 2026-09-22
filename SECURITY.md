# Security Policy

The TinPyUI core team takes the security of the framework and its applications seriously. We appreciate the responsible disclosure of vulnerabilities.

---

## 🛡️ Supported Versions

We provide security patches and fixes for the following versions of TinPyUI:

| Version | Supported | Notes |
| :--- | :--- | :--- |
| `v1.6.x` | :white_check_mark: | Current Stable Release Line |
| `v1.5.x` | :warning: | Critical Security Fixes Only (LTS) |
| `< v1.5` | :x: | End of Life (Upgrade recommended) |

---

## 🔒 Reporting a Vulnerability

If you discover a potential security vulnerability in TinPyUI (including the Python runtime, Go compiler, WebAssembly kernel, or native shells), please follow these steps:

### 1. Do NOT open a public GitHub issue
Please do not disclose security vulnerabilities publicly in GitHub issues, pull requests, or community chat channels before a fix is released.

### 2. Submit a Private Security Advisory
We encourage you to submit the vulnerability using [GitHub Private Vulnerability Reporting](https://github.com/barathanandh-coder/TinUi/security/advisories/new) directly on the repository.

Alternatively, send an email to:
- **Email**: [security@tinpyui.dev](mailto:security@tinpyui.dev) or [barathanandh@gmail.com](mailto:barathanandh@gmail.com)
- **Subject**: `[SECURITY] TinPyUI Vulnerability Report: <Brief Description>`

### 3. Information to Include
To help us triage and resolve the issue quickly, please provide:
- Detailed description of the vulnerability.
- Steps to reproduce or a minimal Proof of Concept (PoC).
- Affected subsystem (e.g., Python runtime `tinpyui.py`, Go WASM kernel `wasm_engine`, C++ native shell `native/engine_core.cc`, SQL/NoSQL reactive database layer, or session security shield).
- The operating system, runtime environment, and TinPyUI version.
- Potential impact and severity assessment.

---

## ⏱️ Response Timeline

- **Initial Acknowledgment**: Within 24-48 hours.
- **Triage & Severity Assessment**: Within 72 hours.
- **Patch Development & Testing**: Typically 7-14 business days depending on complexity.
- **Public Disclosure**: Coordinated release and CVE assignment after patch deployment.

---

## 🏆 Security Bug Bounty & Hall of Fame

We believe in recognizing ethical security researchers:
- Valid security vulnerabilities will be credited in our Release Notes and Security Hall of Fame.
- Researchers may request confidential attribution or public acknowledgement on our official project page.
