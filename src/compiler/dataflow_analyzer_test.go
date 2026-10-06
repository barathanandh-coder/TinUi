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
	if graph.Nodes["TestApp.count"].Type.Kind != TypeInt {
		t.Errorf("Expected count to be Int, got %s", graph.Nodes["TestApp.count"].Type.Kind)
	}
	if graph.Nodes["TestApp.ref_b"].Type.Kind != TypeInt {
		t.Errorf("Expected ref_b to be Int, got %s", graph.Nodes["TestApp.ref_b"].Type.Kind)
	}
	if graph.Nodes["TestApp.ref_c"].Type.Kind != TypeInt {
		t.Errorf("Expected ref_c to be Int, got %s", graph.Nodes["TestApp.ref_c"].Type.Kind)
	}

	// Int + Float = Float
	if graph.Nodes["TestApp.tax"].Type.Kind != TypeFloat {
		t.Errorf("Expected tax to be Float, got %s", graph.Nodes["TestApp.tax"].Type.Kind)
	}
	if graph.Nodes["TestApp.total"].Type.Kind != TypeFloat {
		t.Errorf("Expected total to be Float, got %s", graph.Nodes["TestApp.total"].Type.Kind)
	}

	// Cycle
	if graph.Nodes["TestApp.c1"].Type.Kind != TypeUnknown {
		t.Errorf("Expected c1 to be Unknown due to cycle, got %s", graph.Nodes["TestApp.c1"].Type.Kind)
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
	if graph.Nodes["TestApp.missing"].Type.Kind != TypeUnknown {
		t.Errorf("Expected missing to be Unknown, got %s", graph.Nodes["TestApp.missing"].Type.Kind)
	}

	// Any propagation
	if graph.Nodes["TestApp.dyn"].Type.Kind != TypeAny {
		t.Errorf("Expected dyn to be Any, got %s", graph.Nodes["TestApp.dyn"].Type.Kind)
	}
	if graph.Nodes["TestApp.ref_dyn"].Type.Kind != TypeAny {
		t.Errorf("Expected ref_dyn to be Any, got %s", graph.Nodes["TestApp.ref_dyn"].Type.Kind)
	}

	// Reassignment Widening
	if graph.Nodes["TestApp.x"].Type.Kind != TypeFloat {
		t.Errorf("Expected x to widen to Float, got %s", graph.Nodes["TestApp.x"].Type.Kind)
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
