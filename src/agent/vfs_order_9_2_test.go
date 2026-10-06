package agent

import (
	"encoding/json"
	"sync"
	"testing"
	"time"

	"github.com/tinui/tinui/src/compiler"
)

func TestAIContextVFSOrdering(t *testing.T) {
	// Initialize global environment
	GlobalWorkspace = compiler.NewSemanticWorkspace()
	AIContext = nil
	initAIContext()

	req1 := RequestEnvelope{
		JSONRPC: "2.0",
		ID:      1,
		Method:  "textDocument/didChange",
		Params: json.RawMessage(`{
			"uri": "file://test.tin",
			"version": 1,
			"source": "component Base():\n    state x: 1\n"
		}`),
	}
	handleUpdateDocument(req1)

	// Now we simulate a concurrent update V2 and V3.
	// We want to make sure they process in order, or at least they don't interleave 
	// such that VFS has V3 and Workspace has V2.

	var wg sync.WaitGroup
	wg.Add(2)

	go func() {
		defer wg.Done()
		req2 := RequestEnvelope{
			JSONRPC: "2.0",
			ID:      2,
			Method:  "textDocument/didChange",
			Params: json.RawMessage(`{
				"uri": "file://test.tin",
				"version": 2,
				"source": "component BaseV2():\n    state x: 2\n"
			}`),
		}
		handleUpdateDocument(req2)
	}()

	go func() {
		defer wg.Done()
		// Sleep slightly to make sure V2 starts first
		time.Sleep(10 * time.Millisecond)
		req3 := RequestEnvelope{
			JSONRPC: "2.0",
			ID:      3,
			Method:  "textDocument/didChange",
			Params: json.RawMessage(`{
				"uri": "file://test.tin",
				"version": 3,
				"source": "component BaseV3():\n    state x: 3\n"
			}`),
		}
		handleUpdateDocument(req3)
	}()

	wg.Wait()

	// Now we verify that the VFS matches the Workspace
	vfsMutex.RLock()
	doc := vfs["file://test.tin"]
	vfsMutex.RUnlock()

	wsGraph := GlobalWorkspace.Index.Project.Files["file://test.tin"]
	if wsGraph == nil {
		t.Fatalf("Workspace graph is nil")
	}
	
	// Determine which one won by checking VFS
	var expectedSym string
	if doc.Version == 2 {
		expectedSym = "tinpy://test.tin#BaseV2"
	} else {
		expectedSym = "tinpy://test.tin#BaseV3"
	}

	found := false
	for _, sym := range wsGraph.Symbols {
		if sym.ID == expectedSym {
			found = true
			break
		}
	}

	if !found {
		t.Fatalf("VFS has Version %d, but workspace does not have %s. Workspace state: %+v", doc.Version, expectedSym, wsGraph.Symbols)
	}
}
