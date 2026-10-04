#version 300 es
precision highp float;

out vec4 FragColor;

uniform vec2 u_resolution;
uniform float u_time;

// Procedural pseudo-noise function
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

float fbm(vec2 p) {
    float v = 0.0;
    float a = 0.5;
    vec2 shift = vec2(100.0);
    for (int i = 0; i < 4; ++i) {
        v += a * noise(p);
        p = p * 2.0 + shift;
        a *= 0.5;
    }
    return v;
}

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 p = uv * 3.0;

    // Flowing atmospheric fog simulation
    vec2 flow = vec2(u_time * 0.1, u_time * 0.05);
    float q = fbm(p + flow);
    vec2 r = vec2(fbm(p + 1.0 * q + vec2(1.7, 9.2) + 0.15 * u_time),
                  fbm(p + 1.0 * q + vec2(8.3, 2.8) + 0.126 * u_time));
    float f = fbm(p + r);

    // Dynamic bioluminescent color grading
    vec3 col = mix(vec3(0.05, 0.08, 0.15), vec3(0.0, 0.6, 0.8), clamp((f * f) * 4.0, 0.0, 1.0));
    col = mix(col, vec3(0.2, 0.0, 0.4), clamp(length(q), 0.0, 1.0));
    col = mix(col, vec3(0.0, 0.95, 1.0), clamp(length(r.x), 0.0, 1.0) * 0.5);

    FragColor = vec4((f * f * f + 0.6 * f * f + 0.5 * f) * col, 0.85);
}
