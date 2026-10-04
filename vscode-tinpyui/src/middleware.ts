import {
    createConnection,
    TextDocuments,
    Diagnostic,
    DiagnosticSeverity,
    ProposedFeatures,
    InitializeParams,
    DidChangeConfigurationNotification,
    CompletionItem,
    CompletionItemKind,
    TextDocumentPositionParams,
    TextDocumentSyncKind,
    InitializeResult,
    Hover,
    Definition,
    Location,
    Range,
    Position,
    CodeAction,
    CodeActionKind,
    CodeActionParams
} from 'vscode-languageserver/node';

import {
    TextDocument
} from 'vscode-languageserver-textdocument';

import * as child_process from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

const connection = createConnection(ProposedFeatures.all);
const documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument);

let agentProcess: child_process.ChildProcessWithoutNullStreams;
let requestCounter = 1;
let isShuttingDown = false;
let isRecovering = false;
let restartCount = 0;
let lastRestart = Date.now();

// Callbacks for JSON-RPC pending requests
const pendingRequests = new Map<number, (result: any, err: any) => void>();
const requestQueue: {method: string, params: any, resolve: any, reject: any}[] = [];

async function validateTextDocument(doc: TextDocument) {
    try {
        const checkResult = await sendAgentRequest('check', {
            uri: doc.uri,
            source: doc.getText(),
            version: doc.version
        });
        
        let lspDiagnostics: Diagnostic[] = [];
        if (checkResult && checkResult.diagnostics) {
            lspDiagnostics = checkResult.diagnostics.map((d: any) => {
                let severity: DiagnosticSeverity = DiagnosticSeverity.Error;
                if (d.severity === 'warning') severity = DiagnosticSeverity.Warning;
                if (d.severity === 'info') severity = DiagnosticSeverity.Information;
                if (d.severity === 'hint') severity = DiagnosticSeverity.Hint;
                
                let diag: Diagnostic = {
                    severity,
                    range: {
                        start: { line: d.line, character: d.column },
                        end: { line: d.line, character: d.column + 1 }
                    },
                    message: `[${d.error_code}] ${d.message}`,
                    source: 'tinpyui'
                };

                if (d.repair_suggestion) {
                    diag.data = d.repair_suggestion;
                }
                return diag;
            });
        }
        
        connection.sendDiagnostics({ uri: doc.uri, diagnostics: lspDiagnostics });
    } catch(e) {
        connection.console.error(`Validation failed for ${doc.uri}: ${e}`);
    }
}

function startAgent() {
    // Assuming tinui.exe is in the workspace root or PATH
    // For this implementation, we assume it's in the parent directory
    const agentPath = path.resolve(__dirname, '../../tinui.exe');
    
    agentProcess = child_process.spawn(agentPath, ['agent']);
    
    agentProcess.on('error', (err) => {
        connection.console.error(`Failed to spawn agent: ${err}`);
    });

    let buffer = '';
    agentProcess.stdout.on('data', (data) => {
        buffer += data.toString();
        let newlineIndex = buffer.indexOf('\n');
        while (newlineIndex >= 0) {
            const line = buffer.slice(0, newlineIndex);
            buffer = buffer.slice(newlineIndex + 1);
            newlineIndex = buffer.indexOf('\n');

            if (line.trim().length === 0) continue;

            try {
                const response = JSON.parse(line);
                if (response.id && pendingRequests.has(response.id)) {
                    const callback = pendingRequests.get(response.id);
                    pendingRequests.delete(response.id);
                    if (callback) {
                        callback(response.result, response.error);
                    }
                }
            } catch (e) {
                connection.console.error(`Error parsing agent response: ${e}`);
            }
        }
    });

    agentProcess.stderr.on('data', (data) => {
        connection.console.error(`Agent STDERR: ${data}`);
    });

    agentProcess.on('exit', async (code) => {
        if (isShuttingDown) return;
        connection.console.error(`Agent crashed with code ${code}. Reconnecting...`);
        
        if (Date.now() - lastRestart > 10000) restartCount = 0;
        if (restartCount >= 5) {
            connection.console.error("Agent restart storm detected. Giving up.");
            return;
        }
        
        restartCount++;
        lastRestart = Date.now();
        isRecovering = true;
        
        // Reject all currently pending JSON-RPC requests
        for (const [id, callback] of pendingRequests.entries()) {
            callback(null, {code: -32001, message: "Agent crashed"});
        }
        pendingRequests.clear();
        
        // Restart agent process
        startAgent();
        
        // Re-initialize
        try {
            await sendAgentRequest('initialize', {});
            
            // Replay VFS
            for (const doc of documents.all()) {
                await sendAgentRequest('update_document', {
                    uri: doc.uri,
                    source: doc.getText(),
                    version: doc.version
                });
                validateTextDocument(doc);
            }
            
            // Flush queued requests
            isRecovering = false;
            for (const item of requestQueue) {
                sendAgentRequest(item.method, item.params).then(item.resolve).catch(item.reject);
            }
            requestQueue.length = 0;
            
        } catch(e) {
            connection.console.error("Recovery failed: " + e);
        }
    });
}

