package compiler

import (
	"fmt"
	"strings"
)

type DiagnosticSeverity int

const (
	SeverityError DiagnosticSeverity = 1
	SeverityWarning DiagnosticSeverity = 2
)

type DiagnosticCode string

const (
	CodeMissingProperty          DiagnosticCode = "MissingProperty"
	CodeUnknownProperty          DiagnosticCode = "UnknownProperty"
	CodeDuplicateProperty        DiagnosticCode = "DuplicateProperty"
	CodeTypeConflict             DiagnosticCode = "TypeConflict"
	CodeUnresolvedComponent      DiagnosticCode = "UnresolvedComponentReference"
)

// ComponentDiagnostic extends TypeDiagnostic for component specific errors
type ComponentDiagnostic struct {
	Code          DiagnosticCode
	Severity      DiagnosticSeverity
	Range         Range
	Message       string
	ComponentName string
	PropertyName  string
	ExpectedType  string
	ActualType    string
}

// ComponentTypeChecker is a stateless analyzer for component invocations
type ComponentTypeChecker struct{}

func NewComponentTypeChecker() *ComponentTypeChecker {
	return &ComponentTypeChecker{}
}

// CheckWorkspace runs type checking on all component invocations within a single AST file, resolving signatures via the workspace.
func (c *ComponentTypeChecker) CheckWorkspace(ast *FileAST, workspace *SemanticWorkspace) []ComponentDiagnostic {
	var diagnostics []ComponentDiagnostic
	if ast == nil || workspace == nil {
		return diagnostics
	}

	// A.6 Contextual Data-Flow Graph
	dfAnalyzer := NewDataFlowAnalyzer()
	dfGraph := dfAnalyzer.Analyze(ast)

	// 1. Build local import resolution map
	importMap := make(map[string]string)
	for _, imp := range ast.Imports {
		for _, sym := range imp.Symbols {
			importMap[sym] = buildImportID(ast.URI, imp.Path, sym)
		}
	}

	resolveTargetID := func(name string) string {
		if extID, ok := importMap[name]; ok {
			return extID
		}
		return buildSymbolID(ast.URI, name)
	}

	visiting := make(map[string]bool)

	// 2. Traverse all RootNodes in all components and check invocations
	for _, comp := range ast.Components {
		for _, rootNode := range comp.RootNodes {
			env := NewFlowEnvironment(nil)
			c.checkNode(comp.Name, rootNode, resolveTargetID, workspace, visiting, &diagnostics, env, dfGraph)
		}
	}

	return diagnostics
}

