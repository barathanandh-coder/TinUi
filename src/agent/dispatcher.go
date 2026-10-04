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

func dispatchRequest(req RequestEnvelope) {
	switch req.Method {
	case "initialize":
		handleInitialize(req)
	case "update_document":
		handleUpdateDocument(req)
	case "close_document":
		handleCloseDocument(req)
	case "shutdown":
		os.Exit(0)
	case "context", "schema", "graph":
		// Small sync operations
		go handleSyncRequest(req)
	case "check", "build", "query":
		// Cancellable operations
		ctx, cancel := context.WithCancel(context.Background())
		cancelMutex.Lock()
		cancelMap[req.ID] = cancel
		cancelMutex.Unlock()

		go func(req RequestEnvelope, ctx context.Context) {
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

func emitResponse(res ResponseEnvelope) {
	out, err := json.Marshal(res)
	if err != nil {
		fmt.Fprintf(os.Stderr, "tinui agent output error: %v\n", err)
		return
	}
	outputMutex.Lock()
	fmt.Fprintln(os.Stdout, string(out))
	outputMutex.Unlock()
}
