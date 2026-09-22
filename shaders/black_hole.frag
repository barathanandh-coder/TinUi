#version 300 es
precision highp float;
out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_speed;
uniform float u_intensity;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.35 * u_speed;

    // Schwarzschild radius
    float rs = 0.22;
    float r = length(uv);
    float phi = atan(uv.y, uv.x);

    // Analytical gravitational deflection (General Relativity Einstein ring approximation)
    float defl = (rs * rs) / max(r * r, 0.005);
    vec2 lensedUv = uv * (1.0 + defl * 0.45);

    // Primary & Secondary Lensed Accretion Disk (arched above & below event horizon shadow)
    float tilt = 0.45;
    vec2 diskP = vec2(uv.x, (uv.y + defl * 0.22 * sign(uv.y)) / cos(tilt));
    float diskR = length(diskP);
    float diskPhi = atan(diskP.y, diskP.x);

    // Disk radial boundaries
    float rin = rs * 1.25;
    float rout = rs * 4.2;
    float inDisk = smoothstep(rin, rin + 0.06, diskR) * (1.0 - smoothstep(rout - 0.35, rout, diskR));

    // Keplerian differential shear rotation
    float omega = pow(max(diskR, 0.1), -1.5) * 2.2;
    float spiral = sin(diskPhi * 3.0 - diskR * 14.0 + t * 3.0 - omega) * 0.5 + 0.5;
    float turb = noise(vec2(diskR * 6.0, diskPhi * 3.0 - t * 1.5)) * 0.4;
    float gas = inDisk * (0.6 + 0.4 * spiral + turb);

    // Relativistic Doppler beaming (left side approaches -> boosted & blue-shifted)
    float doppler = 1.0 - sin(diskPhi) * 0.48;
    gas *= pow(doppler, 2.5);

    // Color gradient: hot blue-white interior -> golden amber -> crimson outer edge
    float temp = clamp((rout - diskR) / (rout - rin), 0.0, 1.0) * doppler;
    vec3 colHot = vec3(0.6, 0.88, 1.0) * 2.8;
    vec3 colWarm = vec3(1.0, 0.68, 0.2) * 2.0;
    vec3 colCool = vec3(0.9, 0.16, 0.04) * 1.4;
    vec3 diskCol = mix(colCool, colWarm, smoothstep(0.0, 0.45, temp));
    diskCol = mix(diskCol, colHot, smoothstep(0.45, 1.0, temp));

    // Sharp photon ring caustic enclosing the shadow
    float photonRing = exp(-pow((r - rs * 1.35) * 35.0, 2.0)) * 2.4;

    // Event horizon: jet-black absorbing shadow
    float horizon = smoothstep(rs * 0.94, rs * 1.04, r);

    // Gravitationally deflected background stars
    vec2 starCoord = lensedUv * 90.0;
    vec2 starId = floor(starCoord);
    float sRand = hash(starId);
    float star = 0.0;
    if (sRand > 0.90) {
        float d = length(fract(starCoord) - 0.5);
        star = (0.012 / (d * d + 0.009)) * pow(sRand, 20.0) * 1.4;
    }

    // Milky Way galactic dust band
    float mw = exp(-pow(lensedUv.y * 2.5, 2.0)) * 0.15;
    vec3 bg = (vec3(0.012, 0.016, 0.035) + vec3(0.12, 0.08, 0.18) * mw + vec3(star)) * horizon;

    vec3 finalCol = bg + (diskCol * gas + vec3(0.7, 0.88, 1.0) * photonRing) * horizon;

    // Outer gravitational lensing glow halo
    float halo = 0.025 / (r + 0.08);
    finalCol += vec3(0.1, 0.3, 0.7) * halo * 0.3;

    finalCol *= u_intensity;
    FragColor = vec4(finalCol, 0.90);
}
