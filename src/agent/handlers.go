package agent

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"sync"

	"github.com/tinui/tinui/src/compiler"
)

var (
	vfs      = make(map[string]UpdateDocumentParams)
	vfsMutex sync.RWMutex

	docMutexes sync.Map // per-document synchronization lane
)

func getDocMutex(uri string) *sync.Mutex {
	m, _ := docMutexes.LoadOrStore(uri, &sync.Mutex{})
	return m.(*sync.Mutex)
}

func handleUpdateDocument(req RequestEnvelope) {
	var params UpdateDocumentParams
	if req.Params != nil {
		json.Unmarshal(req.Params, &params)
	}
	if params.URI == "" || params.Version == 0 {
		sendError(req.ID, -32602, "Missing uri or version")
		return
	}

	mu := getDocMutex(params.URI)
	mu.Lock()
	defer mu.Unlock()

	vfsMutex.Lock()
	vfs[params.URI] = params
	vfsMutex.Unlock()
	
	// Sync to semantic workspace
	syncDocument(params.URI, params.Source)
	
	sendResult(req.ID, map[string]interface{}{"status": "updated", "version": params.Version})
}

func handleCloseDocument(req RequestEnvelope) {
	var params CloseDocumentParams
	if req.Params != nil {
		json.Unmarshal(req.Params, &params)
	}
	if params.URI == "" {
		sendError(req.ID, -32602, "Missing uri")
		return
	}
	vfsMutex.Lock()
	delete(vfs, params.URI)
	vfsMutex.Unlock()
	
	// Remove from semantic workspace
	closeDocument(params.URI)
	
	sendResult(req.ID, map[string]interface{}{"status": "closed"})
}

func resolveAndCheckSandbox(rawURI string) (string, error) {
	workspaceRoot, err := os.Getwd()
	if err != nil {
		return "", err
	}

	pathStr := rawURI
	if strings.HasPrefix(pathStr, "file://") {
		pathStr = strings.TrimPrefix(pathStr, "file://")
		if strings.HasPrefix(pathStr, "/") && len(pathStr) > 2 && pathStr[2] == ':' {
			pathStr = pathStr[1:]
		}
	}

	if !filepath.IsAbs(pathStr) {
		pathStr = filepath.Join(workspaceRoot, pathStr)
	}

	canonicalPath, err := filepath.EvalSymlinks(pathStr)
	if err != nil {
		canonicalPath = filepath.Clean(pathStr)
	}

	canonicalRoot, err := filepath.EvalSymlinks(workspaceRoot)
	if err != nil {
		canonicalRoot = filepath.Clean(workspaceRoot)
	}

	rel, err := filepath.Rel(canonicalRoot, canonicalPath)
	if err != nil || strings.HasPrefix(rel, "..") || strings.HasPrefix(rel, string(filepath.Separator)) {
		return "", fmt.Errorf("TIN-0004 Workspace Boundary Violation")
	}

	return canonicalPath, nil
}

func getSourceCode(reqID interface{}, uri string, source string, version int) (string, int, bool) {
	var sourceCode string
	var currentVersion int

	canonicalURI, err := resolveAndCheckSandbox(uri)
	if err != nil {
		sendError(reqID, -32001, err.Error())
		return "", 0, false
	}
	
	if source != "" {
		if version == 0 {
			sendError(reqID, -32602, "Missing 'version' when 'source' is provided")
			return "", 0, false
		}
		sourceCode = source
		currentVersion = version
	} else {
		vfsMutex.RLock()
		doc, ok := vfs[uri]
		vfsMutex.RUnlock()
		if ok {
			if version != 0 && version < doc.Version {
				sendError(reqID, -32002, "Stale Document Version")
				return "", 0, false
			}
			sourceCode = doc.Source
			currentVersion = doc.Version
		} else {
			sourceBytes, err := os.ReadFile(canonicalURI)
			if err != nil {
				sendError(reqID, -32001, fmt.Sprintf("Error reading file: %v", err))
				return "", 0, false
			}
			sourceCode = string(sourceBytes)
		}
	}
	return sourceCode + "\n", currentVersion, true
}

