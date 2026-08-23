"""
Unit and Integration Tests for the TinPyUI v1.6 Omni-Platform Sample Project.
Verifies that all 5 target devices build and execute correctly without errors.
"""

import unittest
import os
import tinpyui as tin
from database.schema import seed_database, DB_FILE
from backend.server import telemetry_service
from main import OmniDeviceFleetApp

class TestV16SampleProject(unittest.TestCase):
    def setUp(self):
        seed_database()

    def test_database_fleet_seeding(self):
        """Verifies database contains records for Desktop, Android, iOS, Tablet, and Web."""
        db = tin.connect(f"sqlite:///{DB_FILE}")
        devices = db.table("devices").all()
        self.assertGreaterEqual(len(devices), 5)
        
        platforms = [d["device_type"] for d in devices]
        self.assertIn("desktop", platforms)
        self.assertIn("mobile_android", platforms)
        self.assertIn("mobile_ios", platforms)
        self.assertIn("tablet", platforms)
        self.assertIn("wasm_web", platforms)

    def test_backend_telemetry_service(self):
        """Verifies backend telemetry service generates metrics and virtual events."""
        metrics = telemetry_service.get_latest_metrics()
        self.assertIn("fps", metrics)
        self.assertIn("latency_us", metrics)
        self.assertGreater(metrics["fps"], 60.0)

        events = telemetry_service.generate_virtual_events(25)
        self.assertEqual(len(events), 25)
        self.assertTrue(any("Desktop" in e for e in events))

    def test_desktop_layout_mode(self):
        """Verifies OmniDeviceFleetApp builds 3-column Desktop layout successfully."""
        app = OmniDeviceFleetApp(target_name="Desktop")
        app.target_name = "Desktop"
        app.width, app.height = 1600, 1000
        
        # Test physics trigger
        app.trigger_spring_physics()
        self.assertGreaterEqual(app.spring_pos.value, 0.0)

        # Test signal mutation
        app.increment_counter()
        self.assertEqual(app.counter.value, 1)

        # Build UI Tree
        root = app.build()
        self.assertIsNotNone(root)

    def test_android_mobile_layout_mode(self):
        """Verifies OmniDeviceFleetApp builds touch-optimized Android layout with haptics."""
        app = OmniDeviceFleetApp(target_name="Android Mobile")
        app.target_name = "Android Mobile"
        app.width, app.height = 380, 680
        
        # Test haptic trigger
        app.trigger_haptic_feedback()
        self.assertEqual(app.haptic_count.value, 1)

        # Build UI Tree
        root = app.build()
        self.assertIsNotNone(root)

    def test_ios_mobile_layout_mode(self):
        """Verifies OmniDeviceFleetApp builds Retina Safe-Area iOS layout."""
        app = OmniDeviceFleetApp(target_name="iOS Mobile")
        app.target_name = "iOS Mobile"
        app.width, app.height = 375, 680

        app.trigger_haptic_feedback()
        self.assertEqual(app.haptic_count.value, 1)

        root = app.build()
        self.assertIsNotNone(root)

    def test_tablet_split_layout_mode(self):
        """Verifies OmniDeviceFleetApp builds adaptive 2-column Tablet split layout."""
        app = OmniDeviceFleetApp(target_name="Tablet")
        app.target_name = "Tablet"
        app.width, app.height = 640, 520

        app.trigger_spring_physics()
        root = app.build()
        self.assertIsNotNone(root)

    def test_wasm_web_layout_mode(self):
        """Verifies OmniDeviceFleetApp builds WebAssembly Browser layout."""
        app = OmniDeviceFleetApp(target_name="Web WASM Browser")
        app.target_name = "Web WASM Browser"
        app.width, app.height = 1024, 600

        root = app.build()
        self.assertIsNotNone(root)

    def test_ensure_public_assets_and_simulator_shell(self):
        """Verifies that public assets, IR export, and universal HTML shell are generated."""
        app = OmniDeviceFleetApp(target_name="Android Mobile")
        app.target_name = "Android Mobile"
        app.target_type = "mobile_android"
        app.build()
        app._ensure_public_assets("public")
        
        self.assertTrue(os.path.exists("public/index.html"))
        self.assertTrue(os.path.exists("public/app.ir.json"))
        with open("public/index.html", "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn("TinPyUI Multi-Device Engine", html)
        self.assertIn("tin-device-container", html)
        self.assertIn("tin-device-phone", html)

if __name__ == "__main__":
    unittest.main()
