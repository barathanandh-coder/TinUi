package compiler

import (
	"testing"
)

func TestComponentTypeChecker(t *testing.T) {
	checker := NewComponentTypeChecker()
	workspace := NewSemanticWorkspace()

	// Define imported file (File B)
	fileBAST := &FileAST{
		URI: "file://fileB.tin",
		Components: []*Component{
			{
				Name: "Button",
				Props: []PropDecl{
					{Name: "disabled", TypeHint: "Bool"},
					{Name: "text", TypeHint: "String", Default: `"Submit"`},
					{Name: "legacy_prop", TypeHint: ""}, // Legacy untyped
				},
			},
		},
	}
	workspace.AddFileAST(fileBAST)

	// Define main file (File A)
	ast := &FileAST{
		URI: "file:///test.tin",
		Imports: []*ImportDecl{
			{Path: `"fileB.tin"`, Symbols: []string{"Button"}},
		},
		Components: []*Component{
			{
				Name: "App",
				RootNodes: []ASTNode{
					&Node{
						Name: "Button",
						Attributes: map[string]string{
							"disabled": "true", // Valid
						},
					},
					&Node{
						Name: "Button",
						Attributes: map[string]string{
							"disabled": "42", // TypeConflict
						},
					},
					&Node{
						Name: "Button",
						Attributes: map[string]string{
							"foo": "true", // UnknownProperty
						},
					},
					&Node{
						Name: "Button",
						Attributes: map[string]string{
							"disabled": "true",
						},
						// Simulating duplicate by using both Positional and Named
						Args: []string{"true"},
					},
					&Node{
						Name: "Button",
						Attributes: map[string]string{
							"disabled": "{loading}", // Dynamic - Valid (TypeAny)
						},
					},
					&Node{
						Name: "Button",
						Attributes: map[string]string{
							"disabled": "true",
							"legacy_prop": "anything", // Legacy - Valid
						},
					},
					&Node{
						Name: "MissingComp", // Not imported
						Attributes: map[string]string{
							"foo": "bar", // Should not trigger property errors, just UnresolvedComponentReference
						},
					},
				},
			},
		},
	}
	workspace.AddFileAST(ast)

	diagnostics := checker.CheckWorkspace(ast, workspace)

	diagMap := make(map[string]int)
	for _, d := range diagnostics {
		t.Logf("Diagnostic: %s", d.Message)
		// Just extract the prefix (e.g. TypeConflict)
		prefix := ""
		for i, c := range d.Message {
			if c == ':' {
				prefix = d.Message[:i]
				break
			}
		}
		diagMap[prefix]++
	}

	if diagMap["MissingProperty"] != 1 {
		t.Errorf("Expected 1 MissingProperty, got %d", diagMap["MissingProperty"])
	}
	if diagMap["TypeMismatch"] != 1 {
		t.Errorf("Expected 1 TypeMismatch (disabled=42), got %d", diagMap["TypeMismatch"])
	}
	if diagMap["UnknownProperty"] != 1 {
		t.Errorf("Expected 1 UnknownProperty (foo=true), got %d", diagMap["UnknownProperty"])
	}
	if diagMap["DuplicateProperty"] != 1 {
		t.Errorf("Expected 1 DuplicateProperty, got %d", diagMap["DuplicateProperty"])
	}
	if diagMap["UnresolvedComponentReference"] != 1 {
		t.Errorf("Expected 1 UnresolvedComponentReference, got %d", diagMap["UnresolvedComponentReference"])
	}
}