function sendAgentRequest(method: string, params?: any): Promise<any> {
    return new Promise((resolve, reject) => {
        if (isRecovering) {
            requestQueue.push({method, params, resolve, reject});
            return;
        }
        
        const id = requestCounter++;
        pendingRequests.set(id, (result, err) => {
            if (err) reject(err);
            else resolve(result);
        });

        const req = {
            jsonrpc: '2.0',
            id,
            method,
            params
        };

        if (agentProcess) {
            try {
                agentProcess.stdin.write(JSON.stringify(req) + '\n');
            } catch (e) {
                reject(new Error(`Failed to write to agent process: ${e}`));
            }
        } else {
            reject(new Error("Agent process not running"));
        }
    });
}

connection.onInitialize(async (params: InitializeParams) => {
    startAgent();
    
    // Handshake
    try {
        await sendAgentRequest('initialize');
    } catch(e) {
        connection.console.error("Agent initialize failed: " + e);
    }

    const result: InitializeResult = {
        capabilities: {
            textDocumentSync: TextDocumentSyncKind.Full,
            completionProvider: {
                resolveProvider: false
            },
            hoverProvider: true,
            definitionProvider: true,
            codeActionProvider: true
        }
    };
    return result;
});

connection.onInitialized(() => {
    connection.console.log("TinPyUI LSP Middleware started.");
});

documents.onDidChangeContent(async change => {
    // 10. Document synchronization & 1. Virtual-document lifecycle
    const doc = change.document;
    try {
        await sendAgentRequest('update_document', {
            uri: doc.uri,
            source: doc.getText(),
            version: doc.version
        });

        // 5. Diagnostics
        validateTextDocument(doc);
    } catch (e) {
        connection.console.error(`Sync error: ${e}`);
    }
});

documents.onDidClose(async e => {
    await sendAgentRequest('close_document', {
        uri: e.document.uri
    });
});

connection.onHover(async (params: TextDocumentPositionParams): Promise<Hover | null> => {
    const doc = documents.get(params.textDocument.uri);
    if (!doc) return null;

    try {
        const res = await sendAgentRequest('query', {
            kind: 'hover',
            document: doc.uri,
            position: params.position,
            version: doc.version
        });

        if (res && res.contents) {
            return {
                contents: res.contents,
                range: res.range
            };
        }
    } catch (e) {
        connection.console.error(`Hover error: ${JSON.stringify(e)}`);
    }
    return null;
});

connection.onDefinition(async (params: TextDocumentPositionParams): Promise<Definition | null> => {
    const doc = documents.get(params.textDocument.uri);
    if (!doc) return null;

    try {
        const res = await sendAgentRequest('query', {
            kind: 'definition',
            document: doc.uri,
            position: params.position,
            version: doc.version
        });

        if (res && res.uri && res.range) {
            return Location.create(res.uri, res.range);
        }
    } catch(e) {
        connection.console.error(`Definition error: ${JSON.stringify(e)}`);
    }
    return null;
});

connection.onCompletion(async (params: TextDocumentPositionParams): Promise<CompletionItem[]> => {
    const doc = documents.get(params.textDocument.uri);
    if (!doc) return [];

    try {
        const res = await sendAgentRequest('query', {
            kind: 'completion',
            document: doc.uri,
            position: params.position,
            version: doc.version
        });

        if (res && res.items) {
            return res.items.map((i: any) => {
                let kind: CompletionItemKind = CompletionItemKind.Text;
                if (i.kind === 'keyword') kind = CompletionItemKind.Keyword;
                if (i.kind === 'component') kind = CompletionItemKind.Class;
                if (i.kind === 'property') kind = CompletionItemKind.Property;

                return {
                    label: i.label,
                    kind,
                    detail: i.detail,
                    documentation: i.documentation
                };
            });
        }
    } catch(e) {
        connection.console.error(`Completion error: ${JSON.stringify(e)}`);
    }
    return [];
});

connection.onCodeAction((params: CodeActionParams): CodeAction[] => {
    const codeActions: CodeAction[] = [];
    
    for (const diag of params.context.diagnostics) {
        if (diag.data) {
            const repair = diag.data as any; // RepairSuggestion from TinPyUI
            if (repair.description && repair.edits) {
                const action: CodeAction = {
                    title: repair.description,
                    kind: CodeActionKind.QuickFix,
                    diagnostics: [diag],
                    isPreferred: repair.is_deterministic,
                    edit: {
                        changes: {
                            [params.textDocument.uri]: repair.edits
                        }
                    }
                };
                codeActions.push(action);
            }
        }
    }
    
    return codeActions;
});

documents.listen(connection);
connection.listen();

connection.onShutdown(async () => {
    isShuttingDown = true;
    if (agentProcess) {
        try {
            await sendAgentRequest('shutdown');
        } catch (e) {}
    }
});

connection.onExit(() => {
    if (agentProcess) {
        agentProcess.kill();
    }
    process.exit(0);
});
