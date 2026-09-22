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
    mat2 rot = mat2(0.8, 0.6, -0.6, 0.8);
    for (int i = 0; i < 4; i++) {
        v += a * noise(p);
        p = rot * p * 2.1;
        a *= 0.5;
    }
    return v;
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.06 * u_speed;

    // 3 iconic towering interstellar dust columns rising from bottom
    // Pillar 1 (Left - Tallest, knuckled)
    float col1Width = mix(0.16, 0.26, smoothstep(0.46, -0.5, uv.y));
    float p1Dist = abs(uv.x + 0.28 + sin(uv.y * 3.0) * 0.04) - col1Width;
    float p1 = max(p1Dist, uv.y - 0.45);

    // Pillar 2 (Center - Pointed spire)
    float col2Width = mix(0.12, 0.22, smoothstep(0.32, -0.5, uv.y));
    float p2Dist = abs(uv.x - 0.04 + sin(uv.y * 2.5) * 0.03) - col2Width;
    float p2 = max(p2Dist, uv.y - 0.30);

    // Pillar 3 (Right - Slanted)
    float col3Width = mix(0.10, 0.18, smoothstep(0.18, -0.5, uv.y));
    float p3Dist = abs(uv.x - 0.35 - uv.y * 0.2) - col3Width;
    float p3 = max(p3Dist, uv.y - 0.16);

    float baseDist = min(p1, min(p2, p3));

    // Domain warp for billowy gaseous erosion
    vec2 warp = uv * 3.2 + vec2(0.0, t * 0.15);
    vec2 q = vec2(fbm(warp), fbm(warp + vec2(4.3, 1.8)));
    float turb = fbm(uv * 4.5 + q * 1.5);

    float density = clamp((-baseDist + turb * 0.38) * 5.0, 0.0, 1.0);

    // Directional UV ionizing radiation vector (from NGC 6611 at top-right)
    vec2 lightDir = normalize(vec2(0.75, 0.65));

    // Surface gradient for illumination
    float eps = 0.015;
    float nX = (abs(uv.x + eps + 0.28) - abs(uv.x - eps + 0.28)) / (2.0 * eps);
    float nY = 1.0;
    vec2 normal = normalize(vec2(nX, nY) + 0.001);

    // Ionization front rims (glowing ultraviolet edges)
    float rim = smoothstep(0.15, 0.45, density) * (1.0 - smoothstep(0.45, 0.85, density));
    float lightFront = max(0.0, dot(normal, lightDir));

    // Hubble & JWST Heritage Palette:
    // [S II]: dense cold dark molecular dust core
    vec3 dustCore = vec3(0.12, 0.06, 0.035);
    // H-alpha: golden amber ionization front
    vec3 hAlpha = vec3(0.98, 0.62, 0.22) * 2.2;
    // [O III]: turquoise/cyan ambient emission fringe
    vec3 oiii = vec3(0.12, 0.82, 0.95) * 2.4;

    // Background cosmic nebula and starfield
    float bgNeb = fbm(uv * 2.5 + vec2(t * 0.08, -t * 0.04));
    vec3 bgCol = mix(vec3(0.015, 0.02, 0.05), vec3(0.04, 0.38, 0.62) * 0.6, bgNeb);

    // Stars
    vec2 starUv = uv * 110.0;
    vec2 starId = floor(starUv);
    float sRand = hash(starId);
    if (sRand > 0.90) {
        float d = length(fract(starUv) - 0.5);
        bgCol += mix(vec3(0.7, 0.88, 1.0), vec3(1.0, 0.85, 0.7), hash(starId + 1.2)) * (0.01 / (d * d + 0.008)) * pow(sRand, 18.0);
    }

    // Composite pillar over nebula
    vec3 pillarCol = dustCore;
    pillarCol += hAlpha * rim * (0.6 + 0.8 * lightFront);
    pillarCol += oiii * pow(rim, 2.2) * 1.5;

    vec3 finalCol = mix(bgCol, pillarCol, density);

    // Infant protostars at pillar fingertips with diffraction spikes
    vec2 pStar1 = vec2(-0.28, 0.44);
    float dStar1 = length(uv - pStar1);
    float spike1 = max(0.0, 1.0 - abs(uv.x - pStar1.x) * 40.0) * max(0.0, 1.0 - abs(uv.y - pStar1.y) * 4.0) +
                   max(0.0, 1.0 - abs(uv.y - pStar1.y) * 40.0) * max(0.0, 1.0 - abs(uv.x - pStar1.x) * 4.0);
    finalCol += vec3(1.0, 0.75, 0.3) * ((0.012 / (dStar1 * dStar1 + 0.004)) + spike1 * 1.6) * 0.45;

    vec2 pStar2 = vec2(-0.04, 0.29);
    float dStar2 = length(uv - pStar2);
    float spike2 = max(0.0, 1.0 - abs(uv.x - pStar2.x) * 45.0) * max(0.0, 1.0 - abs(uv.y - pStar2.y) * 4.5) +
                   max(0.0, 1.0 - abs(uv.y - pStar2.y) * 45.0) * max(0.0, 1.0 - abs(uv.x - pStar2.x) * 4.5);
    finalCol += vec3(0.5, 0.85, 1.0) * ((0.010 / (dStar2 * dStar2 + 0.004)) + spike2 * 1.4) * 0.38;

    finalCol *= u_intensity;
    FragColor = vec4(finalCol, 0.92);
}
