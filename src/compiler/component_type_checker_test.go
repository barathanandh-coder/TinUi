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

func TestA6BranchSensitiveNarrowing(t *testing.T) {
	checker := NewComponentTypeChecker()
	workspace := NewSemanticWorkspace()

	fileBAST := &FileAST{
		URI: "file://fileB.tin",
		Components: []*Component{
			{
				Name: "AdultContent",
				Props: []PropDecl{
					{Name: "verified_age", TypeHint: "String"}, // Fails if narrowed to Int
				},
			},
		},
	}
	workspace.AddFileAST(fileBAST)

	ast := &FileAST{
		URI: "file:///test.tin",
		Imports: []*ImportDecl{
			{Path: `"fileB.tin"`, Symbols: []string{"AdultContent"}},
		},
		Components: []*Component{
			{
				Name: "App",
				States: []*StateDecl{
					{Name: "age", Initial: "{dynamic_age}"}, // TypeAny
				},
				RootNodes: []ASTNode{
					&Node{ // Succeeds outside branch! (Any is assignable to String)
						Name: "AdultContent",
						Attributes: map[string]string{
							"verified_age": "{age}",
						},
					},
					&ConditionalNode{
						ConditionVar: "age",
						Operator: ">",
						Value: "18", // Infers TypeInt -> Narrows {age} to TypeInt
						TrueBranch: []ASTNode{
							&Node{ // Fails inside branch! Int is not assignable to String
								Name: "AdultContent",
								Attributes: map[string]string{
									"verified_age": "{age}",
								},
							},
						},
						FalseBranch: []ASTNode{
							&Node{ // Succeeds inside false branch (since > only narrows TrueBranch in our logic)
								Name: "AdultContent",
								Attributes: map[string]string{
									"verified_age": "{age}",
								},
							},
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
		prefix := ""
		for i, c := range d.Message {
			if c == ':' {
				prefix = d.Message[:i]
				break
			}
		}
		diagMap[prefix]++
		t.Logf("Found diag: %s", d.Message)
	}

	// We expect exactly ONE TypeMismatch: the one INSIDE the true branch.
	if diagMap["TypeMismatch"] != 1 {
		t.Errorf("Expected 1 TypeMismatch inside branch, got %d", diagMap["TypeMismatch"])
	}
}
