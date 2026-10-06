package agent

import (
	"encoding/json"
	"testing"

	"github.com/tinui/tinui/src/compiler"
)

func TestFailureRecovery_MalformedTin(t *testing.T) {
	GlobalWorkspace = compiler.NewSemanticWorkspace()
	AIContext = nil
	initAIContext()

	req := RequestEnvelope{
		JSONRPC: "2.0",
		ID:      1,
		Method:  "textDocument/didChange",
		Params: json.RawMessage(`{
			"uri": "file://malformed.tin",
			"version": 1,
			"source": "component Base()\n    state x = \n    foo bar\n"
		}`),
	}
	
	// This should not crash (panic).
	handleUpdateDocument(req)

	// Ensure the next request works
	req2 := RequestEnvelope{
		JSONRPC: "2.0",
		ID:      2,
		Method:  "textDocument/didChange",
		Params: json.RawMessage(`{
			"uri": "file://valid.tin",
			"version": 1,
			"source": "component Base():\n    state x = 1\n"
		}`),
	}
	handleUpdateDocument(req2)
	
	wsGraph := GlobalWorkspace.Index.Project.Files["file://valid.tin"]
	if wsGraph == nil {
		t.Fatalf("Workspace graph is nil for valid.tin")
	}
}

func TestFailureRecovery_ApplyRollbackCorrectness(t *testing.T) {
	GlobalWorkspace = compiler.NewSemanticWorkspace()
	AIContext = nil
	initAIContext()

	// 1. Initial State
	req1 := RequestEnvelope{
		Method:  "textDocument/didChange",
		Params: json.RawMessage(`{
			"uri": "file://base.tin",
			"version": 1,
			"source": "import Dep from \"dep.tin\"\ncomponent Base():\n    Dep()\n"
		}`),
	}
	handleUpdateDocument(req1)

	sourceDep := "component Dep():\n    state x = 1\n"
	req2 := RequestEnvelope{
		Method:  "textDocument/didChange",
		Params: json.RawMessage(`{
			"uri": "file://dep.tin",
			"version": 1,
			"source": "component Dep():\n    state x = 1\n"
		}`),
	}
	handleUpdateDocument(req2)

	// 2. Propose a change to dep.tin that renames Dep to Dep2, breaking base.tin
	reqPropose := RequestEnvelope{
		Method:  "context.propose",
		Params: json.RawMessage(`{
			"operation": "replace",
			"uri": "file://dep.tin",
			"expected_version": 1,
			"replacement": "component Dep2():\n    state x = 1\n"
		}`),
	}
	resPropose := captureJSONRPC(t, reqPropose)
	var pResult ProposalResult
	b, _ := json.Marshal(resPropose.Result)
	json.Unmarshal(b, &pResult)

	if !pResult.Valid {
		t.Fatalf("Expected valid proposal since local semantics are fine. Got: %v", pResult)
	}

	// 3. Apply it. This should fail the global invariant check and rollback.
	reqApply := RequestEnvelope{
		Method:  "context.apply",
		Params: json.RawMessage(`{
			"proposal_id": "` + pResult.ProposalID + `",
			"uri": "file://dep.tin",
			"expected_version": 1
		}`),
	}
	resApply := captureJSONRPC(t, reqApply)
	var aResult ApplyResult
	b2, _ := json.Marshal(resApply.Result)
	json.Unmarshal(b2, &aResult)

	if aResult.Success {
		t.Fatalf("Expected apply to fail due to unresolved reference")
	}

	// 4. Validate Rollback Correctness
	// VFS version should be 1
	vfsMutex.RLock()
	doc := vfs["file://dep.tin"]
	vfsMutex.RUnlock()

	if doc.Version != 1 {
		t.Fatalf("VFS version did not rollback to 1, got %d", doc.Version)
	}
	if doc.Source != sourceDep {
		t.Fatalf("VFS source did not rollback")
	}

	// Workspace should still have Dep, not Dep2
	wsGraph := GlobalWorkspace.Index.Project.Files["file://dep.tin"]
	foundDep := false
	for _, sym := range wsGraph.Symbols {
		if sym.Name == "Dep" {
			foundDep = true
		}
	}
	if !foundDep {
		t.Fatalf("Workspace did not rollback properly. Dep missing.")
	}

	// 5. Ensure next operation succeeds
	req4 := RequestEnvelope{
		Method:  "context.propose",
		Params: json.RawMessage(`{
			"operation": "replace",
			"uri": "file://dep.tin",
			"expected_version": 1,
			"replacement": "component Dep():\n    state x = 2\n"
		}`),
	}
	resPropose2 := captureJSONRPC(t, req4)
	var pResult2 ProposalResult
	b3, _ := json.Marshal(resPropose2.Result)
	json.Unmarshal(b3, &pResult2)

	if !pResult2.Valid {
		t.Fatalf("Subsequent request failed after rollback: %v", pResult2)
	}
}

func TestFailureRecovery_VersionMismatch(t *testing.T) {
	GlobalWorkspace = compiler.NewSemanticWorkspace()
	AIContext = nil
	initAIContext()

	req2 := RequestEnvelope{
		Method:  "textDocument/didChange",
		Params: json.RawMessage(`{
			"uri": "file://dep.tin",
			"version": 1,
			"source": "component Dep():\n    state x = 1\n"
		}`),
	}
	handleUpdateDocument(req2)

	reqPropose := RequestEnvelope{
		Method:  "context.propose",
		Params: json.RawMessage(`{
			"operation": "replace",
			"uri": "file://dep.tin",
			"expected_version": 1,
			"replacement": "component Dep():\n    state x = 2\n"
		}`),
	}
	resPropose := captureJSONRPC(t, reqPropose)
	var pResult ProposalResult
	b, _ := json.Marshal(resPropose.Result)
	json.Unmarshal(b, &pResult)

	// Simulate user edit (version bump to 2)
	req3 := RequestEnvelope{
		Method:  "textDocument/didChange",
		Params: json.RawMessage(`{
			"uri": "file://dep.tin",
			"version": 2,
			"source": "component Dep():\n    state x = 1\n    state y = 2\n"
		}`),
	}
	handleUpdateDocument(req3)

	// Try to apply proposal that expected version 1
	reqApply := RequestEnvelope{
		Method:  "context.apply",
		Params: json.RawMessage(`{
			"proposal_id": "` + pResult.ProposalID + `",
			"uri": "file://dep.tin",
			"expected_version": 1
		}`),
	}
	resApply := captureJSONRPC(t, reqApply)
	
	if resApply.Error == nil || resApply.Error.Code != -32003 {
		t.Fatalf("Expected version mismatch error -32003, got: %+v", resApply.Error)
	}

	// Verify VFS remains at version 2
	vfsMutex.RLock()
	doc := vfs["file://dep.tin"]
	vfsMutex.RUnlock()

	if doc.Version != 2 {
		t.Fatalf("VFS version was corrupted during failed apply, got %d", doc.Version)
	}
}
