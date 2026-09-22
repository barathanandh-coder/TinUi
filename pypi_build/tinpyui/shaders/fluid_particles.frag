#version 300 es
precision highp float;

out vec4 FragColor;

uniform vec2 u_resolution;
uniform float u_time;

void main() {
    vec2 p = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / min(u_resolution.x, u_resolution.y);

    // Metaball fluid centers
    float field = 0.0;
    vec3 fluidColor = vec3(0.0);

    for (int i = 0; i < 7; i++) {
        float fi = float(i);
        float speed = 0.8 + fi * 0.2;
        vec2 center = vec2(
            sin(u_time * speed + fi * 1.5) * 0.6,
            cos(u_time * speed * 0.7 + fi * 2.1) * 0.5
        );
        float dist = length(p - center);
        float r = 0.18 + sin(fi + u_time) * 0.04;
        float ball = (r * r) / (dist * dist + 0.001);
        field += ball;

        vec3 ballCol = 0.5 + 0.5 * cos(vec3(0.0, 2.0, 4.0) + fi * 0.9 + u_time * 0.5);
        fluidColor += ballCol * ball;
    }

    fluidColor /= max(1.0, field);

    // Threshold cutoff for sharp liquid metaball boundary
    float threshold = 1.2;
    float edge = smoothstep(threshold - 0.1, threshold + 0.1, field);

    // Specular highlight on liquid surface
    float spec = pow(smoothstep(threshold, threshold + 0.8, field), 3.0) * 0.6;
    vec3 finalCol = fluidColor * edge + spec;

    FragColor = vec4(finalCol, edge * 0.9);
}
