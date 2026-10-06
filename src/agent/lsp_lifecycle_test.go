package agent

import (
	"context"
	"encoding/json"
	"testing"

	"github.com/tinui/tinui/src/compiler"
)

// Helper to simulate request
func invokeHandler(method string, params interface{}) {
	b, _ := json.Marshal(params)
	req := RequestEnvelope{
		JSONRPC: "2.0",
		ID:      1,
		Method:  method,
		Params:  json.RawMessage(b),
	}
	
	switch method {
	case "update_document":
		handleUpdateDocument(req)
	case "close_document":
		handleCloseDocument(req)
	case "check":
		handleCheck(context.Background(), req)
	}
}

func TestLSPLifecycleOpenUpdateQuery(t *testing.T) {
	GlobalWorkspace = compiler.NewSemanticWorkspace()

	// 1. Open -> update -> query
	invokeHandler("update_document", UpdateDocumentParams{
		URI:     "file://test1.tin",
		Source:  `component Box():
    span: "Box"`,
		Version: 1,
	})

	// Query
	targetID, _ := getTargetAtPosition("file://test1.tin", Position{Line: 0, Character: 12})
	if targetID != "tinpy://test1.tin#Box" {
		t.Errorf("Expected to hover Box, got %s", targetID)
	}

	// Update document
	invokeHandler("update_document", UpdateDocumentParams{
		URI:     "file://test1.tin",
		Source:  `component Circle():
    span: "Circle"`,
		Version: 2,
	})

	targetID, _ = getTargetAtPosition("file://test1.tin", Position{Line: 0, Character: 12})
	if targetID != "tinpy://test1.tin#Circle" {
		t.Errorf("Expected to hover Circle after update, got %s", targetID)
	}
}

func TestLSPLifecycleCrossFile(t *testing.T) {
	GlobalWorkspace = compiler.NewSemanticWorkspace()

	// 2. Open A -> open B -> update A -> query B
	invokeHandler("update_document", UpdateDocumentParams{
		URI:     "file://A.tin",
		Source:  `component OldComp():
    span: "A"`,
		Version: 1,
	})

	invokeHandler("update_document", UpdateDocumentParams{
		URI:     "file://B.tin",
		Source:  `import OldComp from "A.tin"
component BComp():
    OldComp()`,
		Version: 1,
	})

	// Query B hover over OldComp() at line 2 char 6
	targetID, _ := getTargetAtPosition("file://B.tin", Position{Line: 2, Character: 6})
	if targetID != "tinpy://A.tin#OldComp" {
		t.Errorf("Expected cross-file hover to find OldComp, got %s", targetID)
	}

	// Update A
	invokeHandler("update_document", UpdateDocumentParams{
		URI:     "file://A.tin",
		Source:  `component NewComp():
    span: "A"`,
		Version: 2,
	})

	// B still points to OldComp, but it is now unresolved in the workspace!
	// So ResolveSymbol(targetID) would return nil.
	sym := GlobalWorkspace.ResolveSymbol("tinpy://A.tin#OldComp")
	if sym != nil {
		t.Errorf("Expected OldComp to be gone")
	}

	unres := GlobalWorkspace.GetUnresolved()
	found := false
	for _, u := range unres {
		if u.TargetID == "tinpy://A.tin#OldComp" {
			found = true
		}
	}
	if !found {
		t.Errorf("Expected OldComp to be an unresolved reference")
	}
}

func TestLSPLifecycleCloseFile(t *testing.T) {
	GlobalWorkspace = compiler.NewSemanticWorkspace()

	// 3. Open A -> close A -> query dependent file
	invokeHandler("update_document", UpdateDocumentParams{
		URI:     "file://A.tin",
		Source:  `component Shared():
    span: "A"`,
		Version: 1,
	})

	invokeHandler("update_document", UpdateDocumentParams{
		URI:     "file://Main.tin",
		Source:  `import Shared from "A.tin"
component MainComp():
    Shared()`,
		Version: 1,
	})

	sym := GlobalWorkspace.ResolveSymbol("tinpy://A.tin#Shared")
	if sym == nil {
		t.Fatalf("Shared should exist")
	}

	invokeHandler("close_document", CloseDocumentParams{
		URI: "file://A.tin",
	})

	sym = GlobalWorkspace.ResolveSymbol("tinpy://A.tin#Shared")
	if sym != nil {
		t.Errorf("Shared should be removed")
	}

	unres := GlobalWorkspace.GetUnresolved()
	found := false
	for _, u := range unres {
		if u.TargetID == "tinpy://A.tin#Shared" {
			found = true
		}
	}
	if !found {
		t.Errorf("Expected Shared to become unresolved after closing A")
	}
}

func TestLSPLifecycleConcurrentRace(t *testing.T) {
	GlobalWorkspace = compiler.NewSemanticWorkspace()

	// Run multiple document updates and queries concurrently to test for data races.
	// Since we wrap the Workspace in sync.RWMutex, this should pass `go test -race`.
	done := make(chan bool)

	go func() {
		for i := 0; i < 50; i++ {
			invokeHandler("update_document", UpdateDocumentParams{
				URI:     "file://Race.tin",
				Source:  `component RaceComp(): span: "Race"`,
				Version: i,
			})
		}
		done <- true
	}()

	go func() {
		for i := 0; i < 50; i++ {
			invokeHandler("update_document", UpdateDocumentParams{
				URI:     "file://Race2.tin",
				Source:  `import RaceComp from "Race.tin"\ncomponent Race2(): RaceComp()`,
				Version: i,
			})
		}
		done <- true
	}()

	go func() {
		for i := 0; i < 50; i++ {
			getTargetAtPosition("file://Race2.tin", Position{Line: 1, Character: 5})
			GlobalWorkspace.ResolveSymbol("tinpy://Race.tin#RaceComp")
			GlobalWorkspace.GetUnresolved()
		}
		done <- true
	}()

	<-done
	<-done
	<-done
}
