const { spawn } = require('child_process');
const path = require('path');

const middleware = spawn('node', [path.join(__dirname, 'vscode-tinpyui', 'dist', 'middleware.js'), '--stdio']);

let messageId = 1;
function sendMessage(method, params) {
    const msg = {
        jsonrpc: '2.0',
        id: messageId++,
        method,
        params
    };
    const body = JSON.stringify(msg);
    const payload = `Content-Length: ${Buffer.byteLength(body, 'utf8')}\r\n\r\n${body}`;
    middleware.stdin.write(payload);
}

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
            console.log("Diagnostics received!");
            
            // Hover
            sendMessage('textDocument/hover', {
                textDocument: { uri: 'file:///project/test.tin' },
                position: { line: 1, character: 4 }
            });
        }
        
        if (response.id === 2) {
            // Hover response
            console.log("Hover response received!");
            
            // Completion
            sendMessage('textDocument/completion', {
                textDocument: { uri: 'file:///project/test.tin' },
                position: { line: 1, character: 4 }
            });
        }

        if (response.id === 3) {
            // Completion response
            console.log("Completion response received!");
            
            // Definition
            sendMessage('textDocument/definition', {
                textDocument: { uri: 'file:///project/test.tin' },
                position: { line: 1, character: 4 }
            });
        }

        if (response.id === 4) {
            // Definition response
            console.log("Definition response received!");
            
            // Code action
            sendMessage('textDocument/codeAction', {
                textDocument: { uri: 'file:///project/test.tin' },
                range: { start: { line: 1, character: 4 }, end: { line: 1, character: 4 } },
                context: { diagnostics: [] }
            });
        }

        if (response.id === 5) {
            console.log("Code action response received!");
            
            // Exit
            sendNotification('exit');
        }
    }
});

middleware.stderr.on('data', (data) => {
    console.error(`[LSP Server Error] ${data}`);
});

middleware.on('close', (code) => {
    console.log(`LSP Middleware exited with code ${code}`);
    process.exit(code);
});

// Start testing sequence
sendMessage('initialize', {
    processId: process.pid,
    rootUri: null,
    capabilities: {}
});

setTimeout(() => {
    sendNotification('initialized', {});
    
    // Open & Update
    sendNotification('textDocument/didChange', {
        textDocument: { uri: 'file:///project/test.tin', version: 1 },
        contentChanges: [{ text: "component Main():\n    Text(text=\"Hello\")" }]
    });
}, 500);
