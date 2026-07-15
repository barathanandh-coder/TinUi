package compiler

import (
	"regexp"
	"strconv"
)

type IRGenerator struct {
	instructions []Instruction
	nextID       int
}

func NewIRGenerator() *IRGenerator {
	return &IRGenerator{
		instructions: []Instruction{},
		nextID:       1,
	}
}

func (g *IRGenerator) Generate(components []*Component) IRBlueprint {
	blueprint := IRBlueprint{
		Mutations: make(map[string][]Instruction),
		Nodes:     []Instruction{},
	}

	for _, comp := range components {
		for _, state := range comp.States {
			var val any
			var typ string
			if v, err := strconv.Atoi(state.Initial); err == nil {
				val = v
				typ = "int"
			} else {
				if state.Initial == "start_val" { // Mock resolution for Milestone 1
					val = 0
					typ = "int"
				} else {
					val = state.Initial
					typ = "string"
				}
			}
			g.instructions = append(g.instructions, DeclareState(state.Name, typ, val))
		}

		for k, v := range g.generateMutations(comp.Mutations) {
			blueprint.Mutations[k] = v
		}

		for _, root := range comp.RootNodes {
			g.traverse(root, 0)
		}
	}
	blueprint.Nodes = g.instructions
	return blueprint
}

func (g *IRGenerator) generateMutations(defs []*DefNode) map[string][]Instruction {
	mutationsMap := make(map[string][]Instruction)
	
	for _, def := range defs {
		var instructions []Instruction
		
		for _, mut := range def.Mutations {
			opCode := OpAssign
			if mut.Operator == "+=" {
				opCode = OpIncrement
			} else if mut.Operator == "-=" {
				opCode = OpDecrement
			}
			
			instructions = append(instructions, Instruction{
				Op:       opCode,
				StateKey: mut.StateKey,
				Value:    mut.Value,
			})
		}
		mutationsMap[def.FuncName] = instructions
	}
	
	return mutationsMap
}

var fStringRegex = regexp.MustCompile(`\{([a-zA-Z_][a-zA-Z0-9_]*)\}`)

func (g *IRGenerator) traverse(astNode ASTNode, parentID int) {
	switch n := astNode.(type) {
	case *Node:
		currentID := g.nextID
		g.nextID++

		tag := mapComponentToTag(n.Name)
		g.instructions = append(g.instructions, CreateNode(currentID, tag))

		if len(n.Args) > 0 {
			if n.IsFString {
				template := fStringRegex.ReplaceAllString(n.Args[0], "{}")
				matches := fStringRegex.FindAllStringSubmatch(n.Args[0], -1)

				var stateKeys []string
				for _, match := range matches {
					stateKeys = append(stateKeys, match[1])
				}
				g.instructions = append(g.instructions, BindText(currentID, template, stateKeys))
			} else {
				g.instructions = append(g.instructions, SetText(currentID, n.Args[0]))
			}
		}

		for key, value := range n.Attributes {
			if key == "class_" {
				key = "class"
			}

			if key == "bind" {
				g.instructions = append(g.instructions, BindInput(currentID, value))
				g.instructions = append(g.instructions, SetAttribute(currentID, "data-bind", value))
				continue
			}

			if key == "on_click" {
				g.instructions = append(g.instructions, AddEvent(currentID, "click", value))
			} else {
				g.instructions = append(g.instructions, SetAttribute(currentID, key, value))
			}
		}

		g.instructions = append(g.instructions, AppendChild(parentID, currentID))

		for _, child := range n.Children {
			g.traverse(child, currentID)
		}

	case *ConditionalNode:
		currentID := g.nextID
		g.nextID++
		
		trueInsts := g.generateInstructions(n.TrueBranch, currentID)
		falseInsts := g.generateInstructions(n.FalseBranch, currentID)

		g.instructions = append(g.instructions, CreateConditional(
			currentID,
			parentID,
			n.ConditionVar,
			n.Operator,
			n.Value,
			trueInsts,
			falseInsts,
		))

	case *ForNode:
		currentID := g.nextID
		g.nextID++
		
		loopTemplate := g.generateInstructions(n.Body, currentID)
		
		g.instructions = append(g.instructions, RenderList(
			currentID,
			parentID,
			n.IterableKey,
			n.IteratorName,
			loopTemplate,
		))
	}
}

func (g *IRGenerator) generateInstructions(nodes []ASTNode, parentID int) []Instruction {
	oldInstructions := g.instructions
	g.instructions = []Instruction{}
	for _, n := range nodes {
		g.traverse(n, parentID)
	}
	res := g.instructions
	g.instructions = oldInstructions
	return res
}

func mapComponentToTag(name string) string {
	switch name {
	case "column", "row", "container":
		return "div"
	case "text":
		return "span"
	case "button":
		return "button"
	case "image":
		return "img"
	case "input":
		return "input"
	default:
		return name
	}
}
