import json
from tinpyui.core.aot_compiler import AOTCompiler

c = AOTCompiler()
for morph in ["glass", "neu", "clay", "holo"]:
    src = f"""
component Main():
    Card(morphism="{morph}"):
"""
    ir = c.compile_tin_source(src)
    print(f"MORPH: {morph}")
    print(json.dumps([n for n in ir["nodes"] if n.get("key") in ("morphism", "data-morphism")], indent=2))
