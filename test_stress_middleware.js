const cp = require('child_process');
const path = require('path');
const fs = require('fs');

const middlewarePath = path.resolve(__dirname, 'vscode-tinpyui/dist/middleware.js');

let reqId = 1;
function createLspClient() {
    return cp.spawn('node', [middlewarePath, '--stdio']);
}

async function runTest() {
    console.log("Starting middleware stress test...");
    const client = createLspClient();
    
    let buffer = '';
    let responses = {};
    let diagnosticsCount = 0;
    
    client.stdout.on('data', data => {
        buffer += data.toString();
        while (true) {
            const match = buffer.match(/Content-Length: (\d+)\r\n\r\n/);
            if (!match) break;
            const contentLength = parseInt(match[1], 10);
            const headerLength = match[0].length;
            if (buffer.length < headerLength + contentLength) break;
            
            const bodyStr = buffer.slice(headerLength, headerLength + contentLength);
            buffer = buffer.slice(headerLength + contentLength);
            
            const response = JSON.parse(bodyStr);
            if (response.method === 'window/logMessage') {
                console.log(`[LSP Log] ${response.params.message}`);
            }
            if (response.id) responses[response.id] = response;
            if (response.method === 'textDocument/publishDiagnostics') diagnosticsCount++;
        }
    });

    const sendReq = (method, params) => {
        const id = reqId++;
        const msg = JSON.stringify({ jsonrpc: "2.0", id, method, params });
        client.stdin.write(`Content-Length: ${msg.length}\r\n\r\n${msg}`);
        return id;
    };

    const sendNotif = (method, params) => {
        const msg = JSON.stringify({ jsonrpc: "2.0", method, params });
        client.stdin.write(`Content-Length: ${msg.length}\r\n\r\n${msg}`);
    };

    // 1. Initialize
    sendReq('initialize', {
        processId: process.pid,
        rootUri: `file://${process.cwd().replace(/\\/g, '/')}`,
        capabilities: {}
    });
    sendNotif('initialized', {});
    
    // 2. Open 50 documents
    console.log("Opening 50 documents...");
    for (let i = 0; i < 50; i++) {
        sendNotif('textDocument/didOpen', {
            textDocument: { uri: `file:///project/doc${i}.tin`, languageId: 'tin', version: 1, text: `component Main():\n    Text(text="Doc ${i}")` }
        });
    }
    
    await new Promise(r => setTimeout(r, 2000));
    
    // 3. Trigger a restart storm
    console.log("Triggering 6 rapid crashes to test restart storm protection...");
    const pids = [];
    // We can't kill tinui directly if we don't know the PID, but we can send an invalid request that forces a crash?
    // Actually, tinui.exe crashes are handled. Let's just find tinui.exe processes and kill them.
    for (let i = 0; i < 6; i++) {
        try {
            if (process.platform === 'win32') {
                cp.execSync('taskkill /F /IM tinui.exe /T 2>nul');
            } else {
                cp.execSync('killall -9 tinui');
            }
        } catch(e) {}
        await new Promise(r => setTimeout(r, 500));
    }
    
    await new Promise(r => setTimeout(r, 2000));
    console.log("Restart storm test complete.");
    
    sendReq('shutdown', {});
    sendNotif('exit', {});
    
    setTimeout(() => {
        console.log(`Diagnostics received: ${diagnosticsCount}`);
        client.kill();
        process.exit(0);
    }, 1000);
}

runTest().catch(console.error);
