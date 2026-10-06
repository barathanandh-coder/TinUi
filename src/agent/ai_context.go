package agent

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"strings"
	"sync"

	"github.com/tinui/tinui/src/compiler"
)

type AIContextAPI struct {
	ws *compiler.SemanticWorkspace
	mu sync.RWMutex
	proposals map[string]ValidatedProposal
}

type ValidatedProposal struct {
	Params        AIProposalParams
	PatchedSource string
}

func NewAIContextAPI(ws *compiler.SemanticWorkspace) *AIContextAPI {
	return &AIContextAPI{
		ws: ws,
		proposals: make(map[string]ValidatedProposal),
	}
}

// Data structures for AI Context
type ProjectContext struct {
	Files                []string                       `json:"files"`
	TotalSymbols         int                            `json:"total_symbols"`
	UnresolvedReferences []compiler.UnresolvedReference `json:"unresolved_references"`
}

type FileContext struct {
	URI     string                  `json:"uri"`
	Imports []compiler.Relationship `json:"imports"`
	Symbols []*compiler.Symbol      `json:"symbols"`
}

type SymbolContext struct {
	Symbol        *compiler.Symbol        `json:"symbol"`
	Parent        *compiler.Symbol        `json:"parent,omitempty"`
	Children      []*compiler.Symbol      `json:"children"`
	References    []compiler.Relationship `json:"references"`
	Dependents    []compiler.ReferenceEdge`json:"dependents"`
}

// 1. get_project_context
func (api *AIContextAPI) GetProjectContext() ProjectContext {
	// We need to fetch files from workspace in a thread-safe way.
	return ProjectContext{
		Files:                api.ws.GetFiles(),
		UnresolvedReferences: api.ws.GetUnresolved(),
	}
}

// 2. get_file_context
func (api *AIContextAPI) GetFileContext(uri string) *FileContext {
	symbols := api.ws.GetSymbolsForFile(uri)
	imports := api.ws.GetImports(uri)
	if symbols == nil && imports == nil {
		return nil
	}
	return &FileContext{
		URI:     uri,
		Imports: imports,
		Symbols: symbols,
	}
}

// 3. get_symbol_context
func (api *AIContextAPI) GetSymbolContext(id string) *SymbolContext {
	sym := api.ws.ResolveSymbol(id)
	if sym == nil {
		return nil
	}

	return &SymbolContext{
		Symbol:     sym,
		Parent:     api.ws.GetParent(sym.ID),
		Children:   api.ws.GetChildren(sym.ID),
		References: sym.Relationships,
		Dependents: api.ws.GetDependents(sym.ID),
	}
}

// 4. get_children
func (api *AIContextAPI) GetChildren(id string) []*compiler.Symbol {
	return api.ws.GetChildren(id)
}

// 5. get_parent
func (api *AIContextAPI) GetParent(id string) *compiler.Symbol {
	return api.ws.GetParent(id)
}

// 6. get_references (what this symbol refers to)
func (api *AIContextAPI) GetReferences(id string) []compiler.Relationship {
	sym := api.ws.ResolveSymbol(id)
	if sym != nil {
		return sym.Relationships
	}
	return nil
}

// 7. get_dependents (who refers to this symbol)
func (api *AIContextAPI) GetDependents(id string) []compiler.ReferenceEdge {
	return api.ws.GetDependents(id)
}

// 8. get_imports
func (api *AIContextAPI) GetImports(uri string) []compiler.Relationship {
	return api.ws.GetImports(uri)
}

// 9. get_unresolved_references
func (api *AIContextAPI) GetUnresolvedReferences() []compiler.UnresolvedReference {
	return api.ws.GetUnresolved()
}

type ArchNode struct {
	ID       string     `json:"id"`
	Name     string     `json:"name"`
	Children []ArchNode `json:"children,omitempty"`
}

// 10. get_architecture: Recursive tree of rendered components
func (api *AIContextAPI) GetArchitecture(id string) *ArchNode {
	visited := make(map[string]bool)
	return api.buildArchitectureTree(id, visited)
}

