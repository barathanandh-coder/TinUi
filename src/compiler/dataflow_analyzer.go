package compiler

import (
	"fmt"
	"strings"
)

// FlowKind indicates the type of data movement
type FlowKind string

const (
	FlowDefinition FlowKind = "Definition"
	FlowRead       FlowKind = "Read"
	FlowAssignment FlowKind = "Assignment"
	FlowMutation   FlowKind = "Mutation"
	FlowDependency FlowKind = "Dependency"
)

// FlowEdge represents a directed data-flow link
type FlowEdge struct {
	Kind     FlowKind
	TargetID string
	Range    Range
}

// FlowNode represents a node in the Data-Flow graph
type FlowNode struct {
	ID    string
	Range Range
	Type  TypeResult
	Edges []FlowEdge
}

// DataFlowGraph represents the isolated data-flow network
type DataFlowGraph struct {
	Nodes       map[string]*FlowNode
	Diagnostics []TypeDiagnostic
}

// FlowEnvironment scopes type facts for branch-sensitive analysis
type FlowEnvironment struct {
	parent *FlowEnvironment
	facts  map[string]TypeResult
}

func NewFlowEnvironment(parent *FlowEnvironment) *FlowEnvironment {
	return &FlowEnvironment{
		parent: parent,
		facts:  make(map[string]TypeResult),
	}
}

func (e *FlowEnvironment) Get(key string) (TypeResult, bool) {
	if t, ok := e.facts[key]; ok {
		return t, true
	}
	if e.parent != nil {
		return e.parent.Get(key)
	}
	return TypeResult{}, false
}

func (e *FlowEnvironment) Set(key string, t TypeResult) {
	e.facts[key] = t
}

func (e *FlowEnvironment) Clone() *FlowEnvironment {
	child := NewFlowEnvironment(e)
	return child
}

func MergeEnvironments(trueEnv, falseEnv, parentEnv *FlowEnvironment, rng Range, graph *DataFlowGraph) *FlowEnvironment {
	merged := NewFlowEnvironment(parentEnv)

	// Collect all unique keys from both branches
	keys := make(map[string]bool)
	for k := range trueEnv.facts {
		keys[k] = true
	}
	for k := range falseEnv.facts {
		keys[k] = true
	}

	for k := range keys {
		tTrue, okTrue := trueEnv.facts[k]
		if !okTrue {
			if t, ok := parentEnv.Get(k); ok {
				tTrue = t
			} else if graph != nil && graph.Nodes[k] != nil {
				tTrue = graph.Nodes[k].Type
			} else {
				tTrue = TypeResult{Type: TinType{Kind: TypeUnknown}, Confidence: ConfidenceUnknown}
			}
		}

		tFalse, okFalse := falseEnv.facts[k]
		if !okFalse {
			if t, ok := parentEnv.Get(k); ok {
				tFalse = t
			} else if graph != nil && graph.Nodes[k] != nil {
				tFalse = graph.Nodes[k].Type
			} else {
				tFalse = TypeResult{Type: TinType{Kind: TypeUnknown}, Confidence: ConfidenceUnknown}
			}
		}

		mergedType := mergeTypes(tTrue, tFalse, rng, graph)
		merged.Set(k, mergedType)
	}

	return merged
}

