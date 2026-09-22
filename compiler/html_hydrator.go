package compiler

import (
	"fmt"
	"strings"
)

// GenerateHydrationShell translates the IR blueprint into a static HTML shell for SEO and rapid loading.
func GenerateHydrationShell(blueprint IRBlueprint) string {
	var builder strings.Builder

	builder.WriteString("<!DOCTYPE html>\n")
	builder.WriteString("<html lang=\"en\">\n")
	builder.WriteString("<head>\n")
	builder.WriteString("    <meta charset=\"UTF-8\">\n")
	builder.WriteString("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n")
	builder.WriteString("    <title>TinPyUI Application</title>\n")
	builder.WriteString("    <meta name=\"description\" content=\"TinPyUI — Zero-DOM Hardware-Accelerated UI Engine with Pythonic Syntax and WebAssembly.\">\n")
	builder.WriteString("    <meta name=\"keywords\" content=\"tinpyui, tinui, python gui, webassembly, zero-dom, webgl, python ui framework\">\n")
	builder.WriteString("    <link rel=\"canonical\" href=\"https://github.com/barathanandh-coder/TinUi\">\n")
	builder.WriteString("    <meta property=\"og:title\" content=\"TinPyUI Application\">\n")
	builder.WriteString("    <meta property=\"og:description\" content=\"Zero-DOM Hardware-Accelerated UI Engine powered by TinPyUI.\">\n")
	builder.WriteString("    <meta property=\"og:url\" content=\"https://github.com/barathanandh-coder/TinUi\">\n")
	builder.WriteString("    <meta property=\"og:type\" content=\"website\">\n")
	builder.WriteString("    <meta name=\"twitter:card\" content=\"summary_large_image\">\n")
	builder.WriteString("    <script src=\"https://cdn.tailwindcss.com?plugins=forms,container-queries\"></script>\n")
	builder.WriteString("    <link href=\"https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Sora:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap\" rel=\"stylesheet\">\n")
	builder.WriteString("    <link href=\"https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0\" rel=\"stylesheet\">\n")
	builder.WriteString("    <script id=\"tailwind-config\">\n")
	builder.WriteString("      tailwind.config = {\n")
	builder.WriteString("        darkMode: \"class\",\n")
	builder.WriteString("        theme: {\n")
	builder.WriteString("          extend: {\n")
	builder.WriteString("            \"colors\": {\n")
	builder.WriteString("                    \"on-tertiary-container\": \"#503d00\", \"surface-variant\": \"#36343a\", \"secondary-fixed-dim\": \"#cdc0e9\",\n")
	builder.WriteString("                    \"on-error-container\": \"#ffdad6\", \"tertiary-container\": \"#c9a74d\", \"surface-tint\": \"#cfbcff\",\n")
	builder.WriteString("                    \"primary\": \"#cfbcff\", \"outline-variant\": \"#494551\", \"secondary\": \"#cdc0e9\", \"on-surface\": \"#e6e0e9\",\n")
	builder.WriteString("                    \"on-background\": \"#e6e0e9\", \"surface\": \"#141218\", \"on-secondary-fixed\": \"#1f1635\", \"background\": \"transparent\",\n")
	builder.WriteString("                    \"on-tertiary-fixed\": \"#241a00\", \"on-tertiary\": \"#3e2e00\", \"on-primary-fixed-variant\": \"#4f378a\",\n")
	builder.WriteString("                    \"surface-container-high\": \"#2b292f\", \"primary-container\": \"#6750a4\", \"inverse-surface\": \"#e6e0e9\",\n")
	builder.WriteString("                    \"on-secondary-fixed-variant\": \"#4b4263\", \"surface-container-low\": \"#1d1b20\", \"on-error\": \"#690005\",\n")
	builder.WriteString("                    \"tertiary-fixed-dim\": \"#e7c365\", \"outline\": \"#948e9c\", \"surface-dim\": \"#141218\", \"secondary-container\": \"#4d4465\",\n")
	builder.WriteString("                    \"primary-fixed\": \"#e9ddff\", \"error\": \"#ffb4ab\", \"inverse-primary\": \"#6750a4\", \"on-primary-container\": \"#e0d2ff\",\n")
	builder.WriteString("                    \"on-primary-fixed\": \"#22005d\", \"inverse-on-surface\": \"#322f35\", \"tertiary-fixed\": \"#ffdf93\",\n")
	builder.WriteString("                    \"surface-container\": \"#211f24\", \"on-surface-variant\": \"#cbc4d2\", \"primary-fixed-dim\": \"#cfbcff\",\n")
	builder.WriteString("                    \"on-primary\": \"#381e72\", \"surface-container-lowest\": \"#0f0d13\", \"on-tertiary-fixed-variant\": \"#594400\",\n")
	builder.WriteString("                    \"error-container\": \"#93000a\", \"surface-bright\": \"#3b383e\", \"secondary-fixed\": \"#e9ddff\",\n")
	builder.WriteString("                    \"surface-container-highest\": \"#36343a\", \"on-secondary-container\": \"#bfb2da\", \"on-secondary\": \"#342b4b\",\n")
	builder.WriteString("                    \"tertiary\": \"#e7c365\"\n")
	builder.WriteString("            },\n")
	builder.WriteString("            \"spacing\": { \"margin-desktop\": \"2.5rem\", \"margin-mobile\": \"1rem\", \"max-width\": \"1440px\" },\n")
	builder.WriteString("            \"fontFamily\": { \"label-mono\": [\"JetBrains Mono\"], \"display-lg-mobile\": [\"Sora\"], \"display-lg\": [\"Sora\"], \"headline-md\": [\"Sora\"], \"body-lg\": [\"Plus Jakarta Sans\"], \"body-md\": [\"Plus Jakarta Sans\"] }\n")
	builder.WriteString("          }\n")
	builder.WriteString("        }\n")
	builder.WriteString("      }\n")
	builder.WriteString("    </script>\n")
	builder.WriteString("    <style>\n")
	builder.WriteString("        *, *::before, *::after { box-sizing: border-box; }\n")
	builder.WriteString("        html, body { margin: 0; padding: 0; background: #030712; color: white; font-family: 'Plus Jakarta Sans', sans-serif; overflow-x: hidden; scroll-behavior: smooth; }\n")
	builder.WriteString("        #tinui-root { position: relative; min-height: 100vh; }\n")
	builder.WriteString("        .material-symbols-outlined { font-family: 'Material Symbols Outlined'; font-weight: normal; font-style: normal; line-height: 1; letter-spacing: normal; text-transform: none; display: inline-block; white-space: nowrap; word-wrap: normal; }\n")
	builder.WriteString("        .cursor-trail { position: fixed; width: 20px; height: 20px; border-radius: 50%; pointer-events: none; z-index: 9999; background: radial-gradient(circle, rgba(207,188,255,0.8) 0%, transparent 70%); transition: transform 0.1s ease-out; }\n")
	builder.WriteString("        .glass-card { background: rgba(20, 18, 24, 0.2); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.05); }\n")
	builder.WriteString("        .neon-border-cyan { box-shadow: 0 0 15px rgba(0, 255, 255, 0.2); border-color: rgba(0, 255, 255, 0.3); }\n")
	builder.WriteString("        .neon-border-primary { box-shadow: 0 0 15px rgba(207,188,255,0.2); border-color: rgba(207,188,255,0.3); }\n")
	builder.WriteString("        .reveal-section { transition: all 1s cubic-bezier(0.4, 0, 0.2, 1); opacity: 0; transform: perspective(1000px) translateZ(-100px); filter: blur(10px); }\n")
	builder.WriteString("        .reveal-section.active { opacity: 1; transform: perspective(1000px) translateZ(0); filter: blur(0); }\n")
	builder.WriteString("        .glitch-hover:hover { animation: glitch 0.3s cubic-bezier(.25,.46,.45,.94) both infinite; }\n")
	builder.WriteString("        @keyframes glitch { 0% { transform: translate(0); } 20% { transform: translate(-2px, 2px); } 40% { transform: translate(-2px, -2px); } 60% { transform: translate(2px, 2px); } 80% { transform: translate(2px, -2px); } 100% { transform: translate(0); } }\n")
	builder.WriteString("        .pulse-glitch { animation: pulse-glitch 2s infinite; }\n")
	builder.WriteString("        @keyframes pulse-glitch { 0%, 100% { opacity: 1; filter: hue-rotate(0deg); } 50% { opacity: 0.8; filter: hue-rotate(90deg) brightness(1.2); } }\n")
	builder.WriteString("    </style>\n")

	// Collect style nodes and preloads
	var preloads []string
	var styles string

	preloadMap := make(map[int]map[string]string)
	for _, inst := range blueprint.Nodes {
		if inst.Op == OpSetAttribute && inst.Key != "" {
			if preloadMap[inst.ID] == nil {
				preloadMap[inst.ID] = make(map[string]string)
			}
			preloadMap[inst.ID][inst.Key] = inst.Value
		}
	}

	for _, inst := range blueprint.Nodes {
		if inst.Op == OpCreateNode && inst.Tag == "style" {
			// Find text for style
			for _, childInst := range blueprint.Nodes {
				if childInst.Op == OpSetText && childInst.ID == inst.ID {
					styles += childInst.Value
				}
			}
		}
		if inst.Op == OpCreateNode {
			attrs := preloadMap[inst.ID]
			if attrs["rel"] == "preload" {
				href := attrs["href"]
				as := attrs["as"]
				preloads = append(preloads, fmt.Sprintf("    <link rel=\"preload\" href=\"%s\" as=\"%s\">\n", href, as))
			}
		}
	}

	for _, p := range preloads {
		builder.WriteString(p)
	}

	if styles != "" {
		builder.WriteString("    <style>\n" + styles + "\n    </style>\n")
	}

	builder.WriteString("    <script src=\"wasm_exec.js\"></script>\n")
	builder.WriteString("    <script src=\"tin-runtime.js\"></script>\n")
	builder.WriteString("</head>\n")
	builder.WriteString("<body>\n")
	builder.WriteString("    <div id=\"tinui-root\">\n")

	// Build tree recursively
	tree := buildTree(blueprint.Nodes, 0)
	builder.WriteString(renderTree(tree, 2, preloadMap))

	builder.WriteString("    </div>\n")
	builder.WriteString("</body>\n")
	builder.WriteString("</html>\n")

	return builder.String()
}

