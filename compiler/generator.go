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

func (g *IRGenerator) Generate(components []*Component) []Instruction {
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

		for _, root := range comp.RootNodes {
			g.traverse(root, 0)
		}
	}
	return g.instructions
}

var fStringRegex = regexp.MustCompile(`\{([a-zA-Z_][a-zA-Z0-9_]*)\}`)

func (g *IRGenerator) traverse(node *Node, parentID int) {
	currentID := g.nextID
	g.nextID++

	tag := mapComponentToTag(node.Name)
	g.instructions = append(g.instructions, CreateNode(currentID, tag))

	if len(node.Args) > 0 {
		if node.IsFString {
			template := fStringRegex.ReplaceAllString(node.Args[0], "{}")
			matches := fStringRegex.FindAllStringSubmatch(node.Args[0], -1)

			var stateKeys []string
			for _, match := range matches {
				stateKeys = append(stateKeys, match[1])
			}
			g.instructions = append(g.instructions, BindText(currentID, template, stateKeys))
		} else {
			g.instructions = append(g.instructions, SetText(currentID, node.Args[0]))
		}
	}

	for key, value := range node.Attributes {
		if key == "class_" {
			key = "class"
		}

		if key == "on_click" {
			g.instructions = append(g.instructions, AddEvent(currentID, "click", value))
		} else {
			g.instructions = append(g.instructions, SetAttribute(currentID, key, value))
		}
	}

	g.instructions = append(g.instructions, AppendChild(parentID, currentID))

	for _, child := range node.Children {
		g.traverse(child, currentID)
	}
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
