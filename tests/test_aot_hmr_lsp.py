import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tinpyui.core.aot_compiler import AOTCompiler, build_aot_static_bundle
from tinpyui.core.binary_ir import decode_binary_ir
from tinpyui.core.hmr import HMRTracker
from tinpyui.core.wasm_memory_bridge import WasmMemoryBridge, WASM_BRIDGE_MAGIC

# Import LSP server
sys.path.insert(0, str(PROJECT_ROOT / "vscode-tinpyui" / "server"))
from lsp_server import TinLspServer


class TestAOTCompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = AOTCompiler()
        self.sample_tin = """
component App():
    Section():
        Card(morphism="glass", class_="p-6"):
            Heading(text="Welcome to TinPyUI"):
            Button(text="Click Me", onClick="doSomething"):
        ShaderLayer(effect="black_hole", speed="1.2"):
"""

    def test_compile_tin_source_to_ir(self):
        ir = self.compiler.compile_tin_source(self.sample_tin)
        self.assertIn("nodes", ir)
        nodes = ir["nodes"]
        self.assertTrue(len(nodes) > 0)

        ops = [n["op"] for n in nodes]
        self.assertIn("CREATE_NODE", ops)
        self.assertIn("SET_TEXT", ops)
        self.assertIn("SET_ATTRIBUTE", ops)
        self.assertIn("APPEND_CHILD", ops)

        # Check morphism attribute conversion
        morphism_attrs = [n for n in nodes if n.get("key") == "data-morphism"]
        self.assertTrue(len(morphism_attrs) > 0)
        self.assertEqual(morphism_attrs[0]["value"], "glass-morphism")

        # Check text value
        texts = [n for n in nodes if n["op"] == "SET_TEXT"]
        self.assertTrue(any("Welcome to TinPyUI" in t["value"] for t in texts))

    def test_compile_to_binary_matrix(self):
        bin_matrix = self.compiler.compile_to_binary_matrix(self.sample_tin)
        self.assertIsInstance(bin_matrix, bytes)
        self.assertTrue(bin_matrix.startswith(b"TINB\x01"))
        
        # Decode back to verify roundtrip integrity
        decoded = decode_binary_ir(bin_matrix)
        self.assertIn("nodes", decoded)
        self.assertEqual(len(decoded["nodes"]), len(self.compiler.instructions))

    def test_build_aot_static_bundle(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            entry_file = os.path.join(tmp_dir, "test_app.tin")
            with open(entry_file, "w", encoding="utf-8") as f:
                f.write(self.sample_tin)

            dist_dir = os.path.join(tmp_dir, "dist")
            result = build_aot_static_bundle(entry_file, out_dir=dist_dir, app_name="Test App")

            self.assertEqual(result["status"], "success")
            self.assertTrue(os.path.exists(os.path.join(dist_dir, "index.html")))
            self.assertTrue(os.path.exists(os.path.join(dist_dir, "app.ir.bin")))
            self.assertTrue(os.path.exists(os.path.join(dist_dir, "app.ir.json")))
            self.assertTrue(os.path.exists(os.path.join(dist_dir, "tin-runtime.js")))
            self.assertTrue(os.path.exists(os.path.join(dist_dir, "tinui_engine.wasm")))
            self.assertTrue(os.path.isdir(os.path.join(dist_dir, "shaders")))
            
            # Verify generated index.html contains the application title
            with open(os.path.join(dist_dir, "index.html"), "r", encoding="utf-8") as hf:
                html_content = hf.read()
                self.assertIn("Test App", html_content)
                self.assertIn("app.ir.bin", html_content)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


class TestHMRTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = HMRTracker()

    def test_parse_line(self):
        parsed = self.tracker.parse_line('    Button(text="Submit", class_="btn-primary"):')
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["tag"], "Button")
        self.assertEqual(parsed["props"]["text"], "Submit")
        self.assertEqual(parsed["props"]["class_"], "btn-primary")
        self.assertEqual(parsed["indent"], 4)

    def test_compute_diff_node_patch(self):
        old_src = """
component App():
    Heading(text="Old Title"):
    Button(text="Submit"):
"""
        new_src = """
component App():
    Heading(text="New Title"):
    Button(text="Submit"):
"""
        patches = self.tracker.compute_diff(old_src, new_src)
        self.assertEqual(len(patches), 1)
        self.assertEqual(patches[0]["type"], "patch_node")
        self.assertEqual(patches[0]["action"], "SET_TEXT")
        self.assertEqual(patches[0]["value"], "New Title")

    def test_compute_diff_shader_reload(self):
        old_src = """
component App():
    ShaderLayer(effect="black_hole", speed="1.0"):
"""
        new_src = """
component App():
    ShaderLayer(effect="black_hole", speed="2.5"):
"""
        patches = self.tracker.compute_diff(old_src, new_src)
        self.assertTrue(len(patches) > 0)
        shader_reloads = [p for p in patches if p["type"] == "reload_shader"]
        self.assertEqual(len(shader_reloads), 1)
        self.assertEqual(shader_reloads[0]["param"], "speed")
        self.assertEqual(shader_reloads[0]["value"], "2.5")

    def test_compute_diff_structural_change(self):
        old_src = """
component App():
    Heading(text="Title"):
"""
        new_src = """
component App():
    Heading(text="Title"):
    Button(text="New Button"):
"""
        patches = self.tracker.compute_diff(old_src, new_src)
        self.assertEqual(len(patches), 1)
        self.assertEqual(patches[0]["type"], "reload_ir")


