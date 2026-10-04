package agent

import "encoding/json"

type RequestEnvelope struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      interface{}     `json:"id"`
	Method  string          `json:"method"`
	Params  json.RawMessage `json:"params,omitempty"`
}

type ResponseEnvelope struct {
	JSONRPC string         `json:"jsonrpc"`
	ID      interface{}    `json:"id"`
	Result  interface{}    `json:"result,omitempty"`
	Error   *ProtocolError `json:"error,omitempty"`
}

type ProtocolError struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

type InitializeResponse struct {
	ProtocolVersion string   `json:"protocolVersion"`
	TinuiVersion    string   `json:"tinuiVersion"`
	Capabilities    []string `json:"capabilities"`
}

type Diagnostic struct {
	ErrorCode        string            `json:"error_code"`
	Category         string            `json:"category"`
	Severity         string            `json:"severity"`
	File             string            `json:"file"`
	Line             int               `json:"line"`
	Column           int               `json:"column"` // Wait, protocol specified 'column', but TextEdit uses 'character'. We'll stick to 'column' for diagnostic itself, as per schema
	Message          string            `json:"message"`
	ContextSnippet   string            `json:"context_snippet,omitempty"`
	ASTNode          string            `json:"ast_node,omitempty"`
	RepairSuggestion *RepairSuggestion `json:"repair_suggestion,omitempty"`
}

type RepairSuggestion struct {
	Description     string     `json:"description"`
	Edits           []TextEdit `json:"edits"`
	IsDeterministic bool       `json:"is_deterministic"`
}

type TextEdit struct {
	Range   Range  `json:"range"`
	NewText string `json:"newText"`
}

type Range struct {
	Start Position `json:"start"`
	End   Position `json:"end"`
}

type Position struct {
	Line      int `json:"line"`
	Character int `json:"character"`
}

type ProjectGraph struct {
	Root       string      `json:"root"`
	Components []Component `json:"components"`
}

type Component struct {
	ID           string   `json:"id"`
	File         string   `json:"file"`
	Dependencies []string `json:"dependencies"`
}

type ProgressReport struct {
	Token      string `json:"token"`
	Status     string `json:"status"` // begin, report, end
	Percentage int    `json:"percentage,omitempty"`
	Message    string `json:"message,omitempty"`
}

// CheckParams and BuildParams
type TargetParams struct {
	URI     string `json:"uri,omitempty"`
	Entry   string `json:"entry,omitempty"`
	Target  string `json:"target,omitempty"`
	Source  string `json:"source,omitempty"`
	Version int    `json:"version,omitempty"`
}

type UpdateDocumentParams struct {
	URI     string `json:"uri"`
	Source  string `json:"source"`
	Version int    `json:"version"`
}

type CloseDocumentParams struct {
	URI string `json:"uri"`
}

type CancelParams struct {
	ID interface{} `json:"id"`
}

type QueryParams struct {
	Kind     string   `json:"kind"`
	Document string   `json:"document"`
	Position Position `json:"position"`
	Version  int      `json:"version,omitempty"`
}

type HoverResponse struct {
	Contents string `json:"contents"`
	Range    Range  `json:"range"`
	Version  int    `json:"version,omitempty"`
}

type DefinitionResponse struct {
	URI     string `json:"uri"`
	Range   Range  `json:"range"`
	Version int    `json:"version,omitempty"`
}

type CompletionItem struct {
	Label         string `json:"label"`
	Kind          string `json:"kind,omitempty"`
	Detail        string `json:"detail,omitempty"`
	Documentation string `json:"documentation,omitempty"`
}

type CompletionResponse struct {
	Items   []CompletionItem `json:"items"`
	Version int              `json:"version,omitempty"`
}

