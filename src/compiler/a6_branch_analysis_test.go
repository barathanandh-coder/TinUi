package compiler

import (
	"testing"
)

// TestA6BranchNarrowingIsolation tests true-branch narrowing and verifies
// facts do not leak into false branch.
func TestA6BranchNarrowingIsolation(t *testing.T) {
	parentEnv := NewFlowEnvironment(nil)
	parentEnv.Set("comp.role", TypeResult{Type: TinType{Kind: TypeAny}, Confidence: ConfidenceInferred})

	trueEnv := parentEnv.Clone()
	falseEnv := parentEnv.Clone()

	// Narrow role in true branch
	trueEnv.Set("comp.role", TypeResult{Type: TinType{Kind: TypeString}, Confidence: ConfidenceInferred})

	// Verify true branch has narrowed type
	rTrue, okTrue := trueEnv.Get("comp.role")
	if !okTrue || rTrue.Type.Kind != TypeString {
		t.Fatalf("Expected true branch role to be String, got %s", rTrue.Type.Kind)
	}

	// Verify false branch did NOT receive the fact
	rFalse, okFalse := falseEnv.Get("comp.role")
	if !okFalse || rFalse.Type.Kind != TypeAny {
		t.Fatalf("Expected false branch role to remain Any, got %s", rFalse.Type.Kind)
	}

	// Learn fact in false branch and verify it does NOT leak into true branch
	falseEnv.Set("comp.fallback_code", TypeResult{Type: TinType{Kind: TypeInt}, Confidence: ConfidenceInferred})
	_, okFallbackInTrue := trueEnv.Get("comp.fallback_code")
	if okFallbackInTrue {
		t.Fatalf("Fact learned in false branch leaked into true branch")
	}
}

// TestA6NestedConditions tests hierarchical scope inheritance where inner
// branches inherit facts from outer enclosing branches.
func TestA6NestedConditions(t *testing.T) {
	rootEnv := NewFlowEnvironment(nil)
	rootEnv.Set("comp.level", TypeResult{Type: TinType{Kind: TypeAny}, Confidence: ConfidenceInferred})
	rootEnv.Set("comp.score", TypeResult{Type: TinType{Kind: TypeAny}, Confidence: ConfidenceInferred})

	outerTrue := rootEnv.Clone()
	outerTrue.Set("comp.level", TypeResult{Type: TinType{Kind: TypeString}, Confidence: ConfidenceInferred})

	innerTrue := outerTrue.Clone()
	innerTrue.Set("comp.score", TypeResult{Type: TinType{Kind: TypeInt}, Confidence: ConfidenceInferred})

	// Inner branch must see both outer and local facts
	lvl, okLvl := innerTrue.Get("comp.level")
	if !okLvl || lvl.Type.Kind != TypeString {
		t.Errorf("Expected inherited level to be String, got %s", lvl.Type.Kind)
	}
	sc, okSc := innerTrue.Get("comp.score")
	if !okSc || sc.Type.Kind != TypeInt {
		t.Errorf("Expected inner score to be Int, got %s", sc.Type.Kind)
	}

	// Outer branch must NOT see inner facts
	_, okInnerInOuter := outerTrue.Get("comp.score")
	if okInnerInOuter {
		scOuter, _ := outerTrue.Get("comp.score")
		if scOuter.Type.Kind == TypeInt {
			t.Errorf("Inner fact leaked to outer branch")
		}
	}
}

// TestA6EqualityAndRelationalComparisons tests that equality and relational
// operators properly narrow Any/Unknown types, respecting what the language
// syntax guarantees (==, != in source) and AST-level relational nodes (>, <, >=, <=).
func TestA6EqualityAndRelationalComparisons(t *testing.T) {
	analyzer := NewDataFlowAnalyzer()

	// 1. Language syntax guarantees: == and !=
	source := `
component MetricViewer():
    state status = "{dynamic_status}"
    state mode = "{dynamic_mode}"

    if status == "active":
        Text()

    if mode != "draft":
        Text()
`
	lexer := NewLexer(source)
	parser := NewParser(lexer)
	ast := parser.ParseFileAST("file:///metrics.tin")
	if len(parser.Errors) > 0 {
		t.Fatalf("Parse errors: %v", parser.Errors)
	}

	graph := analyzer.Analyze(ast)
	if len(graph.Diagnostics) > 0 {
		t.Fatalf("Unexpected diagnostics: %v", graph.Diagnostics)
	}

	// 2. AST-level relational comparisons (>, <, >=, <=)
	relationalAST := &FileAST{
		URI: "file:///relational.tin",
		Components: []*Component{
			{
				Name: "RelationalViewer",
				States: []*StateDecl{
					{Name: "count", Initial: "{dynamic_count}"},
					{Name: "ratio", Initial: "{dynamic_ratio}"},
				},
				RootNodes: []ASTNode{
					&ConditionalNode{
						ConditionVar: "count",
						Operator:     ">",
						Value:        "10",
						TrueBranch: []ASTNode{
							&Node{Name: "Text"},
						},
					},
					&ConditionalNode{
						ConditionVar: "ratio",
						Operator:     ">=",
						Value:        "3.14",
						TrueBranch: []ASTNode{
							&Node{Name: "Text"},
						},
					},
				},
			},
		},
	}
	relGraph := analyzer.Analyze(relationalAST)
	if len(relGraph.Diagnostics) > 0 {
		t.Fatalf("Unexpected diagnostics on relational AST: %v", relGraph.Diagnostics)
	}
}

