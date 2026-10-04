#version 300 es
precision highp float;

// Incoming data from the Vertex Shader
flat in int v_type;    // 0 = SDF Background, 1 = MSDF Text
in vec2 v_uv;          // Used for text atlas texture mapping
in vec2 v_pos;         // Local pixel coordinates for SDF math

out vec4 FragColor;

// Textures
uniform sampler2D u_font_atlas;

// Shared Uniforms
uniform vec4 u_color;  // Used as bg_color for Box, text_color for Text
uniform vec2 u_resolution;

// Box Specific Uniforms
uniform vec2 u_box_size;
uniform float u_radius;
uniform float u_border_width;
uniform vec4 u_border_color;
uniform float u_shadow_softness;
uniform vec2 u_shadow_offset;
uniform vec4 u_shadow_color;

// MSDF Median Helper Function
float median(float r, float g, float b) {
    return max(min(r, g), min(max(r, g), b));
}

// SDF Box Helper Function
float sdRoundRect(vec2 p, vec2 b, float r) {
    vec2 d = abs(p) - b + vec2(r);
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)) - r;
}

void main() {
    if (v_type == 0) {
        // ==========================================
        // PATH A: RENDER SDF BUTTON / BOX BACKGROUND
        // ==========================================
        vec2 half_size = u_box_size * 0.5;
        float box_dist = sdRoundRect(v_pos, half_size, u_radius);
        float shadow_dist = sdRoundRect(v_pos - u_shadow_offset, half_size, u_radius);
        
        float aa = 1.0;
        float shadow_alpha = exp(-max(shadow_dist, 0.0) / max(u_shadow_softness, 0.001)) * u_shadow_color.a;
        vec4 shadow = vec4(u_shadow_color.rgb, shadow_alpha);

        float border_mask = 1.0 - smoothstep(0.0, aa, abs(box_dist + u_border_width * 0.5) - u_border_width * 0.5);
        float box_mask = 1.0 - smoothstep(0.0, aa, box_dist);
        
        vec4 final_color = mix(vec4(0.0), shadow, shadow.a);
        final_color = mix(final_color, u_color, box_mask * u_color.a);
        final_color = mix(final_color, u_border_color, border_mask * u_border_color.a);

        FragColor = final_color;
        
    } else if (v_type == 1) {
        // ==========================================
        // PATH B: RENDER MSDF TYPOGRAPHY
        // ==========================================
        // 1. Sample the RGB distance fields from the font texture
        vec3 msd = texture(u_font_atlas, v_uv).rgb;
        
        // 2. Calculate the median distance (the core MSDF algorithm)
        float dist = median(msd.r, msd.g, msd.b) - 0.5;
        
        // 3. Hardware-level anti-aliasing based on screen pixel derivatives
        // fwidth(dist) dynamically calculates how sharp the font edge should be
        float fw = fwidth(dist);
        float opacity = clamp(dist / max(fw, 0.0001) + 0.5, 0.0, 1.0);
        
        // Output the perfectly crisp text pixel
        FragColor = vec4(u_color.rgb, u_color.a * opacity);
    }
}
