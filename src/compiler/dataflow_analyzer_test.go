package compiler

import (
	"testing"
)

func TestDataFlowAnalyzer(t *testing.T) {
	analyzer := NewDataFlowAnalyzer()

	ast := &FileAST{
		URI: "file:///test.tin",
		Components: []*Component{
			{
				Name: "TestApp",
				States: []*StateDecl{
					{Name: "count", Initial: "10"},
					{Name: "ref_b", Initial: "count"},
					{Name: "ref_c", Initial: "ref_b"},
					{Name: "tax", Initial: "2.5"},
					{Name: "total", Initial: "count + tax"},
					{Name: "c1", Initial: "c2"},
					{Name: "c2", Initial: "c1"},
					{Name: "missing", Initial: "does_not_exist"},
					{Name: "dyn", Initial: "{var}"}, 
					{Name: "ref_dyn", Initial: "dyn"},
					{Name: "x", Initial: "10"},
					{Name: "A", Initial: "10"},
					{Name: "B", Initial: "A + 5"},
					{Name: "C", Initial: "B + 2.5"},
					{Name: "D", Initial: "C + 1"},
					{Name: "long", Initial: "10 + 5 + 2.5 + 1"},
				},
				Mutations: []*DefNode{
					{
						FuncName: "Update",
						Mutations: []MutationNode{
							{StateKey: "x", Operator: "=", Value: "20"},
							{StateKey: "x", Operator: "=", Value: "10.5"},
						},
					},
				},
			},
		},
	}

	graph := analyzer.Analyze(ast)

	// A -> B -> C
	if graph.Nodes["TestApp.count"].Type.Type.Kind != TypeInt {
		t.Errorf("Expected count to be Int, got %s", graph.Nodes["TestApp.count"].Type.Type.Kind)
	}
	if graph.Nodes["TestApp.ref_b"].Type.Type.Kind != TypeInt {
		t.Errorf("Expected ref_b to be Int, got %s", graph.Nodes["TestApp.ref_b"].Type.Type.Kind)
	}
	if graph.Nodes["TestApp.ref_c"].Type.Type.Kind != TypeInt {
		t.Errorf("Expected ref_c to be Int, got %s", graph.Nodes["TestApp.ref_c"].Type.Type.Kind)
	}

	// Int + Float = Float
	if graph.Nodes["TestApp.tax"].Type.Type.Kind != TypeFloat {
		t.Errorf("Expected tax to be Float, got %s", graph.Nodes["TestApp.tax"].Type.Type.Kind)
	}
	if graph.Nodes["TestApp.total"].Type.Type.Kind != TypeFloat {
		t.Errorf("Expected total to be Float, got %s", graph.Nodes["TestApp.total"].Type.Type.Kind)
	}

	// Cycle
	if graph.Nodes["TestApp.c1"].Type.Type.Kind != TypeUnknown {
		t.Errorf("Expected c1 to be Unknown due to cycle, got %s", graph.Nodes["TestApp.c1"].Type.Type.Kind)
	}
	hasCycleDiag := false
	for _, d := range graph.Diagnostics {
		if d.Message == "CycleDetected: cyclic dependency detected at TestApp.c1" || 
		   d.Message == "CycleDetected: cyclic dependency detected at TestApp.c2" {
			hasCycleDiag = true
		}
	}
	if !hasCycleDiag {
		t.Errorf("Expected cycle detection diagnostic")
	}

	// Unresolved symbol
	if graph.Nodes["TestApp.missing"].Type.Type.Kind != TypeUnknown {
		t.Errorf("Expected missing to be Unknown, got %s", graph.Nodes["TestApp.missing"].Type.Type.Kind)
	}

	// Any propagation
	if graph.Nodes["TestApp.dyn"].Type.Type.Kind != TypeAny {
		t.Errorf("Expected dyn to be Any, got %s", graph.Nodes["TestApp.dyn"].Type.Type.Kind)
	}
	if graph.Nodes["TestApp.ref_dyn"].Type.Type.Kind != TypeAny {
		t.Errorf("Expected ref_dyn to be Any, got %s", graph.Nodes["TestApp.ref_dyn"].Type.Type.Kind)
	}

	// Reassignment Widening no longer permitted for state variables
	if graph.Nodes["TestApp.x"].Type.Type.Kind != TypeConflict {
		t.Errorf("Expected x to have TypeConflict upon float reassignment, got %s", graph.Nodes["TestApp.x"].Type.Type.Kind)
	}
	
	// A.5.2 chained requirements
	if graph.Nodes["TestApp.A"].Type.Type.Kind != TypeInt {
		t.Errorf("Expected A to be Int, got %s", graph.Nodes["TestApp.A"].Type.Type.Kind)
	}
	if graph.Nodes["TestApp.B"].Type.Type.Kind != TypeInt {
		t.Errorf("Expected B to be Int, got %s", graph.Nodes["TestApp.B"].Type.Type.Kind)
	}
	if graph.Nodes["TestApp.C"].Type.Type.Kind != TypeFloat {
		t.Errorf("Expected C to be Float, got %s", graph.Nodes["TestApp.C"].Type.Type.Kind)
	}
	if graph.Nodes["TestApp.D"].Type.Type.Kind != TypeFloat {
		t.Errorf("Expected D to be Float, got %s", graph.Nodes["TestApp.D"].Type.Type.Kind)
	}
	if graph.Nodes["TestApp.long"].Type.Type.Kind != TypeFloat {
		t.Errorf("Expected long to be Float, got %s", graph.Nodes["TestApp.long"].Type.Type.Kind)
	}
	
	// Ensure edge creation
	hasDep := false
	hasRead := false
	for _, e := range graph.Nodes["TestApp.ref_b"].Edges {
		if e.Kind == FlowDependency && e.TargetID == "TestApp.count" {
			hasDep = true
		}
	}
	for _, e := range graph.Nodes["TestApp.count"].Edges {
		if e.Kind == FlowRead && e.TargetID == "TestApp.ref_b" {
			hasRead = true
		}
	}
	if !hasDep {
		t.Errorf("Expected Dependency edge from ref_b to count")
	}
	if !hasRead {
		t.Errorf("Expected Read edge from count to ref_b")
	}
}

func TestDataFlowAnalyzerBranches(t *testing.T) {
	source := `
component Button(mode: String):
    state role = "unknown"
    state age = "18"

    if role == "admin":
        Text()
    else:
        Text()

    if age == "18":
        Text()
`
	lexer := NewLexer(source)
	parser := NewParser(lexer)
	ast := parser.ParseFileAST("file:///test.tin")

	if len(parser.Errors) > 0 {
		t.Fatalf("Parser failed: %v", parser.Errors)
	}

	analyzer := NewDataFlowAnalyzer()
	graph := analyzer.Analyze(ast)

	if len(graph.Diagnostics) > 0 {
		t.Fatalf("Expected 0 diagnostics, got: %v", graph.Diagnostics)
	}

	// Verify the original facts are intact at the end
	nodeRole := graph.Nodes["Button.role"]
	if nodeRole.Type.Type.Kind != TypeUnknown {
		t.Errorf("Expected role to be Unknown globally, got %s", nodeRole.Type.Type.Kind)
	}
}
