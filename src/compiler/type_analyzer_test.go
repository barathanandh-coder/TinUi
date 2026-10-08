package compiler

import (
	"testing"
)

func TestASTTypeAnalyzer(t *testing.T) {
	analyzer := NewTypeAnalyzer()

	// Build a mock AST that fulfills all requirements in Phase A.4.2
	ast := &FileAST{
		URI: "file:///test.tin",
		Components: []*Component{
			{
				Name: "TestApp",
				States: []*StateDecl{
					{Name: "count", Initial: "10"},
					{Name: "price", Initial: "10.5"},
					{Name: "enabled", Initial: "true"},
					{Name: "name", Initial: `"Barath"`},
					{Name: "dynamic_val", Initial: `{var}`},
					{Name: "unrecognized", Initial: `unquoted_string`},
				},
				Mutations: []*DefNode{
					{
						FuncName: "UpdateValues",
						Mutations: []MutationNode{
							// count = 10, count = 20 -> compatible
							{StateKey: "count", Operator: "=", Value: "20"},       
							// price = 10 (simulated via assign to 10), price = 10.5 -> widening
							// We'll test widening by taking the integer count and assigning to float price
							{StateKey: "price", Operator: "=", Value: "15"},       
							// count = 10, count = "hello" -> TypeConflict
							{StateKey: "count", Operator: "=", Value: `"hello"`}, 
						},
					},
				},
				RootNodes: []ASTNode{
					&Node{
						Name: "Button",
						Args: []string{`"Submit"`},
						Attributes: map[string]string{
							"color": `"red"`,
							"data":  `{dynamic}`,
						},
					},
				},
			},
		},
	}

	res := analyzer.Analyze(ast)

	// Verify States initialized properly
	if tr := res.StateTypes["TestApp.count"]; tr.Type.Kind != TypeConflict {
		t.Errorf("Expected count to result in TypeConflict due to reassignment to string, got %s", tr.Type.Kind)
	}
	if tr := res.StateTypes["TestApp.price"]; tr.Type.Kind != TypeFloat {
		t.Errorf("Expected price to be Float, got %s", tr.Type.Kind)
	}
	if tr := res.StateTypes["TestApp.enabled"]; tr.Type.Kind != TypeBool {
		t.Errorf("Expected enabled to be Bool, got %s", tr.Type.Kind)
	}
	if tr := res.StateTypes["TestApp.name"]; tr.Type.Kind != TypeString {
		t.Errorf("Expected name to be String, got %s", tr.Type.Kind)
	}
	if tr := res.StateTypes["TestApp.dynamic_val"]; tr.Type.Kind != TypeAny {
		t.Errorf("Expected dynamic_val to be Any, got %s", tr.Type.Kind)
	}
	if tr := res.StateTypes["TestApp.unrecognized"]; tr.Type.Kind != TypeUnknown {
		t.Errorf("Expected unrecognized to be Unknown, got %s", tr.Type.Kind)
	}

	// We expect 1 diagnostic based on the mutations above:
	// count (Int) = "hello" (String)
	if len(res.Diagnostics) != 1 {
		t.Errorf("Expected exactly 1 diagnostic, got %d", len(res.Diagnostics))
		for _, d := range res.Diagnostics {
			t.Logf("Diagnostic: %s", d.Message)
		}
	} else {
		if res.Diagnostics[0].Message != "TypeMismatch: Cannot assign String to state (expected Int)" {
			t.Errorf("Unexpected diagnostic 0: %s", res.Diagnostics[0].Message)
		}
	}
	
	// Ensure no panics for nil AST
	_ = analyzer.Analyze(nil)
}
