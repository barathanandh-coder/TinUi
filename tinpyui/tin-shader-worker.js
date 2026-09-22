// tin-shader-worker.js — OffscreenCanvas Web Worker for Hardware WebGL Shaders
// Executes GPU fragment shaders on an isolated worker thread without main-thread jank.

let gl = null;
let canvas = null;
let program = null;
let quadBuffer = null;
let activePreset = 'black_hole';
let speed = 1.0;
let intensity = 1.0;
let qualityScale = 0.40;
let lastRenderTime = 0;
let fpsCapInterval = 28; // ~35 FPS
let startTime = performance.now();
let uTime = null, uRes = null, uSpeed = null, uIntensity = null, aPos = null;

const VS_SOURCE = `#version 300 es
in vec2 a_pos;
void main() { gl_Position = vec4(a_pos, 0.0, 1.0); }
`;

// Fragment shaders map
const SHADERS = {
  black_hole: `#version 300 es
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
void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.35 * u_speed;
    float rs = 0.22;
    float r = length(uv);
    float phi = atan(uv.y, uv.x);
    float defl = (rs * rs) / max(r * r, 0.005);
    vec2 lensedUv = uv * (1.0 + defl * 0.45);
    float tilt = 0.45;
    vec2 diskP = vec2(uv.x, (uv.y + defl * 0.22 * sign(uv.y)) / cos(tilt));
    float diskR = length(diskP);
    float diskPhi = atan(diskP.y, diskP.x);
    float rin = rs * 1.25;
    float rout = rs * 4.2;
    float inDisk = smoothstep(rin, rin + 0.06, diskR) * (1.0 - smoothstep(rout - 0.35, rout, diskR));
    float omega = pow(max(diskR, 0.1), -1.5) * 2.2;
    float spiral = sin(diskPhi * 3.0 - diskR * 14.0 + t * 3.0 - omega) * 0.5 + 0.5;
    float turb = noise(vec2(diskR * 6.0, diskPhi * 3.0 - t * 1.5)) * 0.4;
    float gas = inDisk * (0.6 + 0.4 * spiral + turb);
    float doppler = 1.0 - sin(diskPhi) * 0.48;
    gas *= pow(doppler, 2.5);
    float temp = clamp((rout - diskR) / (rout - rin), 0.0, 1.0) * doppler;
    vec3 colHot = vec3(0.6, 0.88, 1.0) * 2.8;
    vec3 colWarm = vec3(1.0, 0.68, 0.2) * 2.0;
    vec3 colCool = vec3(0.9, 0.16, 0.04) * 1.4;
    vec3 diskCol = mix(colCool, colWarm, smoothstep(0.0, 0.45, temp));
    diskCol = mix(diskCol, colHot, smoothstep(0.45, 1.0, temp));
    float photonRing = exp(-pow((r - rs * 1.35) * 35.0, 2.0)) * 2.4;
    float horizon = smoothstep(rs * 0.94, rs * 1.04, r);
    float halo = 0.025 / (r + 0.08);
    vec3 finalCol = (diskCol * gas + vec3(0.7, 0.88, 1.0) * photonRing + vec3(0.1, 0.3, 0.7) * halo * 0.3) * horizon;
    finalCol *= u_intensity;
    FragColor = vec4(finalCol, 0.90);
}`,

  pillars_of_creation: `#version 300 es
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
    for (int i = 0; i < 4; i++) { v += a * noise(p); p = rot * p * 2.1; a *= 0.5; }
    return v;
}
void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / min(u_resolution.x, u_resolution.y);
    float t = u_time * 0.06 * u_speed;
    float p1 = max(abs(uv.x + 0.28 + sin(uv.y * 3.0) * 0.04) - 0.20, uv.y - 0.45);
    float p2 = max(abs(uv.x - 0.04 + sin(uv.y * 2.5) * 0.03) - 0.16, uv.y - 0.30);
    float p3 = max(abs(uv.x - 0.35 - uv.y * 0.2) - 0.14, uv.y - 0.16);
    float baseDist = min(p1, min(p2, p3));
    float turb = fbm(uv * 4.5 + t * 0.1);
    float density = clamp((-baseDist + turb * 0.38) * 5.0, 0.0, 1.0);
    float rim = smoothstep(0.15, 0.45, density) * (1.0 - smoothstep(0.45, 0.85, density));
    vec3 dustCore = vec3(0.12, 0.06, 0.035);
    vec3 hAlpha = vec3(0.98, 0.62, 0.22) * 2.2;
    vec3 oiii = vec3(0.12, 0.82, 0.95) * 2.4;
    vec3 pillarCol = dustCore + hAlpha * rim + oiii * pow(rim, 2.2) * 1.5;
    vec3 bgCol = mix(vec3(0.015, 0.02, 0.05), vec3(0.04, 0.38, 0.62) * 0.6, fbm(uv * 2.5));
    vec3 finalCol = mix(bgCol, pillarCol, density) * u_intensity;
    FragColor = vec4(finalCol, 0.92);
}`
};

function compileShader(src, type) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    return s;
}

function setPreset(preset) {
    const fsSrc = SHADERS[preset] || SHADERS.black_hole;
    const vs = compileShader(VS_SOURCE, gl.VERTEX_SHADER);
    const fs = compileShader(fsSrc, gl.FRAGMENT_SHADER);
    if (!vs || !fs) return;

    const prog = gl.createProgram();
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);

    program = prog;
    activePreset = preset;
    uTime = gl.getUniformLocation(prog, "u_time");
    uRes = gl.getUniformLocation(prog, "u_resolution");
    uSpeed = gl.getUniformLocation(prog, "u_speed");
    uIntensity = gl.getUniformLocation(prog, "u_intensity");
    aPos = gl.getAttribLocation(prog, "a_pos");
}

function render(currentTime) {
    requestAnimationFrame(render);
    if (!gl || !program || activePreset === 'off') return;

    const now = currentTime || performance.now();
    if (now - lastRenderTime < fpsCapInterval) return;
    lastRenderTime = now;

    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.useProgram(program);
    gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer);
    gl.enableVertexAttribArray(aPos);
    gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

    const elapsed = (now - startTime) * 0.001;
    if (uTime) gl.uniform1f(uTime, elapsed);
    if (uRes) gl.uniform2f(uRes, canvas.width, canvas.height);
    if (uSpeed) gl.uniform1f(uSpeed, speed);
    if (uIntensity) gl.uniform1f(uIntensity, intensity);

    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
}

self.onmessage = function(e) {
    const data = e.data;
    if (data.type === 'INIT') {
        canvas = data.canvas;
        gl = canvas.getContext('webgl2', { antialias: false, depth: false, alpha: true }) ||
             canvas.getContext('webgl', { antialias: false, depth: false, alpha: true });
        quadBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
        setPreset(data.preset || 'black_hole');
        render();
    } else if (data.type === 'SET_PRESET') {
        setPreset(data.preset);
    } else if (data.type === 'RESIZE') {
        if (canvas) {
            canvas.width = data.width;
            canvas.height = data.height;
        }
    } else if (data.type === 'UPDATE_UNIFORMS') {
        if (data.speed !== undefined) speed = data.speed;
        if (data.intensity !== undefined) intensity = data.intensity;
    }
};
