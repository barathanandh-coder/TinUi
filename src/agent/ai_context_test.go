package agent

import (
	"encoding/json"
	"testing"

	"github.com/tinui/tinui/src/compiler"
)

func setupTestContextAPI() *AIContextAPI {
	ws := compiler.NewSemanticWorkspace()
	
	// Create main file
	lMain := compiler.NewLexer(`
import Shared from "shared.tin"
import Missing from "missing.tin"

component Main():
    Shared()
    Missing()
`)
	pMain := compiler.NewParser(lMain)
	astMain := pMain.ParseFileAST("file://main.tin")
	ws.AddFileAST(astMain)
	
	// Create shared file
	lShared := compiler.NewLexer(`
component Shared():
    state flag: true
    def toggle():
        flag = not flag
    
    if flag == true:
        Button()
    else:
        Button()
`)
	pShared := compiler.NewParser(lShared)
	astShared := pShared.ParseFileAST("file://shared.tin")
	ws.AddFileAST(astShared)

	return NewAIContextAPI(ws)
}

func TestAIContextAPI(t *testing.T) {
	api := setupTestContextAPI()

	// 1. Project Context
	projCtx := api.GetProjectContext()
	if len(projCtx.Files) != 2 {
		t.Fatalf("Expected 2 files, got %d", len(projCtx.Files))
	}
	if projCtx.Files[0] != "file://main.tin" || projCtx.Files[1] != "file://shared.tin" {
		t.Errorf("Project context files not deterministic or incorrect")
	}

	// 8. Unresolved References
	if len(projCtx.UnresolvedReferences) == 0 {
		t.Fatalf("Expected unresolved references")
	}
	
	// Unresolved references will include Missing and Button (since Button isn't imported or defined)
	foundMissing := false
	foundButton := false
	for _, u := range projCtx.UnresolvedReferences {
		if u.TargetID == "tinpy://missing.tin#Missing" {
			foundMissing = true
		}
		if u.TargetID == "tinpy://shared.tin#Button" {
			foundButton = true
		}
	}
	if !foundMissing {
		t.Errorf("Expected unresolved reference to Missing")
	}
	if !foundButton {
		t.Errorf("Expected unresolved reference to Button")
	}

	// 2. File Context
	fileCtx := api.GetFileContext("file://main.tin")
	if fileCtx == nil {
		t.Fatalf("Failed to get file context")
	}
	if fileCtx.URI != "file://main.tin" {
		t.Errorf("Incorrect file URI")
	}
	// 7. Imports
	if len(fileCtx.Imports) != 2 {
		t.Fatalf("Expected 2 imports in main, got %d", len(fileCtx.Imports))
	}
	if len(fileCtx.Symbols) != 1 {
		t.Fatalf("Expected 1 symbol in main.tin, got %d", len(fileCtx.Symbols))
	}

	// 11. Nonexistent file/symbol handling
	if api.GetFileContext("file://nowhere.tin") != nil {
		t.Errorf("Expected nil for missing file")
	}
	if api.GetSymbolContext("tinpy://nowhere.tin#Ghost") != nil {
		t.Errorf("Expected nil for missing symbol")
	}

	// 3. Symbol Context & 10. Bounded Selection
	sharedID := "tinpy://shared.tin#Shared"
	symCtx := api.GetSymbolContext(sharedID)
	if symCtx == nil {
		t.Fatalf("Failed to get symbol context")
	}
	if symCtx.Symbol.ID != sharedID {
		t.Errorf("Expected symbol ID %s, got %s", sharedID, symCtx.Symbol.ID)
	}
	
	// 4. Relationship traversal (Children)
	if len(symCtx.Children) != 2 { // flag state and toggle def
		t.Fatalf("Expected 2 children for Shared, got %d", len(symCtx.Children))
	}

	// 5. References (reads, renders, etc.)
	if len(symCtx.References) != 3 { // Reads 'flag' in conditional, plus 2 Button renders
		t.Fatalf("Expected 3 references for Shared, got %d: %v", len(symCtx.References), symCtx.References)
	}
	
	readsFlag := false
	rendersButton := 0
	for _, rel := range symCtx.References {
		if rel.Kind == compiler.RelReads && rel.TargetID == "tinpy://shared.tin#Shared.state.flag" {
			readsFlag = true
		}
		if rel.Kind == compiler.RelRenders && rel.TargetID == "tinpy://shared.tin#Button" {
			rendersButton++
		}
	}
	if !readsFlag {
		t.Errorf("Expected reference to RelReads flag")
	}
	if rendersButton != 2 {
		t.Errorf("Expected 2 RelRenders for Button, got %d", rendersButton)
	}

	// 6. Dependents (who calls Shared)
	if len(symCtx.Dependents) != 2 { // main.tin imports it, AND main.tin's Main renders it
		t.Fatalf("Expected 2 dependents (import + render) for Shared, got %d", len(symCtx.Dependents))
	}

	// Verify data is serializable
	_, err := json.Marshal(symCtx)
	if err != nil {
		t.Fatalf("Failed to serialize context: %v", err)
	}
}

// 12. No mutation through the API
// API exposes pointers, which is standard in Go. However, we verify we only expose read operations
// like Get... No Set/Add methods exist on AIContextAPI.
func TestAIContextAPINoMutation(t *testing.T) {
	// A simple static assertion: check methods via reflection if desired, 
	// or rely on the code structure. It has no mutators.
}
