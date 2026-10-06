package compiler

import (
	"testing"
)

func TestComponentTypeChecker(t *testing.T) {
	checker := NewComponentTypeChecker()

	ast := &FileAST{
		URI: "file:///test.tin",
		Components: []*Component{
			{
				Name: "Button",
				Props: []PropDecl{
					{Name: "disabled", TypeHint: "Bool"},
					{Name: "text", TypeHint: "String", Default: `"Submit"`},
					{Name: "legacy_prop", TypeHint: ""}, // Legacy untyped
				},
				RootNodes: []ASTNode{
					&Node{
						Name: "Text", // Non-component
						Args: []string{`"Click Me"`},
					},
				},
			},
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
				},
			},
		},
	}

	diagnostics := checker.CheckLocalFile(ast)

	diagMap := make(map[string]int)
	for _, d := range diagnostics {
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

	if diagMap["MissingProperty"] != 2 {
		t.Errorf("Expected 2 MissingProperty (one for Button(foo=true), one for Button() via missing args), got %d", diagMap["MissingProperty"])
	}
	if diagMap["TypeConflict"] != 1 {
		t.Errorf("Expected 1 TypeConflict (disabled=42), got %d", diagMap["TypeConflict"])
	}
	if diagMap["UnknownProperty"] != 1 {
		t.Errorf("Expected 1 UnknownProperty (foo=true), got %d", diagMap["UnknownProperty"])
	}
	if diagMap["DuplicateProperty"] != 1 {
		t.Errorf("Expected 1 DuplicateProperty, got %d", diagMap["DuplicateProperty"])
	}
}
