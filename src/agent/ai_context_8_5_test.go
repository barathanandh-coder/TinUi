package agent

import (
	"encoding/json"
	"testing"
	
	"github.com/tinui/tinui/src/compiler"
)

func TestAIContextApplyFlow(t *testing.T) {
	// Initialize global environment
	GlobalWorkspace = compiler.NewSemanticWorkspace()
	AIContext = nil
	initAIContext()

	// 1. Setup VFS and Workspace
	sourceShared := `
component Shared():
    state x: 1
`
	sourceCode := `
import Shared from "shared.tin"

component Base():
    Shared()
`
	vfsMutex.Lock()
	vfs["file://shared.tin"] = UpdateDocumentParams{URI: "file://shared.tin", Version: 1, Source: sourceShared}
	vfs["file://base.tin"] = UpdateDocumentParams{URI: "file://base.tin", Version: 1, Source: sourceCode}
	vfsMutex.Unlock()
	syncDocument("file://shared.tin", sourceShared)
	syncDocument("file://base.tin", sourceCode)

	// 2. AI Proposes a change
	reqPropose := RequestEnvelope{
		JSONRPC: "2.0",
		ID:      1,
		Method:  "context.propose",
		Params: json.RawMessage(`{
			"operation": "replace",
			"uri": "file://base.tin",
			"expected_version": 1,
			"replacement": "import Shared from \"shared.tin\"\n\ncomponent Base():\n    Shared()\n    Shared()\n"
		}`),
	}

	resPropose := captureJSONRPC(t, reqPropose)
	if resPropose.Error != nil {
		t.Fatalf("Propose failed: %v", resPropose.Error)
	}

	var pResult ProposalResult
	b, _ := json.Marshal(resPropose.Result)
	json.Unmarshal(b, &pResult)

	if !pResult.Valid || pResult.ProposalID == "" {
		t.Fatalf("Expected valid proposal, got %v", pResult)
	}

	// 3. Apply the proposal
	reqApply := RequestEnvelope{
		JSONRPC: "2.0",
		ID:      2,
		Method:  "context.apply",
		Params: json.RawMessage(`{
			"proposal_id": "` + pResult.ProposalID + `",
			"uri": "file://base.tin",
			"expected_version": 1
		}`),
	}

	resApply := captureJSONRPC(t, reqApply)
	if resApply.Error != nil {
		t.Fatalf("Apply failed: %v", resApply.Error)
	}

	var aResult ApplyResult
	b2, _ := json.Marshal(resApply.Result)
	json.Unmarshal(b2, &aResult)

	if !aResult.Success {
		t.Fatalf("Expected successful apply, got %v", aResult)
	}

	// 4. Verify VFS bump
	vfsMutex.RLock()
	doc := vfs["file://base.tin"]
	vfsMutex.RUnlock()

	if doc.Version != 2 {
		t.Fatalf("Expected VFS version 2, got %d", doc.Version)
	}
	
	// 5. Apply again -> should fail (proposal consumed + version changed)
	resApply2 := captureJSONRPC(t, reqApply)
	if resApply2.Error == nil || resApply2.Error.Code != -32002 {
		t.Fatalf("Expected -32002 (proposal consumed), got %v", resApply2.Error)
	}
}

func TestAIContextApplyRollback(t *testing.T) {
	// Initialize global environment
	GlobalWorkspace = compiler.NewSemanticWorkspace()
	AIContext = nil
	initAIContext()

	// 1. Setup VFS and Workspace
	sourceCode := `
import Shared from "shared.tin"

component Base():
    Shared()
`
	vfsMutex.Lock()
	vfs["file://base2.tin"] = UpdateDocumentParams{URI: "file://base2.tin", Version: 1, Source: sourceCode}
	vfsMutex.Unlock()
	syncDocument("file://base2.tin", sourceCode)

	// We'll propose a change that is perfectly valid *locally* (e.g. imports something that exists)
	// and then we'll delete that thing from the workspace before applying.

	sourceDep := `
component Dependency():
    state x: 1
`
	vfsMutex.Lock()
	vfs["file://dep.tin"] = UpdateDocumentParams{URI: "file://dep.tin", Version: 1, Source: sourceDep}
	vfsMutex.Unlock()
	syncDocument("file://dep.tin", sourceDep)

	reqPropose := RequestEnvelope{
		JSONRPC: "2.0",
		ID:      1,
		Method:  "context.propose",
		Params: json.RawMessage(`{
			"operation": "replace",
			"uri": "file://base2.tin",
			"expected_version": 1,
			"replacement": "import Dependency from \"dep.tin\"\n\ncomponent Base():\n    Dependency()\n"
		}`),
	}

	resPropose := captureJSONRPC(t, reqPropose)
	var pResult ProposalResult
	b, _ := json.Marshal(resPropose.Result)
	json.Unmarshal(b, &pResult)

	if !pResult.Valid {
		t.Fatalf("Expected valid proposal, got %v", pResult)
	}

	// Now delete dep.tin from the workspace
	closeDocument("file://dep.tin")
	
	// Apply the proposal -> should fail semantic validation and rollback
	reqApply := RequestEnvelope{
		JSONRPC: "2.0",
		ID:      2,
		Method:  "context.apply",
		Params: json.RawMessage(`{
			"proposal_id": "` + pResult.ProposalID + `",
			"uri": "file://base2.tin",
			"expected_version": 1
		}`),
	}

	resApply := captureJSONRPC(t, reqApply)
	var aResult ApplyResult
	b2, _ := json.Marshal(resApply.Result)
	json.Unmarshal(b2, &aResult)

	if aResult.Success {
		t.Fatalf("Expected apply to fail and rollback due to missing dependency")
	}

	// Verify Rollback
	vfsMutex.RLock()
	doc := vfs["file://base2.tin"]
	vfsMutex.RUnlock()

	if doc.Version != 1 {
		t.Fatalf("Expected VFS version 1 after rollback, got %d", doc.Version)
	}
	if doc.Source != sourceCode {
		t.Fatalf("Expected original source after rollback")
	}
}
