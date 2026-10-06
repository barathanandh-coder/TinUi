package agent

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"sync"
)

var (
	outputMutex sync.Mutex
	cancelMap   = make(map[interface{}]context.CancelFunc)
	cancelMutex sync.Mutex
)

// RunAgent is the entry point for `tinui agent` subcommand
func RunAgent(args []string) {
	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		line := scanner.Text()
		if line == "" {
			continue
		}

		var req RequestEnvelope
		if err := json.Unmarshal([]byte(line), &req); err != nil {
			sendError(nil, -32700, "Parse error")
			continue
		}

		if req.JSONRPC != "2.0" {
			sendError(req.ID, -32600, "Invalid Request: missing or invalid jsonrpc version")
			continue
		}

		if req.Method == "$/cancelRequest" {
			handleCancel(req)
			continue
		}

		// Dispatch request
		dispatchRequest(req)
	}
	
	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "tinui agent stdin error: %v\n", err)
	}
}

func handleCancel(req RequestEnvelope) {
	var params CancelParams
	if req.Params != nil {
		json.Unmarshal(req.Params, &params)
	}
	
	cancelMutex.Lock()
	if cancelFunc, exists := cancelMap[params.ID]; exists {
		cancelFunc()
		delete(cancelMap, params.ID)
	}
	cancelMutex.Unlock()
}

func recoverRequest(reqID interface{}) {
	if r := recover(); r != nil {
		fmt.Fprintf(os.Stderr, "[Panic Recovery] Request %v panicked: %v\n", reqID, r)
		sendError(reqID, -32603, "Internal error during request processing")
	}
}

func runSyncHandler(req RequestEnvelope, handler func(RequestEnvelope)) {
	defer recoverRequest(req.ID)
	handler(req)
}

func dispatchRequest(req RequestEnvelope) {
	switch req.Method {
	case "initialize":
		runSyncHandler(req, handleInitialize)
	case "update_document":
		runSyncHandler(req, handleUpdateDocument)
	case "close_document":
		runSyncHandler(req, handleCloseDocument)
	case "shutdown":
		os.Exit(0)
	case "context.project", "context.file", "context.symbol", "context.references", 
		"context.dependents", "context.imports", "context.unresolved",
		"context.impact", "context.architecture", "context.dependencies", 
		"context.related", "context.search", "context.propose", "context.apply":
		go func() {
			defer recoverRequest(req.ID)
			handleAIContextRequest(req)
		}()
	case "context", "schema", "graph":
		// Legacy small sync operations
		go func() {
			defer recoverRequest(req.ID)
			handleSyncRequest(req)
		}()
	case "check", "build", "query":
		// Cancellable operations
		ctx, cancel := context.WithCancel(context.Background())
		cancelMutex.Lock()
		cancelMap[req.ID] = cancel
		cancelMutex.Unlock()

		go func(req RequestEnvelope, ctx context.Context) {
			defer recoverRequest(req.ID)
			defer func() {
				cancelMutex.Lock()
				delete(cancelMap, req.ID)
				cancelMutex.Unlock()
			}()

			switch req.Method {
			case "check":
				handleCheck(ctx, req)
			case "build":
				handleBuild(ctx, req)
			case "query":
				handleQuery(ctx, req)
			}
		}(req, ctx)
	default:
		sendError(req.ID, -32601, "Method not found")
	}
}

func handleSyncRequest(req RequestEnvelope) {
	switch req.Method {
	case "context":
		handleContext(req)
	case "schema":
		handleSchema(req)
	case "graph":
		handleGraph(req)
	}
}

func sendResult(id interface{}, result interface{}) {
	res := ResponseEnvelope{
		JSONRPC: "2.0",
		ID:      id,
		Result:  result,
	}
	emitResponse(res)
}

func sendError(id interface{}, code int, message string) {
	res := ResponseEnvelope{
		JSONRPC: "2.0",
		ID:      id,
		Error: &ProtocolError{
			Code:    code,
			Message: message,
		},
	}
	emitResponse(res)
}

var emitResponse = func(res ResponseEnvelope) {
	out, err := json.Marshal(res)
	if err != nil {
		fmt.Fprintf(os.Stderr, "tinui agent output error: %v\n", err)
		return
	}
	outputMutex.Lock()
	fmt.Fprintln(os.Stdout, string(out))
	outputMutex.Unlock()
}

