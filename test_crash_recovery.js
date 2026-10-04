const { spawn } = require('child_process');
const path = require('path');

const middleware = spawn('node', [path.join(__dirname, 'vscode-tinpyui', 'dist', 'middleware.js'), '--stdio']);

let messageId = 1;
function sendNotification(method, params) {
    const msg = {
        jsonrpc: '2.0',
        method,
        params
    };
    const body = JSON.stringify(msg);
    const payload = `Content-Length: ${Buffer.byteLength(body, 'utf8')}\r\n\r\n${body}`;
    middleware.stdin.write(payload);
}

let buffer = '';
let diagnosticsCount = 0;
let crashDetected = false;

middleware.stdout.on('data', (data) => {
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
        console.log(`[LSP Client] Received:`, JSON.stringify(response, null, 2));

        if (response.method === 'textDocument/publishDiagnostics') {
            diagnosticsCount++;
            console.log(`[LSP Client] Diagnostics received for version: ${response.params.uri} (Count: ${diagnosticsCount})`);
            
            if (diagnosticsCount === 1) {
                console.log("[LSP Client] Test: Killing Go agent to simulate crash...");
                // Note: We need a way to kill the Go agent from the outside, or we can just find it
                // We'll use a hack to kill it by sending a malformed shutdown or just rely on child_process in JS to kill tinui.exe
                spawn('taskkill', ['/F', '/IM', 'tinui.exe']);
            }
            if (diagnosticsCount === 2) {
                console.log("[LSP Client] Test: Recovery successful! Diagnostics received again after restart.");
                sendNotification('exit');
            }
        }
    }
});

middleware.stderr.on('data', (data) => {
    console.log(`[LSP Middleware STDERR] ${data}`);
    if (data.includes("Agent crashed") || data.includes("Reconnecting")) {
        crashDetected = true;
        console.log("[LSP Client] Detected crash logged by middleware!");
    }
});

middleware.on('close', (code) => {
    console.log(`LSP Middleware exited with code ${code}`);
    if (diagnosticsCount >= 2 && crashDetected) {
        console.log("Phase 4.2D Crash Recovery Test: PASSED");
        process.exit(0);
    } else {
        console.log("Phase 4.2D Crash Recovery Test: FAILED");
        process.exit(1);
    }
});

// Start testing sequence
sendNotification('initialize', {
    processId: process.pid,
    rootUri: null,
    capabilities: {}
});

setTimeout(() => {
    sendNotification('initialized', {});
    
    // Open document
    sendNotification('textDocument/didOpen', {
        textDocument: { uri: 'file:///project/test.tin', languageId: 'tin', version: 1, text: "" }
    });
    setTimeout(() => {
        sendNotification('textDocument/didChange', {
            textDocument: { uri: 'file:///project/test.tin', version: 2 },
            contentChanges: [{text: "component Main():\n    Text(text=\"Hello\")"}]
        });
    }, 500);
}, 500);

setTimeout(() => {
    // If we reach 5 seconds and haven't exited, we failed
    console.error("Test timed out!");
    process.exit(1);
}, 10000);
