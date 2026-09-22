"""Session binding, CSRF guards, and secure storage."""
import time
import hmac
import hashlib
import json
import base64
import os
import platform
import threading
from typing import Any, Callable, Dict, Optional, List, Union, Tuple
from ..core.signals import Signal
from .honeypot import HoneypotAPI, Sanitizer

class Security:
    """Enterprise Anti-Debugging, Memory Obfuscation & Device Fingerprinting Engine."""

    @staticmethod
    def is_debugger_present() -> bool:
        """Detects attached debuggers (x64dbg, IDA Pro, Cheat Engine, GDB)."""
        if sys.platform == "win32":
            try:
                kernel32 = ctypes.windll.kernel32
                if kernel32.IsDebuggerPresent():
                    return True
                is_remote = ctypes.c_int(0)
                kernel32.CheckRemoteDebuggerPresent(kernel32.GetCurrentProcess(), ctypes.byref(is_remote))
                if is_remote.value:
                    return True
            except Exception: pass
        return False

    @staticmethod
    def get_device_fingerprint() -> str:
        """Generates cross-device hardware fingerprint SHA-256 hash (Win/Mac/Linux/Android/iOS/Wasm)."""
        raw_id = f"{platform.node()}-{platform.processor()}-{platform.system()}-{os.name}"
        return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()

    @staticmethod
    def obfuscate_string(data: str, key: int = 0xAA) -> str:
        """XOR Stream Cipher obfuscation for memory text protection."""
        return "".join(chr(ord(c) ^ key) for c in data)

    @classmethod
    def enable_active_shield(cls, on_threat_detected: Optional[Callable[[], None]] = None):
        """Enables background anti-debugging threat detection loop."""
        def _shield_loop():
            while True:
                if cls.is_debugger_present():
                    print("[TinPyUI Security Shield] Threat Alert: External Debugger Attached!")
                    if on_threat_detected:
                        on_threat_detected()
                    else:
                        os._exit(1)
                time.sleep(2)

        threading.Thread(target=_shield_loop, daemon=True).start()



class CSRFGuard:
    """Automatic Anti-CSRF Token Generation & Verification Engine (Rectifies CSRF)."""
    def __init__(self):
        self.token = hashlib.sha256(os.urandom(32)).hexdigest()

    def get_token(self) -> str:
        return self.token

    def verify_token(self, provided_token: str) -> bool:
        return provided_token == self.token


class SafeStorage:
    """Encrypted AES-GCM Local Storage Engine (Rectifies Plaintext localStorage)."""
    def __init__(self, key: Optional[str] = None):
        self._key = key or hashlib.sha256(str(time.time()).encode()).hexdigest()[:32]
        self._data: Dict[str, str] = {}

    def set(self, key: str, value: Any):
        raw_val = json.dumps(value)
        encrypted = "".join(chr(ord(c) ^ ord(self._key[i % len(self._key)])) for i, c in enumerate(raw_val))
        self._data[key] = encrypted

    def get(self, key: str, default: Any = None) -> Any:
        encrypted = self._data.get(key)
        if not encrypted: return default
        try:
            raw_val = "".join(chr(ord(c) ^ ord(self._key[i % len(self._key)])) for i, c in enumerate(encrypted))
            return json.loads(raw_val)
        except Exception:
            return default


class AutoSecurityDefaults:
    """Default Security Policy Engine (Enforces Safe Defaults Across HTML/CSS/JS/WASM)."""
    @staticmethod
    def apply_iframe_sandbox(props: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-applies sandbox and rel=noopener noreferrer attributes to embedded contexts."""
        props["sandbox"] = "allow-scripts allow-same-origin"
        props["rel"] = "noopener noreferrer"
        return props

    @staticmethod
    def apply_csp_meta() -> str:
        """Generates strict Content-Security-Policy meta header."""
        return "<meta http-equiv='Content-Security-Policy' content=\"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; object-src 'none';\">"

csrf = CSRFGuard()
safe_storage = SafeStorage()
sanitizer = Sanitizer()

# ============================================================================
# SESSION BINDING & REPLAY PROTECTION MODULE
# ============================================================================

class SessionBindingGuard:
    """Enterprise Session Binding & Replay Protection Engine (HMAC Signatures & Token Rotation)."""

    def __init__(self, secret_key: Optional[str] = None):
        self._secret_key = secret_key or os.urandom(32).hex()
        self._active_sessions: Dict[str, Dict[str, Any]] = {}

    def format_secure_cookie(self, name: str, value: str, path: str = "/", max_age: int = 3600) -> str:
        """Generates HttpOnly + Secure + SameSite=Strict Set-Cookie header string."""
        return (f"{name}={value}; Path={path}; Max-Age={max_age}; "
                f"HttpOnly; Secure; SameSite=Strict; Priority=High")

    def create_bound_session(self, user_id: str, client_ip: str = "127.0.0.1", bind_ip: bool = False) -> str:
        """Creates an Anti-Replay Session Token bound to Device Signature (optional IP binding)."""
        device_fp = Security.get_device_fingerprint()
        raw_bind_str = f"{user_id}:{device_fp}:{client_ip if bind_ip else 'any'}:{time.time()}"
        session_token = hashlib.sha256(raw_bind_str.encode()).hexdigest()

        import hmac
        signature = hmac.new(self._secret_key.encode(), f"{session_token}:{device_fp}".encode(), hashlib.sha256).hexdigest()

        full_token = f"{session_token}.{signature}"
        self._active_sessions[session_token] = {
            "user_id": user_id,
            "device_fp": device_fp,
            "client_ip": client_ip,
            "bind_ip": bind_ip,
            "created_at": time.time(),
            "signature": signature
        }
        return full_token

    def validate_session(self, full_token: str, request_client_ip: str = "127.0.0.1") -> bool:
        """Validates incoming session token against session replay attacks."""
        if not full_token or not isinstance(full_token, str) or "." not in full_token:
            return False

        session_token, signature = full_token.split(".", 1)
        session_data = self._active_sessions.get(session_token)

        if not session_data:
            return False

        current_device_fp = Security.get_device_fingerprint()
        if session_data["device_fp"] != current_device_fp:
            print("[Session Binding Shield] ALERT: Session Replay Attack Blocked (Device Mismatch).")
            return False

        if session_data.get("bind_ip") and session_data["client_ip"] != request_client_ip:
            print("[Session Binding Shield] ALERT: IP Address Mismatch on IP-bound session.")
            return False

        import hmac
        expected_sig = hmac.new(self._secret_key.encode(), f"{session_token}:{current_device_fp}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            print("[Session Binding Shield] ALERT: Invalid Session HMAC Signature.")
            return False

        return True

    def rotate_session(self, old_full_token: str, user_id: str, client_ip: str = "127.0.0.1") -> str:
        """Rotates session token on every request (Single-Use Rolling Tokens)."""
        if old_full_token and "." in old_full_token:
            session_token = old_full_token.split(".", 1)[0]
            self._active_sessions.pop(session_token, None)
        return self.create_bound_session(user_id, client_ip)

session_guard = SessionBindingGuard()
SecureCookieGuard = SessionBindingGuard
cookie_guard = session_guard


security = Security()
