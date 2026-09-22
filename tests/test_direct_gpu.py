"""
Unit tests for TinPyUI Direct Metal / DirectX 12 / Vulkan Hardware Vector Surface Pipeline
"""

import unittest
from tinpyui.renderers.direct_gpu import DirectGpuSurface, GpuBackend

class TestDirectGpuPipeline(unittest.TestCase):

    def test_direct_gpu_surface_creation(self):
        with DirectGpuSurface(1920, 1080, GpuBackend.DIRECTX12) as surface:
            self.assertEqual(surface.width, 1920)
            self.assertEqual(surface.height, 1080)
            self.assertEqual(surface.requested_backend, GpuBackend.DIRECTX12)
            self.assertIn("DirectX 12", surface.backend_name)
            self.assertEqual(surface.frame_count, 0)

            # Test frame submission
            res = surface.render_frame()
            self.assertTrue(res)
            self.assertEqual(surface.frame_count, 1)

            res2 = surface.render_frame()
            self.assertTrue(res2)
            self.assertEqual(surface.frame_count, 2)

    def test_platform_auto_detection(self):
        surface = DirectGpuSurface(800, 600, GpuBackend.AUTO)
        self.assertIn(surface.active_backend, [GpuBackend.DIRECTX12, GpuBackend.METAL, GpuBackend.VULKAN])
        self.assertIsNotNone(surface.backend_name)
        surface.close()

    def test_metal_and_vulkan_surface_types(self):
        surf_metal = DirectGpuSurface(1024, 768, GpuBackend.METAL)
        self.assertEqual(surf_metal.backend_name, "Apple Metal (CAMetalLayer)")
        surf_metal.close()

        surf_vulkan = DirectGpuSurface(1280, 720, GpuBackend.VULKAN)
        self.assertEqual(surf_vulkan.backend_name, "Vulkan Surface")
        surf_vulkan.close()

if __name__ == "__main__":
    unittest.main()