func (c *ComponentTypeChecker) checkNode(compName string, node ASTNode, resolveTargetID func(string) string, workspace *SemanticWorkspace, visiting map[string]bool, diagnostics *[]ComponentDiagnostic, env *FlowEnvironment, graph *DataFlowGraph) {
	if node == nil {
		return
	}

	switch n := node.(type) {
	case *Node:
		// Is this a component invocation?
		if len(n.Name) > 0 && n.Name[0] >= 'A' && n.Name[0] <= 'Z' {
			targetID := resolveTargetID(n.Name)

			if visiting[targetID] {
				// Cycle detected, fail softly
				return
			}

			visiting[targetID] = true
			defer func() { visiting[targetID] = false }()

			sym := workspace.ResolveSymbol(targetID)
			if sym == nil || sym.IsUnresolved {
				*diagnostics = append(*diagnostics, ComponentDiagnostic{
					Code:          CodeUnresolvedComponent,
					Severity:      SeverityError,
					Range:         n.Range,
					Message:       fmt.Sprintf("UnresolvedComponentReference: %s", n.Name),
					ComponentName: n.Name,
				})
			} else {
				c.validateInvocation(compName, n, sym.Props, diagnostics, env, graph)
			}
		}
		
		for _, child := range n.Children {
			c.checkNode(compName, child, resolveTargetID, workspace, visiting, diagnostics, env, graph)
		}
	case *ConditionalNode:
		stateKey := fmt.Sprintf("%s.%s", compName, n.ConditionVar)

		trueEnv := env.Clone()
		falseEnv := env.Clone()

		var currentType TypeResult
		if t, ok := env.Get(stateKey); ok {
			currentType = t
		} else if gNode, ok := graph.Nodes[stateKey]; ok {
			currentType = gNode.Type
		} else {
			currentType = TypeResult{Type: TinType{Kind: TypeUnknown}, Confidence: ConfidenceUnknown}
		}

		// Type Narrowing
		if n.Operator == "==" || n.Operator == ">" || n.Operator == "<" || n.Operator == ">=" || n.Operator == "<=" {
			litRes := InferLiteral(n.Value, n.Range)
			if litRes.Type.Kind == TypeUnknown && n.Value != "" {
				otherKey := fmt.Sprintf("%s.%s", compName, n.Value)
				if otherType, ok := env.Get(otherKey); ok {
					litRes = otherType
				} else if otherNode, ok := graph.Nodes[otherKey]; ok {
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

		for _, child := range n.TrueBranch {
			c.checkNode(compName, child, resolveTargetID, workspace, visiting, diagnostics, trueEnv, graph)
		}
		for _, child := range n.FalseBranch {
			c.checkNode(compName, child, resolveTargetID, workspace, visiting, diagnostics, falseEnv, graph)
		}
	case *ForNode:
		for _, child := range n.Body {
			c.checkNode(compName, child, resolveTargetID, workspace, visiting, diagnostics, env, graph)
		}
	case *HiddenWrapperNode:
		c.checkNode(compName, n.Child, resolveTargetID, workspace, visiting, diagnostics, env, graph)
	}
}

func (c *ComponentTypeChecker) validateInvocation(compName string, n *Node, props []PropDecl, diagnostics *[]ComponentDiagnostic, env *FlowEnvironment, graph *DataFlowGraph) {
	supplied := make(map[string]bool)
	
	// Map positional args to named props
	for i, argVal := range n.Args {
		if i < len(props) {
			propName := props[i].Name
			if supplied[propName] {
				*diagnostics = append(*diagnostics, ComponentDiagnostic{
					Code:          CodeDuplicateProperty,
					Severity:      SeverityError,
					Range:         n.Range,
					Message:       fmt.Sprintf("DuplicateProperty: property %s supplied multiple times", propName),
					ComponentName: n.Name,
					PropertyName:  propName,
				})
			}
			supplied[propName] = true
			c.validateProperty(compName, n.Name, props[i], argVal, n.Range, diagnostics, env, graph)
		} else {
			*diagnostics = append(*diagnostics, ComponentDiagnostic{
				Code:          CodeUnknownProperty,
				Severity:      SeverityError,
				Range:         n.Range,
				Message:       fmt.Sprintf("UnknownProperty: unexpected positional argument %d", i),
				ComponentName: n.Name,
			})
		}
	}

	// Map named attributes
	for attrName, attrVal := range n.Attributes {
		if supplied[attrName] {
			*diagnostics = append(*diagnostics, ComponentDiagnostic{
				Code:          CodeDuplicateProperty,
				Severity:      SeverityError,
				Range:         n.Range,
				Message:       fmt.Sprintf("DuplicateProperty: property %s supplied multiple times", attrName),
				ComponentName: n.Name,
				PropertyName:  attrName,
			})
			// Even if duplicate, we validate the latest one provided
		}
		
		supplied[attrName] = true
		
		// Find property signature
		var matchedProp *PropDecl
		for i := range props {
			if props[i].Name == attrName {
				matchedProp = &props[i]
				break
			}
		}
		
		if matchedProp == nil {
			*diagnostics = append(*diagnostics, ComponentDiagnostic{
				Code:          CodeUnknownProperty,
				Severity:      SeverityError,
				Range:         n.Range,
				Message:       fmt.Sprintf("UnknownProperty: property %s is not defined on %s", attrName, n.Name),
				ComponentName: n.Name,
				PropertyName:  attrName,
			})
		} else {
			c.validateProperty(compName, n.Name, *matchedProp, attrVal, n.Range, diagnostics, env, graph)
		}
	}

	// Check for missing required properties
	for _, p := range props {
		if !supplied[p.Name] {
			// It is required if it has a TypeHint but no Default
			if p.TypeHint != "" && p.Default == "" {
				*diagnostics = append(*diagnostics, ComponentDiagnostic{
					Code:          CodeMissingProperty,
					Severity:      SeverityError,
					Range:         n.Range,
					Message:       fmt.Sprintf("MissingProperty: required property %s is missing", p.Name),
					ComponentName: n.Name,
					PropertyName:  p.Name,
					ExpectedType:  p.TypeHint,
				})
			}
		}
	}
}

func (c *ComponentTypeChecker) validateProperty(parentCompName string, compName string, prop PropDecl, val string, rng Range, diagnostics *[]ComponentDiagnostic, env *FlowEnvironment, graph *DataFlowGraph) {
	// Determine expected type
	var expectedType TinType
	if prop.TypeHint == "" {
		expectedType = TinType{Kind: TypeAny}
	} else {
		expectedType = TinType{Kind: TypeKind(prop.TypeHint)} // E.g., "Bool", "String", "Int"
	}

	// Determine supplied type
	suppliedRes := InferLiteral(val, rng)

	// A.6 Contextual Binding Lookup
	if suppliedRes.Type.Kind == TypeAny && strings.HasPrefix(val, "{") && strings.HasSuffix(val, "}") {
		stateName := val[1 : len(val)-1]
		stateKey := fmt.Sprintf("%s.%s", parentCompName, stateName)

		if t, ok := env.Get(stateKey); ok {
			suppliedRes = t
		} else if gNode, ok := graph.Nodes[stateKey]; ok {
			suppliedRes = gNode.Type
		}
	}

	suppliedType := suppliedRes.Type

	if !CheckAssignmentCompatibility(expectedType, suppliedType) {
		*diagnostics = append(*diagnostics, ComponentDiagnostic{
			Code:          CodeTypeConflict,
			Severity:      SeverityError,
			Range:         rng,
			Message:       fmt.Sprintf("TypeMismatch: Cannot assign %s to %s for property %s", readableType(suppliedType.Kind), readableType(expectedType.Kind), prop.Name),
			ComponentName: compName,
			PropertyName:  prop.Name,
			ExpectedType:  string(expectedType.Kind),
			ActualType:    string(suppliedType.Kind),
		})
	}
}
