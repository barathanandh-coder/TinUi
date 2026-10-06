package agent

import (
	"encoding/json"
)

var AIContext *AIContextAPI

// Ensure AIContext is initialized alongside the GlobalWorkspace.
func initAIContext() {
	if AIContext == nil && GlobalWorkspace != nil {
		AIContext = NewAIContextAPI(GlobalWorkspace)
	}
}

type TextPosition struct {
	Line   int `json:"line"`
	Column int `json:"column"`
}

type TextRange struct {
	Start TextPosition `json:"start"`
	End   TextPosition `json:"end"`
}

type AIProposalParams struct {
	Operation       string    `json:"operation"`
	URI             string    `json:"uri"`
	Range           TextRange `json:"range"`
	ExpectedVersion int       `json:"expected_version"`
	Replacement     string    `json:"replacement"`
}

type ProposalResult struct {
	Valid       bool     `json:"valid"`
	Diagnostics []string `json:"diagnostics,omitempty"`
	ProposalID  string   `json:"proposal_id,omitempty"`
}

type AIApplyParams struct {
	ProposalID      string `json:"proposal_id"`
	URI             string `json:"uri"`
	ExpectedVersion int    `json:"expected_version"`
}

type ApplyResult struct {
	Success     bool     `json:"success"`
	Diagnostics []string `json:"diagnostics,omitempty"`
}

type AIContextParams struct {
	URI   string `json:"uri,omitempty"`
	ID    string `json:"id,omitempty"`
	Query string `json:"query,omitempty"`
}

