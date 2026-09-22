"""Honeypot decoys, masked RAM state, and input sanitizers."""
import time
import html
import re
import random
import threading
from typing import Any, Dict, List, Optional
from ..core.signals import Signal

class HoneypotAPI:
    """Deceptive Network Traffic Honeypot Generator for Decoying Reverse Engineers."""
    _decoy_endpoints = [
        "https://api.decoy-node.internal/v1/auth/login",
        "https://telemetry.mock-gateway.net/v2/handshake",
        "https://vault.shadow-cluster.org/v1/tokens"
    ]
    _running = False

    @classmethod
    def start_decoy_traffic(cls, interval_seconds: int = 15):
        """Launches continuous fake API traffic background threads to confuse network sniffers."""
        cls._running = True
        def _loop():
            while cls._running:
                try:
                    target_url = random.choice(cls._decoy_endpoints)
                    fake_payload = {
                        "device_hash": hashlib.sha256(str(time.time()).encode()).hexdigest()[:16],
                        "session_nonce": random.randint(100000, 999999),
                        "token": f"bearer_{hashlib.md5(str(random.random()).encode()).hexdigest()}"
                    }
                    HTTPClient.post(target_url, fake_payload, on_success=lambda r: None, on_error=lambda e: None)
                except Exception: pass
                time.sleep(interval_seconds)

        threading.Thread(target=_loop, daemon=True).start()

    @classmethod
    def stop_decoy_traffic(cls):
        cls._running = False



class RAMMaskedState(Signal):
    """Memory-masked reactive state cell (obfuscates RAM against casual process string scans)."""
    def __init__(self, initial_value: Any = ""):
        self._xor_key = random.randint(1, 255)
        super().__init__(self._encrypt(str(initial_value)))

    def _encrypt(self, val: str) -> str:
        return "".join(chr(ord(c) ^ self._xor_key) for c in val)

    @property
    def raw_value(self) -> str:
        return self._encrypt(self.value)

    def set_masked(self, val: str):
        self.value = self._encrypt(val)

# Backward-compatibility alias
EncryptedState = RAMMaskedState

# COMPREHENSIVE WEB & NATIVE LANGUAGE SECURITY RECTIFICATION ENGINE
# ============================================================================

class Sanitizer:
    """Automatic HTML Output Escaping & Input Sanitization Engine (Rectifies XSS & CSS Exfiltration)."""
    @staticmethod
    def escape(text: Any) -> str:
        if text is None: return ""
        s = str(text)
        return (s.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace('"', "&quot;")
                 .replace("'", "&#x27;"))

    @staticmethod
    def sanitize_css(css_str: str) -> str:
        """Sanitizes CSS string to prevent CSS Attribute-Selector Data Exfiltration."""
        if "url(" in css_str and ("input[" in css_str or "value^=" in css_str):
            return "/* Blocked Malicious CSS Data Exfiltration Pattern */"
        return css_str



honeypot = HoneypotAPI()
sanitizer = Sanitizer()
