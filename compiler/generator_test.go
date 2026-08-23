package compiler

import (
	"strings"
	"testing"
)

func TestSceneASTInlining(t *testing.T) {
	source := `component Main():
    Router():
        Route(path="/", scene="Dashboard")

component Dashboard():
    Container(align="center", justify="center", width="full", padding=50):
        GradientText(text="Welcome to the Matrix", size="hero")
        Spacer(height=20)
        Text(text="Your Hybrid Wasm engine is running.", color="muted")
`

	lexer := NewLexer(source)
	parser := NewParser(lexer)
	astRoots := parser.Parse()

	if len(parser.Errors) > 0 {
		t.Fatalf("Parser errors: %v", parser.Errors)
	}

	gen := NewIRGenerator()
	blueprint := gen.Generate(astRoots)

	// Verify that blueprint contains the child nodes of Dashboard
	foundRoute := false
	foundGradientText := false
	foundText := false

	for _, node := range blueprint.Nodes {
		if node.Op == OpSetAttribute && node.Key == "data-route-scene" && node.Value == "Dashboard" {
			foundRoute = true
		}
		if node.Op == OpSetText && node.Value == "Welcome to the Matrix" {
			foundGradientText = true
		}
		if node.Op == OpSetText && node.Value == "Your Hybrid Wasm engine is running." {
			foundText = true
		}
	}

	if !foundRoute {
		t.Errorf("Expected Route with data-route-scene=Dashboard, but not found")
	}
	if !foundGradientText {
		t.Errorf("Expected GradientText child node inside IR stream, but not found")
	}
	if !foundText {
		t.Errorf("Expected Text child node inside IR stream, but not found")
	}
}

func TestMultiComponentStateAndMutations(t *testing.T) {
	source := `component Main():
    Router():
        Route(path="/", scene="CounterScene")

component CounterScene():
    state count = 10
    def increment():
        count += 1
    Button(text="Increment", on_click="increment")
`

	lexer := NewLexer(source)
	parser := NewParser(lexer)
	astRoots := parser.Parse()

	if len(parser.Errors) > 0 {
		t.Fatalf("Parser errors: %v", parser.Errors)
	}

	gen := NewIRGenerator()
	blueprint := gen.Generate(astRoots)

	// Verify that state 'count' is declared
	foundState := false
	for _, node := range blueprint.Nodes {
		if node.Op == OpDeclareState && node.Key == "count" {
			foundState = true
		}
	}
	if !foundState {
		t.Errorf("Expected state 'count' to be declared, but not found")
	}

	// Verify mutation 'increment' exists in blueprint
	if muts, exists := blueprint.Mutations["increment"]; !exists || len(muts) == 0 {
		t.Errorf("Expected mutation 'increment' in blueprint, but found none")
	}
}

func TestPythonBooleanProperties(t *testing.T) {
	source := `component Main():
    Navbar(padding=20, blur=True):
        Row(wrap=True):
            Text(text="TinPyUI", color="neon-cyan")
`

	lexer := NewLexer(source)
	parser := NewParser(lexer)
	astRoots := parser.Parse()

	if len(parser.Errors) > 0 {
		t.Fatalf("Parser errors: %v", parser.Errors)
	}

	gen := NewIRGenerator()
	blueprint := gen.Generate(astRoots)

	foundBlur := false
	foundWrap := false

	for _, node := range blueprint.Nodes {
		if node.Op == OpSetAttribute && node.Key == "style" {
			if strings.Contains(node.Value, "backdrop-filter: blur") {
				foundBlur = true
			}
			if strings.Contains(node.Value, "flex-wrap: wrap") {
				foundWrap = true
			}
		}
	}

	if !foundBlur {
		t.Errorf("Expected backdrop-filter: blur from blur=True, but not found in styles")
	}
	if !foundWrap {
		t.Errorf("Expected flex-wrap: wrap from wrap=True, but not found in styles")
	}
}

func TestHydrationShellGeneration(t *testing.T) {
	source := `component Main():
    Section(paddingY=40, align="center"):
        Heading(text="Welcome to TinPyUI", color="white")
        Text(text="Native speed with Pythonic simplicity.", color="muted")
`

	lexer := NewLexer(source)
	parser := NewParser(lexer)
	astRoots := parser.Parse()

	if len(parser.Errors) > 0 {
		t.Fatalf("Parser errors: %v", parser.Errors)
	}

	gen := NewIRGenerator()
	blueprint := gen.Generate(astRoots)

	html := GenerateHydrationShell(blueprint)

	if !strings.Contains(html, "<section") {
		t.Errorf("Expected <section in hydration HTML, got %s", html)
	}
	if !strings.Contains(html, "Welcome to TinPyUI") {
		t.Errorf("Expected 'Welcome to TinPyUI' in hydration HTML")
	}
	if !strings.Contains(html, "tin-runtime.js") && !strings.Contains(html, "tailwind.config") {
		t.Errorf("Expected Tailwind config or runtime in hydration shell")
	}
}

func TestVirtualStackCompilation(t *testing.T) {
	source := `component Main():
    VirtualStack(itemHeight=50, totalCount=100000):
        Card(padding=10):
            Text(text="Virtual Row", color="white")
`

	lexer := NewLexer(source)
	parser := NewParser(lexer)
	astRoots := parser.Parse()

	if len(parser.Errors) > 0 {
		t.Fatalf("Parser errors: %v", parser.Errors)
	}

	gen := NewIRGenerator()
	blueprint := gen.Generate(astRoots)

	foundVirtualStack := false
	foundItemHeight := false
	foundTotalCount := false

	for _, node := range blueprint.Nodes {
		if node.Op == OpSetAttribute && node.Key == "data-virtual-stack" && node.Value == "true" {
			foundVirtualStack = true
		}
		if node.Op == OpSetAttribute && node.Key == "data-item-height" && node.Value == "50" {
			foundItemHeight = true
		}
		if node.Op == OpSetAttribute && node.Key == "data-total-count" && node.Value == "100000" {
			foundTotalCount = true
		}
	}

	if !foundVirtualStack {
		t.Errorf("Expected data-virtual-stack attribute on VirtualStack node")
	}
	if !foundItemHeight {
		t.Errorf("Expected data-item-height=50 attribute on VirtualStack node")
	}
	if !foundTotalCount {
		t.Errorf("Expected data-total-count=100000 attribute on VirtualStack node")
	}
}
