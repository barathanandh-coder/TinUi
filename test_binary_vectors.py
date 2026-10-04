import json
import sys
import tempfile
import subprocess
from pathlib import Path

pkg_dir = Path("src").resolve()
sys.path.insert(0, str(pkg_dir))

from tinpyui.core.binary_ir import encode_binary_ir
from tinpyui.core.aot_compiler import find_tinui_executable

TEST_TIN = """component Main():
    Row(class_="test"):
        Text(text="Hello")
"""

def test_golden_vectors():
    exe = find_tinui_executable()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        source_file = tmp_path / "main.tin"
        source_file.write_text(TEST_TIN, encoding="utf-8")
        
        # We need to compile via Go directly to get both JSON and BIN outputs
        subprocess.run([exe, "build", str(source_file)], cwd=tmpdir, check=True)
        
        # Read Go generated outputs from dist/ (default outDir for build)
        go_json_path = tmp_path / "main.ir.json"
        go_bin_path = tmp_path / "main.ir.bin"
        
        with open(go_json_path, 'r', encoding='utf-8') as f:
            go_ir = json.load(f)
            
        with open(go_bin_path, 'rb') as f:
            go_bin = f.read()
            
        # Generate Python binary using the canonical IR dictionary
        python_bin = encode_binary_ir(go_ir)
        
        if python_bin == go_bin:
            print("SUCCESS: Go app.ir.bin matches Python encode_binary_ir() byte-for-byte!")
        else:
            print(f"FAILED: Byte mismatch!")
            print(f"  Python bin size: {len(python_bin)}")
            print(f"  Go bin size:     {len(go_bin)}")
            
            # Print diff of first 100 bytes
            min_len = min(len(python_bin), len(go_bin))
            for i in range(min_len):
                if python_bin[i] != go_bin[i]:
                    print(f"  Mismatch at offset {i}: Py=0x{python_bin[i]:02x}, Go=0x{go_bin[i]:02x}")
                    break
            
if __name__ == "__main__":
    test_golden_vectors()
