package compiler

import (
	"testing"
)

func TestSemanticWorkspace(t *testing.T) {
	ws := NewSemanticWorkspace()

	// Add file 1
	input1 := `component Button():
    span: "Click me"`
	p1 := NewParser(NewLexer(input1))
	ws.AddFileAST(p1.ParseFileAST("file://ui/button.tin"))

	// Add file 2
	input2 := `import Button from "ui/button.tin"
component Card():
    Button()`
	p2 := NewParser(NewLexer(input2))
	ws.AddFileAST(p2.ParseFileAST("file://ui/card.tin"))

	// Add file 3
	input3 := `import Card from "ui/card.tin"
import Missing from "ui/missing.tin"
component Main():
    Card()`
	p3 := NewParser(NewLexer(input3))
	ws.AddFileAST(p3.ParseFileAST("file:///project/src/main.tin"))

	// Verify symbol -> file mapping (GetFileForSymbol)
	buttonFile := ws.GetFileForSymbol("tinpy://ui/button.tin#Button")
	if buttonFile != "file://ui/button.tin" {
		t.Errorf("Expected Button to map to file://ui/button.tin, got %s", buttonFile)
	}

	// Verify cross-file resolution
	buttonSym := ws.ResolveSymbol("tinpy://ui/button.tin#Button")
	if buttonSym == nil {
		t.Fatalf("Failed to resolve cross-file symbol Button")
	}

	// Verify file -> symbols mapping
	cardSymbols := ws.GetSymbolsForFile("file://ui/card.tin")
	if len(cardSymbols) != 1 {
		t.Fatalf("Expected 1 symbol in card.tin, got %d", len(cardSymbols))
	}
	if cardSymbols[0].Name != "Card" {
		t.Errorf("Expected Card symbol, got %s", cardSymbols[0].Name)
	}

	// Verify Unresolved (Missing)
	unresolved := ws.GetUnresolved()
	if len(unresolved) == 0 {
		t.Fatalf("Expected unresolved references for Missing")
	}

	// Remove a file cleanly (card.tin)
	ws.RemoveFile("file://ui/card.tin")

	// Verify it's gone
	if ws.GetFileForSymbol("tinpy://ui/card.tin#Card") != "" { // But wait, GetFileForSymbol derives from string, so it always works even if missing. 
		// Actually GetFileForSymbol looks up in Index.FindSymbol! So it returns "" if missing.
		// Let's verify it returns ""
		if ws.GetFileForSymbol("tinpy://ui/card.tin#Card") != "" {
			t.Errorf("Expected GetFileForSymbol to return empty string after removal")
		}
	}
	
	cardSym := ws.ResolveSymbol("tinpy://ui/card.tin#Card")
	if cardSym != nil {
		t.Errorf("Expected Card symbol to be removed")
	}

	// The index should rebuild and now Main's import of Card should be unresolved!
	unresolved2 := ws.GetUnresolved()
	foundCardUnresolved := false
	for _, u := range unresolved2 {
		if u.TargetID == "tinpy://ui/card.tin#Card" {
			foundCardUnresolved = true
		}
	}
	if !foundCardUnresolved {
		t.Errorf("Expected Card to become an unresolved reference after its file was removed")
	}
}