func handleQuery(ctx context.Context, req RequestEnvelope) {
	select {
	case <-ctx.Done():
		sendError(req.ID, -32800, "Request Cancelled")
		return
	default:
	}

	var params QueryParams
	if req.Params != nil {
		json.Unmarshal(req.Params, &params)
	}
	if params.Kind == "" || params.Document == "" {
		sendError(req.ID, -32602, "Missing 'kind' or 'document'")
		return
	}

	_, currentVersion, ok := getSourceCode(req.ID, params.Document, "", params.Version)
	if !ok {
		return
	}

	targetID, smallestRange := getTargetAtPosition(params.Document, params.Position)
	if targetID == "" && params.Kind != "documentSymbols" && params.Kind != "workspaceSymbols" {
		sendError(req.ID, -32602, "No symbol found at position")
		return
	}

	switch params.Kind {
	case "hover":
		hoverMsg := getHover(targetID)
		r := Range{}
		if smallestRange != nil {
			r = Range{Start: Position{Line: smallestRange.Start.Line, Character: smallestRange.Start.Character}, End: Position{Line: smallestRange.End.Line, Character: smallestRange.End.Character}}
		}
		sendResult(req.ID, HoverResponse{
			Contents: hoverMsg,
			Range:    r,
			Version:  currentVersion,
		})
	case "definition":
		sym := GlobalWorkspace.ResolveSymbol(targetID)
		if sym == nil {
			sendError(req.ID, -32602, "Symbol is unresolved")
			return
		}
		uri := GlobalWorkspace.GetFileForSymbol(sym.ID)
		sendResult(req.ID, DefinitionResponse{
			URI: uri,
			Range: Range{
				Start: Position{Line: sym.Range.Start.Line, Character: sym.Range.Start.Character},
				End:   Position{Line: sym.Range.End.Line, Character: sym.Range.End.Character},
			},
			Version: currentVersion,
		})
	case "references":
		deps := GlobalWorkspace.GetDependents(targetID)
		var locations []Location
		for _, edge := range deps {
			depURI := edge.SourceID
			
			// If SourceID is a symbol (starts with tinpy://), resolve it to a file
			if strings.HasPrefix(depURI, "tinpy://") {
				depURI = GlobalWorkspace.GetFileForSymbol(edge.SourceID)
			}
			
			if depURI != "" {
				locations = append(locations, Location{
					URI: depURI,
					Range: Range{
						Start: Position{Line: edge.Range.Start.Line, Character: edge.Range.Start.Character},
						End:   Position{Line: edge.Range.End.Line, Character: edge.Range.End.Character},
					},
				})
			}
		}
		sendResult(req.ID, ReferencesResponse{
			Locations: locations,
			Version:   currentVersion,
		})
	case "documentSymbols":
		symbols := GlobalWorkspace.GetSymbolsForFile(params.Document)
		var infos []SymbolInformation
		for _, sym := range symbols {
			infos = append(infos, resolveSymbolInfo(sym))
		}
		sendResult(req.ID, DocumentSymbolsResponse{
			Symbols: infos,
			Version: currentVersion,
		})
	case "workspaceSymbols":
		var infos []SymbolInformation
		for _, f := range GlobalWorkspace.Index.Project.Files {
			for _, sym := range f.Symbols {
				infos = append(infos, resolveSymbolInfo(sym))
			}
		}
		sendResult(req.ID, WorkspaceSymbolsResponse{
			Symbols: infos,
			Version: currentVersion,
		})
	default:
		sendError(req.ID, -32601, "Method not found: unsupported query kind")
	}
}

func handleInitialize(req RequestEnvelope) {
	sendResult(req.ID, InitializeResponse{
		ProtocolVersion: "1.0",
		TinuiVersion:    "1.9.0",
		Capabilities: []string{
			"context",
			"schema",
			"diagnostics",
			"graph",
			"build",
			"repair",
		},
	})
}

