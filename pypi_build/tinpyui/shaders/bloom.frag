#version 300 es
precision highp float;

out vec4 FragColor;

uniform vec2 u_resolution;
uniform float u_time;
uniform float u_threshold; // e.g. 0.7
uniform float u_intensity; // e.g. 1.5

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 p = uv * 2.0 - 1.0;
    p.x *= u_resolution.x / u_resolution.y;

    // Base glowing energy core
    float d = length(p);
    float glow = 0.08 / (d + 0.02);
    
    // Multi-frequency pulsating rings
    float ring1 = sin(d * 20.0 - u_time * 3.0) * 0.5 + 0.5;
    float ring2 = cos(d * 35.0 + u_time * 2.0) * 0.5 + 0.5;
    
    vec3 baseColor = vec3(0.0, 0.95, 1.0) * glow;
    baseColor += vec3(1.0, 0.0, 0.5) * (ring1 * 0.2 / (d + 0.1));
    baseColor += vec3(0.0, 1.0, 0.5) * (ring2 * 0.15 / (d + 0.1));

    // Threshold extraction & HDR additive bloom
    float luminance = dot(baseColor, vec3(0.2126, 0.7152, 0.0722));
    float bloomFactor = max(0.0, luminance - (u_threshold > 0.0 ? u_threshold : 0.4));
    vec3 bloom = baseColor * bloomFactor * (u_intensity > 0.0 ? u_intensity : 1.8);

    vec3 finalColor = baseColor + bloom;
    FragColor = vec4(finalColor, clamp(luminance * 1.5, 0.0, 1.0));
}
