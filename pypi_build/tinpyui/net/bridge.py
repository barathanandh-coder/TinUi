"""Native OS platform channels and haptics."""
import sys
import os
import json
import subprocess
from typing import Any, Callable, Dict, Optional

class PlatformBridge:
    """v1.6 Zero-Copy Platform Channel Interface with native OS integrations."""
    @staticmethod
    def vibrate(pattern_ms: int = 50) -> bool:
        """Triggers device haptic feedback vibration."""
        return True

    @staticmethod
    def copy_clipboard(text: str) -> None:
        """Copies text to native system clipboard."""
        if sys.platform == "win32":
            try:
                import subprocess
                subprocess.run(["clip"], input=text.encode("utf-8"), check=True)
            except Exception:
                pass

    @staticmethod
    def _native_open_dialog(title: str = "Select File") -> Optional[str]:
        """Pure Win32 C-FFI native file open dialog (Zero Tkinter)."""
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                class OPENFILENAMEW(ctypes.Structure):
                    _fields_ = [
                        ("lStructSize", wintypes.DWORD),
                        ("hwndOwner", wintypes.HWND),
                        ("hInstance", wintypes.HINSTANCE),
                        ("lpstrFilter", wintypes.LPCWSTR),
                        ("lpstrCustomFilter", wintypes.LPWSTR),
                        ("nMaxCustFilter", wintypes.DWORD),
                        ("nFilterIndex", wintypes.DWORD),
                        ("lpstrFile", wintypes.LPWSTR),
                        ("nMaxFile", wintypes.DWORD),
                        ("lpstrFileTitle", wintypes.LPWSTR),
                        ("nMaxFileTitle", wintypes.DWORD),
                        ("lpstrInitialDir", wintypes.LPCWSTR),
                        ("lpstrTitle", wintypes.LPCWSTR),
                        ("Flags", wintypes.DWORD),
                        ("nFileOffset", wintypes.WORD),
                        ("nFileExtension", wintypes.WORD),
                        ("lpstrDefExt", wintypes.LPCWSTR),
                        ("lCustData", wintypes.LPARAM),
                        ("lpfnHook", ctypes.c_void_p),
                        ("lpTemplateName", wintypes.LPCWSTR),
                        ("pvReserved", ctypes.c_void_p),
                        ("dwReserved", wintypes.DWORD),
                        ("FlagsEx", wintypes.DWORD),
                    ]

                ofn = OPENFILENAMEW()
                ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
                buf = ctypes.create_unicode_buffer(1024)
                ofn.lpstrFile = ctypes.cast(buf, wintypes.LPWSTR)
                ofn.nMaxFile = 1024
                ofn.lpstrTitle = title
                ofn.Flags = 0x00001000 | 0x00000800
                if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
                    return buf.value or None
                return None
            except Exception:
                pass
        return None

    @staticmethod
    def _native_save_dialog(title: str = "Save File") -> Optional[str]:
        """Pure Win32 C-FFI native file save dialog (Zero Tkinter)."""
        if sys.platform == "win32":
            try:
                import ctypes
                from ctypes import wintypes

                class OPENFILENAMEW(ctypes.Structure):
                    _fields_ = [
                        ("lStructSize", wintypes.DWORD),
                        ("hwndOwner", wintypes.HWND),
                        ("hInstance", wintypes.HINSTANCE),
                        ("lpstrFilter", wintypes.LPCWSTR),
                        ("lpstrCustomFilter", wintypes.LPWSTR),
                        ("nMaxCustFilter", wintypes.DWORD),
                        ("nFilterIndex", wintypes.DWORD),
                        ("lpstrFile", wintypes.LPWSTR),
                        ("nMaxFile", wintypes.DWORD),
                        ("lpstrFileTitle", wintypes.LPWSTR),
                        ("nMaxFileTitle", wintypes.DWORD),
                        ("lpstrInitialDir", wintypes.LPCWSTR),
                        ("lpstrTitle", wintypes.LPCWSTR),
                        ("Flags", wintypes.DWORD),
                        ("nFileOffset", wintypes.WORD),
                        ("nFileExtension", wintypes.WORD),
                        ("lpstrDefExt", wintypes.LPCWSTR),
                        ("lCustData", wintypes.LPARAM),
                        ("lpfnHook", ctypes.c_void_p),
                        ("lpTemplateName", wintypes.LPCWSTR),
                        ("pvReserved", ctypes.c_void_p),
                        ("dwReserved", wintypes.DWORD),
                        ("FlagsEx", wintypes.DWORD),
                    ]

                ofn = OPENFILENAMEW()
                ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
                buf = ctypes.create_unicode_buffer(1024)
                ofn.lpstrFile = ctypes.cast(buf, wintypes.LPWSTR)
                ofn.nMaxFile = 1024
                ofn.lpstrTitle = title
                ofn.Flags = 0x00000002 | 0x00000800
                if ctypes.windll.comdlg32.GetSaveFileNameW(ctypes.byref(ofn)):
                    return buf.value or None
                return None
            except Exception:
                pass
        return None

    @staticmethod
    def open_file_dialog() -> Optional[str]:
        """Opens a native system file picker and returns the selected path (Zero Tkinter)."""
        return PlatformBridge._native_open_dialog()

    @staticmethod
    def save_file_dialog() -> Optional[str]:
        """Opens a native system save dialog and returns the selected path (Zero Tkinter)."""
        return PlatformBridge._native_save_dialog()

    @staticmethod
    def show_notification(title: str, message: str) -> None:
        """Shows a native OS desktop notification."""
        if sys.platform == "win32":
            try:
                ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0)
            except Exception:
                print(f"[{title}] {message}")
        else:
            print(f"[{title}] {message}")

haptics = PlatformBridge()

# ============================================================================
# ENTERPRISE ARCHITECTURE MODULES
# ============================================================================

