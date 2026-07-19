package compiler

type OpCode string

const (
	OpCreateNode   OpCode = "CREATE_NODE"
	OpAppendChild  OpCode = "APPEND_CHILD"
	OpSetText      OpCode = "SET_TEXT"
	OpSetAttribute OpCode = "SET_ATTRIBUTE"
	OpAddEvent     OpCode = "ADD_EVENT"
	OpDeclareState OpCode = "DECLARE_STATE"
	OpBindText          OpCode = "BIND_TEXT"
	OpCreateConditional OpCode = "CREATE_CONDITIONAL"
	OpBindInput         OpCode = "BIND_INPUT"
	OpAssign            OpCode = "ASSIGN"
	OpIncrement         OpCode = "INCREMENT"
	OpDecrement         OpCode = "DECREMENT"
	OpRenderList        OpCode = "RENDER_LIST"
	OpBindLoading       OpCode = "BIND_LOADING"
)

type Instruction struct {
	Op        OpCode   `json:"op"`
	ID        int      `json:"id,omitempty"`
	Tag       string   `json:"tag,omitempty"`
	Parent    int      `json:"parent,omitempty"`
	Child     int      `json:"child,omitempty"`
	Key       string   `json:"key,omitempty"`
	Value        string   `json:"value,omitempty"`
	Type         string   `json:"type,omitempty"`
	Initial      any      `json:"initial,omitempty"`
	Template     string   `json:"template,omitempty"`
	StateKeys    []string `json:"state_keys,omitempty"`
	Event        string   `json:"event,omitempty"`
	Mutation     string   `json:"mutation,omitempty"`
	IsHidden     bool     `json:"is_hidden,omitempty"`
	StateKey    string        `json:"state_key,omitempty"`
	Operator    string        `json:"operator,omitempty"`
	CompareVal  string        `json:"compare_val,omitempty"`
	TrueBranch  []Instruction `json:"true_branch,omitempty"`
	FalseBranch []Instruction `json:"false_branch,omitempty"`
	
	IterableKey  string        `json:"iterable_key,omitempty"`
	IteratorName string        `json:"iterator_name,omitempty"`
	LoopTemplate []Instruction `json:"loop_template,omitempty"`
}

type IRBlueprint struct {
	Mutations map[string][]Instruction `json:"mutations"`
	Nodes     []Instruction            `json:"nodes"`
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

func CreateConditional(id int, parent int, stateKey string, operator string, compareVal string, trueBranch []Instruction, falseBranch []Instruction) Instruction {
	return Instruction{
		Op:          OpCreateConditional,
		ID:          id,
		Parent:      parent,
		StateKey:    stateKey,
		Operator:    operator,
		CompareVal:  compareVal,
		TrueBranch:  trueBranch,
		FalseBranch: falseBranch,
	}
}

func BindInput(id int, stateKey string) Instruction {
	return Instruction{Op: OpBindInput, ID: id, StateKey: stateKey}
}

func RenderList(id int, parent int, iterableKey string, iteratorName string, loopTemplate []Instruction) Instruction {
	return Instruction{
		Op:           OpRenderList,
		ID:           id,
		Parent:       parent,
		IterableKey:  iterableKey,
		IteratorName: iteratorName,
		LoopTemplate: loopTemplate,
	}
}

func BindLoading(id int, stateKey string, loaderType string, loaderSpeed string) Instruction {
	return Instruction{
		Op:       OpBindLoading,
		ID:       id,
		StateKey: stateKey,
		Tag:      loaderType,
		Value:    loaderSpeed,
	}
}

