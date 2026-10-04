#version 300 es
precision highp float;

out vec4 FragColor;

uniform vec2 u_resolution;
uniform float u_time;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 p = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;

    // Horizon perspective projection
    float horizon = 0.1;
    if (p.y < horizon) {
        float z = 0.3 / (horizon - p.y);
        vec2 gridUv = vec2(p.x * z, z + u_time * 1.5);

        // Anti-aliased grid lines
        vec2 grid = abs(fract(gridUv - 0.5) - 0.5) / fwidth(gridUv);
        float line = 1.0 - min(min(grid.x, grid.y), 1.0);

        // Depth fog attenuation
        float depthFog = exp(-z * 0.12);
        vec3 neonColor = mix(vec3(1.0, 0.0, 0.6), vec3(0.0, 0.95, 1.0), sin(gridUv.y * 0.2) * 0.5 + 0.5);
        vec3 col = neonColor * line * depthFog * 2.0;

        // Scanlines overlay
        float scanline = sin(gl_FragCoord.y * 1.5) * 0.08;
        col -= scanline;

        FragColor = vec4(col, depthFog);
    } else {
        // Sky glow gradient above horizon
        float skyGrad = (p.y - horizon) / 0.8;
        vec3 skyColor = mix(vec3(0.05, 0.02, 0.1), vec3(0.0, 0.0, 0.02), skyGrad);
        FragColor = vec4(skyColor, 1.0);
    }
}
