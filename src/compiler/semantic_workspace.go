package compiler

import (
	"sort"
	"strings"
	"sync"
)

// SemanticWorkspace manages the semantic graph across multiple files.
// It acts as the coordinator between the raw ASTs, the analyzer, and the query index.
type SemanticWorkspace struct {
	Index *SemanticIndex
	mu    sync.RWMutex
}

// NewSemanticWorkspace initializes an empty semantic workspace.
func NewSemanticWorkspace() *SemanticWorkspace {
	return &SemanticWorkspace{
		Index: NewSemanticIndex(),
	}
}

// AddFileAST takes a raw FileAST, analyzes it to produce a Semantic File graph,
// and updates the workspace index.
func (ws *SemanticWorkspace) AddFileAST(ast *FileAST) {
	if ast == nil || ast.URI == "" {
		return
	}
	fileGraph := AnalyzeFile(ast)
	
	ws.mu.Lock()
	defer ws.mu.Unlock()
	
	ws.Index.Project.Files[ast.URI] = fileGraph
	ws.Index.RebuildIndex()
}

// RemoveFile cleanly removes a file from the workspace and rebuilds the index.
func (ws *SemanticWorkspace) RemoveFile(uri string) {
	ws.mu.Lock()
	defer ws.mu.Unlock()
	
	if _, exists := ws.Index.Project.Files[uri]; exists {
		delete(ws.Index.Project.Files, uri)
		ws.Index.RebuildIndex()
	}
}

// GetUnresolved returns a deterministic list of all unresolved references across the workspace.
func (ws *SemanticWorkspace) GetUnresolved() []UnresolvedReference {
	ws.mu.RLock()
	defer ws.mu.RUnlock()
	return ws.Index.GetUnresolvedReferences()
}

// ResolveSymbol resolves a deterministic tinpy:// ID to its Symbol representation.
func (ws *SemanticWorkspace) ResolveSymbol(id string) *Symbol {
	ws.mu.RLock()
	defer ws.mu.RUnlock()
	return ws.Index.FindSymbol(id)
}

// GetFileForSymbol determines which File URI owns a given Symbol ID.
func (ws *SemanticWorkspace) GetFileForSymbol(id string) string {
	ws.mu.RLock()
	sym := ws.Index.FindSymbol(id)
	ws.mu.RUnlock()
	
	if sym == nil {
		return ""
	}
	
	// id format: tinpy://<workspace-uri>/<path>#<name>
	// Because buildSymbolID strips 'file://' and prepends 'tinpy://',
	// we can reliably reverse this to find the owning file URI.
	parts := strings.Split(id, "#")
	if len(parts) >= 1 {
		return strings.Replace(parts[0], "tinpy://", "file://", 1)
	}
	return ""
}

// GetSymbolsForFile returns all symbols contained within a specific file URI.
func (ws *SemanticWorkspace) GetSymbolsForFile(uri string) []*Symbol {
	ws.mu.RLock()
	fileGraph, exists := ws.Index.Project.Files[uri]
	ws.mu.RUnlock()
	
	if !exists {
		return nil
	}

	var symbols []*Symbol
	for _, sym := range fileGraph.Symbols {
		symbols = append(symbols, sym)
	}

	// For determinism, we sort it:
	sort.Slice(symbols, func(i, j int) bool {
		return symbols[i].ID < symbols[j].ID
	})
	return symbols
}

// GetFiles returns a sorted list of all active files in the workspace.
func (ws *SemanticWorkspace) GetFiles() []string {
	ws.mu.RLock()
	defer ws.mu.RUnlock()
	
	var files []string
	for uri := range ws.Index.Project.Files {
		files = append(files, uri)
	}
	sort.Strings(files)
	return files
}

// GetParent safely retrieves a symbol's parent.
func (ws *SemanticWorkspace) GetParent(id string) *Symbol {
	ws.mu.RLock()
	defer ws.mu.RUnlock()
	return ws.Index.GetParent(id)
}

// GetChildren safely retrieves a symbol's children.
func (ws *SemanticWorkspace) GetChildren(id string) []*Symbol {
	ws.mu.RLock()
	defer ws.mu.RUnlock()
	return ws.Index.GetChildren(id)
}

// GetImports safely retrieves a file's imports.
func (ws *SemanticWorkspace) GetImports(uri string) []Relationship {
	ws.mu.RLock()
	defer ws.mu.RUnlock()
	return ws.Index.GetImports(uri)
}

// GetDependents fetches the dependents mapping securely
func (ws *SemanticWorkspace) GetDependents(targetID string) []ReferenceEdge {
	ws.mu.RLock()
	defer ws.mu.RUnlock()
	return ws.Index.GetDependents(targetID)
}
