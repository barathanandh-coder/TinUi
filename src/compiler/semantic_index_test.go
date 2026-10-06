package compiler

import (
	"testing"
)

func TestSemanticIndex(t *testing.T) {
	input1 := `import Card from "ui/card.tin"
import Missing from "ui/missing.tin"

component App():
    state count = 0
    def increment():
        count += 1
    div:
        Card()
`
	input2 := `component Card():
    span: "Hello"
`

	idx := NewSemanticIndex()

	l1 := NewLexer(input1)
	p1 := NewParser(l1)
	f1 := AnalyzeFile(p1.ParseFileAST("file:///project/src/main.tin"))
	idx.AddFile(f1)

	l2 := NewLexer(input2)
	p2 := NewParser(l2)
	f2 := AnalyzeFile(p2.ParseFileAST("file://ui/card.tin"))
	idx.AddFile(f2)

	// Test 1: Symbol lookup by tinpy:// ID
	appSym := idx.FindSymbol("tinpy:///project/src/main.tin#App")
	if appSym == nil {
		t.Fatalf("Failed to find App symbol by ID")
	}

	// Test 2: Lookup by name/kind
	cards := idx.FindSymbolsByNameAndKind("Card", SymbolComponent)
	if len(cards) != 1 {
		t.Fatalf("Expected 1 Card component, got %d", len(cards))
	}
	if cards[0].ID != "tinpy://ui/card.tin#Card" {
		t.Errorf("Unexpected Card ID: %s", cards[0].ID)
	}

	// Test 3: Relationship traversal (GetChildren)
	children := idx.GetChildren(appSym.ID)
	if len(children) != 2 { // state.count and def.increment
		t.Fatalf("Expected 2 children for App, got %d", len(children))
	}

	// Test 4: Parent traversal (GetParent)
	parent := idx.GetParent(children[0].ID)
	if parent == nil || parent.ID != appSym.ID {
		t.Errorf("Failed to traverse to parent correctly")
	}

	// Test 5: Imports lookup
	imports := idx.GetImports("file:///project/src/main.tin")
	if len(imports) != 2 {
		t.Fatalf("Expected 2 imports, got %d", len(imports))
	}

	// Test 6: Dependents querying
	// Card is imported by App and rendered by App (2 dependents)
	cardID := "tinpy://ui/card.tin#Card"
	dependents := idx.GetDependents(cardID)
	if len(dependents) != 2 {
		t.Fatalf("Expected Card to have 2 dependents, got %d", len(dependents))
	}

	// Test 7: Unresolved references
	unresolved := idx.GetUnresolvedReferences()
	if len(unresolved) == 0 {
		t.Fatalf("Expected unresolved references for 'Missing'")
	}
	
	foundMissing := false
	for _, u := range unresolved {
		if u.TargetID == "tinpy://ui/missing.tin#Missing" {
			foundMissing = true
		}
	}
	if !foundMissing {
		t.Errorf("Failed to find unresolved reference to Missing")
	}
}
