# TinPyUI Project Governance

This document outlines the governance model, contributor roles, decision-making processes, and RFC (Request for Comments) procedures for the **TinPyUI** open-source project.

---

## 🏛️ Governance Philosophy

TinPyUI is committed to open, transparent, and welcoming open-source development. We prioritize:
- **Architectural Soundness**: Sub-millisecond performance, zero runtime bloat, and rock-solid memory safety.
- **Developer Delight**: Intuitive declarative Python and `.tin` DSL syntax with seamless multi-engine databases and 120 FPS hardware acceleration.
- **Community Collaboration**: Empowering contributors of all experience levels to shape the roadmap and improve the engine.

---

## 👥 Contributor Roles & Pathways

```
 +-------------------------------------------------------+
 |                 Benevolent Dictator / Lead            |
 +-------------------------------------------------------+
                            │
                            ▼
 +-------------------------------------------------------+
 |                  Core Maintainers                     |
 +-------------------------------------------------------+
                            │
                            ▼
 +-------------------------------------------------------+
 |               Subsystem Maintainers                   |
 |  (Python Runtime, Go WASM Kernel, Native Shells, etc.)|
 +-------------------------------------------------------+
                            │
                            ▼
 +-------------------------------------------------------+
 |                Active Contributors                    |
 +-------------------------------------------------------+
                            │
                            ▼
 +-------------------------------------------------------+
 |                 Community Members                     |
 +-------------------------------------------------------+
```

### 1. Community Member
- Anyone who uses TinPyUI, files bug reports, proposes feature suggestions, or joins discussions.

### 2. Contributor
- Any community member who submits merged Pull Requests (code, documentation, benchmarks, bug fixes, or examples).

### 3. Subsystem Maintainer
- Experienced contributors responsible for specific domains:
  - **Python Runtime (`tinpyui.py`)**
  - **Compiler & Generator (`compiler/`, `main.go`)**
  - **WASM Engine & Shaders (`wasm_engine/`)**
  - **Native C++ & OS Bridges (`native/`, `cli/`)**
  - **Documentation & Ecosystem (`tinui-syntax/`, `tinui-npm/`)**

### 4. Core Maintainer
- Active leads who hold triage, commit, and release permissions across the entire project. Core maintainers oversee releases, CI pipelines, and security advisories.

---

## 🗳️ Decision-Making Process

### Daily Development & Small Enhancements
- Bug fixes, documentation updates, performance micro-optimizations, and non-breaking feature additions follow standard Pull Request review.
- Requires approval from at least **one Maintainer**.

### Major Architectural Changes (RFC Process)
Major changes require an **RFC (Request for Comments)**:
- Adding new compiler keywords or DSL primitives.
- Modifying the WASM IR specification or runtime wire protocol.
- Introducing new platform targets or breaking API changes.

#### RFC Workflow:
1. Open an issue using the [RFC Proposal Template](.github/ISSUE_TEMPLATE/rfc_proposal.yml) or submit a PR adding an RFC markdown doc in `rfcs/`.
2. Engage in community discussion for a minimum of 7 calendar days.
3. Core Maintainers achieve consensus. If consensus is reached, the RFC is marked **Accepted** and scheduled on the [ROADMAP.md](ROADMAP.md).

---

## 🚀 Release Process & Versioning

TinPyUI adheres strictly to [Semantic Versioning 2.0.0 (SemVer)](https://semver.org/):
- **MAJOR** version bumps (`v2.0.0`): Incompatible API or DSL breaking changes.
- **MINOR** version bumps (`v1.7.0`): Backward-compatible new features, platform targets, or new components.
- **PATCH** version bumps (`v1.6.2`): Backward-compatible bug fixes and security patches.
