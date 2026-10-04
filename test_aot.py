import sys
from pathlib import Path

pkg_dir = Path("src").resolve()
sys.path.insert(0, str(pkg_dir))

from tinpyui.core.aot_compiler import AOTCompiler, build_aot_static_bundle

source = "component Main():\n    Row():\n        Text(text=\"Hello\")\n"
c = AOTCompiler()
res = c.compile_tin_source(source)
print("IR Dict:")
print(res)

build_res = build_aot_static_bundle("final_test_project/main.tin", "final_test_project/dist")
print("Build Bundle Res:")
print(build_res)
