package compiler

import (
	"sort"
)

type ReferenceEdge struct {
	SourceID string
	Range    Range
}

type SemanticIndex struct {
	Project *Project
	
	// Fast lookup map
	SymbolMap map[string]*Symbol
	
	// targetID -> []ReferenceEdge
	Dependents map[string][]ReferenceEdge
}

func NewSemanticIndex() *SemanticIndex {
	return &SemanticIndex{
		Project: &Project{
			Files: make(map[string]*File),
		},
		SymbolMap:  make(map[string]*Symbol),
		Dependents: make(map[string][]ReferenceEdge),
	}
}

func (idx *SemanticIndex) AddFile(file *File) {
	idx.Project.Files[file.URI] = file
	idx.RebuildIndex()
}

func (idx *SemanticIndex) RebuildIndex() {
	idx.SymbolMap = make(map[string]*Symbol)
	idx.Dependents = make(map[string][]ReferenceEdge)

	// Populate symbols
	for _, f := range idx.Project.Files {
		for id, sym := range f.Symbols {
			idx.SymbolMap[id] = sym
		}
	}

	// Populate relationships (dependents)
	for _, f := range idx.Project.Files {
		for _, imp := range f.Imports {
			idx.Dependents[imp.TargetID] = append(idx.Dependents[imp.TargetID], ReferenceEdge{
				SourceID: f.URI,
				Range:    imp.Range,
			})
		}

		for _, sym := range f.Symbols {
			for _, rel := range sym.Relationships {
				idx.Dependents[rel.TargetID] = append(idx.Dependents[rel.TargetID], ReferenceEdge{
					SourceID: sym.ID,
					Range:    rel.Range,
				})
			}
		}
	}

	// Deduplicate and sort dependent lists for deterministic results
	for targetID, sources := range idx.Dependents {
		unique := make(map[string]bool)
		var list []ReferenceEdge
		for _, s := range sources {
			// Use SourceID + Range as unique key to prevent exact duplicate edges
			key := s.SourceID + string(rune(s.Range.Start.Line)) + string(rune(s.Range.Start.Character))
			if !unique[key] {
				unique[key] = true
				list = append(list, s)
			}
		}
		sort.Slice(list, func(i, j int) bool {
			if list[i].SourceID != list[j].SourceID {
				return list[i].SourceID < list[j].SourceID
			}
			if list[i].Range.Start.Line != list[j].Range.Start.Line {
				return list[i].Range.Start.Line < list[j].Range.Start.Line
			}
			return list[i].Range.Start.Character < list[j].Range.Start.Character
		})
		idx.Dependents[targetID] = list
	}
}

func (idx *SemanticIndex) FindSymbol(id string) *Symbol {
	return idx.SymbolMap[id]
}

func (idx *SemanticIndex) FindSymbolsByNameAndKind(name string, kind SymbolKind) []*Symbol {
	var results []*Symbol
	for _, sym := range idx.SymbolMap {
		if sym.Name == name && sym.Kind == kind {
			results = append(results, sym)
		}
	}
	// Sort by ID to ensure deterministic output
	sort.Slice(results, func(i, j int) bool {
		return results[i].ID < results[j].ID
	})
	return results
}

func (idx *SemanticIndex) GetChildren(parentID string) []*Symbol {
	var children []*Symbol
	for _, sym := range idx.SymbolMap {
		if sym.ParentID == parentID {
			children = append(children, sym)
		}
	}
	sort.Slice(children, func(i, j int) bool {
		return children[i].ID < children[j].ID
	})
	return children
}

func (idx *SemanticIndex) GetParent(childID string) *Symbol {
	child := idx.FindSymbol(childID)
	if child != nil && child.ParentID != "" {
		return idx.FindSymbol(child.ParentID)
	}
	return nil
}

func (idx *SemanticIndex) GetImports(uri string) []Relationship {
	if f, exists := idx.Project.Files[uri]; exists {
		return f.Imports
	}
	return nil
}

func (idx *SemanticIndex) GetDependents(id string) []ReferenceEdge {
	return idx.Dependents[id]
}

func (idx *SemanticIndex) GetRelationships(id string) []Relationship {
	sym := idx.FindSymbol(id)
	if sym != nil {
		return sym.Relationships
	}
	return nil
}

type UnresolvedReference struct {
	SourceID string
	TargetID string
	Range    Range
}

func (idx *SemanticIndex) GetUnresolvedReferences() []UnresolvedReference {
	var unresolved []UnresolvedReference

	for _, f := range idx.Project.Files {
		for _, imp := range f.Imports {
			if _, exists := idx.SymbolMap[imp.TargetID]; !exists {
				unresolved = append(unresolved, UnresolvedReference{
					SourceID: f.URI,
					TargetID: imp.TargetID,
					Range:    imp.Range,
				})
			}
		}

		for _, sym := range f.Symbols {
			for _, rel := range sym.Relationships {
				if _, exists := idx.SymbolMap[rel.TargetID]; !exists {
					unresolved = append(unresolved, UnresolvedReference{
						SourceID: sym.ID,
						TargetID: rel.TargetID,
						Range:    rel.Range,
					})
				}
			}
		}
	}

	sort.Slice(unresolved, func(i, j int) bool {
		if unresolved[i].SourceID == unresolved[j].SourceID {
			return unresolved[i].TargetID < unresolved[j].TargetID
		}
		return unresolved[i].SourceID < unresolved[j].SourceID
	})

	return unresolved
}