func handleContext(req RequestEnvelope) {
	// Equivalent to main.go command "context"
	hasManifest := false
	if _, err := os.Stat("tinpyui.project"); err == nil {
		hasManifest = true
	}

	result := map[string]interface{}{
		"architecture": "Go/WASM Core + Python AOT Frontend",
		"manifest":     "tinpyui.project",
		"has_manifest": hasManifest,
	}
	sendResult(req.ID, result)
}

func handleSchema(req RequestEnvelope) {
	result := map[string]interface{}{
		"schema_explorer": []map[string]string{
			{"file": "tinpyui.project", "description": "Project configuration (TOML-like)"},
			{"file": "app.ir.json", "description": "Generated IR file. DO NOT EDIT. Contains '_tinpyui' metadata with 'runtime_abi' versioning."},
		},
	}
	sendResult(req.ID, result)
}

func handleGraph(req RequestEnvelope) {
	// A mock graph for v1.9 phase 1, as the real graph logic isn't fully extracted in compiler
	var params TargetParams
	if req.Params != nil {
		json.Unmarshal(req.Params, &params)
	}
	if params.Entry == "" {
		params.Entry = "main.tin"
	}
	result := ProjectGraph{
		Root: params.Entry,
		Components: []Component{
			{
				ID:           "Main",
				File:         params.Entry,
				Dependencies: []string{},
			},
		},
	}
	sendResult(req.ID, result)
}

var errorRegex = regexp.MustCompile(`^\[line (\d+):(\d+)\] (.*)$`)

func parseDiagnostics(file string, errors []string) []Diagnostic {
	var diags []Diagnostic
	for _, errStr := range errors {
		line := 1
		col := 1
		msg := errStr
		
		matches := errorRegex.FindStringSubmatch(errStr)
		if len(matches) == 4 {
			line, _ = strconv.Atoi(matches[1])
			col, _ = strconv.Atoi(matches[2])
			msg = matches[3]
		}
		
		diag := Diagnostic{
			ErrorCode: "TIN-0001",
			Category:  "syntax",
			Severity:  "error",
			File:      file,
			Line:      line - 1,
			Column:    col - 1, 
			Message:   msg,
		}

		// Hacky repair suggestion for common missing quote
		if strings.Contains(msg, "Expected component attribute") && strings.Contains(msg, ":") {
			diag.RepairSuggestion = &RepairSuggestion{
				Description: "Replace ':' with '=' for attribute assignment",
				Edits: []TextEdit{
					{
						Range: Range{
							Start: Position{Line: line - 1, Character: col - 2},
							End:   Position{Line: line - 1, Character: col - 1},
						},
						NewText: "=",
					},
				},
				IsDeterministic: true,
			}
		}

		diags = append(diags, diag)
	}
	return diags
}

func translateComponentDiagnostics(uri string, compilerDiags []compiler.ComponentDiagnostic) []Diagnostic {
	var diags []Diagnostic
	for _, d := range compilerDiags {
		severity := "error"
		if d.Severity == compiler.SeverityWarning {
			severity = "warning"
		}

		msg := d.Message

		diags = append(diags, Diagnostic{
			ErrorCode:        string(d.Code),
			Category:         "semantic",
			Severity:         severity,
			File:             uri,
			Line:             d.Range.Start.Line,
			Column:           d.Range.Start.Character,
			Message:          msg,
			ContextSnippet:   fmt.Sprintf("Expected: %s, Actual: %s", d.ExpectedType, d.ActualType),
			ASTNode:          d.ComponentName,
		})
	}
	return diags
}

