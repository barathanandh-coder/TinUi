package compiler

import (
	"testing"
)

func TestASTRangeExtraction(t *testing.T) {
	input := `import Card from "ui/card.tin"

component App(title):
    state count = 0
    
    def increment():
        count += 1
        
    div:
        h1: f"{title}"
        Card()
`

	l := NewLexer(input)
	p := NewParser(l)
	fileAST := p.ParseFileAST("file:///test.tin")

	if len(p.Errors) > 0 {
		t.Fatalf("Parser encountered errors: %v", p.Errors)
	}

	if fileAST.URI != "file:///test.tin" {
		t.Errorf("Expected URI 'file:///test.tin', got '%s'", fileAST.URI)
	}

	if len(fileAST.Imports) != 1 {
		t.Fatalf("Expected 1 import, got %d", len(fileAST.Imports))
	}
	
	imp := fileAST.Imports[0]
	if imp.Path != `ui/card.tin` {
		t.Errorf("Expected import path 'ui/card.tin', got '%s'", imp.Path)
	}
	
	// import is on line 1, characters 0 to 30. (0-based: line 0, char 0 to 30)
	if imp.Range.Start.Line != 0 || imp.Range.Start.Character != 0 {
		t.Errorf("Expected import start 0:0, got %v", imp.Range.Start)
	}

	if len(fileAST.Components) != 1 {
		t.Fatalf("Expected 1 component, got %d", len(fileAST.Components))
	}
	
	comp := fileAST.Components[0]
	if comp.Name != "App" {
		t.Errorf("Expected component Name 'App', got '%s'", comp.Name)
	}
	
	// Component starts on line 3 (index 2).
	if comp.Range.Start.Line != 2 || comp.Range.Start.Character != 0 {
		t.Errorf("Expected component start 2:0, got %v", comp.Range.Start)
	}

	// State check
	if len(comp.States) != 1 {
		t.Fatalf("Expected 1 state, got %d", len(comp.States))
	}
	state := comp.States[0]
	if state.Name != "count" {
		t.Errorf("Expected state 'count', got '%s'", state.Name)
	}
	if state.Range.Start.Line != 3 { // line index 3
		t.Errorf("Expected state start line 3, got %d", state.Range.Start.Line)
	}

	// Mutation check
	if len(comp.Mutations) != 1 {
		t.Fatalf("Expected 1 mutation, got %d", len(comp.Mutations))
	}
	mut := comp.Mutations[0]
	if mut.FuncName != "increment" {
		t.Errorf("Expected def 'increment', got '%s'", mut.FuncName)
	}
	if mut.Range.Start.Line != 5 { // line index 5
		t.Errorf("Expected def start line 5, got %d", mut.Range.Start.Line)
	}
	
	// Node check
	if len(comp.RootNodes) != 1 {
		t.Fatalf("Expected 1 root node, got %d", len(comp.RootNodes))
	}
	div := comp.RootNodes[0].(*Node)
	if div.Name != "div" {
		t.Errorf("Expected node 'div', got '%s'", div.Name)
	}
	if div.Range.Start.Line != 8 { // line index 8
		t.Errorf("Expected div start line 8, got %d", div.Range.Start.Line)
	}
}
