#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');
const os = require('os');

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
