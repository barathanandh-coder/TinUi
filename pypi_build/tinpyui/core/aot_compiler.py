"""
TinPyUI Ahead-of-Time (AOT) Static Compilation Pipeline.
Compiles indentation-based .tin source templates into optimized binary data matrices (app.ir.bin)
and a complete static web deployment bundle with zero runtime parsing overhead.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from .binary_ir import encode_binary_ir

COMPONENT_TAG_MAP = {
    "Section": "section",
    "Row": "div",
    "Column": "div",
    "Card": "div",
    "Container": "div",
    "Grid": "div",
    "Surface": "div",
    "HeroContainer": "div",
    "Header": "header",
    "Footer": "footer",
    "Main": "main",
    "Navbar": "nav",
    "NavLink": "a",
    "Link": "a",
    "Button": "button",
    "Input": "input",
    "Heading": "h2",
    "Text": "p",
    "GradientText": "span",
    "Badge": "span",
    "Icon": "span",
    "Marquee": "marquee",
    "Modal": "dialog",
    "Tooltip": "div",
    "ShaderLayer": "div",
    "WebGLCanvas": "canvas",
    "ParticleField": "div",
    "AnimatedBackground": "div",
    "Spacer": "div",
    "Divider": "hr",
}

def parse_props(prop_str: str) -> Dict[str, str]:
    """Extracts key=val pairs from a prop string, respecting quotes."""
    props = {}
    pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s,)]+))')
    for match in pattern.finditer(prop_str):
        k = match.group(1)
        val = match.group(2) if match.group(2) is not None else (
              match.group(3) if match.group(3) is not None else match.group(4))
        props[k] = val or ""
    return props

class AOTCompiler:
    """Pure Pythonic AOT Compiler for .tin indentation syntax."""

    def __init__(self):
        self.instructions: List[Dict[str, Any]] = []
        self.next_id = 1

    def compile_tin_source(self, source_code: str) -> Dict[str, Any]:
        """Parses indentation-based .tin template and returns IR dictionary."""
        lines = source_code.splitlines()
        self.instructions = []
        self.next_id = 1

        # Stack holds: (node_id, indent_level)
        stack: List[Tuple[Optional[int], int]] = []
        root_nodes: List[int] = []

        line_regex = re.compile(r'^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*(?:\((.*)\))?\s*(?::\s*)?(?:#.*)?$')

        for raw_line in lines:
            line_no_comment = raw_line.split("#")[0].rstrip()
            if not line_no_comment.strip():
                continue

            match = line_regex.match(line_no_comment)
            if not match:
                continue

            indent_str = match.group(1)
            indent = len(indent_str.replace("\t", "    "))
            tag_name = match.group(2)
            prop_str = match.group(3) or ""

            # Ignore top-level component definition wrapper (e.g. `component Main():`)
            if tag_name == "component":
                continue

            # Pop nodes from stack that have >= current indent level
            while stack and stack[-1][1] >= indent:
                stack.pop()

            parent_id = stack[-1][0] if stack else None

            node_id = self.next_id
            self.next_id += 1

            html_tag = COMPONENT_TAG_MAP.get(tag_name, "div")
            self.instructions.append({
                "op": "CREATE_NODE",
                "id": node_id,
                "tag": html_tag
            })

            props = parse_props(prop_str)

            # Process special props
            for k, v in props.items():
                if k == "text":
                    self.instructions.append({
                        "op": "SET_TEXT",
                        "id": node_id,
                        "value": v
                    })
                elif k == "class_":
                    self.instructions.append({
                        "op": "SET_ATTRIBUTE",
                        "id": node_id,
                        "key": "class",
                        "value": v
                    })
                elif k == "morphism":
                    m_val = v.lower()
                    if not m_val.endswith("-morphism"):
                        m_val = f"{m_val}-morphism"
                    self.instructions.append({
                        "op": "SET_ATTRIBUTE",
                        "id": node_id,
                        "key": "data-morphism",
                        "value": m_val
                    })
                else:
                    self.instructions.append({
                        "op": "SET_ATTRIBUTE",
                        "id": node_id,
                        "key": k,
                        "value": v
                    })

            # Append to parent or record as root
            if parent_id is not None:
                self.instructions.append({
                    "op": "APPEND_CHILD",
                    "parent": parent_id,
                    "child": node_id
                })
            else:
                self.instructions.append({
                    "op": "APPEND_CHILD",
                    "parent": None,
                    "child": node_id
                })
                root_nodes.append(node_id)

            stack.append((node_id, indent))

        return {"nodes": self.instructions}

    def compile_to_binary_matrix(self, source_code: str) -> bytes:
        """Compiles source code directly into compact TINB binary data matrix."""
        ir = self.compile_tin_source(source_code)
        return encode_binary_ir(ir)


def build_aot_static_bundle(
    entry_file: str,
    out_dir: str = "dist",
    app_name: str = "TinPyUI Application"
) -> Dict[str, Any]:
    """
    Executes full AOT static compilation for an entry file into an optimized
    production-ready deployment directory with zero client-side parser overhead.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    entry_path = Path(entry_file)

    if not entry_path.exists():
        raise FileNotFoundError(f"Entry file '{entry_file}' does not exist.")

    source_code = entry_path.read_text(encoding="utf-8")
    compiler = AOTCompiler()

    # 1. Compile IR (both binary matrix and json)
    ir_dict = compiler.compile_tin_source(source_code)
    bin_matrix = encode_binary_ir(ir_dict)

    bin_dest = out_path / "app.ir.bin"
    bin_dest.write_bytes(bin_matrix)

    import json
    json_dest = out_path / "app.ir.json"
    json_dest.write_text(json.dumps(ir_dict, indent=2), encoding="utf-8")

    # 2. Bundle static runtime assets
    repo_root = Path(__file__).resolve().parent.parent.parent
    pkg_dir = Path(__file__).resolve().parent.parent

    # Copy tin-runtime.js
    runtime_sources = [
        pkg_dir / "tin-runtime.js",
        repo_root / "tin-runtime.js",
        repo_root / "public" / "tin-runtime.js"
    ]
    for src in runtime_sources:
        if src.exists():
            shutil.copyfile(src, out_path / "tin-runtime.js")
            break

    # Copy tin-shader-worker.js
    worker_sources = [
        pkg_dir / "tin-shader-worker.js",
        repo_root / "tin-shader-worker.js"
    ]
    for src in worker_sources:
        if src.exists():
            shutil.copyfile(src, out_path / "tin-shader-worker.js")
            break

    # Copy wasm_exec.js and Wasm engine if available
    for wasm_file in ["wasm_exec.js", "tinui_engine.wasm"]:
        for src in [pkg_dir / wasm_file, repo_root / wasm_file, repo_root / "public" / wasm_file]:
            if src.exists():
                shutil.copyfile(src, out_path / wasm_file)
                if wasm_file == "tinui_engine.wasm":
                    shutil.copyfile(src, out_path / "app.wasm")
                break

    # Copy shaders directory
    shaders_dest = out_path / "shaders"
    shaders_dest.mkdir(exist_ok=True)
    for s_dir in [pkg_dir / "shaders", repo_root / "shaders"]:
        if s_dir.exists():
            for f in s_dir.glob("*.frag"):
                shutil.copyfile(f, shaders_dest / f.name)
            for f in s_dir.glob("*.vert"):
                shutil.copyfile(f, shaders_dest / f.name)
            break

    # 3. Generate production HTML harness with JSON-LD structured data
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{app_name} — Powered by TinPyUI</title>
    <meta name="description" content="{app_name} — High-Performance Zero-DOM WebAssembly & WebGL Application powered by TinPyUI.">
    <meta name="keywords" content="tinpyui, tinui, python gui, webassembly, zero-dom, webgl, python ui framework">
    <link rel="canonical" href="https://github.com/barathanandh-coder/TinUi">

    <!-- OpenGraph Metadata -->
    <meta property="og:title" content="{app_name} — Powered by TinPyUI">
    <meta property="og:description" content="High-Performance Zero-DOM WebAssembly & WebGL Application powered by TinPyUI.">
    <meta property="og:url" content="https://github.com/barathanandh-coder/TinUi">
    <meta property="og:type" content="website">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{app_name} — Powered by TinPyUI">

    <!-- Schema.org SoftwareApplication JSON-LD Structured Data for Search Engines -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "{app_name}",
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Cross-platform",
        "author": {{
            "@type": "Person",
            "name": "Barath Anandh",
            "url": "https://github.com/barathanandh-coder/TinUi"
        }},
        "sameAs": [
            "https://github.com/barathanandh-coder/TinUi",
            "https://pypi.org/project/tinpyui-ff/",
            "https://www.npmjs.com/package/tinui"
        ],
        "description": "The official compiler and CLI for the TinUI framework, featuring a Pythonic, indentation-based syntax powered by WebAssembly."
    }}
    </script>

    <!-- Google Fonts & Material Symbols -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Sora:wght@600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />

    <!-- Tailwind CSS Engine -->
    <script src="https://cdn.tailwindcss.com"></script>

    <style>
        *, *::before, *::after {{ box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}
        body {{
            margin: 0;
            padding: 0;
            background-color: #03050c;
            color: #f8fafc;
            font-family: 'Plus Jakarta Sans', sans-serif;
            overflow-x: hidden;
        }}
        .reveal-on-scroll {{
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .reveal-on-scroll.is-visible {{
            opacity: 1;
            transform: translateY(0);
        }}
        .glass-morphism {{
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .neu-morphism {{
            background: #0d121d;
            box-shadow: 8px 8px 20px #04060a, -8px -8px 20px #162034;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .clay-morphism {{
            background: rgba(30, 41, 59, 0.8);
            border-radius: 24px;
            box-shadow: inset 4px 4px 8px rgba(255,255,255,0.1), inset -4px -4px 8px rgba(0,0,0,0.4), 0 12px 24px rgba(0,0,0,0.5);
        }}
        .holo-morphism {{
            background: linear-gradient(135deg, rgba(6,182,212,0.12), rgba(168,85,247,0.12));
            border: 1px solid rgba(168,85,247,0.4);
            box-shadow: 0 0 25px rgba(168,85,247,0.25);
        }}
    </style>
</head>
<body>
    <div id="tinui-root" data-ir="app.ir.bin">
        <!-- High-speed AOT Binary Opcode Stream mounts here -->
    </div>
    <script src="wasm_exec.js"></script>
    <script src="tin-runtime.js"></script>
</body>
</html>
"""
    (out_path / "index.html").write_text(html_content, encoding="utf-8")

    return {
        "status": "success",
        "output_dir": str(out_path),
        "binary_matrix_size": len(bin_matrix),
        "json_size": len(json_dest.read_bytes()),
        "node_count": len(ir_dict.get("nodes", [])),
    }
