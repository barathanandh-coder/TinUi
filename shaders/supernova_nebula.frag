#version 300 es
precision highp float;
out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform float u_intensity;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}
float fbm(vec2 p) {
    float v = 0.0; float a = 0.5;
    mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
    for (int i = 0; i < 4; ++i) { v += a * noise(p); p = rot * p * 2.1; a *= 0.5; }
    return v;
}

void main() {
    vec2 p = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.12 * u_speed;
    float r = length(p);
    float phi = atan(p.y, p.x);

    // Shockwave expanding bubble
    float ring = abs(r - 0.46 - sin(phi * 5.0 + t) * 0.04);
    float shock = 0.026 / (ring + 0.018);

    // Multi-filament plasma web
    float filaments = fbm(p * 3.6 + vec2(sin(t * 0.4), cos(t * 0.3)));
    filaments += 0.5 * fbm(p * 7.2 - vec2(t * 0.2, t * 0.1));

    // Core pulsar glow
    float core = 0.07 / (r + 0.035);

    vec3 colCyan = vec3(0.08, 0.88, 0.98);
    vec3 colViolet = vec3(0.78, 0.22, 0.98);
    vec3 colGold = vec3(1.0, 0.72, 0.22);

    vec3 col = mix(colCyan, colViolet, filaments);
    col = col * shock * 0.78 + colGold * core * 1.3;

    col *= u_intensity;
    FragColor = vec4(col, clamp(r * 0.45 + 0.4, 0.0, 0.92));
}
