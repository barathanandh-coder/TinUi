"""
Unit tests for TinPyUI v1.7.0 Showcase Features:
- WebGL 2.0 Hardware Shader Engine & Presets
- New Layout & UI Components (Container, Grid, Surface, Header, Footer, Main, ShaderLayer, WebGLCanvas, ParticleField, Icon, Link, etc.)
- Dynamic Scrolling Velocity & Inertia API
- Scroll Reveal (IntersectionObserver)
- Component Adjusting & Moving Sandbox
- Modern UI Morphisms (Glass, Neu, Clay, Holo)
- Cinematic Page Redirect Transitions & Overlays
"""

import unittest
from pathlib import Path

import tinpyui as tin
from tinpyui import (
    Card, Container, Grid, Surface, HeroContainer, Header, Footer, Main, Marquee, Modal, Tooltip,
    ShaderLayer, WebGLCanvas, ParticleField, Icon, Link,
    ShaderPreset, GpuPerformanceMode, get_shader_code, set_shader_preset, set_gpu_mode,
    Morphism, get_morphism_style,
    RedirectTransition, redirect_page, show_toast,
    ScrollSpeedPreset, set_scroll_speed, toggle_auto_scroll
)

class TestShowcaseFeatures(unittest.TestCase):

    def test_new_components_instantiation(self):
        """Test instantiation and IR structure of all new Showcase components."""
        c = Container(id="test-container", align="center", justify="between")
        self.assertEqual(c.tag, "Container")
        self.assertEqual(c.props.get("id"), "test-container")

        g = Grid(cols=4, gap=24, class_="grid-showcase")
        self.assertEqual(g.tag, "Grid")
        self.assertEqual(g.props.get("cols"), "4")
        self.assertEqual(g.props.get("gap"), "24")

        s = Surface(elevation=2)
        self.assertEqual(s.tag, "Surface")

        h = Header(class_="sticky top-0")
        self.assertEqual(h.tag, "Header")

        f = Footer(class_="border-t")
        self.assertEqual(f.tag, "Footer")

        m = Main(class_="min-h-screen")
        self.assertEqual(m.tag, "Main")

        mq = Marquee(direction="left")
        self.assertEqual(mq.tag, "Marquee")

        md = Modal(open=True)
        self.assertEqual(md.tag, "Modal")
        self.assertTrue(md.props.get("open"))

        tt = Tooltip(text="Quick info")
        self.assertEqual(tt.tag, "Tooltip")
        self.assertEqual(tt.props.get("text"), "Quick info")

        sl = ShaderLayer(effect="pillars_of_creation", speed=1.5, intensity=0.9)
        self.assertEqual(sl.tag, "ShaderLayer")
        self.assertEqual(sl.props.get("effect"), "pillars_of_creation")
        self.assertEqual(sl.props.get("speed"), "1.5")
        self.assertEqual(sl.props.get("intensity"), "0.9")

        wgl = WebGLCanvas(id="shader-canvas", preset="black_hole")
        self.assertEqual(wgl.tag, "WebGLCanvas")
        self.assertEqual(wgl.props.get("id"), "shader-canvas")
        self.assertEqual(wgl.props.get("preset"), "black_hole")

        pf = ParticleField(count=120, color="neon-cyan", speed=1.2, interactive=True)
        self.assertEqual(pf.tag, "ParticleField")
        self.assertEqual(pf.props.get("count"), "120")
        self.assertEqual(pf.props.get("color"), "neon-cyan")
        self.assertTrue(pf.props.get("interactive"))

        ic = Icon(name="terminal", size="24px", color="cyan")
        self.assertEqual(ic.tag, "Icon")
        self.assertEqual(ic.props.get("name"), "terminal")

        lk = Link(text="Explore Features", href="#features", target="_self")
        self.assertEqual(lk.tag, "Link")
        self.assertEqual(lk.props.get("href"), "#features")

    def test_visual_props_processing(self):
        """Test morphism, reveal_on_scroll, movable, glow, and redirect_to handling."""
        card = tin.Card(
            morphism="glass",
            reveal_on_scroll=True,
            movable=True,
            glow=75,
            redirect_to="#features",
            class_="p-6 rounded-2xl"
        )
        self.assertEqual(card.props.get("data-morphism"), "glass-morphism")
        self.assertEqual(card.props.get("data-scroll-reveal"), "true")
        self.assertEqual(card.props.get("data-movable"), "true")
        self.assertEqual(card.props.get("data-glow"), "75")
        self.assertEqual(card.props.get("data-redirect-to"), "#features")

        # Verify class_ contains morphism and reveal-on-scroll
        classes = card.props.get("class_")
        self.assertIn("glass-morphism", classes)
        self.assertIn("reveal-on-scroll", classes)
        self.assertIn("p-6", classes)

    def test_all_morphisms(self):
        """Test the 4 modern UI Morphisms."""
        morphisms = [Morphism.GLASS, Morphism.NEUMORPHIC, Morphism.CLAY, Morphism.HOLO]
        for m in morphisms:
            style = get_morphism_style(m)
            self.assertTrue(len(style) > 0, f"Morphism style for {m} should not be empty")

        self.assertIn("backdrop-filter", get_morphism_style("glass"))
        self.assertIn("box-shadow", get_morphism_style("neu"))
        self.assertIn("inset", get_morphism_style("clay"))
        self.assertIn("gradient", get_morphism_style("holo"))

    def test_all_shader_presets_load(self):
        """Test that all 8 built-in WebGL 2.0 fragment shaders load cleanly."""
        presets = [
            ShaderPreset.BLACK_HOLE,
            ShaderPreset.PILLARS_OF_CREATION,
            ShaderPreset.SUPERNOVA_NEBULA,
            ShaderPreset.CYBER_MESH,
            ShaderPreset.AURORA_FLUX,
            ShaderPreset.FLUID_PARTICLES,
            ShaderPreset.VOLUMETRIC_FOG,
            ShaderPreset.BLOOM
        ]

        for p in presets:
            code = get_shader_code(p)
            self.assertIsInstance(code, str)
            self.assertTrue(len(code) > 100, f"Shader {p} code should be substantial")
            self.assertIn("#version 300 es", code, f"Shader {p} must be WebGL 2.0 (#version 300 es)")

        # Verify JS generator helpers
        js_switch = set_shader_preset(ShaderPreset.BLACK_HOLE)
        self.assertEqual(js_switch, "switchShaderPreset(null, 'black_hole')")

        js_mode = set_gpu_mode(GpuPerformanceMode.ECO)
        self.assertIn("setGpuPerformanceMode", js_mode)

    def test_cinematic_redirect_transitions(self):
        """Test cinematic routing transitions."""
        styles = RedirectTransition.ALL
        self.assertEqual(len(styles), 5)
        self.assertIn("Quantum Warp", styles)
        self.assertIn("Hyper-Speed Shutter", styles)
        self.assertIn("Prismatic Blur", styles)
        self.assertIn("Gateway Tunnel", styles)
        self.assertIn("Quantum Portal", styles)

        js_redirect = redirect_page("Telemetry", "#telemetry", RedirectTransition.QUANTUM_WARP)
        self.assertIn("triggerPageRedirect", js_redirect)
        self.assertIn("Telemetry", js_redirect)
        self.assertIn("#telemetry", js_redirect)
        self.assertIn("Quantum Warp", js_redirect)

        js_toast = show_toast("Shader initialized", "emerald")
        self.assertIn("window.showToast", js_toast)
        self.assertIn("Shader initialized", js_toast)

    def test_scroll_velocity_helpers(self):
        """Test dynamic scroll speed multipliers and auto-scroll tour."""
        self.assertEqual(ScrollSpeedPreset.GLIDE, 0.5)
        self.assertEqual(ScrollSpeedPreset.STANDARD, 1.0)
        self.assertEqual(ScrollSpeedPreset.TURBO, 2.0)
        self.assertEqual(ScrollSpeedPreset.HYPER, 3.5)

        js_speed = set_scroll_speed(ScrollSpeedPreset.TURBO)
        self.assertEqual(js_speed, "setScrollSpeedMultiplier(2.0)")

        js_tour_toggle = toggle_auto_scroll()
        self.assertEqual(js_tour_toggle, "toggleAutoScroll()")

        js_tour_on = toggle_auto_scroll(True)
        self.assertEqual(js_tour_on, "toggleAutoScroll(true)")

    def test_runtime_contains_showcase_engines(self):
        """Verify that tin-runtime.js bundles all showcase subsystems."""
        runtime_path = Path(__file__).resolve().parent.parent / "tin-runtime.js"
        self.assertTrue(runtime_path.exists(), "tin-runtime.js must exist")
        content = runtime_path.read_text(encoding="utf-8")

        # 1. WebGL 2.0 Engine & all 8 shaders
        self.assertIn("class WebGLShaderEngine", content)
        self.assertIn("black_hole:", content)
        self.assertIn("pillars_of_creation:", content)
        self.assertIn("supernova_nebula:", content)
        self.assertIn("cyber_mesh:", content)
        self.assertIn("aurora_flux:", content)
        self.assertIn("fluid_particles:", content)
        self.assertIn("volumetric_fog:", content)
        self.assertIn("bloom:", content)

        # 2. Dynamic Scroll
        self.assertIn("scrollSpeedMultiplier", content)
        self.assertIn("setScrollSpeedMultiplier", content)
        self.assertIn("toggleAutoScroll", content)

        # 3. Scroll Reveal
        self.assertIn("initScrollReveal", content)
        self.assertIn("reveal-on-scroll", content)

        # 4. Component Moving Sandbox
        self.assertIn("updateMovableComponent", content)
        self.assertIn("setComponentMorphism", content)
        self.assertIn("compState", content)

        # 5. Cinematic Redirect Overlay
        self.assertIn("triggerPageRedirect", content)
        self.assertIn("page-redirect-overlay", content)
        self.assertIn("redirect-progress-bar", content)

        # 6. Toast & Clipboard
        self.assertIn("showToast", content)
        self.assertIn("copyToClipboard", content)

    def test_declarative_nested_layout(self):
        """Verify context manager nesting of new components producing valid to_dict()."""
        with Container(class_="bg-dark") as root:
            with Grid(cols=3, gap=16):
                with Card(morphism="glass", reveal_on_scroll=True):
                    Icon(name="bolt", color="cyan")
                    tin.Heading(text="Go AOT")
                    tin.Text(text="Ultra-fast compilation")
                    Link(text="Docs", href="#docs")

        d = root.to_dict()
        self.assertEqual(d["tag"], "Container")
        self.assertEqual(len(d["children"]), 1)
        grid_dict = d["children"][0]
        self.assertEqual(grid_dict["tag"], "Grid")
        self.assertEqual(len(grid_dict["children"]), 1)
        card_dict = grid_dict["children"][0]
        self.assertEqual(card_dict["tag"], "Card")
        self.assertIn("glass-morphism", card_dict["props"]["class_"])
        self.assertIn("reveal-on-scroll", card_dict["props"]["class_"])
        self.assertEqual(len(card_dict["children"]), 4)
        self.assertEqual(card_dict["children"][0]["tag"], "Icon")
        self.assertEqual(card_dict["children"][3]["tag"], "Link")

if __name__ == "__main__":
    unittest.main()
