import sys
import json
import shutil
import tempfile
import subprocess
import unittest
from pathlib import Path

pkg_dir = Path("src").resolve()
sys.path.insert(0, str(pkg_dir))

from tinpyui.core.aot_compiler import AOTCompiler, build_aot_static_bundle, find_tinui_executable

TEST_TIN = """component Main():
    Row():
        Text(text="Hello")
"""

class TestCompilerBridgeConformance(unittest.TestCase):
    def test_bridge_vs_native_go_ir(self):
        """
        Prove that `AOTCompiler.compile_tin_source` produces the EXACT same 
        IR as running `tinui compile` natively.
        """
        c = AOTCompiler()
        
        # 1. Generate via Python API Bridge
        python_ir = c.compile_tin_source(TEST_TIN)
        
        # 2. Generate via Native Go execution
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source_file = tmp_path / "main.tin"
            source_file.write_text(TEST_TIN, encoding="utf-8")
            
            exe = find_tinui_executable()
            subprocess.run([exe, "compile", str(source_file)], cwd=tmpdir, check=True)
            
            go_ir_file = tmp_path / "main.ir.json"
            go_ir = json.loads(go_ir_file.read_text(encoding="utf-8"))
            
        # Strip timestamp/source from metadata to avoid spurious failures
        python_ir["_tinpyui"]["timestamp"] = ""
        python_ir["_tinpyui"]["source"] = ""
        go_ir["_tinpyui"]["timestamp"] = ""
        go_ir["_tinpyui"]["source"] = ""
        
        self.assertEqual(python_ir, go_ir)
        
    def test_syntax_error_propagation(self):
        """Prove that Go syntax errors are correctly raised as Python exceptions."""
        bad_tin = "component Main():\n    Row():\n        Text(text=\"Hello\n" # Missing closing quote
        c = AOTCompiler()
        with self.assertRaises(SyntaxError):
            c.compile_tin_source(bad_tin)

if __name__ == "__main__":
    unittest.main()