func (api *AIContextAPI) buildArchitectureTree(id string, visited map[string]bool) *ArchNode {
	if visited[id] {
		return nil // Avoid infinite cycles
	}
	visited[id] = true

	sym := api.ws.ResolveSymbol(id)
	if sym == nil {
		return nil
	}

	node := &ArchNode{
		ID:   sym.ID,
		Name: sym.Name,
	}

	for _, rel := range sym.Relationships {
		if rel.Kind == compiler.RelRenders {
			childNode := api.buildArchitectureTree(rel.TargetID, visited)
			if childNode != nil {
				node.Children = append(node.Children, *childNode)
			} else if api.ws.ResolveSymbol(rel.TargetID) == nil {
				// Leaf node (like a missing component)
				node.Children = append(node.Children, ArchNode{
					ID:   rel.TargetID,
					Name: "Unknown",
				})
			}
		}
	}
	return node
}

// 11. get_impact: Recursive tree of what depends on this symbol
func (api *AIContextAPI) GetImpact(id string) *ArchNode {
	visited := make(map[string]bool)
	return api.buildImpactTree(id, visited)
}

func (api *AIContextAPI) buildImpactTree(id string, visited map[string]bool) *ArchNode {
	if visited[id] {
		return nil
	}
	visited[id] = true

	// Note: We might be impacting something that isn't a direct symbol (e.g. an unresolved ID)
	// but mostly we want the dependent's ID
	sym := api.ws.ResolveSymbol(id)
	name := "Unknown"
	if sym != nil {
		name = sym.Name
	}

	node := &ArchNode{
		ID:   id,
		Name: name,
	}

	deps := api.ws.GetDependents(id)
	for _, edge := range deps {
		childNode := api.buildImpactTree(edge.SourceID, visited)
		if childNode != nil {
			node.Children = append(node.Children, *childNode)
		}
	}
	return node
}

// 12. get_dependencies: Transitive relationships (all kinds)
func (api *AIContextAPI) GetDependencies(id string) *ArchNode {
	visited := make(map[string]bool)
	return api.buildDependenciesTree(id, visited)
}

func (api *AIContextAPI) buildDependenciesTree(id string, visited map[string]bool) *ArchNode {
	if visited[id] {
		return nil
	}
	visited[id] = true

	sym := api.ws.ResolveSymbol(id)
	if sym == nil {
		return nil
	}

	node := &ArchNode{
		ID:   sym.ID,
		Name: sym.Name,
	}

	for _, rel := range sym.Relationships {
		childNode := api.buildDependenciesTree(rel.TargetID, visited)
		if childNode != nil {
			node.Children = append(node.Children, *childNode)
		} else if api.ws.ResolveSymbol(rel.TargetID) == nil {
			// Leaf node (like a missing dependency)
			node.Children = append(node.Children, ArchNode{
				ID:   rel.TargetID,
				Name: "Unknown",
			})
		}
	}
	return node
}

// 13. get_search: Search workspace symbols by substring
func (api *AIContextAPI) SearchSymbols(query string) []compiler.Symbol {
	var results []compiler.Symbol
	if query == "" {
		return results
	}
	
	queryLower := strings.ToLower(query)
	files := api.ws.GetFiles()
	for _, uri := range files {
		symbols := api.ws.GetSymbolsForFile(uri)
		for _, sym := range symbols {
			if strings.Contains(strings.ToLower(sym.Name), queryLower) || strings.Contains(strings.ToLower(sym.ID), queryLower) {
				results = append(results, *sym)
			}
		}
	}
	return results
}

// 14. get_related: Return siblings or co-located symbols
func (api *AIContextAPI) GetRelated(id string) []compiler.Symbol {
	var results []compiler.Symbol
	sym := api.ws.ResolveSymbol(id)
	if sym == nil {
		return results
	}
	
	// Add parent
	parent := api.ws.GetParent(id)
	if parent != nil {
		results = append(results, *parent)
	}

	// Add children
	children := api.ws.GetChildren(id)
	for _, c := range children {
		results = append(results, *c)
	}

	// Easiest "related" heuristic is all other top-level symbols in the same file
	uri := strings.Split(sym.ID, "#")[0]
	symbols := api.ws.GetSymbolsForFile(uri)
	for _, s := range symbols {
		if s.ID != sym.ID && (parent == nil || s.ID != parent.ID) {
			results = append(results, *s)
		}
	}
	return results
}

