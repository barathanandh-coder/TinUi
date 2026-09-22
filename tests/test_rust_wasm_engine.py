"""
Unit Tests for TinUI v1.8.0 Rust WebAssembly Core Engine
Verifies engine artifacts, size reductions, and runtime loader integration.
"""

import os
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

class TestRustWasmEngine(unittest.TestCase):

    def test_wasm_binary_size_optimization(self):
        """Ensure the new Rust WASM engine is under 500KB (massive drop from Go's 3.5MB)."""
        wasm_path = ROOT_DIR / "tinui_engine.wasm"
        self.assertTrue(wasm_path.exists(), f"WASM engine not found at {wasm_path}")

        size_bytes = wasm_path.stat().st_size
        size_kb = size_bytes / 1024

        # Verify it is significantly smaller than the 3.5MB Go engine
        self.assertLess(size_kb, 500.0, f"WASM engine too large: {size_kb:.1f} KB (Expected < 500 KB)")
        print(f"\n[Test] Rust WASM Engine Size: {size_kb:.1f} KB (Go was ~3,450 KB - {100 - (size_kb/3450)*100:.1f}% reduction!)")

    def test_runtime_dual_engine_loader(self):
        """Ensure tin-runtime.js contains the Rust WASM priority loader with Go fallback."""
        runtime_path = ROOT_DIR / "tin-runtime.js"
        self.assertTrue(runtime_path.exists())

        content = runtime_path.read_text(encoding="utf-8")
        self.assertIn("wasm_bindgen", content)
        self.assertIn("Rust WebAssembly Core Engine v1.8.0 active", content)
        self.assertIn("Legacy Fallback: Go WASM Engine", content)

    def test_dist_artifacts_synchronization(self):
        """Ensure all distribution targets receive the compiled WASM engine."""
        targets = [
            ROOT_DIR / "public" / "tinui_engine.wasm",
            ROOT_DIR / "tinpyui" / "tinui_engine.wasm",
            ROOT_DIR / "pypi_build" / "tinpyui" / "tinui_engine.wasm",
        ]
        for target in targets:
            self.assertTrue(target.exists(), f"Target missing: {target}")
            self.assertGreater(target.stat().st_size, 10000)

    def test_crate_configuration(self):
        """Verify Rust crate configuration has size-optimization profile."""
        cargo_path = ROOT_DIR / "crates" / "tin_wasm_engine" / "Cargo.toml"
        self.assertTrue(cargo_path.exists())

        cargo_text = cargo_path.read_text(encoding="utf-8")
        self.assertIn('opt-level = "z"', cargo_text)
        self.assertIn("lto = true", cargo_text)
        self.assertIn("panic = \"abort\"", cargo_text)

if __name__ == "__main__":
    unittest.main()
