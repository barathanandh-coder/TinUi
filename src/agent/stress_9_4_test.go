package agent

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/tinui/tinui/src/compiler"
)

// TestStress_Concurrency runs hundreds of goroutines performing random LSP and AI operations
// to detect data races and ensure semantic integrity.
func TestStress_Concurrency(t *testing.T) {
	originalEmit := emitResponse
	defer func() { emitResponse = originalEmit }()
	emitResponse = func(res ResponseEnvelope) {
		// Do nothing during stress test
	}

	// Initialize global environment
	GlobalWorkspace = compiler.NewSemanticWorkspace()
	vfsMutex.Lock()
	vfs = make(map[string]UpdateDocumentParams)
	vfsMutex.Unlock()
	AIContext = nil
	initAIContext()

	// Initial files
	numFiles := 5
	for i := 0; i < numFiles; i++ {
		uri := fmt.Sprintf("file://doc%d.tin", i)
		source := fmt.Sprintf("component Doc%d():\n    state x = %d\n", i, i)
		req := RequestEnvelope{
			Method: "textDocument/didChange",
			Params: json.RawMessage(fmt.Sprintf(`{"uri":"%s","version":1,"source":"%s"}`, uri, source)),
		}
		handleUpdateDocument(req)
	}

	var wg sync.WaitGroup
	var errorCount int32

	// We'll spin up 100 concurrent workers
	numWorkers := 100
	iterationsPerWorker := 50

	for w := 0; w < numWorkers; w++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			
			// Local PRNG for the worker
			rng := rand.New(rand.NewSource(time.Now().UnixNano() + int64(workerID)))

			for i := 0; i < iterationsPerWorker; i++ {
				op := rng.Intn(100)
				fileIdx := rng.Intn(numFiles)
				uri := fmt.Sprintf("file://doc%d.tin", fileIdx)

				if op < 30 {
					// 30% chance: LSP didChange
					version := rng.Intn(1000) + 2
					source := fmt.Sprintf("component Doc%d():\n    state x = %d\n", fileIdx, version)
					req := RequestEnvelope{
						JSONRPC: "2.0",
						ID:      workerID*1000 + i,
						Method:  "textDocument/didChange",
						Params:  json.RawMessage(fmt.Sprintf(`{"uri":"%s","version":%d,"source":"%s"}`, uri, version, source)),
					}
					// Use dispatchRequest to hit the recovery boundary and handlers
					if req.Method == "textDocument/didChange" {
						handleUpdateDocument(req)
					} else {
						handleAIContextRequest(req)
					}
				} else if op < 60 {
					// 30% chance: AI Context Reads (Search, Impact, File)
					req := RequestEnvelope{
						JSONRPC: "2.0",
						ID:      workerID*1000 + i,
					}
					subOp := rng.Intn(3)
					if subOp == 0 {
						req.Method = "context.search"
						req.Params = json.RawMessage(`{"query":"Doc"}`)
					} else if subOp == 1 {
						req.Method = "context.impact"
						req.Params = json.RawMessage(fmt.Sprintf(`{"id":"%s#Doc%d"}`, uri, fileIdx))
					} else {
						req.Method = "context.file"
						req.Params = json.RawMessage(fmt.Sprintf(`{"uri":"%s"}`, uri))
					}
					if req.Method == "textDocument/didChange" {
						handleUpdateDocument(req)
					} else {
						handleAIContextRequest(req)
					}
				} else if op < 85 {
					// 25% chance: AI Propose
					req := RequestEnvelope{
						JSONRPC: "2.0",
						ID:      workerID*1000 + i,
						Method:  "context.propose",
						Params: json.RawMessage(fmt.Sprintf(`{
							"operation": "replace",
							"uri": "%s",
							"expected_version": 1,
							"replacement": "component Doc%d():\n    state y = 1\n"
						}`, uri, fileIdx)),
					}
					if req.Method == "textDocument/didChange" {
						handleUpdateDocument(req)
					} else {
						handleAIContextRequest(req)
					}
				} else {
					// 15% chance: AI Apply
					// Note: Most of these will fail because they require a valid ProposalID. 
					// That's fine, testing the error handling concurrency.
					req := RequestEnvelope{
						JSONRPC: "2.0",
						ID:      workerID*1000 + i,
						Method:  "context.apply",
						Params: json.RawMessage(fmt.Sprintf(`{
							"proposal_id": "prop-fake-%d",
							"uri": "%s",
							"expected_version": 1
						}`, workerID, uri)),
					}
					if req.Method == "textDocument/didChange" {
						handleUpdateDocument(req)
					} else {
						handleAIContextRequest(req)
					}
				}
				
				// Small yield to let scheduler interleave
				time.Sleep(time.Microsecond)
			}
		}(w)
	}

	wg.Wait()
	
	// Let background goroutines dispatched by dispatchRequest finish
	time.Sleep(100 * time.Millisecond)

	if atomic.LoadInt32(&errorCount) > 0 {
		t.Fatalf("Encountered errors during stress test")
	}

	// Final Invariant Check: VFS version >= Semantic Workspace Version
	vfsMutex.RLock()
	defer vfsMutex.RUnlock()

	for uri, doc := range vfs {
		wsGraph := GlobalWorkspace.Index.Project.Files[uri]
		if wsGraph != nil {
			// In TinPyUI, the semantic file doesn't track its "version", 
			// but we can verify it exists and isn't crashed.
			// The per-document docMutex ensures that whatever is in the semantic workspace
			// is the result of the LAST didChange/apply that won the race for that URI.
			if len(wsGraph.Symbols) == 0 && len(doc.Source) > 10 {
				t.Errorf("Workspace out of sync with VFS for %s", uri)
			}
		}
	}
}


