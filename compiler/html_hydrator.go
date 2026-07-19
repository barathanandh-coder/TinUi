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
	builder.WriteString("    <script>\n")
	builder.WriteString("        const go = new Go();\n")
	builder.WriteString("        WebAssembly.instantiateStreaming(fetch('app.wasm'), go.importObject).then(result => {\n")
	builder.WriteString("            go.run(result.instance);\n")
	builder.WriteString("            fetch('app.ir.json').then(r => r.text()).then(json => {\n")
	builder.WriteString("                BootTinUI(json);\n")
	builder.WriteString("            });\n")
	builder.WriteString("        });\n")
	builder.WriteString("    </script>\n")
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
	ID int
	Tag string
	Text string
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
