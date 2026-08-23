"""
TinPyUI v1.6.0 Sample Project — Database Layer
Provides declarative Active Record models and SQLite persistence for multi-device fleet telemetry.
"""

import os
import sys

# Ensure project root is in sys.path when executed standalone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tinpyui as tin

DB_FILE = os.path.join(os.path.dirname(__file__), "fleet.db")
db = tin.connect(f"sqlite:///{DB_FILE}")

# Initialize Tables
devices_table = db.table("devices")
telemetry_table = db.table("telemetry_logs")

def seed_database():
    """Seeds initial multi-device fleet records representing all target platforms."""
    # Ensure fresh seed
    devices_table.delete(where={"status": "online"})
    devices_table.delete(where={"status": "standby"})
    
    fleet_nodes = [
        {
            "id": 1,
            "name": "Titan-Desktop-01",
            "platform": "Desktop (Win32 / DirectX 12)",
            "device_type": "desktop",
            "resolution": "1600x1000",
            "fps_target": 120,
            "status": "online",
            "haptics_enabled": 0
        },
        {
            "id": 2,
            "name": "Galaxy-Tab-Pro",
            "platform": "Android Tablet (Split-View)",
            "device_type": "tablet",
            "resolution": "640x520",
            "fps_target": 120,
            "status": "online",
            "haptics_enabled": 1
        },
        {
            "id": 3,
            "name": "Pixel-9-Cyber",
            "platform": "Android Mobile (Touch Engine)",
            "device_type": "mobile_android",
            "resolution": "380x680",
            "fps_target": 120,
            "status": "online",
            "haptics_enabled": 1
        },
        {
            "id": 4,
            "name": "iPhone-16-Pro",
            "platform": "Apple iOS (Retina Safe-Area)",
            "device_type": "mobile_ios",
            "resolution": "375x680",
            "fps_target": 120,
            "status": "online",
            "haptics_enabled": 1
        },
        {
            "id": 5,
            "name": "WASM-Edge-Worker",
            "platform": "Web WASM Browser (WebGPU)",
            "device_type": "wasm_web",
            "resolution": "1024x600",
            "fps_target": 120,
            "status": "online",
            "haptics_enabled": 0
        }
    ]

    for node in fleet_nodes:
        devices_table.upsert(where={"id": node["id"]}, **node)

    # Seed sample telemetry logs
    for i in range(1, 21):
        telemetry_table.insert(
            event_id=f"EVT-{1000 + i}",
            device_id=(i % 5) + 1,
            metric="Render Frame Latency",
            value_us=420 + (i * 15),
            fps=120.0
        )

    return len(fleet_nodes)

if __name__ == "__main__":
    count = seed_database()
    print(f"[TinPyUI Database] Successfully seeded {count} universal multi-device fleet records into database/fleet.db")