class TestWasmMemoryBridge(unittest.TestCase):
    def setUp(self):
        self.bridge = WasmMemoryBridge(capacity_nodes=64)

    def test_header_initialization(self):
        ctrl = self.bridge.read_control()
        self.assertEqual(ctrl["magic"], WASM_BRIDGE_MAGIC)
        self.assertEqual(ctrl["frame_counter"], 0)
        self.assertEqual(ctrl["active_nodes"], 0)

    def test_write_and_read_node_state(self):
        self.bridge.write_node_state(
            node_id=3,
            pos_x=12.5,
            pos_y=45.0,
            scale_x=2.0,
            scale_y=1.5,
            rotation=3.14159,
            opacity=0.85,
            speed=2.0
        )

        state = self.bridge.read_node_state(3)
        self.assertAlmostEqual(state["pos_x"], 12.5, places=4)
        self.assertAlmostEqual(state["pos_y"], 45.0, places=4)
        self.assertAlmostEqual(state["scale_x"], 2.0, places=4)
        self.assertAlmostEqual(state["scale_y"], 1.5, places=4)
        self.assertAlmostEqual(state["rotation"], 3.14159, places=4)
        self.assertAlmostEqual(state["opacity"], 0.85, places=4)
        self.assertAlmostEqual(state["speed"], 2.0, places=4)

    def test_advance_frame(self):
        initial = self.bridge.read_control()["frame_counter"]
        new_fc = self.bridge.advance_frame(active_nodes=10)
        self.assertEqual(new_fc, initial + 1)
        ctrl = self.bridge.read_control()
        self.assertEqual(ctrl["frame_counter"], initial + 1)
        self.assertEqual(ctrl["active_nodes"], 10)


class TestTinLspServer(unittest.TestCase):
    def test_completions(self):
        completions = TinLspServer.get_completions()
        self.assertTrue(len(completions) > 10)
        labels = [c["label"] for c in completions]
        self.assertIn("Section", labels)
        self.assertIn("Card", labels)
        self.assertIn("ShaderLayer", labels)
        self.assertIn("WebGLCanvas", labels)
        self.assertIn("ParticleField", labels)

    def test_validation_clean_document(self):
        clean_code = """
component Main():
    Section():
        Card(morphism="glass"):
            Heading(text="Hello"):
"""
        diagnostics = TinLspServer.validate_document(clean_code)
        self.assertEqual(len(diagnostics), 0)

    def test_validation_odd_indentation(self):
        odd_indent_code = """
component Main():
   Section():
"""
        diagnostics = TinLspServer.validate_document(odd_indent_code)
        self.assertTrue(len(diagnostics) > 0)
        self.assertIn("Odd indentation", diagnostics[0]["message"])

    def test_validation_missing_colon_block(self):
        code_missing_colon = """
component Main():
    Section()
        Card(morphism="glass"):
"""
        diagnostics = TinLspServer.validate_document(code_missing_colon)
        self.assertTrue(len(diagnostics) > 0)
        self.assertTrue(any("missing a colon" in d["message"] for d in diagnostics))


class TestAOTCompilerEdgeCases(unittest.TestCase):
    def setUp(self):
        self.compiler = AOTCompiler()

    def test_deep_nested_hierarchy_with_comments(self):
        deep_src = """
# Top-level comment
component Main():
    # Section starts
    Section(id="main_sec"):
        # Level 1
        Container(class_="wrapper"):
            # Level 2
            Grid(cols="3", gap=16):
                # Level 3
                Card(morphism="clay"):
                    # Level 4
                    Heading(text="Deep Header"):
                    Text(text="Nested Text"):
"""
        ir = self.compiler.compile_tin_source(deep_src)
        nodes = ir["nodes"]
        self.assertTrue(len(nodes) > 0)

        # Ensure all 6 elements were created
        creates = [n for n in nodes if n["op"] == "CREATE_NODE"]
        self.assertEqual(len(creates), 6)

        # Check that parent-child relationships were linked
        appends = [n for n in nodes if n["op"] == "APPEND_CHILD"]
        self.assertEqual(len(appends), 6)
        
        # Verify text nodes
        texts = {n["id"]: n["value"] for n in nodes if n["op"] == "SET_TEXT"}
        self.assertTrue(any("Deep Header" in v for v in texts.values()))
        self.assertTrue(any("Nested Text" in v for v in texts.values()))

    def test_all_morphism_variants(self):
        for morph in ["glass", "neu", "clay", "holo"]:
            src = f"""
component Morph():
    Card(morphism="{morph}"):
"""
            ir = self.compiler.compile_tin_source(src)
            morph_nodes = [n for n in ir["nodes"] if n.get("key") == "data-morphism"]
            self.assertEqual(len(morph_nodes), 1)
            self.assertEqual(morph_nodes[0]["value"], f"{morph}-morphism")