func mergeTypes(t1, t2 TypeResult, rng Range, graph *DataFlowGraph) TypeResult {
	k1 := t1.Type.Kind
	if k1 == "" {
		k1 = TypeUnknown
	}
	k2 := t2.Type.Kind
	if k2 == "" {
		k2 = TypeUnknown
	}

	if k1 == k2 {
		return t1
	}

	if k1 == TypeUnknown || k2 == TypeUnknown {
		return TypeResult{Type: TinType{Kind: TypeUnknown}, Confidence: ConfidenceUnknown}
	}

	if k1 == TypeAny || k2 == TypeAny {
		return TypeResult{Type: TinType{Kind: TypeAny}, Confidence: ConfidenceInferred}
	}

	// Float widens Int
	if (k1 == TypeInt && k2 == TypeFloat) || (k1 == TypeFloat && k2 == TypeInt) {
		return TypeResult{Type: TinType{Kind: TypeFloat}, Confidence: ConfidenceInferred}
	}

	// Conflict
	diag := TypeDiagnostic{
		Range:   rng,
		Message: fmt.Sprintf("TypeMismatch: Conflicting branch types %s and %s", readableType(k1), readableType(k2)),
	}
	if graph != nil {
		graph.Diagnostics = append(graph.Diagnostics, diag)
	}
	return TypeResult{Type: TinType{Kind: TypeUnknown}, Confidence: ConfidenceInferred, Diagnostic: &diag} // Merging conflict to Unknown per strict rules
}

// DataFlowAnalyzer orchestrates data-flow mapping
type DataFlowAnalyzer struct {
	graph *DataFlowGraph
}

func NewDataFlowAnalyzer() *DataFlowAnalyzer {
	return &DataFlowAnalyzer{
		graph: &DataFlowGraph{
			Nodes:       make(map[string]*FlowNode),
			Diagnostics: make([]TypeDiagnostic, 0),
		},
	}
}

// Analyze constructs a DataFlowGraph from an AST
func (a *DataFlowAnalyzer) Analyze(ast *FileAST) *DataFlowGraph {
	if ast == nil {
		return a.graph
	}

	ctx := &AnalysisContext{
		TypeCache: make(map[string]TypeResult),
	}

	for _, comp := range ast.Components {
		a.analyzeComponent(comp, ctx)
	}

	return a.graph
}

// AnalysisContext holds per-analysis-pass transient state
type AnalysisContext struct {
	TypeCache map[string]TypeResult
}

