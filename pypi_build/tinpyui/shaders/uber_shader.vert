#version 300 es
precision highp float;

layout(location = 0) in vec2 a_pos;
layout(location = 1) in vec2 a_uv;
layout(location = 2) in int a_type;

uniform vec2 u_resolution;

flat out int v_type;
out vec2 v_uv;
out vec2 v_pos;

void main() {
    v_type = a_type;
    v_uv = a_uv;
    v_pos = a_pos;
    
    // Normalize coordinates into WebGL clip space [-1, 1]
    vec2 zeroToOne = a_pos / u_resolution;
    vec2 clipSpace = (zeroToOne * 2.0) - 1.0;
    gl_Position = vec4(clipSpace.x, -clipSpace.y, 0.0, 1.0);
}
