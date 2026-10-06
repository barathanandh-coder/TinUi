package compiler

type Position struct {
	Line      int `json:"line"`
	Character int `json:"character"`
}

type Range struct {
	Start Position `json:"start"`
	End   Position `json:"end"`
}

type ImportDecl struct {
	Path    string   `json:"path"`
	Symbols []string `json:"symbols"`
	Range   Range    `json:"range"`
}

type FileAST struct {
	URI        string
	Imports    []*ImportDecl
	Components []*Component
}

type Node struct {
	Name       string
	Args       []string
	Attributes map[string]string
	Children   []ASTNode
	IsFString  bool // True if Args[0] was an f-string
	Range      Range
}

type ASTNode interface {
	isASTNode()
	GetRange() Range
}

func (n *Node) isASTNode()              {}
func (c *ConditionalNode) isASTNode()   {}
func (f *ForNode) isASTNode()           {}
func (h *HiddenWrapperNode) isASTNode() {}

func (n *Node) GetRange() Range              { return n.Range }
func (c *ConditionalNode) GetRange() Range   { return c.Range }
func (f *ForNode) GetRange() Range           { return f.Range }
func (h *HiddenWrapperNode) GetRange() Range { return h.Child.GetRange() }

type HiddenWrapperNode struct {
	Child ASTNode
}

type ConditionalNode struct {
	ConditionVar string
	Operator     string
	Value        string
	TrueBranch   []ASTNode
	FalseBranch  []ASTNode
	Range        Range
}

type ForNode struct {
	IteratorName string
	IterableKey  string
	Body         []ASTNode
	Range        Range
}

// PropDecl represents a property definition for a Component.
type PropDecl struct {
	Name     string
	TypeHint string
	Default  string
}

type Component struct {
	Name      string
	Props     []PropDecl
	States    []*StateDecl
	Mutations []*DefNode
	RootNodes []ASTNode
	Range     Range
}

type StateDecl struct {
	Name    string
	Initial string
	Range   Range
}

type MutationNode struct {
	StateKey string
	Operator string
	Value    string
	Range    Range
}

type DefNode struct {
	FuncName  string
	Mutations []MutationNode
	Range     Range
}

