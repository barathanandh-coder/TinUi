package agent

import (
	"fmt"
	"strings"

	"github.com/tinui/tinui/src/compiler"
)

var GlobalWorkspace = compiler.NewSemanticWorkspace()

// syncDocument parses and adds the document to the global Semantic Workspace
func syncDocument(uri string, source string) {
	if !strings.HasPrefix(uri, "file://") {
		uri = "file://" + uri
	}
	l := compiler.NewLexer(source)
	p := compiler.NewParser(l)
	ast := p.ParseFileAST(uri)
	GlobalWorkspace.AddFileAST(ast)
}

// closeDocument removes the document from the global Semantic Workspace
func closeDocument(uri string) {
	if !strings.HasPrefix(uri, "file://") {
		uri = "file://" + uri
	}
	GlobalWorkspace.RemoveFile(uri)
}

// containsPos checks if a Position is within a compiler.Range
func containsPos(r compiler.Range, p Position) bool {
	if p.Line < r.Start.Line || p.Line > r.End.Line {
		return false
	}
	if p.Line == r.Start.Line && p.Character < r.Start.Character {
		return false
	}
	if p.Line == r.End.Line && p.Character >= r.End.Character {
		return false
	}
	return true
}

// isSmaller checks if r1 is a tighter/smaller range than r2
func isSmaller(r1 compiler.Range, r2 compiler.Range) bool {
	lines1 := r1.End.Line - r1.Start.Line
	lines2 := r2.End.Line - r2.Start.Line
	if lines1 != lines2 {
		return lines1 < lines2
	}
	// If same lines, compare characters (approximation)
	chars1 := r1.End.Character - r1.Start.Character
	chars2 := r2.End.Character - r2.Start.Character
	return chars1 < chars2
}

// getTargetAtPosition returns the target ID of what is under the cursor.
// It checks relationships (usages) first, then symbol definitions.
func getTargetAtPosition(uri string, pos Position) (string, *compiler.Range) {
	if !strings.HasPrefix(uri, "file://") {
		uri = "file://" + uri
	}
	symbols := GlobalWorkspace.GetSymbolsForFile(uri)

	var smallestRange *compiler.Range
	var targetID string

	// 1. Relationships (hovering over usage/invocation)
	for _, sym := range symbols {
		for _, rel := range sym.Relationships {
			if containsPos(rel.Range, pos) {
				if smallestRange == nil || isSmaller(rel.Range, *smallestRange) {
					r := rel.Range
					smallestRange = &r
					targetID = rel.TargetID
				}
			}
		}
	}

	if targetID != "" {
		return targetID, smallestRange
	}

	// 2. Definition directly (hovering over its own definition block)
	for _, sym := range symbols {
		if containsPos(sym.Range, pos) {
			if smallestRange == nil || isSmaller(sym.Range, *smallestRange) {
				r := sym.Range
				smallestRange = &r
				targetID = sym.ID
			}
		}
	}

	return targetID, smallestRange
}

// resolveSymbol helper maps a resolved compiler.Symbol to a SymbolInformation
func resolveSymbolInfo(sym *compiler.Symbol) SymbolInformation {
	uri := GlobalWorkspace.GetFileForSymbol(sym.ID)
	// Strip file:// prefix for the LSP response URI to match standard agent paths if needed,
	// but agent uses both. We'll leave file:// as many LSP clients expect it.
	
	parentName := ""
	if sym.ParentID != "" {
		parts := strings.Split(sym.ParentID, "#")
		if len(parts) == 2 {
			parentName = parts[1]
		}
	}

	return SymbolInformation{
		Name: string(sym.Name),
		Kind: string(sym.Kind),
		Location: Location{
			URI: uri,
			Range: Range{
				Start: Position{Line: sym.Range.Start.Line, Character: sym.Range.Start.Character},
				End:   Position{Line: sym.Range.End.Line, Character: sym.Range.End.Character},
			},
		},
		ContainerName: parentName,
	}
}

// getHover constructs a hover message for the target
func getHover(targetID string) string {
	sym := GlobalWorkspace.ResolveSymbol(targetID)
	if sym == nil {
		return fmt.Sprintf("Unresolved reference: `%s`", targetID)
	}

	hover := fmt.Sprintf("**%s** `%s`", sym.Kind, sym.Name)
	if sym.ParentID != "" {
		parts := strings.Split(sym.ParentID, "#")
		if len(parts) == 2 {
			hover += fmt.Sprintf("\n*(Part of %s)*", parts[1])
		}
	}
	
	// Summarize relationships
	renders := 0
	reads := 0
	triggers := 0
	for _, rel := range sym.Relationships {
		switch rel.Kind {
		case compiler.RelRenders:
			renders++
		case compiler.RelReads:
			reads++
		case compiler.RelTriggers:
			triggers++
		}
	}
	
	if renders > 0 || reads > 0 || triggers > 0 {
		hover += fmt.Sprintf("\n\nRenders: %d | Reads: %d | Triggers: %d", renders, reads, triggers)
	}
	
	return hover
}