func handleCheck(ctx context.Context, req RequestEnvelope) {
	select {
	case <-ctx.Done():
		sendError(req.ID, -32800, "Request Cancelled")
		return
	default:
	}

	var params TargetParams
	if req.Params != nil {
		json.Unmarshal(req.Params, &params)
	}
	
	uri := params.URI
	if uri == "" {
		uri = params.Entry
	}
	
	if uri == "" {
		sendError(req.ID, -32602, "Missing 'uri' or 'entry' in params")
		return
	}

	sourceCode, _, ok := getSourceCode(req.ID, uri, params.Source, params.Version)
	if !ok {
		return
	}

	l := compiler.NewLexer(sourceCode)
	p := compiler.NewParser(l)
	ast := p.ParseFileAST(uri)

	// Ensure the workspace is updated with the latest AST for this file
	GlobalWorkspace.AddFileAST(ast)

	select {
	case <-ctx.Done():
		sendError(req.ID, -32800, "Request Cancelled")
		return
	default:
	}

	diags := parseDiagnostics(params.Entry, p.Errors)

	// Add Semantic Diagnostics (Unresolved References)
	unresolved := GlobalWorkspace.GetUnresolved()
	for _, u := range unresolved {
		if u.SourceID == uri || u.SourceID == "file://" + uri {
			diags = append(diags, Diagnostic{
				ErrorCode: "TIN-0005",
				Category:  "semantic",
				Severity:  "error",
				File:      uri,
				Line:      u.Range.Start.Line,
				Column:    u.Range.Start.Character,
				Message:   fmt.Sprintf("Unresolved reference to %s", u.TargetID),
			})
		}
	}

	// Check component type signatures
	typeChecker := compiler.NewComponentTypeChecker()
	compDiags := typeChecker.CheckWorkspace(ast, GlobalWorkspace)

	diags = append(diags, translateComponentDiagnostics(uri, compDiags)...)

	status := "passed"
	if len(diags) > 0 {
		status = "failed"
	}
	
	result := map[string]interface{}{
		"status":      status,
		"diagnostics": diags,
	}
	sendResult(req.ID, result)
}

func handleBuild(ctx context.Context, req RequestEnvelope) {
	select {
	case <-ctx.Done():
		sendError(req.ID, -32800, "Request Cancelled")
		return
	default:
	}

	var params TargetParams
	if req.Params != nil {
		json.Unmarshal(req.Params, &params)
	}
	
	uri := params.URI
	if uri == "" {
		uri = params.Entry
	}

	if uri == "" {
		sendError(req.ID, -32602, "Missing 'uri' or 'entry' in params")
		return
	}

	outDir := params.Target
	if outDir == "" {
		outDir = "dist"
	}
	canonicalOutDir, err := resolveAndCheckSandbox(outDir)
	if err != nil {
		sendError(req.ID, -32001, err.Error())
		return
	}
	os.MkdirAll(canonicalOutDir, 0755)

	sourceCode, _, ok := getSourceCode(req.ID, uri, params.Source, params.Version)
	if !ok {
		return
	}

	l := compiler.NewLexer(sourceCode)
	p := compiler.NewParser(l)
	astNodes := p.Parse()

	select {
	case <-ctx.Done():
		sendError(req.ID, -32800, "Request Cancelled")
		return
	default:
	}

	if len(p.Errors) > 0 {
		diags := parseDiagnostics(params.Entry, p.Errors)
		result := map[string]interface{}{
			"success":     false,
			"diagnostics": diags,
		}
		sendResult(req.ID, result)
		return
	}

	generator := compiler.NewIRGenerator()
	ir := generator.Generate(astNodes)
	jsonOut, _ := json.MarshalIndent(ir, "", "  ")

	base := strings.TrimSuffix(filepath.Base(params.Entry), filepath.Ext(params.Entry))
	outputFile := filepath.Join(canonicalOutDir, base+".ir.json")
	os.WriteFile(outputFile, jsonOut, 0644)
	
	binOut, _ := compiler.EncodeBinaryIR(ir.Nodes)
	os.WriteFile(filepath.Join(canonicalOutDir, base+".ir.bin"), binOut, 0644)

	result := map[string]interface{}{
		"success": true,
		"metrics": map[string]interface{}{
			"nodes":             len(astNodes),
			"binary_size_bytes": len(binOut),
		},
	}
	sendResult(req.ID, result)
}
