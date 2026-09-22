#version 300 es
precision highp float;
out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform float u_intensity;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    vec2 p = uv * 2.0 - 1.0;
    p.x *= u_resolution.x / u_resolution.y;

    float t = u_time * 0.4 * u_speed;
    float wave = sin(p.x * 2.5 + t) * 0.35 + cos(p.x * 1.8 - t * 0.7) * 0.25 + sin(p.x * 4.0 + t * 1.2) * 0.15;
    float dist = abs(p.y - wave);
    float glow = 0.09 / (dist + 0.035);

    vec3 col1 = vec3(0.0, 0.95, 0.85);
    vec3 col2 = vec3(0.65, 0.2, 1.0);
    vec3 col3 = vec3(0.1, 0.4, 0.95);

    vec3 aurora = mix(col1, col2, sin(p.x * 2.0 + t) * 0.5 + 0.5);
    aurora = mix(aurora, col3, cos(p.y * 3.0 + t) * 0.5 + 0.5);

    vec3 finalCol = aurora * glow * (1.8 * u_intensity);
    float alpha = clamp(glow * 0.65, 0.0, 0.85);
    FragColor = vec4(finalCol, alpha);
}