// applyPatch replaces the text in source designated by textRange with replacement
func applyPatch(source string, startLine, startCol, endLine, endCol int, replacement string) string {
	if startLine <= 0 {
		return replacement // Replace all
	}
	
	lines := strings.Split(source, "\n")
	
	// Convert to 0-based index
	sl := startLine - 1
	sc := startCol - 1
	el := endLine - 1
	ec := endCol - 1

	if sl < 0 || sl >= len(lines) {
		return source
	}
	if el < 0 || el >= len(lines) {
		return source
	}
	if sc < 0 { sc = 0 }
	if ec < 0 { ec = 0 }

	// Ensure columns don't exceed line lengths
	if sc > len(lines[sl]) { sc = len(lines[sl]) }
	if ec > len(lines[el]) { ec = len(lines[el]) }

	prefix := ""
	for i := 0; i < sl; i++ {
		prefix += lines[i] + "\n"
	}
	prefix += lines[sl][:sc]

	suffix := lines[el][ec:]
	if el < len(lines)-1 {
		suffix += "\n"
	}
	for i := el + 1; i < len(lines); i++ {
		suffix += lines[i]
		if i < len(lines)-1 {
			suffix += "\n"
		}
	}

	return prefix + replacement + suffix
}

// 15. validate_proposal: Validates a proposed change against the semantic constraints
func (api *AIContextAPI) ValidateProposal(pParams AIProposalParams, originalSource string) ProposalResult {
	// 1. Apply patch
	patchedSource := applyPatch(originalSource, 
		pParams.Range.Start.Line, pParams.Range.Start.Column, 
		pParams.Range.End.Line, pParams.Range.End.Column, 
		pParams.Replacement)
		
	// 2. Syntax Validation
	lexer := compiler.NewLexer(patchedSource)
	parser := compiler.NewParser(lexer)
	ast := parser.ParseFileAST(pParams.URI)
	
	if len(parser.Errors) > 0 {
		return ProposalResult{
			Valid:       false,
			Diagnostics: parser.Errors,
		}
	}

	// 3. Semantic Consistency Validation
	fileGraph := compiler.AnalyzeFile(ast)
	
	var diagnostics []string
	
	// Check for unresolved references inside the newly proposed file
	for _, sym := range fileGraph.Symbols {
		for _, rel := range sym.Relationships {
			if !strings.HasPrefix(rel.TargetID, "tinpy://") {
				continue
			}
			
			// Resolve symbol against current workspace
			if api.ws.ResolveSymbol(rel.TargetID) == nil {
				// Symbol not in global workspace. Check if it's introduced locally in the patch.
				foundLocally := false
				for _, localSym := range fileGraph.Symbols {
					if localSym.ID == rel.TargetID {
						foundLocally = true
						break
					}
				}
				if !foundLocally {
					diagnostics = append(diagnostics, "Unresolved semantic reference in patch: "+rel.TargetID)
				}
			}
		}
	}

	if len(diagnostics) > 0 {
		return ProposalResult{
			Valid:       false,
			Diagnostics: diagnostics,
		}
	}

	// Generate proposal ID
	hasher := sha256.New()
	hasher.Write([]byte(fmt.Sprintf("%s:%d:%s", pParams.URI, pParams.ExpectedVersion, patchedSource)))
	proposalID := "proposal-" + hex.EncodeToString(hasher.Sum(nil))[:16]

	// Save to map
	api.mu.Lock()
	api.proposals[proposalID] = ValidatedProposal{
		Params:        pParams,
		PatchedSource: patchedSource,
	}
	api.mu.Unlock()

	return ProposalResult{
		Valid:      true,
		ProposalID: proposalID,
	}
}
