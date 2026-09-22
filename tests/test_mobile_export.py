"""
Tests for TinPyUI Mobile Export Pipeline (Android / Gradle).
"""

import unittest
import os
import shutil
import sys
import tempfile

import unittest
import os
import shutil
import sys
import tempfile

import tinpyui as tin
try:
    from pypi_build.tinpyui.mobile_export import export_android_project
except ImportError:
    from tinpyui.mobile_export import export_android_project


class TestMobileExportPipeline(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="tinpyui_mobile_test_")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_export_android_project_structure(self):
        """Verifies that export_android_project generates standard Android Gradle structure."""
        out_dir = os.path.join(self.test_dir, "android_app")
        pkg_name = "com.example.cyberapp"
        app_name = "CyberApp"

        res = export_android_project(
            target_file="main.tin",
            output_dir=out_dir,
            app_name=app_name,
            package_name=pkg_name,
            build_apk=False
        )

        self.assertTrue(os.path.exists(out_dir))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "settings.gradle")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "build.gradle")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "gradle.properties")))
        self.assertTrue(os.path.exists(os.path.join(out_dir, "app", "build.gradle")))

        # Check AndroidManifest.xml
        manifest_path = os.path.join(out_dir, "app", "src", "main", "AndroidManifest.xml")
        self.assertTrue(os.path.exists(manifest_path))
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_content = f.read()
            self.assertIn("android.permission.VIBRATE", manifest_content)
            self.assertIn("android.permission.INTERNET", manifest_content)
            self.assertIn("hardwareAccelerated=\"true\"", manifest_content)

        # Check MainActivity.java
        java_path = os.path.join(out_dir, "app", "src", "main", "java", "com", "example", "cyberapp", "MainActivity.java")
        self.assertTrue(os.path.exists(java_path))
        with open(java_path, "r", encoding="utf-8") as f:
            java_content = f.read()
            self.assertIn("package com.example.cyberapp;", java_content)
            self.assertIn("WebViewAssetLoader", java_content)
            self.assertIn("TinBridge", java_content)
            self.assertIn("vibrate", java_content)

        # Check assets
        assets_dir = os.path.join(out_dir, "app", "src", "main", "assets")
        self.assertTrue(os.path.exists(os.path.join(assets_dir, "index.html")))
        self.assertTrue(os.path.exists(os.path.join(assets_dir, "app.ir.json")))

    def test_top_level_export_mobile_api(self):
        """Verifies that tin.export_mobile() helper function works."""
        out_dir = os.path.join(self.test_dir, "android_api_test")
        res = tin.export_mobile(
            target_file="main.tin",
            output_dir=out_dir,
            app_name="TestApp",
            package_name="com.test.app"
        )
        self.assertIn("output_dir", res)
        self.assertTrue(os.path.exists(os.path.join(out_dir, "settings.gradle")))

if __name__ == "__main__":
    unittest.main()
