package compiler

type Node struct {
	Name       string
	Args       []string
	Attributes map[string]string
	Children   []*Node
	IsFString  bool // True if Args[0] was an f-string
}

type Component struct {
	Name      string
	Args      []string
	States    []*StateDecl
	Mutations []*Mutation
	RootNodes []*Node
}

type StateDecl struct {
	Name    string
	Initial string
}

type Mutation struct {
	Name string
	Body string
}