func handleAIContextRequest(req RequestEnvelope) {
	initAIContext()
	
	if AIContext == nil {
		sendError(req.ID, -32000, "AI Context API not initialized")
		return
	}

	if req.Method == "context.propose" {
		var pParams AIProposalParams
		if req.Params != nil {
			if err := json.Unmarshal(req.Params, &pParams); err != nil {
				sendError(req.ID, -32602, "Invalid proposal parameters")
				return
			}
		}
		
		// 1. Verify VFS boundary
		vfsMutex.RLock()
		doc, exists := vfs[pParams.URI]
		vfsMutex.RUnlock()

		if !exists {
			sendError(req.ID, -32002, "Document not open in workspace")
			return
		}
		if doc.Version != pParams.ExpectedVersion {
			sendError(req.ID, -32003, "Version mismatch. Proposal rejected.")
			return
		}
		
		// 2. Delegate to API for validation
		result := AIContext.ValidateProposal(pParams, doc.Source)
		sendResult(req.ID, result)
		return
	}

	if req.Method == "context.apply" {
		var aParams AIApplyParams
		if req.Params != nil {
			if err := json.Unmarshal(req.Params, &aParams); err != nil {
				sendError(req.ID, -32602, "Invalid apply parameters")
				return
			}
		}

		// 1. Get Proposal
		AIContext.mu.RLock()
		proposal, exists := AIContext.proposals[aParams.ProposalID]
		AIContext.mu.RUnlock()

		if !exists {
			sendError(req.ID, -32002, "Proposal not found or expired")
			return
		}

		if proposal.Params.URI != aParams.URI {
			sendError(req.ID, -32002, "Proposal URI mismatch")
			return
		}

		// 2. Acquire per-document sync lane
		mu := getDocMutex(aParams.URI)
		mu.Lock()
		defer mu.Unlock()

		// 3. Check Version
		vfsMutex.Lock()
		doc, docExists := vfs[aParams.URI]
		if !docExists {
			vfsMutex.Unlock()
			sendError(req.ID, -32002, "Document no longer open in workspace")
			return
		}
		if doc.Version != aParams.ExpectedVersion || doc.Version != proposal.Params.ExpectedVersion {
			vfsMutex.Unlock()
			sendError(req.ID, -32003, "Version mismatch. Cannot apply proposal.")
			return
		}

		// Save old source for rollback
		oldSource := doc.Source

		// Pre-apply snapshot of unresolved references to detect regressions anywhere in workspace
		preUnresolved := AIContext.ws.GetUnresolved()
		preUnresolvedMap := make(map[string]bool)
		for _, u := range preUnresolved {
			preUnresolvedMap[u.SourceID+"->"+u.TargetID] = true
		}

		// 4. Atomic VFS update (in-memory)
		doc.Source = proposal.PatchedSource
		doc.Version++ // Bump version
		vfs[aParams.URI] = doc
		vfsMutex.Unlock()

		// 5. Sync Document with Global Semantic Workspace
		syncDocument(doc.URI, doc.Source)

		// 5. Final Semantic Validation to ensure no global regressions
		postUnresolved := AIContext.ws.GetUnresolved()
		var rollbackRequired bool
		var diagnostics []string
		
		for _, u := range postUnresolved {
			key := u.SourceID+"->"+u.TargetID
			if !preUnresolvedMap[key] {
				rollbackRequired = true
				diagnostics = append(diagnostics, "Unresolved semantic reference after apply: " + u.TargetID)
			}
		}

		// 6. Rollback if validation fails
		if rollbackRequired {
			// Rollback VFS
			vfsMutex.Lock()
			doc.Source = oldSource
			doc.Version-- // Revert bump
			vfs[aParams.URI] = doc
			vfsMutex.Unlock()

			// Rollback Semantic Workspace
			syncDocument(doc.URI, oldSource)

			sendResult(req.ID, ApplyResult{
				Success:     false,
				Diagnostics: diagnostics,
			})
			return
		}

		// 7. Clear proposal (consume it)
		AIContext.mu.Lock()
		delete(AIContext.proposals, aParams.ProposalID)
		AIContext.mu.Unlock()

		sendResult(req.ID, ApplyResult{
			Success: true,
		})
		return
	}

	var params AIContextParams
	if req.Params != nil {
		if err := json.Unmarshal(req.Params, &params); err != nil {
			sendError(req.ID, -32602, "Invalid parameters")
			return
		}
	}

	switch req.Method {
	case "context.project":
		result := AIContext.GetProjectContext()
		sendResult(req.ID, result)

	case "context.file":
		if params.URI == "" {
			sendError(req.ID, -32602, "Missing 'uri' parameter")
			return
		}
		result := AIContext.GetFileContext(params.URI)
		if result == nil {
			sendError(req.ID, -32001, "File not found in semantic workspace")
			return
		}
		sendResult(req.ID, result)

	case "context.symbol":
		if params.ID == "" {
			sendError(req.ID, -32602, "Missing 'id' parameter")
			return
		}
		result := AIContext.GetSymbolContext(params.ID)
		if result == nil {
			sendError(req.ID, -32002, "Symbol not found in semantic workspace")
			return
		}
		sendResult(req.ID, result)

	case "context.references":
		if params.ID == "" {
			sendError(req.ID, -32602, "Missing 'id' parameter")
			return
		}
		result := AIContext.GetReferences(params.ID)
		sendResult(req.ID, map[string]interface{}{"references": result})

	case "context.dependents":
		if params.ID == "" {
			sendError(req.ID, -32602, "Missing 'id' parameter")
			return
		}
		result := AIContext.GetDependents(params.ID)
		sendResult(req.ID, map[string]interface{}{"dependents": result})

	case "context.imports":
		if params.URI == "" {
			sendError(req.ID, -32602, "Missing 'uri' parameter")
			return
		}
		result := AIContext.GetImports(params.URI)
		sendResult(req.ID, map[string]interface{}{"imports": result})

	case "context.unresolved":
		result := AIContext.GetUnresolvedReferences()
		sendResult(req.ID, map[string]interface{}{"unresolved": result})

	case "context.architecture":
		if params.ID == "" {
			sendError(req.ID, -32602, "Missing 'id' parameter")
			return
		}
		result := AIContext.GetArchitecture(params.ID)
		if result == nil {
			sendError(req.ID, -32002, "Symbol not found in semantic workspace")
			return
		}
		sendResult(req.ID, map[string]interface{}{"architecture": result})

	case "context.impact":
		if params.ID == "" {
			sendError(req.ID, -32602, "Missing 'id' parameter")
			return
		}
		result := AIContext.GetImpact(params.ID)
		if result == nil {
			sendError(req.ID, -32002, "Symbol not found in semantic workspace")
			return
		}
		sendResult(req.ID, map[string]interface{}{"impact": result})

	case "context.dependencies":
		if params.ID == "" {
			sendError(req.ID, -32602, "Missing 'id' parameter")
			return
		}
		result := AIContext.GetDependencies(params.ID)
		if result == nil {
			sendError(req.ID, -32002, "Symbol not found in semantic workspace")
			return
		}
		sendResult(req.ID, map[string]interface{}{"dependencies": result})

	case "context.related":
		if params.ID == "" {
			sendError(req.ID, -32602, "Missing 'id' parameter")
			return
		}
		result := AIContext.GetRelated(params.ID)
		sendResult(req.ID, map[string]interface{}{"related": result})

	case "context.search":
		if params.Query == "" {
			sendError(req.ID, -32602, "Missing 'query' parameter")
			return
		}
		result := AIContext.SearchSymbols(params.Query)
		sendResult(req.ID, map[string]interface{}{"search": result})

	default:
		sendError(req.ID, -32601, "Method not found")
	}
}