func (a *DataFlowAnalyzer) analyzeComponent(comp *Component, ctx *AnalysisContext) {
	if comp == nil {
		return
	}

	stateInitializers := make(map[string]string)

	for _, state := range comp.States {
		key := fmt.Sprintf("%s.%s", comp.Name, state.Name)
		a.graph.Nodes[key] = &FlowNode{
			ID:    key,
			Range: state.Range,
			Type:  TypeResult{Type: TinType{Kind: TypeUnknown}, Confidence: ConfidenceUnknown},
			Edges: []FlowEdge{
				{Kind: FlowDefinition, TargetID: key, Range: state.Range},
			},
		}
		stateInitializers[key] = state.Initial
	}

	visited := make(map[string]bool)
	visiting := make(map[string]bool)

	var resolveType func(key string) TypeResult
	resolveType = func(key string) TypeResult {
		if visiting[key] {
			diag := TypeDiagnostic{
				Range:   a.graph.Nodes[key].Range,
				Message: fmt.Sprintf("CycleDetected: cyclic dependency detected at %s", key),
			}
			a.graph.Diagnostics = append(a.graph.Diagnostics, diag)
			return TypeResult{Type: TinType{Kind: TypeUnknown}, Confidence: ConfidenceUnknown, Diagnostic: &diag}
		}

		if cached, ok := ctx.TypeCache[key]; ok {
			return cached
		}

		visiting[key] = true
		defer func() {
			visiting[key] = false
			visited[key] = true
		}()

		initialValue := stateInitializers[key]
		
		litRes := InferLiteral(initialValue, a.graph.Nodes[key].Range)
		
		if litRes.Type.Kind != TypeUnknown {
			a.graph.Nodes[key].Type = litRes
			ctx.TypeCache[key] = litRes
			return litRes
		}
		
		tokens := strings.Fields(initialValue)
		
		if len(tokens) == 0 {
			a.graph.Nodes[key].Type = TypeResult{Type: TinType{Kind: TypeUnknown}, Confidence: ConfidenceUnknown}
			ctx.TypeCache[key] = a.graph.Nodes[key].Type
			return a.graph.Nodes[key].Type
		}
		
		// Evaluate first token
		var currentType TypeResult
		firstTok := tokens[0]
		firstDepKey := fmt.Sprintf("%s.%s", comp.Name, firstTok)
		
		if firstNode, exists := a.graph.Nodes[firstDepKey]; exists {
			a.graph.Nodes[key].Edges = append(a.graph.Nodes[key].Edges, FlowEdge{
				Kind: FlowDependency, TargetID: firstDepKey, Range: a.graph.Nodes[key].Range,
			})
			firstNode.Edges = append(firstNode.Edges, FlowEdge{
				Kind: FlowRead, TargetID: key, Range: a.graph.Nodes[key].Range,
			})
			currentType = resolveType(firstDepKey)
		} else {
			currentType = InferLiteral(firstTok, a.graph.Nodes[key].Range)
		}
		
		// Evaluate remaining operator-operand pairs linearly
		for i := 1; i < len(tokens)-1; i += 2 {
			op := tokens[i]
			nextTok := tokens[i+1]
			nextDepKey := fmt.Sprintf("%s.%s", comp.Name, nextTok)
			var nextType TypeResult
			
			if nextNode, exists := a.graph.Nodes[nextDepKey]; exists {
				a.graph.Nodes[key].Edges = append(a.graph.Nodes[key].Edges, FlowEdge{
					Kind: FlowDependency, TargetID: nextDepKey, Range: a.graph.Nodes[key].Range,
				})
				nextNode.Edges = append(nextNode.Edges, FlowEdge{
					Kind: FlowRead, TargetID: key, Range: a.graph.Nodes[key].Range,
				})
				nextType = resolveType(nextDepKey)
			} else {
				nextType = InferLiteral(nextTok, a.graph.Nodes[key].Range)
			}
			
			// Delegate strictly to Type Engine
			currentType = InferExpression(currentType, op, nextType, a.graph.Nodes[key].Range)
			if currentType.Diagnostic != nil {
				a.graph.Diagnostics = append(a.graph.Diagnostics, *currentType.Diagnostic)
			}
		}
		
		a.graph.Nodes[key].Type = currentType
		ctx.TypeCache[key] = currentType
		return currentType
	}

	// Resolve initial states
	for _, state := range comp.States {
		key := fmt.Sprintf("%s.%s", comp.Name, state.Name)
		resolveType(key)
	}
	
	// Evaluate mutations
	for _, def := range comp.Mutations {
		for _, mut := range def.Mutations {
			key := fmt.Sprintf("%s.%s", comp.Name, mut.StateKey)
			
			if node, exists := a.graph.Nodes[key]; exists {
				originalType := node.Type
				
				var newTypeRes TypeResult
				if mut.Operator == "=" {
					node.Edges = append(node.Edges, FlowEdge{
						Kind:     FlowAssignment,
						TargetID: key,
						Range:    mut.Range,
					})
					newTypeRes = InferAssignment(originalType, mut.Value, mut.Range)
				} else if mut.Operator == "+=" || mut.Operator == "-=" || mut.Operator == "*=" || mut.Operator == "/=" {
					node.Edges = append(node.Edges, FlowEdge{
						Kind:     FlowMutation,
						TargetID: key,
						Range:    mut.Range,
					})
					rightTypeRes := InferLiteral(mut.Value, mut.Range)
					op := mut.Operator[:1]
					exprRes := InferExpression(originalType, op, rightTypeRes, mut.Range)
					
					if exprRes.Diagnostic != nil {
						a.graph.Diagnostics = append(a.graph.Diagnostics, *exprRes.Diagnostic)
					}
					
					if exprRes.Type.Kind != TypeConflict {
						if !CheckAssignmentCompatibility(originalType.Type, exprRes.Type) {
							diagnostic := TypeDiagnostic{
								Range:   mut.Range,
								Message: fmt.Sprintf("TypeMismatch: Cannot assign %s to state (expected %s)", readableType(exprRes.Type.Kind), readableType(originalType.Type.Kind)),
							}
							a.graph.Diagnostics = append(a.graph.Diagnostics, diagnostic)
							exprRes.Type.Kind = TypeConflict
							exprRes.Diagnostic = &diagnostic
						}
					}
					newTypeRes = exprRes
				}
				
				if newTypeRes.Diagnostic != nil {
					a.graph.Diagnostics = append(a.graph.Diagnostics, *newTypeRes.Diagnostic)
				}
				
				if newTypeRes.Type.Kind != TypeConflict {
					node.Type = newTypeRes // Widening applied
				} else {
					node.Type = newTypeRes // Preserve conflict
				}
			}
		}
	}
	// A.6 Phase: Traverse UI nodes with FlowEnvironment to enrich contextual facts
	rootEnv := NewFlowEnvironment(nil)
	a.analyzeUIBlock(comp.Name, comp.RootNodes, rootEnv)
}

