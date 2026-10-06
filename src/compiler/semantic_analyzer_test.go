package compiler

import (
	"testing"
)

func TestSemanticAnalyzer(t *testing.T) {
	input := `import Card from "ui/card.tin"

component App(title):
    state count = 0
    
    def increment():
        count += 1
        
    div:
        h1: f"{title}"
        Card()
        Button(on_click="increment")
`

	l := NewLexer(input)
	p := NewParser(l)
	fileAST := p.ParseFileAST("file:///project/src/main.tin")

	if len(p.Errors) > 0 {
		t.Fatalf("Parser encountered errors: %v", p.Errors)
	}

	graph := AnalyzeFile(fileAST)

	// 10. imports
	if len(graph.Imports) != 1 {
		t.Fatalf("Expected 1 import, got %d", len(graph.Imports))
	}
	imp := graph.Imports[0]
	if imp.Kind != RelImports {
		t.Errorf("Expected RelImports, got %v", imp.Kind)
	}
	if imp.TargetID != "tinpy://ui/card.tin#Card" {
		t.Errorf("Expected tinpy://ui/card.tin#Card, got %s", imp.TargetID)
	}

	// 1. Component symbol creation & 5. deterministic IDs
	appID := "tinpy:///project/src/main.tin#App"
	appSym, exists := graph.Symbols[appID]
	if !exists {
		t.Fatalf("Component App symbol not found in graph")
	}
	if appSym.Kind != SymbolComponent {
		t.Errorf("Expected App kind Component, got %v", appSym.Kind)
	}
	if appSym.Name != "App" {
		t.Errorf("Expected App name, got %s", appSym.Name)
	}

	// 2. State symbol creation & 6. component hierarchy
	stateID := appID + ".state.count"
	stateSym, exists := graph.Symbols[stateID]
	if !exists {
		t.Fatalf("State count symbol not found")
	}
	if stateSym.Kind != SymbolState {
		t.Errorf("Expected State kind, got %v", stateSym.Kind)
	}
	if stateSym.ParentID != appID {
		t.Errorf("Expected state parent ID to be App, got %s", stateSym.ParentID)
	}
	// 4. Source ranges
	if stateSym.Range.Start.Line != 3 {
		t.Errorf("Expected state line 3, got %d", stateSym.Range.Start.Line)
	}

	// 3. Definition symbol creation
	defID := appID + ".def.increment"
	defSym, exists := graph.Symbols[defID]
	if !exists {
		t.Fatalf("Def increment symbol not found")
	}
	if defSym.Kind != SymbolDefinition {
		t.Errorf("Expected Def kind, got %v", defSym.Kind)
	}
	if defSym.ParentID != appID {
		t.Errorf("Expected def parent ID to be App, got %s", defSym.ParentID)
	}

	// 8. reads
	foundReads := false
	for _, rel := range defSym.Relationships {
		if rel.Kind == RelReads && rel.TargetID == stateID {
			foundReads = true
		}
	}
	if !foundReads {
		t.Errorf("Expected 'reads' relationship on def for state 'count'")
	}

	// 7. renders & 9. triggers
	foundRenders := false
	foundTriggers := false
	for _, rel := range appSym.Relationships {
		if rel.Kind == RelRenders && rel.TargetID == "tinpy://ui/card.tin#Card" {
			foundRenders = true
		}
		if rel.Kind == RelTriggers && rel.TargetID == defID {
			foundTriggers = true
		}
	}
	if !foundRenders {
		t.Errorf("Expected 'renders' relationship for 'Card'")
	}
	if !foundTriggers {
		t.Errorf("Expected 'triggers' relationship for 'increment'")
	}
}

func TestSemanticAnalyzerDuplicates(t *testing.T) {
	input := `
component App():
    div()
component App():
    span()
`
	l := NewLexer(input)
	p := NewParser(l)
	fileAST := p.ParseFileAST("file:///project/src/dupe.tin")
	graph := AnalyzeFile(fileAST)

	// Should just have 1 component symbol (overwrites or merges based on map behavior)
	if len(graph.Symbols) != 1 {
		t.Fatalf("Expected 1 symbol due to duplicate collapse, got %d", len(graph.Symbols))
	}

	appID := "tinpy:///project/src/dupe.tin#App"
	_, exists := graph.Symbols[appID]
	if !exists {
		t.Fatalf("Expected App to exist")
	}
}
