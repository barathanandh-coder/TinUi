#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

const command = process.argv[2];

if (command === 'init' || command === 'create' || command === 'new') {
    const readline = require('readline');
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    const ask = (query) => new Promise(resolve => rl.question(query, resolve));

    (async () => {
        console.log(`\n\x1b[1;36m+==============================================================================+\x1b[0m`);
        console.log(`\x1b[1;36m|   \x1b[1;97m[*] TinPyUI v1.7.1 Project Scaffolding Wizard\x1b[1;36m                              |\x1b[0m`);
        console.log(`\x1b[1;36m+==============================================================================+\x1b[0m\n`);

        let targetDirArg = process.argv[3] || '';
        let targetDir = targetDirArg.trim();
        if (!targetDir) {
            targetDir = await ask('\x1b[1;36m>> Enter project name/directory \x1b[1;97m[default: my-cyber-app]\x1b[0m: \x1b[1;33m');
            process.stdout.write('\x1b[0m');
            targetDir = targetDir.trim() || 'my-cyber-app';
        }

        console.log(`\n\x1b[1;97mSelect target device architecture for your project:\x1b[0m`);
        console.log(`  \x1b[1;36m[1]\x1b[0m \x1b[1;97m🌐 Universal Omni-Platform\x1b[0m  \x1b[0;36m(All Devices: Android Mobile + iOS Mobile + Tablet + Web WASM)\x1b[0m`);
        console.log(`  \x1b[1;32m[2]\x1b[0m \x1b[1;97m💻 Native Desktop Specified\x1b[0m \x1b[0;32m(Windows / macOS / Linux C-FFI Vector Surface)\x1b[0m`);
        console.log(`  \x1b[1;94m[3]\x1b[0m \x1b[1;97m📱 Mobile Touch Specified\x1b[0m   \x1b[0;94m(Android & iOS Touch-First with Haptics)\x1b[0m`);
        console.log(`  \x1b[1;35m[4]\x1b[0m \x1b[1;97m📱 Tablet / iPad Specified\x1b[0m  \x1b[0;35m(Adaptive Dual-Column Split View)\x1b[0m`);
        console.log(`  \x1b[1;33m[5]\x1b[0m \x1b[1;97m🌐 WebAssembly Specified\x1b[0m   \x1b[0;33m(Zero-DOM WebGL / WebGPU Browser App)\x1b[0m\n`);

        let devChoice = await ask('\x1b[1;36m>> Select device mode \x1b[1;97m(1-5)\x1b[0m \x1b[90m[default: 1]\x1b[0m: \x1b[1;33m');
        process.stdout.write('\x1b[0m');
        devChoice = devChoice.trim() || '1';

        const devMap = {
            '1': { title: 'Universal (Mobile + Tablet + Web WASM)', slug: 'universal' },
            '2': { title: 'Native Desktop Specified', slug: 'desktop' },
            '3': { title: 'Mobile Touch Specified', slug: 'mobile' },
            '4': { title: 'Tablet / iPad Specified', slug: 'tablet' },
            '5': { title: 'WebAssembly Specified', slug: 'web' }
        };
        const selected = devMap[devChoice] || devMap['1'];

        const resolvedPath = path.resolve(targetDir);
        console.log(`\n\x1b[1;97mReady to scaffold:\x1b[0m`);
        console.log(`  • Target Directory:  \x1b[1;36m${resolvedPath}\x1b[0m`);
        console.log(`  • Device Target:     \x1b[1;32m${selected.title}\x1b[0m`);

        const confirm = await ask('\n\x1b[1;36m>> Proceed with creating project? \x1b[1;97m(Y/n)\x1b[0m \x1b[90m[default: Y]\x1b[0m: \x1b[1;33m');
        process.stdout.write('\x1b[0m');
        rl.close();

        if (confirm.trim() && !['y', 'yes'].includes(confirm.trim().toLowerCase())) {
            console.log(`\n\x1b[1;33m[!] Project creation aborted by user.\x1b[0m\n`);
            process.exit(0);
        }

        console.log(`\n\x1b[1;32m[+] Initializing fresh TinPyUI v1.6.1 project architecture in: ${targetDir}...\x1b[0m`);

        const srcPath = path.join(targetDir, 'src');
        if (!fs.existsSync(srcPath)){
            fs.mkdirSync(srcPath, { recursive: true });
        }

        const publicPath = path.join(targetDir, 'public');
        if (!fs.existsSync(publicPath)){
            fs.mkdirSync(publicPath, { recursive: true });
        }

        const databasePath = path.join(targetDir, 'database');
        if (!fs.existsSync(databasePath)){
            fs.mkdirSync(databasePath, { recursive: true });
        }

        const backendPath = path.join(targetDir, 'backend');
        if (!fs.existsSync(backendPath)){
            fs.mkdirSync(backendPath, { recursive: true });
        }

        const indexHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${path.basename(resolvedPath)} — ${selected.title}</title>
    <script src="wasm_exec.js"></script>
    <script>
        const go = new Go();
        const _wasmSources = ["tinui_engine.wasm", "app.wasm", "/tinui_engine.wasm", "/app.wasm"];
        let _wasmPromise = null;
        for (const src of _wasmSources) {
            if (!_wasmPromise) {
                _wasmPromise = fetch(src).then(res => {
                    if (!res.ok) throw new Error("Status " + res.status);
                    return res;
                });
            } else {
                _wasmPromise = _wasmPromise.catch(() => fetch(src).then(res => {
                    if (!res.ok) throw new Error("Status " + res.status);
                    return res;
                }));
            }
        }

        _wasmPromise.then(res => WebAssembly.instantiateStreaming(res, go.importObject)).then((result) => {
            go.run(result.instance);
            const bootApp = () => {
                fetch("app.ir.json").then(res => res.text()).then(irString => {
                    try {
                        let ret = BootTinUI(irString);
                        if (ret) console.log(ret);
                    } catch(e) {
                        console.error("TinUI Boot Error:", e);
                    }
                }).catch(e => {
                    console.error("Failed to fetch app.ir.json:", e);
                });
            };
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', bootApp);
            } else {
                bootApp();
            }
        }).catch((err) => {
            console.error("WASM Boot Error:", err);
        });
    </script>
</head>
<body style="margin: 0; padding: 0; background-color: #0a0b10; color: #ffffff; font-family: 'Inter', sans-serif;">
    <div id="tinui-root"></div>
</body>
</html>`;
        fs.writeFileSync(path.join(publicPath, 'index.html'), indexHtml);

        // Copy wasm bootloader files
        const binDir = path.join(__dirname, 'bin');
        if (fs.existsSync(path.join(binDir, 'wasm_exec.js'))) {
            fs.copyFileSync(path.join(binDir, 'wasm_exec.js'), path.join(publicPath, 'wasm_exec.js'));
        }
        if (fs.existsSync(path.join(binDir, 'tinui_engine.wasm'))) {
            fs.copyFileSync(path.join(binDir, 'tinui_engine.wasm'), path.join(publicPath, 'tinui_engine.wasm'));
            fs.copyFileSync(path.join(binDir, 'tinui_engine.wasm'), path.join(publicPath, 'app.wasm'));
        }

        const boilerplateTin = `component Main():
    AnimatedBackground(effect="cyber-wave", primaryColor="neon-purple", secondaryColor="neon-cyan"):
        Navbar(padding=20, blur=true):
            Row(align="center", justify="space-between", width="full"):
                Row(align="center", gap=10):
                    Text(text="${path.basename(resolvedPath)} (${selected.title})", color="neon-cyan", weight="bold")
                
                Row(gap=30, color="white"):
                    NavLink(text="Dashboard", href="/")
                    NavLink(text="Documentation", href="/docs")

        Section(align="center", paddingY=80, maxWidth=800, justify="center"):
            GradientText(text="${path.basename(resolvedPath)}", size="hero")
            Text(text="Target: ${selected.title}", size="large", color="white", weight="bold", marginTop=20)
            Text(text="Native Hardware-Accelerated Pythonic UI Engine", color="muted", marginTop=10)
`;
        fs.writeFileSync(path.join(srcPath, 'index.tin'), boilerplateTin);
        fs.writeFileSync(path.join(targetDir, 'main.tin'), boilerplateTin);
        
        const configData = {
            name: path.basename(resolvedPath),
            version: "1.0.0",
            targetDevice: selected.slug,
            compilerSettings: { entry: "src/index.tin", output: "public/app.ir.json" }
        };
        fs.writeFileSync(path.join(targetDir, 'tinpyui.config.json'), JSON.stringify(configData, null, 2));

        const mainPy = `import tinpyui as tin

class App(tin.App):
    def __init__(self):
        super().__init__(title="${path.basename(resolvedPath)} — ${selected.title}", width=1280, height=820)
        self.count = tin.Signal(0)

    def build(self):
        with tin.LayoutWindow(title="${path.basename(resolvedPath)}") as root:
            with tin.Column(width="full", padding=24, gap=16):
                tin.GradientText("🚀 ${path.basename(resolvedPath)}", gradient=["neon-cyan", "neon-purple"], size="hero")
                tin.Badge("Target: ${selected.title}", variant="neon-cyan")
                tin.Text(text=lambda: f"Reactive Counter: {self.count.value}", color="white")
                with tin.Row(gap=12):
                    tin.Button("Increment Counter", on_click=lambda: self.count.set(self.count.value + 1))
                    tin.Button("📳 Haptic Pulse", on_click=lambda: tin.haptics.vibrate(60))
        return root

if __name__ == "__main__":
    app = App()
    app.run(prompt_target=True)
`;
        fs.writeFileSync(path.join(targetDir, 'main.py'), mainPy);

        fs.writeFileSync(path.join(databasePath, '.gitkeep'), '');
        fs.writeFileSync(path.join(backendPath, '.gitkeep'), '');

        console.log(`\n\x1b[1;32m✔ [TinPyUI Scaffold] Successfully created project '${path.basename(resolvedPath)}'!\x1b[0m\n`);
        console.log(`\x1b[1;97mNext steps:\x1b[0m`);
        console.log(`  \x1b[1;36mcd ${targetDir}\x1b[0m`);
        console.log(`  \x1b[1;36mpython main.py\x1b[0m      \x1b[90m# Run multi-device interactive launcher\x1b[0m`);
        console.log(`  \x1b[1;36mtinpyui serve\x1b[0m       \x1b[90m# Start local web dev server\x1b[0m\n`);
        process.exit(0);
    })();
    return;
}



if (command === 'serve') {
    const http = require('http');
    const targetDir = process.argv[3] || '.';
    const publicDir = path.join(targetDir, 'public');

    if (!fs.existsSync(publicDir)) {
        console.error('[Error] Could not find "public" directory. Have you run "tinpyui init"?');
        process.exit(1);
    }

    http.createServer((req, res) => {
        let filePath = path.join(publicDir, req.url === '/' ? 'index.html' : req.url);
        let extname = path.extname(filePath);
        let contentType = 'text/html';
        switch (extname) {
            case '.js': contentType = 'text/javascript'; break;
            case '.wasm': contentType = 'application/wasm'; break;
            case '.json': contentType = 'application/json'; break;
        }

        fs.readFile(filePath, (error, content) => {
            if (error) {
                if (error.code == 'ENOENT') {
                    res.writeHead(404);
                    res.end('File not found');
                } else {
                    res.writeHead(500);
                    res.end('Server Error: ' + error.code);
                }
            } else {
                res.writeHead(200, { 'Content-Type': contentType });
                res.end(content, 'utf-8');
            }
        });
    }).listen(3000, () => {
        console.log('[Info] TinPyUI Dev Server running at http://localhost:3000/');
    });
    return;
}

// 1. Identify the user's operating system
const platform = os.platform();
let binaryName = 'tinui-linux'; // Default to Linux

if (platform === 'win32') {
    binaryName = 'tinui-win.exe';
} else if (platform === 'darwin') {
    binaryName = 'tinui-macos';
}

// 2. Locate the correct Go binary in the bin/ folder
const binPath = path.join(__dirname, 'bin', binaryName);

// 3. Grab the commands the user typed (e.g., 'compile app.tin')
const args = process.argv.slice(2);

// 4. Execute the Go binary and pass the output directly back to the terminal
const result = spawnSync(binPath, args, { stdio: 'inherit' });

// Ensure the Node script exits with the same status code as the Go binary
process.exit(result.status);
