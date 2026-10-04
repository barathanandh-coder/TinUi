"""Cinematic routing transitions and page redirect helpers."""
from typing import Optional

class RedirectTransition:
    """Supported cinematic routing transitions."""
    QUANTUM_WARP = "Quantum Warp"
    SHUTTER = "Hyper-Speed Shutter"
    PRISMATIC_BLUR = "Prismatic Blur"
    GATEWAY_TUNNEL = "Gateway Tunnel"
    QUANTUM_PORTAL = "Quantum Portal"

    ALL = [QUANTUM_WARP, SHUTTER, PRISMATIC_BLUR, GATEWAY_TUNNEL, QUANTUM_PORTAL]

def redirect_page(destination_name: str, target_url: str, transition_style: str = "Quantum Warp") -> str:
    """
    Generates a client JavaScript snippet to trigger a cinematic page redirect.
    Supports both internal page anchors (e.g. '#features') and external web URLs.
    """
    safe_dest = destination_name.replace("'", "\\'")
    safe_url = target_url.replace("'", "\\'")
    safe_style = transition_style.replace("'", "\\'")
    return f"triggerPageRedirect('{safe_dest}', '{safe_url}', '{safe_style}')"

def show_toast(message: str, toast_type: str = "cyan") -> str:
    """Generates a client JavaScript snippet to display a toast notification."""
    safe_msg = message.replace("'", "\\'")
    return f"window.showToast('{safe_msg}', '{toast_type}')"
