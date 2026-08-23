import unittest
import tinpyui as tin

class TestV16Features(unittest.TestCase):
    def test_virtual_stack_node(self):
        v_stack = tin.VirtualStack(total_count=50000, item_height=45.0)
        self.assertEqual(v_stack.tag, "VirtualStack")
        self.assertEqual(v_stack.props.get("total_count"), 50000)
        self.assertEqual(v_stack.props.get("item_height"), 45.0)

    def test_virtual_list_node(self):
        items = [f"Item {i}" for i in range(100)]
        v_list = tin.VirtualList(items=items, item_height=30.0)
        self.assertEqual(v_list.tag, "VirtualList")
        self.assertEqual(len(v_list.props.get("items")), 100)

    def test_spring_physics(self):
        spring = tin.Spring(tension=180.0, friction=20.0)
        spring.target = 100.0
        # Step through 60 frames at 120 FPS
        for _ in range(60):
            pos = spring.step(1.0 / 120.0)
        self.assertGreater(pos, 0.0)
        self.assertLessEqual(pos, 150.0)

    def test_platform_bridge(self):
        self.assertTrue(tin.haptics.vibrate(100))
        # Verify clipboard copy doesn't raise
        tin.PlatformBridge.copy_clipboard("TinPyUI v1.6.0")

    def test_target_selection_options(self):
        from unittest.mock import patch
        app = tin.App("Test Target App")

        # Option 1: Desktop
        with patch('builtins.input', return_value="1"):
            target = app.select_target_interactive()
            self.assertEqual(target, "Native Desktop App")
            self.assertEqual((app.width, app.height), (1600, 1000))

        # Option 2: Android
        with patch('builtins.input', return_value="2"):
            target = app.select_target_interactive()
            self.assertEqual(target, "Android Mobile")
            self.assertEqual((app.width, app.height), (380, 680))

        # Option 3: iOS
        with patch('builtins.input', return_value="3"):
            target = app.select_target_interactive()
            self.assertEqual(target, "iOS Mobile")
            self.assertEqual((app.width, app.height), (375, 680))

        # Option 4: Tablet
        with patch('builtins.input', return_value="4"):
            target = app.select_target_interactive()
            self.assertEqual(target, "Tablet")
            self.assertEqual((app.width, app.height), (640, 520))

        # Option 5: WebAssembly
        with patch('builtins.input', return_value="5"):
            target = app.select_target_interactive()
            self.assertEqual(target, "Web WASM Browser")
            self.assertEqual((app.width, app.height), (1024, 600))

    def test_signal_set_get_update(self):
        sig = tin.Signal("Initial")
        self.assertEqual(sig.get(), "Initial")
        sig.set("Updated")
        self.assertEqual(sig.value, "Updated")
        self.assertEqual(sig.get(), "Updated")
        sig.update(lambda v: v + " Value")
        self.assertEqual(sig.value, "Updated Value")

    def test_navitem_active_state(self):
        active_tab = tin.Signal("Overview")
        nav_overview = tin.NavItem("Overview", active=lambda: active_tab.value == "Overview", on_click=lambda: active_tab.set("Overview"))
        nav_hardware = tin.NavItem("Hardware", active=lambda: active_tab.value == "Hardware", on_click=lambda: active_tab.set("Hardware"))
        
        self.assertEqual(tin.eval_prop(nav_overview.props.get("active")), True)
        self.assertEqual(tin.eval_prop(nav_hardware.props.get("active")), False)
        
        # Trigger navigation redirection
        nav_hardware.props["on_click"]()
        self.assertEqual(active_tab.value, "Hardware")
        self.assertEqual(tin.eval_prop(nav_overview.props.get("active")), False)
        self.assertEqual(tin.eval_prop(nav_hardware.props.get("active")), True)

if __name__ == "__main__":
    unittest.main()