// TestA6UnknownAndAnyNarrowing tests that both TypeUnknown and TypeAny
// safely narrow when an equality/relational guard is evaluated.
func TestA6UnknownAndAnyNarrowing(t *testing.T) {
	checker := NewComponentTypeChecker()
	workspace := NewSemanticWorkspace()

	importedAST := &FileAST{
		URI: "file:///target.tin",
		Components: []*Component{
			{
				Name: "StringConsumer",
				Props: []PropDecl{
					{Name: "val", TypeHint: "String"},
				},
			},
			{
				Name: "IntConsumer",
				Props: []PropDecl{
					{Name: "count", TypeHint: "Int"},
				},
			},
		},
	}
	workspace.AddFileAST(importedAST)

	sourceAST := &FileAST{
		URI: "file:///main.tin",
		Imports: []*ImportDecl{
			{Path: `"target.tin"`, Symbols: []string{"StringConsumer", "IntConsumer"}},
		},
		Components: []*Component{
			{
				Name: "App",
				States: []*StateDecl{
					{Name: "any_val", Initial: "{from_api}"},
					{Name: "unknown_val", Initial: "unresolved_ref"},
				},
				RootNodes: []ASTNode{
					&ConditionalNode{
						ConditionVar: "any_val",
						Operator:     "==",
						Value:        `"verified"`,
						TrueBranch: []ASTNode{
							&Node{
								Name: "StringConsumer",
								Attributes: map[string]string{
									"val": "{any_val}", // Valid when narrowed to String
								},
							},
						},
					},
					&ConditionalNode{
						ConditionVar: "unknown_val",
						Operator:     ">",
						Value:        "5",
						TrueBranch: []ASTNode{
							&Node{
								Name: "IntConsumer",
								Attributes: map[string]string{
									"count": "{unknown_val}", // Valid when narrowed to Int
								},
							},
						},
					},
				},
			},
		},
	}
	workspace.AddFileAST(sourceAST)

	diags := checker.CheckWorkspace(sourceAST, workspace)
	for _, d := range diags {
		if d.Code == CodeTypeConflict {
			t.Errorf("Unexpected TypeConflict: %s", d.Message)
		}
	}
}

// TestA6BranchMergeCompatibleWidening verifies that when branch types
// differ compatibly (Int vs Float), the merge safely widens to Float.
func TestA6BranchMergeCompatibleWidening(t *testing.T) {
	parentEnv := NewFlowEnvironment(nil)
	trueEnv := parentEnv.Clone()
	falseEnv := parentEnv.Clone()

	trueEnv.Set("comp.val", TypeResult{Type: TinType{Kind: TypeInt}, Confidence: ConfidenceInferred})
	falseEnv.Set("comp.val", TypeResult{Type: TinType{Kind: TypeFloat}, Confidence: ConfidenceInferred})

	graph := &DataFlowGraph{Diagnostics: make([]TypeDiagnostic, 0)}
	merged := MergeEnvironments(trueEnv, falseEnv, parentEnv, Range{}, graph)

	res, ok := merged.Get("comp.val")
	if !ok {
		t.Fatalf("Expected comp.val in merged environment")
	}
	if res.Type.Kind != TypeFloat {
		t.Errorf("Expected Int + Float merge to widen to Float, got %s", res.Type.Kind)
	}
	if len(graph.Diagnostics) != 0 {
		t.Errorf("Expected 0 diagnostics on compatible widening, got %d", len(graph.Diagnostics))
	}
}

// TestA6BranchMergeIncompatibleConflict verifies that when branches disagree
// with conflicting concrete types (String vs Int), MergeEnvironments records
// a TypeMismatch diagnostic and safely yields Unknown.
func TestA6BranchMergeIncompatibleConflict(t *testing.T) {
	parentEnv := NewFlowEnvironment(nil)
	trueEnv := parentEnv.Clone()
	falseEnv := parentEnv.Clone()

	trueEnv.Set("comp.val", TypeResult{Type: TinType{Kind: TypeString}, Confidence: ConfidenceInferred})
	falseEnv.Set("comp.val", TypeResult{Type: TinType{Kind: TypeInt}, Confidence: ConfidenceInferred})

	graph := &DataFlowGraph{Diagnostics: make([]TypeDiagnostic, 0)}
	merged := MergeEnvironments(trueEnv, falseEnv, parentEnv, Range{}, graph)

	res, ok := merged.Get("comp.val")
	if !ok {
		t.Fatalf("Expected comp.val in merged environment")
	}
	if res.Type.Kind != TypeUnknown {
		t.Errorf("Expected conflicting merge to degrade to Unknown, got %s", res.Type.Kind)
	}
	if len(graph.Diagnostics) != 1 {
		t.Fatalf("Expected 1 TypeMismatch diagnostic, got %d", len(graph.Diagnostics))
	}
	expectedMsg := "TypeMismatch: Conflicting branch types String and Int"
	if graph.Diagnostics[0].Message != expectedMsg {
		t.Errorf("Expected diagnostic %q, got %q", expectedMsg, graph.Diagnostics[0].Message)
	}
}