type NodeTree struct {
	ID       int
	Tag      string
	Text     string
	Children []*NodeTree
	IsHidden bool
}

func buildTree(instructions []Instruction, rootID int) *NodeTree {
	nodes := make(map[int]*NodeTree)

	for _, inst := range instructions {
		if inst.Op == OpCreateNode {
			nodes[inst.ID] = &NodeTree{ID: inst.ID, Tag: inst.Tag, IsHidden: inst.IsHidden}
		}
	}

	for _, inst := range instructions {
		if inst.Op == OpSetText || inst.Op == OpBindText {
			if node, ok := nodes[inst.ID]; ok {
				if inst.Value != "" {
					node.Text = inst.Value
				} else {
					node.Text = inst.Template // for bind text fallback
				}
			}
		} else if inst.Op == OpAppendChild {
			if parent, ok := nodes[inst.Parent]; ok {
				if child, ok := nodes[inst.Child]; ok {
					parent.Children = append(parent.Children, child)
				}
			}
		} else if inst.Op == OpCreateConditional {
			if parent, ok := nodes[inst.Parent]; ok {
				child := &NodeTree{ID: inst.ID, Tag: "div"}
				parent.Children = append(parent.Children, child)
			}
		} else if inst.Op == OpRenderList {
			if parent, ok := nodes[inst.Parent]; ok {
				child := &NodeTree{ID: inst.ID, Tag: "div"}
				parent.Children = append(parent.Children, child)
			}
		}
	}

	root := &NodeTree{ID: 0}
	for _, inst := range instructions {
		if inst.Op == OpAppendChild && inst.Parent == 0 {
			if child, ok := nodes[inst.Child]; ok {
				root.Children = append(root.Children, child)
			}
		}
	}

	return root
}

