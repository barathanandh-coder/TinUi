#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');
const os = require('os');
const fs = require('fs');

const command = process.argv[2];

if (command === 'init') {
    const targetDir = process.argv[3] || '.';
    const srcPath = path.join(targetDir, 'src');
    
    console.log(`🚀 Initializing fresh TinPyUI v1.3 project architecture...`);

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
        });
    </script>
</head>
<body style="margin: 0; padding: 0; background-color: #0a0b10; color: #ffffff; font-family: 'Inter', sans-serif;">
    <div id="app"></div>
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

    console.log(`✅ Project scaffold complete! Run "tinpyui compile src/index.tin" to build.`);
    process.exit(0);
}



if (command === 'serve') {
    const http = require('http');
    const targetDir = process.argv[3] || '.';
    const publicDir = path.join(targetDir, 'public');

    if (!fs.existsSync(publicDir)) {
        console.error('❌ Could not find "public" directory. Have you run "tinpyui init"?');
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
        console.log('🚀 TinPyUI Dev Server running at http://localhost:3000/');
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
