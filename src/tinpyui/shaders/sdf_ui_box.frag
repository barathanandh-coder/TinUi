#version 300 es
precision highp float;

// Output color to the monitor
out vec4 FragColor;

// Uniforms updated instantly via the Python shared memory queue
uniform vec2 u_resolution;      // Total size of the WebGL canvas/bounding box
uniform vec2 u_box_size;        // Actual width/height of the UI rectangle
uniform float u_radius;         // Border radius in pixels
uniform float u_border_width;   // Border stroke thickness
uniform float u_shadow_softness;// How blurred the shadow is (e.g., 10.0)
uniform vec2 u_shadow_offset;   // X, Y direction of the shadow cast

uniform vec4 u_bg_color;        // Background fill color (RGBA)
uniform vec4 u_border_color;    // Stroke color (RGBA)
uniform vec4 u_shadow_color;    // Shadow color (RGBA)

// The core SDF equation for a rounded rectangle
float sdRoundRect(vec2 p, vec2 b, float r) {
    vec2 d = abs(p) - b + vec2(r);
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)) - r;
}

void main() {
    // 1. Center the coordinate system for this specific UI element
    vec2 uv = gl_FragCoord.xy - (u_resolution.xy * 0.5);
    vec2 half_size = u_box_size * 0.5;

    // 2. Calculate mathematical distances
    // box_dist is negative inside the box, 0.0 at the exact edge, and positive outside.
    float box_dist = sdRoundRect(uv, half_size, u_radius);
    float shadow_dist = sdRoundRect(uv - u_shadow_offset, half_size, u_radius);

    // 3. Hardware Anti-Aliasing setup
    // We use a 1.0 pixel gradient to blend edges perfectly into the background
    float aa = 1.0; 

    // 4. Calculate Drop Shadow (Exponential Decay)
    // If the pixel is outside the box, fade it out based on distance and softness
    float shadow_alpha = exp(-max(shadow_dist, 0.0) / max(u_shadow_softness, 0.001)) * u_shadow_color.a;
    vec4 shadow = vec4(u_shadow_color.rgb, shadow_alpha);

    // 5. Calculate the Border (Stroke)
    // We carve out a ring by checking if the pixel's distance is within the border width
    float border_mask = 1.0 - smoothstep(0.0, aa, abs(box_dist + u_border_width * 0.5) - u_border_width * 0.5);
    
    // 6. Calculate the Main Box Fill
    // smoothstep(0.0, 1.0, distance) cleanly masks the exact boundary of the box
    float box_mask = 1.0 - smoothstep(0.0, aa, box_dist);

    // 7. Layer Compositing (Painter's Algorithm)
    // Start with a transparent canvas, blend the shadow, then the fill, then the border
    vec4 final_color = mix(vec4(0.0), shadow, shadow.a);
    final_color = mix(final_color, u_bg_color, box_mask * u_bg_color.a);
    final_color = mix(final_color, u_border_color, border_mask * u_border_color.a);

    FragColor = final_color;
}
