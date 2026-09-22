"""WebGL 2.0 Shader Engine presets and shader helpers."""
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

class ShaderPreset:
    """Built-in hardware WebGL 2.0 fragment shader presets."""
    BLACK_HOLE = "black_hole"
    PILLARS_OF_CREATION = "pillars_of_creation"
    SUPERNOVA_NEBULA = "supernova_nebula"
    CYBER_MESH = "cyber_mesh"
    AURORA_FLUX = "aurora_flux"
    FLUID_PARTICLES = "fluid_particles"
    VOLUMETRIC_FOG = "volumetric_fog"
    BLOOM = "bloom"
    OFF = "off"

    ALL = [
        BLACK_HOLE, PILLARS_OF_CREATION, SUPERNOVA_NEBULA,
        CYBER_MESH, AURORA_FLUX, FLUID_PARTICLES,
        VOLUMETRIC_FOG, BLOOM, OFF
    ]

class GpuPerformanceMode:
    """GPU Load modes to optimize framerate and energy consumption."""
    ULTRA_ECO = 0.25   # Minimum GPU Load (25% render scale)
    ECO = 0.40         # Cool & Quiet GPU (40% render scale, cuts 84% pixel workload)
    BALANCED = 0.60    # Balanced Detail (60% render scale)
    NATIVE = 1.00      # 100% Native Resolution

def get_shaders_dir() -> Path:
    """Returns absolute path to the package's shaders directory."""
    pkg_dir = Path(__file__).resolve().parent
    local_shaders = pkg_dir / "shaders"
    if local_shaders.exists():
        return local_shaders
    # Fallback to root repo shaders dir
    repo_shaders = pkg_dir.parent / "shaders"
    if repo_shaders.exists():
        return repo_shaders
    return local_shaders

def get_shader_code(preset: str) -> str:
    """Loads GLSL fragment shader source code for a preset name."""
    s_name = preset.strip().lower()
    if s_name.endswith(".frag"):
        file_name = s_name
    else:
        file_name = f"{s_name}.frag"
        
    s_dir = get_shaders_dir()
    target_file = s_dir / file_name
    if target_file.exists():
        return target_file.read_text(encoding="utf-8")
        
    raise FileNotFoundError(f"Shader preset '{preset}' not found in {s_dir}. Available: {ShaderPreset.ALL}")

def set_shader_preset(preset: str) -> str:
    """Returns the JavaScript invocation to switch the active WebGL shader."""
    return f"switchShaderPreset(null, '{preset}')"

def set_gpu_mode(mode: Union[float, str]) -> str:
    """Returns the JavaScript invocation to set GPU performance mode."""
    return f"setGpuPerformanceMode({float(mode)})"