// TestA6BranchMergeAgreedTypes verifies that when both branches agree on a type,
// the post-conditional environment preserves that agreed type.
func TestA6BranchMergeAgreedTypes(t *testing.T) {
	parentEnv := NewFlowEnvironment(nil)
	trueEnv := parentEnv.Clone()
	falseEnv := parentEnv.Clone()

	trueEnv.Set("comp.tag", TypeResult{Type: TinType{Kind: TypeString}, Confidence: ConfidenceInferred})
	falseEnv.Set("comp.tag", TypeResult{Type: TinType{Kind: TypeString}, Confidence: ConfidenceInferred})

	graph := &DataFlowGraph{Diagnostics: make([]TypeDiagnostic, 0)}
	merged := MergeEnvironments(trueEnv, falseEnv, parentEnv, Range{}, graph)

	res, ok := merged.Get("comp.tag")
	if !ok || res.Type.Kind != TypeString {
		t.Errorf("Expected agreed type String to be preserved, got %s", res.Type.Kind)
	}
}

// TestA6BranchMergeDisagreedFallback verifies that when only one branch narrows,
// the merged environment retains the broader un-narrowed type.
func TestA6BranchMergeDisagreedFallback(t *testing.T) {
	parentEnv := NewFlowEnvironment(nil)
	parentEnv.Set("comp.data", TypeResult{Type: TinType{Kind: TypeAny}, Confidence: ConfidenceInferred})

	trueEnv := parentEnv.Clone()
	falseEnv := parentEnv.Clone()

	// Only true branch narrows
	trueEnv.Set("comp.data", TypeResult{Type: TinType{Kind: TypeString}, Confidence: ConfidenceInferred})

	graph := &DataFlowGraph{Diagnostics: make([]TypeDiagnostic, 0)}
	merged := MergeEnvironments(trueEnv, falseEnv, parentEnv, Range{}, graph)

	res, ok := merged.Get("comp.data")
	if !ok || res.Type.Kind != TypeAny {
		t.Errorf("Expected merged environment to retain Any when one branch didn't narrow, got %s", res.Type.Kind)
	}
}

// TestA6ParentFactPreservation verifies that facts present in the parent
// scope are preserved when a branch does not touch them.
func TestA6ParentFactPreservation(t *testing.T) {
	parentEnv := NewFlowEnvironment(nil)
	parentEnv.Set("comp.global_config", TypeResult{Type: TinType{Kind: TypeString}, Confidence: ConfidenceInferred})

	trueEnv := parentEnv.Clone()
	falseEnv := parentEnv.Clone()
	trueEnv.Set("comp.temp", TypeResult{Type: TinType{Kind: TypeInt}, Confidence: ConfidenceInferred})

	graph := &DataFlowGraph{Diagnostics: make([]TypeDiagnostic, 0)}
	merged := MergeEnvironments(trueEnv, falseEnv, parentEnv, Range{}, graph)

	cfg, ok := merged.Get("comp.global_config")
	if !ok || cfg.Type.Kind != TypeString {
		t.Errorf("Expected parent fact global_config to be preserved, got %s", cfg.Type.Kind)
	}
}

// TestA6DeterministicRepeatedAnalysis verifies that repeated analysis passes
// produce identical, deterministic results with zero state leakage.
func TestA6DeterministicRepeatedAnalysis(t *testing.T) {
	source := `
component RepeatCheck():
    state mode = "{api_mode}"
    if mode == "read_only":
        Text()
    else:
        Text()
`
	lexer := NewLexer(source)
	parser := NewParser(lexer)
	ast := parser.ParseFileAST("file:///repeat.tin")
	if len(parser.Errors) > 0 {
		t.Fatalf("Parse errors: %v", parser.Errors)
	}

	analyzer := NewDataFlowAnalyzer()
	pass1 := analyzer.Analyze(ast)
	pass2 := analyzer.Analyze(ast)

	if len(pass1.Diagnostics) != len(pass2.Diagnostics) {
		t.Errorf("Diagnostics count changed across passes: %d vs %d", len(pass1.Diagnostics), len(pass2.Diagnostics))
	}
	if len(pass1.Nodes) != len(pass2.Nodes) {
		t.Errorf("Nodes count changed across passes: %d vs %d", len(pass1.Nodes), len(pass2.Nodes))
	}
	for k, v1 := range pass1.Nodes {
		v2 := pass2.Nodes[k]
		if v2 == nil || v1.Type.Type.Kind != v2.Type.Type.Kind {
			t.Errorf("Node %s changed type across passes", k)
		}
	}
}