class TestHMRTrackerEdgeCases(unittest.TestCase):
    def setUp(self):
        self.tracker = HMRTracker()

    def test_identical_sources_return_empty_patches(self):
        src = """
component App():
    Heading(text="Static"):
    Button(text="Ok"):
"""
        patches = self.tracker.compute_diff(src, src)
        self.assertEqual(len(patches), 0)

    def test_compute_diff_attribute_change(self):
        old_src = """
component App():
    Button(text="Submit", class_="btn-primary"):
"""
        new_src = """
component App():
    Button(text="Submit", class_="btn-accent neon-glow"):
"""
        patches = self.tracker.compute_diff(old_src, new_src)
        self.assertEqual(len(patches), 1)
        self.assertEqual(patches[0]["type"], "patch_node")
        self.assertEqual(patches[0]["action"], "SET_ATTRIBUTE")
        self.assertEqual(patches[0]["key"], "class")
        self.assertEqual(patches[0]["value"], "btn-accent neon-glow")

    def test_compute_diff_multiple_simultaneous_node_edits(self):
        old_src = """
component App():
    Heading(text="Title 1"):
    Button(text="Action 1"):
"""
        new_src = """
component App():
    Heading(text="Title 2"):
    Button(text="Action 2"):
"""
        patches = self.tracker.compute_diff(old_src, new_src)
        self.assertEqual(len(patches), 2)
        self.assertEqual(patches[0]["value"], "Title 2")
        self.assertEqual(patches[1]["value"], "Action 2")


class TestWasmMemoryBridgeStress(unittest.TestCase):
    def setUp(self):
        self.bridge = WasmMemoryBridge(capacity_nodes=32)

    def test_capacity_wrapping_modulo(self):
        # Node ID 35 should wrap to slot 35 % 32 = 3
        self.bridge.write_node_state(node_id=35, pos_x=99.5, pos_y=120.0)
        state = self.bridge.read_node_state(3)
        self.assertAlmostEqual(state["pos_x"], 99.5, places=4)
        self.assertAlmostEqual(state["pos_y"], 120.0, places=4)

    def test_batch_node_writes_integrity(self):
        for i in range(32):
            self.bridge.write_node_state(
                node_id=i,
                pos_x=float(i * 10),
                pos_y=float(i * 20),
                scale_x=1.0 + (i * 0.1),
                speed=float(i)
            )

        for i in range(32):
            state = self.bridge.read_node_state(i)
            self.assertAlmostEqual(state["pos_x"], float(i * 10), places=3)
            self.assertAlmostEqual(state["pos_y"], float(i * 20), places=3)
            self.assertAlmostEqual(state["scale_x"], 1.0 + (i * 0.1), places=3)
            self.assertAlmostEqual(state["speed"], float(i), places=3)


class TestCliBuildProgrammatic(unittest.TestCase):
    def test_cli_cmd_build_webgl_execution(self):
        import argparse
        from tinpyui.cli import cmd_build

        tmp_dir = tempfile.mkdtemp()
        try:
            entry = os.path.join(tmp_dir, "cli_test.tin")
            with open(entry, "w", encoding="utf-8") as f:
                f.write("""
component App():
    Section():
        Heading(text="CLI Build Test"):
""")
            out_dist = os.path.join(tmp_dir, "dist_output")
            args = argparse.Namespace(
                file=entry,
                target_file=None,
                target="webgl",
                out=out_dist,
                app_name="CLI App",
                mobile=False,
                android=False,
                ios=False,
                desktop=False,
                package="com.cli.app",
                bundle_id="com.cli.app",
                apk=False,
                ipa=False
            )
            cmd_build(args)

            self.assertTrue(os.path.exists(os.path.join(out_dist, "index.html")))
            self.assertTrue(os.path.exists(os.path.join(out_dist, "app.ir.bin")))
            self.assertTrue(os.path.exists(os.path.join(out_dist, "app.ir.json")))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
