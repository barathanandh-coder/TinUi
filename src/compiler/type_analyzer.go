package compiler

import (
	"fmt"
)

// TypeAnalysisResult represents the collected semantic type data for an AST.
type TypeAnalysisResult struct {
	StateTypes  map[string]TypeResult // Mapping from Component.State.Name to TypeResult
	Diagnostics []TypeDiagnostic
}

// TypeAnalyzer is a completely stateless analyzer that extracts types from a FileAST.
type TypeAnalyzer struct{}

func NewTypeAnalyzer() *TypeAnalyzer {
	return &TypeAnalyzer{}
}

// Analyze traverses a FileAST and produces an isolated TypeAnalysisResult.
func (a *TypeAnalyzer) Analyze(ast *FileAST) *TypeAnalysisResult {
	result := &TypeAnalysisResult{
		StateTypes:  make(map[string]TypeResult),
		Diagnostics: make([]TypeDiagnostic, 0),
	}

	if ast == nil {
		return result
	}

	for _, comp := range ast.Components {
		a.analyzeComponent(comp, result)
	}

	return result
}

func (a *TypeAnalyzer) analyzeComponent(comp *Component, result *TypeAnalysisResult) {
	if comp == nil {
		return
	}

	// 1. First pass: Initialize state types based on StateDecl
	for _, state := range comp.States {
		key := fmt.Sprintf("%s.%s", comp.Name, state.Name)
		tr := InferStateInitialization(state)
		result.StateTypes[key] = tr
	}

	// 2. Second pass: Evaluate mutations and check compatibility
	for _, def := range comp.Mutations {
		for _, mut := range def.Mutations {
			key := fmt.Sprintf("%s.%s", comp.Name, mut.StateKey)
			
			// Does this state exist in our map?
			originalType, exists := result.StateTypes[key]
			if !exists {
				continue
			}

			if mut.Operator == "=" {
				newTypeRes := InferAssignment(originalType, mut.Value, mut.Range)
				
				if newTypeRes.Diagnostic != nil {
					result.Diagnostics = append(result.Diagnostics, *newTypeRes.Diagnostic)
				}
				
				// Update state type in map
				result.StateTypes[key] = newTypeRes
			} else if mut.Operator == "+=" || mut.Operator == "-=" || mut.Operator == "*=" || mut.Operator == "/=" {
				// Mutating operators imply numeric operations
				rightTypeRes := InferLiteral(mut.Value, mut.Range)
				
				op := mut.Operator[:1] // strip the '='
				newTypeRes := InferExpression(originalType, op, rightTypeRes, mut.Range)
				
				if newTypeRes.Diagnostic != nil {
					result.Diagnostics = append(result.Diagnostics, *newTypeRes.Diagnostic)
				}
				
				if newTypeRes.Type.Kind != TypeConflict {
					if !CheckAssignmentCompatibility(originalType.Type, newTypeRes.Type) {
						diagnostic := TypeDiagnostic{
							Range:   mut.Range,
							Message: fmt.Sprintf("TypeConflict: Cannot assign result of %s to %s", newTypeRes.Type.Kind, originalType.Type.Kind),
						}
						result.Diagnostics = append(result.Diagnostics, diagnostic)
						newTypeRes.Type.Kind = TypeConflict
						newTypeRes.Diagnostic = &diagnostic
					}
				}
				
				result.StateTypes[key] = newTypeRes
			}
		}
	}

	// 3. Traverse RootNodes to infer literals from args and attributes (isolated)
	// Phase A.4.2: we just infer them to ensure no panics and valid operation.
	for _, rootNode := range comp.RootNodes {
		a.analyzeNodeArgsAndAttrs(rootNode)
	}
}

func (a *TypeAnalyzer) analyzeNodeArgsAndAttrs(node ASTNode) {
	if node == nil {
		return
	}

	switch n := node.(type) {
	case *Node:
		for _, arg := range n.Args {
			_ = InferLiteral(arg, n.Range)
		}
		for _, val := range n.Attributes {
			_ = InferLiteral(val, n.Range)
		}
		for _, child := range n.Children {
			a.analyzeNodeArgsAndAttrs(child)
		}
	case *ConditionalNode:
		for _, child := range n.TrueBranch {
			a.analyzeNodeArgsAndAttrs(child)
		}
		for _, child := range n.FalseBranch {
			a.analyzeNodeArgsAndAttrs(child)
		}
	case *ForNode:
		for _, child := range n.Body {
			a.analyzeNodeArgsAndAttrs(child)
		}
	case *HiddenWrapperNode:
		a.analyzeNodeArgsAndAttrs(n.Child)
	}
}
