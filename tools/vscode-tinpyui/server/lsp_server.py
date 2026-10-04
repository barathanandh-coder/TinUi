"""
Lightweight Language Server Protocol (LSP) Engine for TinPyUI (.tin).
Provides structural indentation checking, syntax validation, and tag completions.
"""

from typing import Dict, List, Any, Optional

TAG_COMPLETIONS = [
    {"label": "Section", "detail": "Semantic section layout container", "insertText": "Section():\n    $0"},
    {"label": "Row", "detail": "Horizontal flex layout container", "insertText": "Row(gap=${1:16}, align=\"center\"):\n    $0"},
    {"label": "Column", "detail": "Vertical flex layout container", "insertText": "Column(gap=${1:16}):\n    $0"},
    {"label": "Card", "detail": "Visual depth container with morphism support", "insertText": "Card(morphism=\"${1:glass}\", class_=\"p-6 rounded-2xl\"):\n    $0"},
    {"label": "Container", "detail": "General layout container", "insertText": "Container(class_=\"$1\"):\n    $0"},
    {"label": "Grid", "detail": "Responsive CSS Grid container", "insertText": "Grid(cols=\"${1:3}\", gap=${2:24}):\n    $0"},
    {"label": "Surface", "detail": "Layered depth surface", "insertText": "Surface():\n    $0"},
    {"label": "ShaderLayer", "detail": "Hardware WebGL 2.0 fragment shader layer", "insertText": "ShaderLayer(effect=\"${1:black_hole}\", speed=\"1.0\")"},
    {"label": "WebGLCanvas", "detail": "Direct WebGL canvas surface", "insertText": "WebGLCanvas(id=\"${1:shader-canvas}\", preset=\"${2:black_hole}\")"},
    {"label": "ParticleField", "detail": "Interactive particle dynamics canvas", "insertText": "ParticleField(count=${1:60}, color=\"${2:neon-cyan}\")"},
    {"label": "AnimatedBackground", "detail": "Full-screen procedural shader backdrop", "insertText": "AnimatedBackground(effect=\"${1:pillars_of_creation}\"):\n    $0"},
    {"label": "Navbar", "detail": "Top navigation header bar", "insertText": "Navbar(class_=\"fixed top-0 w-full backdrop-blur-xl\"):\n    $0"},
    {"label": "Link", "detail": "Navigation hyperlink element", "insertText": "Link(text=\"${1:Click}\", href=\"${2:#}\")"},
    {"label": "Button", "detail": "Interactive button element", "insertText": "Button(text=\"${1:Submit}\", onClick=\"${2:}\")"},
    {"label": "Input", "detail": "Form input field", "insertText": "Input(type=\"${1:text}\", placeholder=\"${2:Enter value...}\")"},
    {"label": "Heading", "detail": "Header typography", "insertText": "Heading(text=\"${1:Title}\", size=\"${2:2xl}\")"},
    {"label": "Text", "detail": "Paragraph text typography", "insertText": "Text(text=\"${1:Content}\")"},
    {"label": "GradientText", "detail": "Luminous gradient typography", "insertText": "GradientText(text=\"${1:Title}\")"},
    {"label": "Badge", "detail": "Status badge label", "insertText": "Badge(text=\"${1:Active}\", variant=\"neon-cyan\")"},
    {"label": "Icon", "detail": "Material Symbols icon", "insertText": "Icon(name=\"${1:terminal}\")"},
    {"label": "Modal", "detail": "Dialog modal overlay", "insertText": "Modal(open=${1:True}):\n    $0"},
    {"label": "Tooltip", "detail": "Hover tooltip popup", "insertText": "Tooltip(text=\"${1:Info}\")"}
]

class TinLspServer:
    """Provides diagnostics and completion intelligence for .tin files."""

    @staticmethod
    def validate_document(content: str) -> List[Dict[str, Any]]:
        """
        Validates indentation structure and reports diagnostics.
        Rules:
          - Indentation must be composed of spaces or tabs consistently.
          - Colons at end of line indicate an indentation block.
        """
        diagnostics = []
        lines = content.splitlines()

        for idx, line in enumerate(lines):
            line_num = idx + 1
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Check indentation consistency (spaces should be multiple of 2 or 4)
            leading_spaces = len(line) - len(line.lstrip(" "))
            if leading_spaces % 2 != 0 and "\t" not in line[:leading_spaces]:
                diagnostics.append({
                    "line": line_num,
                    "character": 0,
                    "severity": 2, # Warning
                    "message": f"Line {line_num}: Odd indentation count ({leading_spaces} spaces). Standard is 4 (or 2) spaces per block level."
                })

            # Check unclosed quotes
            single_quotes = stripped.count("'")
            double_quotes = stripped.count('"')
            if single_quotes % 2 != 0:
                diagnostics.append({
                    "line": line_num,
                    "character": len(line),
                    "severity": 1, # Error
                    "message": f"Line {line_num}: Unclosed single quote (') detected."
                })
            if double_quotes % 2 != 0:
                diagnostics.append({
                    "line": line_num,
                    "character": len(line),
                    "severity": 1, # Error
                    "message": f"Line {line_num}: Unclosed double quote (\") detected."
                })

            # Check for missing colon if following line has deeper indentation
            next_idx = idx + 1
            while next_idx < len(lines):
                next_line = lines[next_idx]
                next_stripped = next_line.strip()
                if next_stripped and not next_stripped.startswith("#"):
                    next_indent = len(next_line) - len(next_line.lstrip(" "))
                    if next_indent > leading_spaces and not stripped.endswith(":"):
                        diagnostics.append({
                            "line": line_num,
                            "character": len(line),
                            "severity": 2, # Warning
                            "message": f"Line {line_num}: Block appears to be missing a colon (':') before indented block."
                        })
                    break
                next_idx += 1

        return diagnostics

    @staticmethod
    def get_completions(prefix: str = "") -> List[Dict[str, Any]]:
        """Returns tag suggestions filtered by prefix."""
        pref = prefix.strip().lower()
        if not pref:
            return TAG_COMPLETIONS
        return [item for item in TAG_COMPLETIONS if item["label"].lower().startswith(pref)]