func (a *DataFlowAnalyzer) analyzeUIBlock(compName string, nodes []ASTNode, env *FlowEnvironment) *FlowEnvironment {
	currentEnv := env
	for _, node := range nodes {
		currentEnv = a.analyzeUINode(compName, node, currentEnv)
	}
	return currentEnv
}

func (a *DataFlowAnalyzer) analyzeUINode(compName string, node ASTNode, env *FlowEnvironment) *FlowEnvironment {
	if node == nil {
		return env
	}

	switch n := node.(type) {
	case *Node:
		a.analyzeUIBlock(compName, n.Children, env)
		return env
	case *ConditionalNode:
		stateKey := fmt.Sprintf("%s.%s", compName, n.ConditionVar)

		trueEnv := env.Clone()
		falseEnv := env.Clone()

		// 1. Fetch current known type
		var currentType TypeResult
		if t, ok := env.Get(stateKey); ok {
			currentType = t
		} else if gNode, ok := a.graph.Nodes[stateKey]; ok {
			currentType = gNode.Type
		} else {
			currentType = TypeResult{Type: TinType{Kind: TypeUnknown}, Confidence: ConfidenceUnknown}
		}

		// 2. Type Narrowing (only if safe based on existing semantics)
		// We only narrow on strict equality to a literal if the current type is Any/Unknown.
		if n.Operator == "==" || n.Operator == ">" || n.Operator == "<" || n.Operator == ">=" || n.Operator == "<=" {
			litRes := InferLiteral(n.Value, n.Range)
			if litRes.Type.Kind == TypeUnknown && n.Value != "" {
				otherKey := fmt.Sprintf("%s.%s", compName, n.Value)
				if otherType, ok := env.Get(otherKey); ok {
					litRes = otherType
				} else if otherNode, ok := a.graph.Nodes[otherKey]; ok {
					litRes = otherNode.Type
				} else {
					litRes = InferLiteral(`"`+n.Value+`"`, n.Range)
				}
			}
			if currentType.Type.Kind == TypeAny || currentType.Type.Kind == TypeUnknown {
				if litRes.Type.Kind != TypeUnknown {
					narrowedType := TypeResult{Type: TinType{Kind: litRes.Type.Kind}, Confidence: ConfidenceInferred}
					trueEnv.Set(stateKey, narrowedType)
				}
			}
		}

		// Traverse Branches
		endTrueEnv := a.analyzeUIBlock(compName, n.TrueBranch, trueEnv)
		endFalseEnv := a.analyzeUIBlock(compName, n.FalseBranch, falseEnv)

		// Merge Post-Conditional Environment
		return MergeEnvironments(endTrueEnv, endFalseEnv, env, n.Range, a.graph)

	case *ForNode:
		a.analyzeUIBlock(compName, n.Body, env)
		return env
	case *HiddenWrapperNode:
		return a.analyzeUINode(compName, n.Child, env)
	}

	return env
}