func renderTree(node *NodeTree, indentLevel int, attrs map[int]map[string]string) string {
	if node == nil {
		return ""
	}

	if node.ID == 0 {
		var b strings.Builder
		for _, child := range node.Children {
			b.WriteString(renderTree(child, indentLevel, attrs))
		}
		return b.String()
	}

	nodeAttrs := attrs[node.ID]
	if node.Tag == "style" || nodeAttrs["rel"] == "preload" {
		return ""
	}

	indent := strings.Repeat("    ", indentLevel)
	var b strings.Builder

	b.WriteString(fmt.Sprintf("%s<%s id=\"tin-node-%d\"", indent, node.Tag, node.ID))

	var styleStr string
	for k, v := range nodeAttrs {
		if k == "style" {
			styleStr = v
			continue
		}
		if k == "innerText" {
			continue
		}
		escaped := strings.ReplaceAll(v, "\"", "&quot;")
		b.WriteString(fmt.Sprintf(" %s=\"%s\"", k, escaped))
	}

	if node.IsHidden {
		if styleStr != "" {
			styleStr += " display: none !important;"
		} else {
			styleStr = "display: none !important;"
		}
	}

	if styleStr != "" {
		b.WriteString(fmt.Sprintf(" style=\"%s\"", strings.ReplaceAll(styleStr, "\"", "&quot;")))
	}

	b.WriteString(">\n")

	if node.Text != "" {
		b.WriteString(fmt.Sprintf("%s    %s\n", indent, node.Text))
	}

	for _, child := range node.Children {
		b.WriteString(renderTree(child, indentLevel+1, attrs))
	}

	b.WriteString(fmt.Sprintf("%s</%s>\n", indent, node.Tag))
	return b.String()
}
