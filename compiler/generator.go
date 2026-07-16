package compiler

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
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

	if len(GlobalKeyframes) > 0 {
		styleNodeID := g.nextID
		g.nextID++
		g.instructions = append(g.instructions, CreateNode(styleNodeID, "style"))
		var allFrames []string
		for _, v := range GlobalKeyframes {
			allFrames = append(allFrames, v)
		}
		g.instructions = append(g.instructions, SetText(styleNodeID, strings.Join(allFrames, " ")))
		g.instructions = append(g.instructions, AppendChild(0, styleNodeID))
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

		mappedTag, ok := TagMap[n.Name]
		if !ok {
			mappedTag = n.Name
		}
		g.instructions = append(g.instructions, CreateNode(currentID, mappedTag))

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

		compiledAttrs := CompileAttributes(n.Name, n.Attributes)

		for key, value := range compiledAttrs {
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
			} else if key == "innerText" {
				// handled differently if needed, but innerText can just be an attribute or text node
				g.instructions = append(g.instructions, SetText(currentID, value))
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

var GlobalKeyframes map[string]string

func RegisterGlobalKeyframes(name, frames string) {
	if GlobalKeyframes == nil {
		GlobalKeyframes = make(map[string]string)
	}
	GlobalKeyframes[name] = frames
}

// TagMap maps TinPyUI high-level components to browser primitives
var TagMap = map[string]string{
	"Section":            "div",
	"Row":                "div",
	"Card":               "div",
	"Form":               "div",
	"Heading":            "h2",
	"Text":               "p",
	"GradientText":       "h1",
	"Button":             "button",
	"Input":              "input",
	"AnimatedBackground": "div",
	"Navbar":             "nav",
	"NavLink":            "a",
	"Marquee":            "marquee",
}

// ColorPalette defines the framework's internal global design variables
var ColorPalette = map[string]string{
	"neon-cyan":   "#00f2fe",
	"neon-purple": "#9b51e0",
	"neon-pink":   "#ff007f",
	"dark-core":   "#0a0b10",
	"dark-glass":  "rgba(18, 19, 28, 0.75)",
	"white":       "#ffffff",
	"muted":       "#747d8c",
}

// CompileAttributes converts parsed TinPyUI properties into a raw inline style string
func CompileAttributes(componentName string, props map[string]string) map[string]string {
	attributes := make(map[string]string)
	var styles []string

	// Apply component-specific base styling defaults
	switch componentName {
	case "AnimatedBackground":
		styles = append(styles, "position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; overflow-y: auto; box-sizing: border-box;")
		if _, ok := props["primaryColor"]; ok {
			styles = append(styles, fmt.Sprintf("background: radial-gradient(circle at top right, rgba(155,81,224,0.15), %s);", ColorPalette["dark-core"]))
		} else {
			styles = append(styles, fmt.Sprintf("background: %s;", ColorPalette["dark-core"]))
		}
		if p, ok := props["particles"]; ok && p == "true" {
			attributes["data-render-particles"] = "enabled"
			if count, ok := props["particleCount"]; ok {
				attributes["data-particle-count"] = count
			} else {
				attributes["data-particle-count"] = "30"
			}
		}
	case "Marquee":
		styles = append(styles, "display: flex; white-space: nowrap; overflow: hidden; width: 100%; font-family: monospace;")
		if dir, ok := props["direction"]; ok {
			attributes["direction"] = dir
		} else {
			attributes["direction"] = "left"
		}
		if scrollSpeed, ok := props["speed"]; ok {
			if scrollSpeed == "fast" {
				attributes["scrollamount"] = "12"
			} else {
				attributes["scrollamount"] = "6"
			}
		}
	case "Row":
		styles = append(styles, "display: flex; flex-direction: row; box-sizing: border-box;")
	case "Form", "Section", "Card":
		styles = append(styles, "display: flex; flex-direction: column; box-sizing: border-box;")
	case "Navbar":
		styles = append(styles, "display: flex; position: sticky; top: 0; width: 100%; z-index: 100; box-sizing: border-box;")
	case "Button":
		styles = append(styles, "cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-weight: 600; border: none; transition: all 0.2s ease;")
	case "Input":
		styles = append(styles, "outline: none; box-sizing: border-box; background: rgba(0,0,0,0.2); color: #ffffff;")
	}

	// Dynamic property conversion
	for key, val := range props {
		switch key {
		case "align":
			if val == "center" {
				styles = append(styles, "align-items: center;")
			}
		case "justify":
			if val == "center" {
				styles = append(styles, "justify-content: center;")
			} else if val == "space-between" {
				styles = append(styles, "justify-content: space-between;")
			}
		case "maxWidth":
			styles = append(styles, fmt.Sprintf("max-width: %spx; width: 100%%; margin-left: auto; margin-right: auto;", val))
		case "width":
			if val == "full" {
				styles = append(styles, "width: 100%;")
			}
		case "padding", "paddingY", "paddingBottom":
			// Map padding models quickly
			if key == "padding" {
				styles = append(styles, fmt.Sprintf("padding: %spx;", val))
			} else if key == "paddingY" {
				styles = append(styles, fmt.Sprintf("padding-top: %spx; padding-bottom: %spx;", val, val))
			} else {
				styles = append(styles, fmt.Sprintf("padding-bottom: %spx;", val))
			}
		case "marginTop", "marginBottom":
			if key == "marginTop" {
				styles = append(styles, fmt.Sprintf("margin-top: %spx;", val))
			} else {
				styles = append(styles, fmt.Sprintf("margin-bottom: %spx;", val))
			}
		case "gap":
			styles = append(styles, fmt.Sprintf("gap: %spx;", val))
		case "hoverGlow":
			if hex, exists := ColorPalette[val]; exists {
				attributes["data-hover-glow"] = hex
				hasTransition := false
				for _, s := range styles {
					if strings.Contains(s, "transition:") {
						hasTransition = true
						break
					}
				}
				if !hasTransition {
					styles = append(styles, "transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);")
				}
			}
		case "animation":
			duration := "0.6s"
			if d, customDuration := props["duration"]; customDuration {
				duration = d + "s"
			}
			
			switch val {
			case "fade-in-up":
				styles = append(styles, fmt.Sprintf("animation: fadeInUp %s cubic-bezier(0.16, 1, 0.3, 1) forwards;", duration))
				RegisterGlobalKeyframes("fadeInUp", "@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }")
			case "pulse":
				speed := "2s"
				if s, customSpeed := props["speed"]; customSpeed {
					if s == "slow" { speed = "3.5s" } else if s == "fast" { speed = "1s" }
				}
				styles = append(styles, fmt.Sprintf("animation: pulse %s infinite ease-in-out;", speed))
				RegisterGlobalKeyframes("pulse", "@keyframes pulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.03); opacity: 0.8; } }")
			}
		case "color":
			if hex, exists := ColorPalette[val]; exists {
				styles = append(styles, fmt.Sprintf("color: %s;", hex))
			}
		case "background":
			if hex, exists := ColorPalette[val]; exists {
				styles = append(styles, fmt.Sprintf("background-color: %s;", hex))
			}
		case "border":
			if hex, exists := ColorPalette[val]; exists {
				styles = append(styles, fmt.Sprintf("border: 1px solid %s;", hex))
			} else if val == "subtle" {
				styles = append(styles, "border: 1px solid rgba(255,255,255,0.1);")
			}
		case "radius":
			if val == "pill" {
				styles = append(styles, "border-radius: 9999px;")
			} else {
				styles = append(styles, fmt.Sprintf("border-radius: %spx;", val))
			}
		case "weight":
			if val == "bold" {
				styles = append(styles, "font-weight: bold;")
			}
		case "size":
			if val == "hero" {
				styles = append(styles, "font-size: 3.5rem; font-weight: 800; margin: 0;")
			} else if val == "large" {
				styles = append(styles, "font-size: 1.25rem; margin: 0;")
			}
		case "blur":
			if val == "true" {
				styles = append(styles, "backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);")
			}
		case "placeholder":
			attributes["placeholder"] = val
		case "value":
			attributes["value"] = val
		case "text":
			attributes["innerText"] = val
		case "class_", "bind", "on_click":
			attributes[key] = val
		}
	}

	// Handle gradient text effects explicitly
	if componentName == "GradientText" {
		styles = append(styles, "background: linear-gradient(45deg, #00f2fe, #9b51e0); -webkit-background-clip: text; -webkit-text-fill-color: transparent;")
	}

	// Consolidate array slice to style attribute
	if len(styles) > 0 {
		attributes["style"] = strings.Join(styles, " ")
	}

	return attributes
}
