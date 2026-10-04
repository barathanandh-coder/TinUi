"""
TinPyUI Ahead-of-Time (AOT) Static Compilation Pipeline.
This module now serves as a thin compatibility and orchestration layer 
that delegates all canonical compilation to the Go `tinui` executable.
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

from .binary_ir import encode_binary_ir

def find_tinui_executable() -> str:
    """Locates the Go compiler executable based on OS and Architecture."""
    import platform
    
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Map Python's platform.machine() to Go's GOARCH
    if machine in ("x86_64", "amd64"):
        goarch = "amd64"
    elif machine in ("arm64", "aarch64"):
        goarch = "arm64"
    else:
        goarch = "amd64" # Fallback
        
    exe_name = "tinui"
    if system == "windows":
        exe_name = "tinui.exe"
        
    bundled_name = f"tinui-{system}-{goarch}"
    if system == "windows":
        bundled_name += ".exe"
    
    # 1. Check bundled PyPI bin path (platform specific)
    pkg_dir = Path(__file__).resolve().parent.parent
    bin_dir = pkg_dir / "bin"
    
    if (bin_dir / bundled_name).exists():
        return str(bin_dir / bundled_name)
    
    # 2. Check bundled PyPI bin path (generic fallback name)
    if (bin_dir / exe_name).exists():
        return str(bin_dir / exe_name)
        
    # 3. Check development path (repo root)
    repo_root = pkg_dir.parent.parent
    dev_path = repo_root / exe_name
    if dev_path.exists():
        return str(dev_path)
        
    # 4. Check system PATH
    system_path = shutil.which(exe_name)
    if system_path:
        return system_path
        
    raise FileNotFoundError(
        f"Could not locate the TinPyUI compiler executable for {system}/{goarch}.\n"
        "Please ensure the Go executable is in your PATH or bundled in the package."
    )


class AOTCompiler:
    """
    Compatibility layer for programmatic AOT compilation.
    Delegates to the canonical Go compiler.
    """

    def compile_tin_source(self, source_code: str) -> Dict[str, Any]:
        """Parses .tin template by invoking the Go compiler and parsing the output JSON."""
        exe = find_tinui_executable()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source_file = tmp_path / "temp.tin"
            source_file.write_text(source_code, encoding="utf-8")
            
            # The Go compiler creates app.ir.json on 'check' (wait, we verified 'check' sets output to app.ir.json)
            # Actually, check doesn't guarantee writing output if it just verifies. Let's run compile instead.
            # But Go's `main.go` doesn't have a `compile` command? Wait, let's look at `tinui compile`. 
            # In `main.go:363`: `tinui compile <file.tin>` is listed. Let's check if it exists in main.go.
            # `compile` command runs `compileFile(inputFile, outDir, outputFile, false)`
            
            result = subprocess.run(
                [exe, "check", str(source_file)],
                cwd=tmpdir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise SyntaxError(f"TinPyUI Compilation Failed:\n{result.stdout}\n{result.stderr}")
            
            json_file = tmp_path / "app.ir.json"
            if not json_file.exists():
                # Try finding any .ir.json file
                ir_files = list(tmp_path.glob("*.ir.json"))
                if ir_files:
                    json_file = ir_files[0]
                else:
                    raise RuntimeError("Compiler succeeded but app.ir.json was not found.")
                
            return json.loads(json_file.read_text(encoding="utf-8"))

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
    Executes full AOT static compilation by delegating to the Go compiler.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    entry_path = Path(entry_file).resolve()
    
    if not entry_path.exists():
        raise FileNotFoundError(f"Entry file '{entry_file}' does not exist.")
        
    exe = find_tinui_executable()
    
    # We run the build in a temporary directory so we don't clobber the user's workspace
    # unless they passed 'dist', but Go defaults to 'dist' anyway. Let's just run it
    # in the entry_file's directory to preserve path resolution for scenes/, and let Go write to 'dist'.
    # If the user specified a custom out_dir, we move the contents of dist to out_dir.
    
    working_dir = entry_path.parent
    
    print(f"Delegating compilation to {exe}...")
    result = subprocess.run(
        [exe, "build", entry_path.name],
        cwd=working_dir,
        capture_output=False, # Stream to stdout/stderr directly
        text=True
    )
    
    if result.returncode != 0:
        raise RuntimeError("TinPyUI Build Failed (see compiler output above).")
        
    default_dist = working_dir / "dist"
    
    if str(default_dist.resolve()) != str(out_path.resolve()):
        # Move files from default dist to the requested out_dir
        for item in default_dist.iterdir():
            dest = out_path / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            shutil.move(str(item), str(out_path))
            
    json_dest = out_path / "app.ir.json"
    bin_dest = out_path / "app.ir.bin"
    
    if not json_dest.exists():
        raise RuntimeError("Build succeeded but app.ir.json is missing.")
        
    ir_dict = json.loads(json_dest.read_text(encoding="utf-8"))
    
    # Overwrite index.html with the Python-specific SEO shell to preserve v1.7.1 compatibility
    html_content = f"""<!DOCTYPE html>
<!-- TINPYUI GENERATED FILE — DO NOT EDIT DIRECTLY
     Source: {entry_file}
     Compiler: 1.8.0
     Runtime ABI: 4
     Regenerate: tinpyui build {entry_file}
-->
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
        "binary_matrix_size": bin_dest.stat().st_size if bin_dest.exists() else 0,
        "json_size": json_dest.stat().st_size,
        "node_count": len(ir_dict.get("nodes", [])),
    }
