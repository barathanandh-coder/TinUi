package compiler

import (
	"fmt"
)

// ComponentDiagnostic extends TypeDiagnostic for component specific errors
type ComponentDiagnostic struct {
	Range   Range
	Message string
}

// ComponentTypeChecker is a stateless analyzer for component invocations
type ComponentTypeChecker struct{}

func NewComponentTypeChecker() *ComponentTypeChecker {
	return &ComponentTypeChecker{}
}

// CheckLocalFile runs type checking on all component invocations within a single AST file
func (c *ComponentTypeChecker) CheckLocalFile(ast *FileAST) []ComponentDiagnostic {
	var diagnostics []ComponentDiagnostic
	if ast == nil {
		return diagnostics
	}

	// 1. Build a local registry of component signatures
	registry := make(map[string][]PropDecl)
	for _, comp := range ast.Components {
		registry[comp.Name] = comp.Props
	}

	// 2. Traverse all RootNodes in all components and check invocations
	for _, comp := range ast.Components {
		for _, rootNode := range comp.RootNodes {
			c.checkNode(rootNode, registry, &diagnostics)
		}
	}

	return diagnostics
}

func (c *ComponentTypeChecker) checkNode(node ASTNode, registry map[string][]PropDecl, diagnostics *[]ComponentDiagnostic) {
	if node == nil {
		return
	}

	switch n := node.(type) {
	case *Node:
		// Is this a component invocation?
		if len(n.Name) > 0 && n.Name[0] >= 'A' && n.Name[0] <= 'Z' {
			if props, exists := registry[n.Name]; exists {
				c.validateInvocation(n, props, diagnostics)
			}
		}
		
		for _, child := range n.Children {
			c.checkNode(child, registry, diagnostics)
		}
	case *ConditionalNode:
		for _, child := range n.TrueBranch {
			c.checkNode(child, registry, diagnostics)
		}
		for _, child := range n.FalseBranch {
			c.checkNode(child, registry, diagnostics)
		}
	case *ForNode:
		for _, child := range n.Body {
			c.checkNode(child, registry, diagnostics)
		}
	case *HiddenWrapperNode:
		c.checkNode(n.Child, registry, diagnostics)
	}
}

func (c *ComponentTypeChecker) validateInvocation(n *Node, props []PropDecl, diagnostics *[]ComponentDiagnostic) {
	supplied := make(map[string]bool)
	
	// Map positional args to named props
	for i, argVal := range n.Args {
		if i < len(props) {
			propName := props[i].Name
			if supplied[propName] {
				*diagnostics = append(*diagnostics, ComponentDiagnostic{
					Range:   n.Range,
					Message: fmt.Sprintf("DuplicateProperty: property %s supplied multiple times", propName),
				})
			}
			supplied[propName] = true
			c.validateProperty(props[i], argVal, n.Range, diagnostics)
		} else {
			*diagnostics = append(*diagnostics, ComponentDiagnostic{
				Range:   n.Range,
				Message: fmt.Sprintf("UnknownProperty: unexpected positional argument %d", i),
			})
		}
	}

	// Map named attributes
	for attrName, attrVal := range n.Attributes {
		if supplied[attrName] {
			*diagnostics = append(*diagnostics, ComponentDiagnostic{
				Range:   n.Range,
				Message: fmt.Sprintf("DuplicateProperty: property %s supplied multiple times", attrName),
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
				Range:   n.Range,
				Message: fmt.Sprintf("UnknownProperty: property %s is not defined on %s", attrName, n.Name),
			})
		} else {
			c.validateProperty(*matchedProp, attrVal, n.Range, diagnostics)
		}
	}

	// Check for missing required properties
	for _, p := range props {
		if !supplied[p.Name] {
			// It is required if it has a TypeHint but no Default
			if p.TypeHint != "" && p.Default == "" {
				*diagnostics = append(*diagnostics, ComponentDiagnostic{
					Range:   n.Range,
					Message: fmt.Sprintf("MissingProperty: required property %s is missing", p.Name),
				})
			}
		}
	}
}

func (c *ComponentTypeChecker) validateProperty(prop PropDecl, val string, rng Range, diagnostics *[]ComponentDiagnostic) {
	// Determine expected type
	var expectedType TinType
	if prop.TypeHint == "" {
		expectedType = TinType{Kind: TypeAny}
	} else {
		expectedType = TinType{Kind: TypeKind(prop.TypeHint)} // E.g., "Bool", "String", "Int"
	}

	// Determine supplied type
	suppliedRes := InferLiteral(val, rng)
	suppliedType := suppliedRes.Type

	if !CheckAssignmentCompatibility(expectedType, suppliedType) {
		*diagnostics = append(*diagnostics, ComponentDiagnostic{
			Range:   rng,
			Message: fmt.Sprintf("TypeConflict: Cannot assign %s to %s for property %s", suppliedType.Kind, expectedType.Kind, prop.Name),
		})
	}
}
