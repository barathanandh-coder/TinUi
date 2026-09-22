package compiler

import (
	"fmt"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

type IRGenerator struct {
	instructions []Instruction
	nextID       int
	components   map[string]*Component
}

func NewIRGenerator() *IRGenerator {
	return &IRGenerator{
		instructions: []Instruction{},
		nextID:       1,
		components:   make(map[string]*Component),
	}
}

func (g *IRGenerator) Generate(components []*Component) IRBlueprint {
	blueprint := IRBlueprint{
		Mutations: make(map[string][]Instruction),
		Nodes:     []Instruction{},
	}

	// Build component lookup map
	for _, comp := range components {
		g.components[comp.Name] = comp
	}

	// Declare state and mutations across all components
	declaredStates := make(map[string]bool)
	for _, comp := range components {
		for _, state := range comp.States {
			if declaredStates[state.Name] {
				continue
			}
			declaredStates[state.Name] = true
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
	}

	// Traverse the main component as root (fallback to App or first component)
	var rootComp *Component
	for _, comp := range components {
		if comp.Name == "Main" || comp.Name == "App" {
			rootComp = comp
			break
		}
	}
	if rootComp == nil && len(components) > 0 {
		rootComp = components[0]
	}

	if rootComp != nil {
		for _, root := range rootComp.RootNodes {
			g.traverse(root, 0, nil)
		}
	}

	// Add core framework styles unconditionally
	styleNodeID := g.nextID
	g.nextID++
	g.instructions = append(g.instructions, CreateNode(styleNodeID, "style"))
	
	coreStyles := `
    *, *::before, *::after { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; background: #030712 !important; color: white !important; font-family: 'Plus Jakarta Sans', sans-serif; overflow-x: hidden; scroll-behavior: smooth; }
    #tinui-root { position: relative; min-height: 100vh; }
    .material-symbols-outlined { font-family: 'Material Symbols Outlined'; font-weight: normal; font-style: normal; line-height: 1; letter-spacing: normal; text-transform: none; display: inline-block; white-space: nowrap; word-wrap: normal; }
    .cursor-trail { position: fixed; width: 20px; height: 20px; border-radius: 50%; pointer-events: none; z-index: 9999; background: radial-gradient(circle, rgba(207,188,255,0.8) 0%, transparent 70%); transition: transform 0.1s ease-out; }
    .glass-card { background: rgba(20, 18, 24, 0.2); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.05); }
    .neon-border-cyan { box-shadow: 0 0 15px rgba(0, 255, 255, 0.2); border-color: rgba(0, 255, 255, 0.3); }
    .neon-border-primary { box-shadow: 0 0 15px rgba(207,188,255,0.2); border-color: rgba(207,188,255,0.3); }
    .reveal-section { transition: all 1s cubic-bezier(0.4, 0, 0.2, 1); opacity: 0; transform: perspective(1000px) translateZ(-100px); filter: blur(10px); }
    .reveal-section.active { opacity: 1; transform: perspective(1000px) translateZ(0); filter: blur(0); }
    .glitch-hover:hover { animation: glitch 0.3s cubic-bezier(.25,.46,.45,.94) both infinite; }
    @keyframes glitch { 0% { transform: translate(0); } 20% { transform: translate(-2px, 2px); } 40% { transform: translate(-2px, -2px); } 60% { transform: translate(2px, 2px); } 80% { transform: translate(2px, -2px); } 100% { transform: translate(0); } }
    .pulse-glitch { animation: pulse-glitch 2s infinite; }
    @keyframes pulse-glitch { 0%, 100% { opacity: 1; filter: hue-rotate(0deg); } 50% { opacity: 0.8; filter: hue-rotate(90deg) brightness(1.2); } }
`
	var allFrames []string
	allFrames = append(allFrames, coreStyles)

	if len(GlobalKeyframes) > 0 {
		// Sort keyframes for determinism too!
		var frameKeys []string
		for k := range GlobalKeyframes {
			frameKeys = append(frameKeys, k)
		}
		sort.Strings(frameKeys)
		for _, k := range frameKeys {
			allFrames = append(allFrames, GlobalKeyframes[k])
		}
	}
	g.instructions = append(g.instructions, SetText(styleNodeID, strings.Join(allFrames, " ")))
	g.instructions = append(g.instructions, AppendChild(0, styleNodeID))

	// Dynamically inject Tailwind Config
	twConfigID := g.nextID
	g.nextID++
	g.instructions = append(g.instructions, CreateNode(twConfigID, "script"))
	g.instructions = append(g.instructions, SetAttribute(twConfigID, "id", "tailwind-config"))
	twConfigStr := `
	window.tailwind = window.tailwind || {};
	window.tailwind.config = {
		darkMode: "class",
		theme: {
		  extend: {
			"colors": {
					"on-tertiary-container": "#503d00", "surface-variant": "#36343a", "secondary-fixed-dim": "#cdc0e9",
					"on-error-container": "#ffdad6", "tertiary-container": "#c9a74d", "surface-tint": "#cfbcff",
					"primary": "#cfbcff", "outline-variant": "#494551", "secondary": "#cdc0e9", "on-surface": "#e6e0e9",
					"on-background": "#e6e0e9", "surface": "#141218", "on-secondary-fixed": "#1f1635", "background": "transparent",
					"on-tertiary-fixed": "#241a00", "on-tertiary": "#3e2e00", "on-primary-fixed-variant": "#4f378a",
					"surface-container-high": "#2b292f", "primary-container": "#6750a4", "inverse-surface": "#e6e0e9",
					"on-secondary-fixed-variant": "#4b4263", "surface-container-low": "#1d1b20", "on-error": "#690005",
					"tertiary-fixed-dim": "#e7c365", "outline": "#948e9c", "surface-dim": "#141218", "secondary-container": "#4d4465",
					"primary-fixed": "#e9ddff", "error": "#ffb4ab", "inverse-primary": "#6750a4", "on-primary-container": "#e0d2ff",
					"on-primary-fixed": "#22005d", "inverse-on-surface": "#322f35", "tertiary-fixed": "#ffdf93",
					"surface-container": "#211f24", "on-surface-variant": "#cbc4d2", "primary-fixed-dim": "#cfbcff",
					"on-primary": "#381e72", "surface-container-lowest": "#0f0d13", "on-tertiary-fixed-variant": "#594400",
					"error-container": "#93000a", "surface-bright": "#3b383e", "secondary-fixed": "#e9ddff",
					"surface-container-highest": "#36343a", "on-secondary-container": "#bfb2da", "on-secondary": "#342b4b",
					"tertiary": "#e7c365"
			},
			"spacing": { "margin-desktop": "2.5rem", "margin-mobile": "1rem", "max-width": "1440px" },
			"fontFamily": { "label-mono": ["JetBrains Mono"], "display-lg-mobile": ["Sora"], "display-lg": ["Sora"], "headline-md": ["Sora"], "body-lg": ["Plus Jakarta Sans"], "body-md": ["Plus Jakarta Sans"] }
		  }
		}
	}
	`
	g.instructions = append(g.instructions, SetText(twConfigID, twConfigStr))
	g.instructions = append(g.instructions, AppendChild(0, twConfigID))

	// Dynamically inject Tailwind CDN
	twCDNID := g.nextID
	g.nextID++
	g.instructions = append(g.instructions, CreateNode(twCDNID, "script"))
	g.instructions = append(g.instructions, SetAttribute(twCDNID, "src", "https://cdn.tailwindcss.com?plugins=forms,container-queries"))
	g.instructions = append(g.instructions, AppendChild(0, twCDNID))

	// Dynamically inject Google Fonts (Sora & Plus Jakarta Sans)
	fontID := g.nextID
	g.nextID++
	g.instructions = append(g.instructions, CreateNode(fontID, "link"))
	g.instructions = append(g.instructions, SetAttribute(fontID, "href", "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Sora:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap"))
	g.instructions = append(g.instructions, SetAttribute(fontID, "rel", "stylesheet"))
	g.instructions = append(g.instructions, AppendChild(0, fontID))

	// Dynamically inject Material Symbols
	iconID := g.nextID
	g.nextID++
	g.instructions = append(g.instructions, CreateNode(iconID, "link"))
	g.instructions = append(g.instructions, SetAttribute(iconID, "href", "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0"))
	g.instructions = append(g.instructions, SetAttribute(iconID, "rel", "stylesheet"))
	g.instructions = append(g.instructions, AppendChild(0, iconID))


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

func (g *IRGenerator) traverse(astNode ASTNode, parentID int, props map[string]string) {
	switch n := astNode.(type) {
	case *Node:
		// Substitute props in attributes
		if props != nil {
			for k, v := range n.Attributes {
				if propVal, exists := props[v]; exists {
					n.Attributes[k] = propVal
				}
			}
			for i, arg := range n.Args {
				if propVal, exists := props[arg]; exists {
					n.Args[i] = propVal
				}
			}
		}

		if compDef, exists := g.components[n.Name]; exists {
			// Inline custom component
			childProps := make(map[string]string)
			for i, argName := range compDef.Args {
				if i < len(n.Args) {
					childProps[argName] = n.Args[i]
				} else if val, ok := n.Attributes[argName]; ok {
					childProps[argName] = val
				}
			}
			// Map any other attributes passed
			for k, v := range n.Attributes {
				if _, exists := childProps[k]; !exists {
					childProps[k] = v
				}
			}

			for _, child := range compDef.RootNodes {
				g.traverse(child, parentID, childProps)
			}
			return
		}

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

		// Sort attributes for deterministic output
		var attrKeys []string
		for k := range compiledAttrs {
			attrKeys = append(attrKeys, k)
		}
		sort.Strings(attrKeys)

		for _, key := range attrKeys {
			value := compiledAttrs[key]
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
			} else if key == "data-bind-loading" {
				// We don't have loaderType easily here unless we pass it from attrs, so we just add the attribute and let Wasm handle it, OR we emit OpBindLoading.
				// Since we add data-loader-type via attributes too, we can emit OpBindLoading with it.
				// For simplicity, we just emit SetAttribute, and we also emit OpBindLoading by extracting types from attrs map.
				loaderType, hasType := compiledAttrs["data-loader-type"]
				if !hasType {
					loaderType = "skeleton"
				}
				loaderSpeed, hasSpeed := compiledAttrs["data-loader-speed"]
				if !hasSpeed {
					loaderSpeed = "steady"
				}
				g.instructions = append(g.instructions, BindLoading(currentID, value, loaderType, loaderSpeed))
				g.instructions = append(g.instructions, SetAttribute(currentID, key, value))
			} else {
				g.instructions = append(g.instructions, SetAttribute(currentID, key, value))
			}
		}

		g.instructions = append(g.instructions, AppendChild(parentID, currentID))

		for _, child := range n.Children {
			g.traverse(child, currentID, props)
		}

		// If this is a Route node with a scene or component attribute, inline that component's nodes as children
		if n.Name == "Route" {
			sceneName := n.Attributes["scene"]
			if sceneName == "" {
				sceneName = n.Attributes["component"]
			}
			sceneName = strings.Trim(sceneName, "\"'")
			if sceneComp, exists := g.components[sceneName]; exists {
				for _, sceneNode := range sceneComp.RootNodes {
					g.traverse(sceneNode, currentID, props)
				}
			}
		}

	case *ConditionalNode:
		currentID := g.nextID
		g.nextID++

		trueInsts := g.generateInstructions(n.TrueBranch, currentID, props)
		falseInsts := g.generateInstructions(n.FalseBranch, currentID, props)

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

		loopTemplate := g.generateInstructions(n.Body, currentID, props)

		g.instructions = append(g.instructions, RenderList(
			currentID,
			parentID,
			n.IterableKey,
			n.IteratorName,
			loopTemplate,
		))

	case *HiddenWrapperNode:
		startIdx := len(g.instructions)
		g.traverse(n.Child, parentID, props)

		for i := startIdx; i < len(g.instructions); i++ {
			if g.instructions[i].Op == OpCreateNode {
				g.instructions[i].IsHidden = true
				break
			}
		}
	}
}

func (g *IRGenerator) generateInstructions(nodes []ASTNode, parentID int, props map[string]string) []Instruction {
	oldInstructions := g.instructions
	g.instructions = []Instruction{}
	for _, n := range nodes {
		g.traverse(n, parentID, props)
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
	"Section":            "section",
	"Row":                "div",
	"Card":               "div",
	"Form":               "form",
	"Heading":            "h2",
	"Text":               "p",
	"GradientText":       "span",
	"Button":             "button",
	"Input":              "input",
	"AnimatedBackground": "div",
	"ShaderLayer":        "div",
	"WebGLCanvas":        "canvas",
	"ParticleField":      "div",
	"Navbar":             "nav",
	"NavLink":            "a",
	"Marquee":            "marquee",
	"HeroContainer":      "div",
	"Span":               "span",
	"Router":             "div",
	"Route":              "div",
	"Container":          "div",
	"Surface":            "div",
	"CustomShader":       "canvas",
	"Preload":            "div",
	"Font":               "link",
	"Image":              "img",
	"Video":              "video",
	"Audio":              "audio",
	"Header":             "header",
	"Footer":             "footer",
	"Main":               "main",
	"Grid":               "div",
	"Badge":              "span",
	"Divider":            "hr",
	"Icon":               "span",
	"Link":               "a",
	"Label":              "label",
	"Select":             "select",
	"Textarea":           "textarea",
	"Modal":              "dialog",
	"Tooltip":            "div",
	"Progress":           "progress",
	"Spacer":             "div",
	"VirtualStack":       "div",
	"VirtualList":        "div",
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
		styles = append(styles, "position: relative; width: 100%; min-height: 100vh; box-sizing: border-box; z-index: 0;")
		effect := props["effect"]
		if effect == "" {
			effect = "particles"
		}
		attributes["data-shader-effect"] = effect
		attributes["data-bg-fixed"] = "true"
		if primary, ok := props["primaryColor"]; ok {
			attributes["data-shader-primary"] = primary
			if hex, exists := ColorPalette[primary]; exists {
				styles = append(styles, fmt.Sprintf("background: radial-gradient(circle at top right, %s22, %s);", hex, ColorPalette["dark-core"]))
			} else {
				styles = append(styles, fmt.Sprintf("background: radial-gradient(circle at top right, rgba(155,81,224,0.15), %s);", ColorPalette["dark-core"]))
			}
		} else {
			styles = append(styles, fmt.Sprintf("background: %s;", ColorPalette["dark-core"]))
		}
		if secondary, ok := props["secondaryColor"]; ok {
			attributes["data-shader-secondary"] = secondary
		}
	case "ShaderLayer":
		styles = append(styles, "position: relative; overflow: hidden; display: block;")
		effect := props["effect"]
		if effect == "" {
			effect = "cyber-wave"
		}
		attributes["data-shader-effect"] = effect
		if speed, ok := props["speed"]; ok {
			attributes["data-shader-speed"] = speed
		}
		if primary, ok := props["primaryColor"]; ok {
			attributes["data-shader-primary"] = primary
		}
		if secondary, ok := props["secondaryColor"]; ok {
			attributes["data-shader-secondary"] = secondary
		}
	case "WebGLCanvas":
		styles = append(styles, "display: block; width: 100%; height: 100%; pointer-events: none;")
		if code, ok := props["fragmentCode"]; ok {
			if errs := ValidateGLSL(code); len(errs) > 0 {
				fmt.Printf("\n--- TinPyUI GLSL Validation Error ---\n")
				for _, e := range errs {
					fmt.Println(e.Error())
				}
				fmt.Printf("--------------------------------------\n\n")
			}
			attributes["data-shader-code"] = code
			attributes["data-webgl-canvas"] = "true"
		}
		if uniforms, ok := props["uniforms"]; ok {
			attributes["data-shader-uniforms"] = uniforms
		}
	case "ParticleField":
		styles = append(styles, "position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; overflow: hidden;")
		attributes["data-particle-field"] = "true"
		if count, ok := props["count"]; ok {
			attributes["data-particle-count"] = count
		} else {
			attributes["data-particle-count"] = "60"
		}
		if color, ok := props["color"]; ok {
			attributes["data-particle-color"] = color
		}
		if speed, ok := props["speed"]; ok {
			attributes["data-particle-speed"] = speed
		}
		if interactive, ok := props["interactive"]; ok {
			attributes["data-particle-interactive"] = interactive
		}
	case "Icon":
		styles = append(styles, "font-family: 'Material Symbols Outlined'; font-size: 24px; display: inline-flex; align-items: center; justify-content: center;")
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
	case "Grid":
		cols := props["cols"]
		if cols == "" {
			cols = "3"
		}
		styles = append(styles, fmt.Sprintf("display: grid; grid-template-columns: repeat(%s, 1fr); box-sizing: border-box;", cols))
	case "Form", "Section", "Card":
		styles = append(styles, "display: flex; flex-direction: column; box-sizing: border-box;")
	case "Modal":
		styles = append(styles, "position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 1000; border: none; padding: 0;")
	case "HeroContainer":
		styles = append(styles, "display: flex; flex-direction: column; box-sizing: border-box; position: relative; overflow: hidden; min-height: 400px;")
	case "Container":
		styles = append(styles, "display: flex; flex-direction: column; box-sizing: border-box;")
	case "Surface":
		styles = append(styles, "display: block; position: relative; overflow: hidden;")
	case "CustomShader":
		styles = append(styles, "display: block; width: 100%; height: 100%; pointer-events: none;")
	case "VirtualStack", "VirtualList":
		styles = append(styles, "display: block; position: relative; width: 100%; overflow-y: auto; box-sizing: border-box;")
		attributes["data-virtual-stack"] = "true"
		if ih, ok := props["itemHeight"]; ok {
			attributes["data-item-height"] = ih
		}
		if tc, ok := props["totalCount"]; ok {
			attributes["data-total-count"] = tc
		}
	case "Router":
		styles = append(styles, "display: block; position: relative; width: 100%; min-height: calc(100vh - 80px);")
	case "Route":
		styles = append(styles, "display: block; position: relative; width: 100%;")
	case "Navbar":
		styles = append(styles, "display: flex; position: sticky; top: 0; width: 100%; z-index: 100; box-sizing: border-box;")
	case "Button":
		styles = append(styles, "cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-weight: 600; border: none; transition: all 0.2s ease; padding: 12px 28px; border-radius: 8px; font-size: 15px; font-family: inherit;")
		variant := props["variant"]
		if variant == "outline" {
			styles = append(styles, "background: transparent; border: 1px solid #00f2fe; color: #00f2fe;")
		} else {
			styles = append(styles, "background: #00f2fe; color: #0a0b10;")
		}
		if glow, ok := props["glow"]; ok {
			if hex, exists := ColorPalette[glow]; exists {
				styles = append(styles, fmt.Sprintf("box-shadow: 0 0 20px %s88;", hex))
			} else {
				styles = append(styles, fmt.Sprintf("box-shadow: 0 0 20px %s;", glow))
			}
		}
	case "Text":
		styles = append(styles, "margin: 0; color: #ffffff;")
	case "Input", "Textarea":
		styles = append(styles, "outline: none; box-sizing: border-box; background: rgba(0,0,0,0.2); color: #ffffff; padding: 10px 16px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.15);")
	case "Preload":
		styles = append(styles, "display: none;")
	case "Divider":
		styles = append(styles, "border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 0; width: 100%;")
	case "Font":
		if url, ok := props["url"]; ok {
			attributes["href"] = url
			attributes["rel"] = "preload"
			attributes["as"] = "font"
			attributes["crossorigin"] = "anonymous"
		}
	case "Image":
		if src, ok := props["src"]; ok {
			attributes["src"] = src
		}
		if alt, ok := props["alt"]; ok {
			attributes["alt"] = alt
		}
		if url, ok := props["url"]; ok {
			attributes["href"] = url
			attributes["rel"] = "preload"
			attributes["as"] = "image"
		}
	case "NavLink":
		if link, ok := props["link"]; ok {
			attributes["href"] = link
		}
		if target, ok := props["target"]; ok {
			attributes["target"] = target
		}
	}

	// Dynamic property conversion
	var propKeys []string
	for key := range props {
		propKeys = append(propKeys, key)
	}
	sort.Strings(propKeys)

	for _, key := range propKeys {
		val := props[key]
		switch key {
		case "align":
			switch val {
			case "center":
				styles = append(styles, "align-items: center;")
			case "flex-start", "start":
				styles = append(styles, "align-items: flex-start;")
			case "flex-end", "end":
				styles = append(styles, "align-items: flex-end;")
			case "stretch":
				styles = append(styles, "align-items: stretch;")
			}
		case "justify":
			switch val {
			case "center":
				styles = append(styles, "justify-content: center;")
			case "space-between":
				styles = append(styles, "justify-content: space-between;")
			case "space-around":
				styles = append(styles, "justify-content: space-around;")
			case "flex-start", "start":
				styles = append(styles, "justify-content: flex-start;")
			case "flex-end", "end":
				styles = append(styles, "justify-content: flex-end;")
			}
		case "maxWidth":
			if val != "0" {
				styles = append(styles, fmt.Sprintf("max-width: %spx; width: 100%%; margin-left: auto; margin-right: auto;", val))
			}
		case "minHeight":
			if val == "screen" {
				styles = append(styles, "min-height: 100vh;")
			} else {
				styles = append(styles, fmt.Sprintf("min-height: %spx;", val))
			}
		case "height":
			if val == "screen" {
				styles = append(styles, "height: 100vh;")
			} else if val == "full" {
				styles = append(styles, "height: 100%;")
			} else {
				styles = append(styles, fmt.Sprintf("height: %spx;", val))
			}
		case "overflow":
			styles = append(styles, fmt.Sprintf("overflow: %s;", val))
		case "opacity":
			styles = append(styles, fmt.Sprintf("opacity: %s;", val))
		case "flex":
			if val == "1" || val == "auto" {
				styles = append(styles, fmt.Sprintf("flex: %s;", val))
			}
		case "wrap":
			if strings.ToLower(val) == "true" || val == "1" {
				styles = append(styles, "flex-wrap: wrap;")
			}
		case "cols":
			// handled in Grid component init above
		case "width":
			if val == "full" {
				styles = append(styles, "width: 100%;")
			} else if val != "" {
				styles = append(styles, fmt.Sprintf("width: %spx;", val))
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
		case "position":
			styles = append(styles, fmt.Sprintf("position: %s;", val))
		case "top":
			styles = append(styles, fmt.Sprintf("top: %spx;", val))
		case "right":
			styles = append(styles, fmt.Sprintf("right: %spx;", val))
		case "zIndex":
			styles = append(styles, fmt.Sprintf("z-index: %s;", val))
		case "hoverGlow":
			if hex, exists := ColorPalette[val]; exists {
				// Inject the global hover rule if not already present
				RegisterGlobalKeyframes("hoverGlowRule", "[data-hover-glow] { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; cursor: pointer; } [data-hover-glow]:hover { box-shadow: 0 0 25px var(--hover-color, currentColor) !important; transform: translateY(-2px) scale(1.02) !important; }")

				attributes["data-hover-glow"] = hex
				styles = append(styles, fmt.Sprintf("--hover-color: %s;", hex))
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
					if s == "slow" {
						speed = "3.5s"
					} else if s == "fast" {
						speed = "1s"
					}
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
			switch val {
			case "hero":
				styles = append(styles, "font-size: 3.5rem; font-weight: 800; margin: 0;")
			case "h1":
				styles = append(styles, "font-size: 2.5rem; font-weight: 800; margin: 0;")
			case "h2":
				styles = append(styles, "font-size: 2rem; font-weight: 700; margin: 0;")
			case "h3":
				styles = append(styles, "font-size: 1.5rem; font-weight: 600; margin: 0;")
			case "large":
				styles = append(styles, "font-size: 1.25rem; margin: 0;")
			case "normal":
				styles = append(styles, "font-size: 1rem; margin: 0;")
			case "small":
				styles = append(styles, "font-size: 0.75rem; margin: 0;")
			}
		case "blur":
			if strings.ToLower(val) == "true" || val == "1" {
				styles = append(styles, "backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);")
			}
		case "placeholder":
			attributes["placeholder"] = val
		case "value":
			attributes["value"] = val
		case "text":
			attributes["innerText"] = val
		case "hoverEffect":
			attributes["data-hover-effect"] = val
		case "clickEffect":
			attributes["data-click-effect"] = val
		case "interactionSpeed":
			speed := "0.3s"
			if val == "fast" {
				speed = "0.15s"
			} else if val == "slow" {
				speed = "0.5s"
			}
			styles = append(styles, fmt.Sprintf("transition: all %s cubic-bezier(0.4, 0, 0.2, 1);", speed))
			attributes["data-speed"] = val
		case "bindLoading":
			attributes["data-bind-loading"] = val
		case "loaderType":
			attributes["data-loader-type"] = val
		case "loaderSpeed":
			attributes["data-loader-speed"] = val
		case "scrollReveal":
			attributes["data-scroll-reveal"] = val
		case "revealOffset":
			attributes["data-reveal-offset"] = val
		case "parallaxSpeed":
			attributes["data-parallax-speed"] = val
		case "heroBackground", "effect":
			attributes["data-hero-background"] = val
		case "entranceChoreography":
			attributes["data-entrance-choreography"] = val
		case "textCycle":
			attributes["data-text-cycle"] = val
		case "cycleEffect":
			attributes["data-cycle-effect"] = val
		case "attentionEffect":
			attributes["data-attention-effect"] = val
		case "attentionInterval":
			attributes["data-attention-interval"] = val
		case "attentionTrigger":
			attributes["data-attention-trigger"] = val
		case "transitionIn":
			attributes["data-transition-in"] = val
		case "transitionOut":
			attributes["data-transition-out"] = val
		case "transitionDuration":
			attributes["data-transition-duration"] = val
		case "global_transition", "transition":
			attributes["data-transition"] = val
		case "path":
			attributes["data-route-path"] = val
		case "scene":
			attributes["data-route-scene"] = val
		case "default_route":
			attributes["data-default-route"] = val
		case "fragment_code":
			code := strings.Trim(val, "\"")
			code = strings.TrimSpace(code)
			// Trigger basic GLSL static analysis
			if errs := ValidateGLSL(code); len(errs) > 0 {
				fmt.Printf("\n--- TinPyUI Compiler Error ---\n")
				for _, e := range errs {
					fmt.Println(e.Error())
				}
				fmt.Printf("------------------------------\n\n")
			}
			// Encode string properly to avoid breaking HTML attributes
			attributes["data-shader-code"] = code
		case "uniforms":
			attributes["data-shader-uniforms"] = val
		case "assetPriority":
			if val == "lazy" {
				attributes["loading"] = "lazy"
			}
			attributes["data-asset-priority"] = val
		case "destroyStrategy":
			attributes["data-destroy-strategy"] = val
		case "route":
			attributes["href"] = val
		case "action":
			attributes["data-action"] = val
		case "dataBind":
			attributes["data-bind"] = val
		case "class_", "bind", "on_click", "id":
			attributes[key] = val
		default:
			attributes[key] = val
		}
	}

	// Handle gradient text effects explicitly
	if componentName == "GradientText" {
		gradFrom := "#00f2fe"
		gradTo := "#9b51e0"
		if g, ok := props["gradient"]; ok {
			// gradient = ["neon-cyan", "neon-purple"] parsed as JSON array string
			parts := strings.Split(strings.Trim(g, "[]"), ",")
			if len(parts) >= 2 {
				c1 := strings.Trim(strings.TrimSpace(parts[0]), `"`)
				c2 := strings.Trim(strings.TrimSpace(parts[1]), `"`)
				if hex1, ok := ColorPalette[c1]; ok {
					gradFrom = hex1
				}
				if hex2, ok := ColorPalette[c2]; ok {
					gradTo = hex2
				}
			}
		}
		styles = append(styles, fmt.Sprintf("background: linear-gradient(135deg, %s, %s); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; display: inline-block;", gradFrom, gradTo))
	}

	// Consolidate array slice to style attribute
	if len(styles) > 0 {
		attributes["style"] = strings.Join(styles, " ")
	}

	return attributes
}
