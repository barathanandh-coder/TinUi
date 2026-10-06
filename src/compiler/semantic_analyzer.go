package compiler

import (
	"fmt"
	"strings"
)

type SymbolKind string

const (
	SymbolComponent  SymbolKind = "Component"
	SymbolState      SymbolKind = "State"
	SymbolDefinition SymbolKind = "Definition"
	SymbolEvent      SymbolKind = "Event"
)

type RelationshipKind string

const (
	RelRenders  RelationshipKind = "renders"
	RelReads    RelationshipKind = "reads"
	RelTriggers RelationshipKind = "triggers"
	RelImports  RelationshipKind = "imports"
)

type Relationship struct {
	Kind     RelationshipKind `json:"kind"`
	TargetID string           `json:"target_id"`
	Range    Range            `json:"range"`
}

type Symbol struct {
	ID            string         `json:"id"`
	Kind          SymbolKind     `json:"kind"`
	Name          string         `json:"name"`
	Range         Range          `json:"range"`
	ParentID      string         `json:"parent_id,omitempty"`
	Relationships []Relationship `json:"relationships"`
	IsUnresolved  bool           `json:"is_unresolved"`
}

type File struct {
	URI     string             `json:"uri"`
	Imports []Relationship     `json:"imports"`
	Symbols map[string]*Symbol `json:"symbols"`
}

type Project struct {
	RootURI string           `json:"root_uri"`
	Files   map[string]*File `json:"files"`
}

func buildSymbolID(uri string, name string) string {
	base := strings.Replace(uri, "file://", "tinpy://", 1)
	return fmt.Sprintf("%s#%s", base, name)
}

func buildImportID(uri string, importPath string, symbolName string) string {
	// Simple resolution: if we import "ui/card.tin" from "file:///project/src/main.tin"
	// For this analyzer, we will just use tinpy://<importPath>#<symbolName>
	// In a real robust system, this would resolve relative paths.
	// We assume absolute or workspace-relative for this phase.
	cleanPath := strings.Trim(importPath, "\"")
	return fmt.Sprintf("tinpy://%s#%s", cleanPath, symbolName)
}

// AnalyzeFile takes an AST and produces a Semantic Graph File node.
func AnalyzeFile(ast *FileAST) *File {
	f := &File{
		URI:     ast.URI,
		Imports: []Relationship{},
		Symbols: make(map[string]*Symbol),
	}

	importMap := make(map[string]string)
	
	for _, imp := range ast.Imports {
		for _, sym := range imp.Symbols {
			targetID := buildImportID(ast.URI, imp.Path, sym)
			importMap[sym] = targetID
			
			f.Imports = append(f.Imports, Relationship{
				Kind:     RelImports,
				TargetID: targetID,
				Range:    imp.Range,
			})
		}
	}

	resolveTargetID := func(name string) string {
		if extID, ok := importMap[name]; ok {
			return extID
		}
		return buildSymbolID(ast.URI, name)
	}

	for _, comp := range ast.Components {
		compID := buildSymbolID(ast.URI, comp.Name)
		
		compSymbol := &Symbol{
			ID:            compID,
			Kind:          SymbolComponent,
			Name:          comp.Name,
			Range:         comp.Range,
			Relationships: []Relationship{},
		}
		
		f.Symbols[compID] = compSymbol

		for _, state := range comp.States {
			stateID := fmt.Sprintf("%s.state.%s", compID, state.Name)
			f.Symbols[stateID] = &Symbol{
				ID:            stateID,
				Kind:          SymbolState,
				Name:          state.Name,
				Range:         state.Range,
				ParentID:      compID,
				Relationships: []Relationship{},
			}
		}

		for _, mut := range comp.Mutations {
			mutID := fmt.Sprintf("%s.def.%s", compID, mut.FuncName)
			
			mutSymbol := &Symbol{
				ID:            mutID,
				Kind:          SymbolDefinition,
				Name:          mut.FuncName,
				Range:         mut.Range,
				ParentID:      compID,
				Relationships: []Relationship{},
			}
			
			// Detect 'reads' relationship: what state does this mutate/read?
			for _, m := range mut.Mutations {
				targetStateID := fmt.Sprintf("%s.state.%s", compID, m.StateKey)
				mutSymbol.Relationships = append(mutSymbol.Relationships, Relationship{
					Kind:     RelReads,
					TargetID: targetStateID,
					Range:    m.Range, // Using mutation operation range
				})
			}
			
			f.Symbols[mutID] = mutSymbol
		}

		// Traverse AST tree to find relationships (renders, triggers)
		for _, rootNode := range comp.RootNodes {
			analyzeNodeRelationships(ast.URI, compID, rootNode, compSymbol, resolveTargetID)
		}
	}

	return f
}

func analyzeNodeRelationships(uri string, compID string, astNode ASTNode, parentSymbol *Symbol, resolveTarget func(string) string) {
	if astNode == nil {
		return
	}

	switch n := astNode.(type) {
	case *Node:
		// Is it a component instantiation? (Starts with uppercase)
		if len(n.Name) > 0 && n.Name[0] >= 'A' && n.Name[0] <= 'Z' {
			// It renders a component
			targetID := resolveTarget(n.Name)

			parentSymbol.Relationships = append(parentSymbol.Relationships, Relationship{
				Kind:     RelRenders,
				TargetID: targetID,
				Range:    n.Range,
			})
		}

		// Does it have events?
		for k, v := range n.Attributes {
			if strings.HasPrefix(k, "on_") {
				// Event trigger
				targetDefID := fmt.Sprintf("%s.def.%s", compID, v)
				parentSymbol.Relationships = append(parentSymbol.Relationships, Relationship{
					Kind:     RelTriggers,
					TargetID: targetDefID,
					Range:    n.Range, // Approximate
				})
			}
		}
		
		for _, child := range n.Children {
			analyzeNodeRelationships(uri, compID, child, parentSymbol, resolveTarget)
		}
	case *ConditionalNode:
		// It reads a state
		targetStateID := fmt.Sprintf("%s.state.%s", compID, n.ConditionVar)
		parentSymbol.Relationships = append(parentSymbol.Relationships, Relationship{
			Kind:     RelReads,
			TargetID: targetStateID,
			Range:    n.Range,
		})
		for _, child := range n.TrueBranch {
			analyzeNodeRelationships(uri, compID, child, parentSymbol, resolveTarget)
		}
		for _, child := range n.FalseBranch {
			analyzeNodeRelationships(uri, compID, child, parentSymbol, resolveTarget)
		}
	case *ForNode:
		targetStateID := fmt.Sprintf("%s.state.%s", compID, n.IterableKey)
		parentSymbol.Relationships = append(parentSymbol.Relationships, Relationship{
			Kind:     RelReads,
			TargetID: targetStateID,
			Range:    n.Range,
		})
		for _, child := range n.Body {
			analyzeNodeRelationships(uri, compID, child, parentSymbol, resolveTarget)
		}
	case *HiddenWrapperNode:
		analyzeNodeRelationships(uri, compID, n.Child, parentSymbol, resolveTarget)
	}
}
