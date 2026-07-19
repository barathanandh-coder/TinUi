#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

const command = process.argv[2];

if (command === 'init') {
    const targetDir = process.argv[3] || '.';
    const srcPath = path.join(targetDir, 'src');
    
    console.log(`[Info] Initializing fresh TinPyUI v1.3 project architecture...`);

    if (!fs.existsSync(srcPath)){
        fs.mkdirSync(srcPath, { recursive: true });
    }

    const publicPath = path.join(targetDir, 'public');
    if (!fs.existsSync(publicPath)){
        fs.mkdirSync(publicPath, { recursive: true });
    }

    const indexHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TinPyUI App</title>
    <script src="wasm_exec.js"></script>
    <script>
        const go = new Go();
        WebAssembly.instantiateStreaming(fetch("tinui_engine.wasm"), go.importObject).then((result) => {
            go.run(result.instance);
            
            // Start the TinUI engine with the generated Intermediate Representation
            const bootApp = () => {
                fetch("app.ir.json").then(res => res.text()).then(irString => {
                    try {
                        let ret = BootTinUI(irString);
                        if (ret) {
                            console.log(ret);
                        }

                        // Wire up global event listeners for TinUI interactivity
                        document.addEventListener('click', (e) => {
                            let actionElement = e.target.closest ? e.target.closest('[data-action]') : e.target;
                            if (actionElement) {
                                let action = actionElement.getAttribute('data-action');
                                if (action && typeof TinUIDispatch === 'function') {
                                    TinUIDispatch(action);
                                }
                            }
                        });

                        document.addEventListener('input', (e) => {
                            let stateKey = e.target.getAttribute('data-bind');
                            if (stateKey && typeof TinUIMutateState === 'function') {
                                TinUIMutateState(stateKey, e.target.value);
                            }
                        });
                    } catch(e) {
                        console.error("TinUI Boot Error:", e);
                        document.getElementById('tinui-root').innerHTML = "JS Error: " + e.message;
                    }
                }).catch(e => {
                    console.error("Failed to fetch app.ir.json:", e);
                    document.getElementById('tinui-root').innerHTML = "Failed to load app.ir.json";
                });
            };

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', bootApp);
            } else {
                bootApp();
            }
        }).catch((err) => {
            console.error("WASM Boot Error:", err);
            const displayErr = () => {
                document.getElementById('tinui-root').innerHTML = "<div style='padding: 20px; color: #ff5555;'>Failed to start WebAssembly engine: " + err.message + "<br><br><b>Note:</b> You cannot open this file directly in the browser. You MUST use a local web server (e.g. run <code>tinpyui serve</code> or start your Flask app).</div>";
            };
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', displayErr);
            } else {
                displayErr();
            }
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
    }

    // Default template showcasing correct pythonic indentation configuration
    const boilerplateTin = `component Main():
    AnimatedBackground(effect="cyber-wave", primaryColor="neon-purple", secondaryColor="neon-cyan"):
        
        Navbar(padding=20, blur=true):
            Row(align="center", justify="space-between", width="full"):
                Row(align="center", gap=10):
                    Text(text="TinPyUI NextGen", color="neon-cyan", weight="bold")
                
                Row(gap=30, color="white"):
                    NavLink(text="Learn")
                    NavLink(text="Reference")

        Section(align="center", paddingY=120, maxWidth=800, justify="center"):
            GradientText(text="TinPyUI", size="hero")
            Text(text="The framework for native WebAssembly user interfaces", size="large", color="white", weight="bold", marginTop=20)
`;

    fs.writeFileSync(path.join(srcPath, 'index.tin'), boilerplateTin);
    
    // Create base configuration mapping schema
    const configData = {
        name: path.basename(path.resolve(targetDir)),
        version: "1.0.0",
        compilerSettings: { entry: "src/index.tin", output: "public/app.ir.json" }
    };
    fs.writeFileSync(path.join(targetDir, 'tinpyui.config.json'), JSON.stringify(configData, null, 2));

    const appPyContent = `from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='public')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    print("[Info] Starting TinPyUI Flask Server on http://localhost:5000")
    app.run(debug=True, port=5000)
`;
    fs.writeFileSync(path.join(targetDir, 'app.py'), appPyContent);


    console.log(`[Success] Project scaffold complete! Run "tinpyui compile src/index.tin" to build.`);
    process.exit(0);
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
