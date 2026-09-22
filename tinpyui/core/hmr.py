"""
Hot Module Replacement (HMR) Engine for Indentation-Based .tin Syntax.
Performs incremental AST and parameter diffing to update WebGL uniforms and
targeted node attributes in the live browser without remounting the canvas or refreshing.
"""

import re
from typing import Dict, List, Any, Optional, Tuple

class HMRTracker:
    """Incremental state and AST parameter tracker for live indentation templates."""

    def __init__(self):
        self.last_source: Optional[str] = None
        self.node_registry: Dict[int, Dict[str, Any]] = {}

    @staticmethod
    def parse_line(raw_line: str) -> Optional[Dict[str, Any]]:
        clean = raw_line.split("#")[0].rstrip()
        if not clean.strip():
            return None
        indent = len(clean) - len(clean.lstrip(" "))
        match = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:\((.*)\))?', clean)
        if not match:
            return None
        tag = match.group(1)
        prop_str = match.group(2) or ""

        props = {}
        for m in re.finditer(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s,)]+))', prop_str):
            k = m.group(1)
            v = m.group(2) if m.group(2) is not None else (m.group(3) if m.group(3) is not None else m.group(4))
            props[k] = v or ""

        return {"indent": indent, "tag": tag, "props": props}

    def compute_diff(self, old_source: str, new_source: str) -> List[Dict[str, Any]]:
        """
        Compares old and new source code.
        Returns a list of granular HMR patch instructions.
        """
        old_lines = [l for l in old_source.splitlines() if l.strip() and not l.strip().startswith("#")]
        new_lines = [l for l in new_source.splitlines() if l.strip() and not l.strip().startswith("#")]

        # If line count changed, fallback to incremental structural IR reload
        if len(old_lines) != len(new_lines):
            return [{"type": "reload_ir"}]

        patches = []
        node_counter = 1

        for i, (l_old, l_new) in enumerate(zip(old_lines, new_lines)):
            p_old = self.parse_line(l_old)
            p_new = self.parse_line(l_new)

            if not p_old or not p_new:
                continue

            # If component wrapper
            if p_old["tag"] == "component" or p_new["tag"] == "component":
                continue

            node_id = node_counter
            node_counter += 1

            # If tag or indentation changed, structural topology changed
            if p_old["tag"] != p_new["tag"] or p_old["indent"] != p_new["indent"]:
                return [{"type": "reload_ir"}]

            props_old = p_old["props"]
            props_new = p_new["props"]

            # 1. Check for Shader Uniform changes
            if p_new["tag"] in ("ShaderLayer", "WebGLCanvas", "AnimatedBackground"):
                for uniform_key in ["speed", "intensity", "effect", "primaryColor", "secondaryColor"]:
                    if props_old.get(uniform_key) != props_new.get(uniform_key):
                        patches.append({
                            "type": "reload_shader",
                            "node_id": node_id,
                            "target": "shader-canvas",
                            "param": uniform_key,
                            "value": props_new.get(uniform_key)
                        })

            # 2. Check for Text changes
            if props_old.get("text") != props_new.get("text"):
                patches.append({
                    "type": "patch_node",
                    "action": "SET_TEXT",
                    "node_id": node_id,
                    "value": props_new.get("text", "")
                })

            # 3. Check for Attribute changes
            for k, v in props_new.items():
                if k != "text" and props_old.get(k) != v:
                    patches.append({
                        "type": "patch_node",
                        "action": "SET_ATTRIBUTE",
                        "node_id": node_id,
                        "key": "class" if k == "class_" else k,
                        "value": v
                    })

        return patches if patches else []
