package compiler

type Node struct {
	Name       string
	Args       []string
	Attributes map[string]string
	Children   []ASTNode
	IsFString  bool // True if Args[0] was an f-string
}

type ASTNode interface {
	isASTNode()
}

func (n *Node) isASTNode() {}
func (c *ConditionalNode) isASTNode() {}
func (f *ForNode) isASTNode() {}
func (h *HiddenWrapperNode) isASTNode() {}

type HiddenWrapperNode struct {
	Child ASTNode
}

type ConditionalNode struct {
	ConditionVar string
	Operator     string
	Value        string
	TrueBranch   []ASTNode
	FalseBranch  []ASTNode
}

type ForNode struct {
	IteratorName string
	IterableKey  string
	Body         []ASTNode
}

type Component struct {
	Name      string
	Args      []string
	States    []*StateDecl
	Mutations []*DefNode
	RootNodes []ASTNode
}

type StateDecl struct {
	Name    string
	Initial string
}

type MutationNode struct {
	StateKey string
	Operator string
	Value    string
}

type DefNode struct {
	FuncName  string
	Mutations []MutationNode
}
