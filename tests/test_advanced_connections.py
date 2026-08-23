import unittest
import os
import json
import sys
from unittest.mock import patch, MagicMock

# Mock the optional 'websocket' library to avoid import errors when testing
sys.modules['websocket'] = MagicMock()

import tinpyui as tin

class TestAdvancedConnections(unittest.TestCase):
    def tearDown(self):
        for f in ["test_app.ir.json"]:
            if os.path.exists(f):
                try: os.remove(f)
                except Exception: pass

    def test_websocket_reactivity(self):
        socket = tin.use_socket("ws://echo.websocket.events")
        # Assert initial status change
        self.assertIn(socket.status.value, ["connecting", "open"])

        # Force offline mock fallback for local assertion
        socket._ws = None
        socket.send("Hello TinPyUI")
        self.assertEqual(socket.message.value, "Echo: Hello TinPyUI")

        # Test socket close
        socket.close()
        self.assertEqual(socket.status.value, "closed")

    def test_sse_stream(self):
        sse_sig = tin.use_sse("https://stream.wikimedia.org/v2/stream/recentchange")
        self.assertIsInstance(sse_sig, tin.Signal)

    @patch("tkinter.filedialog.askopenfilename")
    @patch("tkinter.filedialog.asksaveasfilename")
    def test_platform_bridge_features(self, mock_save, mock_open):
        mock_open.return_value = "/path/to/file.txt"
        mock_save.return_value = "/path/to/save.txt"

        path = tin.PlatformBridge.open_file_dialog()
        self.assertEqual(path, "/path/to/file.txt")

        save_path = tin.PlatformBridge.save_file_dialog()
        self.assertEqual(save_path, "/path/to/save.txt")

        # Notify shouldn't raise exceptions
        with patch("ctypes.windll.user32.MessageBoxW") as mock_msg:
            tin.PlatformBridge.show_notification("Alert", "System online")

    def test_app_export_ir(self):
        app = tin.Window(title="Test Dynamic IR App", width=1280, height=800)
        with app:
            with tin.Section():
                tin.Heading(text="Welcome to Dynamic IR")
                tin.Button(text="Click Me", variant="neon-cyan")

        ir_path = "test_app.ir.json"
        app.export_ir(ir_path)
        
        self.assertTrue(os.path.exists(ir_path))
        with open(ir_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["title"], "Test Dynamic IR App")
        self.assertEqual(data["width"], 1280)
        self.assertEqual(data["root"]["tag"], "Window")
        self.assertEqual(data["root"]["children"][0]["tag"], "Section")
        self.assertEqual(data["root"]["children"][0]["children"][0]["tag"], "Heading")
        self.assertEqual(data["root"]["children"][0]["children"][1]["tag"], "Button")

if __name__ == "__main__":
    unittest.main()
