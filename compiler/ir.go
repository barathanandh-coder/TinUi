package compiler

type OpCode string

const (
	OpCreateNode   OpCode = "CREATE_NODE"
	OpAppendChild  OpCode = "APPEND_CHILD"
	OpSetText      OpCode = "SET_TEXT"
	OpSetAttribute OpCode = "SET_ATTRIBUTE"
	OpAddEvent     OpCode = "ADD_EVENT"
	OpDeclareState OpCode = "DECLARE_STATE"
	OpBindText     OpCode = "BIND_TEXT"
)

type Instruction struct {
	Op        OpCode   `json:"op"`
	ID        int      `json:"id,omitempty"`
	Tag       string   `json:"tag,omitempty"`
	Parent    int      `json:"parent,omitempty"`
	Child     int      `json:"child,omitempty"`
	Key       string   `json:"key,omitempty"`
	Value     string   `json:"value,omitempty"`
	Type      string   `json:"type,omitempty"`
	Initial   any      `json:"initial,omitempty"`
	Template  string   `json:"template,omitempty"`
	StateKeys []string `json:"state_keys,omitempty"`
	Event     string   `json:"event,omitempty"`
	Mutation  string   `json:"mutation,omitempty"`
}

func CreateNode(id int, tag string) Instruction {
	return Instruction{Op: OpCreateNode, ID: id, Tag: tag}
}

func AppendChild(parent int, child int) Instruction {
	return Instruction{Op: OpAppendChild, Parent: parent, Child: child}
}

func SetText(id int, value string) Instruction {
	return Instruction{Op: OpSetText, ID: id, Value: value}
}

func SetAttribute(id int, key string, value string) Instruction {
	return Instruction{Op: OpSetAttribute, ID: id, Key: key, Value: value}
}

func AddEvent(id int, event string, mutation string) Instruction {
	return Instruction{Op: OpAddEvent, ID: id, Event: event, Mutation: mutation}
}

func DeclareState(key string, typeStr string, initial any) Instruction {
	return Instruction{Op: OpDeclareState, Key: key, Type: typeStr, Initial: initial}
}

func BindText(id int, template string, stateKeys []string) Instruction {
	return Instruction{Op: OpBindText, ID: id, Template: template, StateKeys: stateKeys}
}
