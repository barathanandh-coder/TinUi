package compiler

import (
	"testing"
)

func TestComponentPropsParsing(t *testing.T) {
	input := `
component Legacy(text, disabled):
	View()

component Typed(text: String, count: Int):
	View()

component Defaulted(text: String = "Submit", flag: Bool = true):
	View()
`

	l := NewLexer(input)
	p := NewParser(l)
	ast := p.Parse()

	if len(p.Errors) > 0 {
		t.Fatalf("Parser errors: %v", p.Errors)
	}

	if len(ast) != 3 {
		t.Fatalf("Expected 3 components, got %d", len(ast))
	}

	// Legacy
	comp1 := ast[0]
	if len(comp1.Props) != 2 || comp1.Props[0].Name != "text" || comp1.Props[1].Name != "disabled" {
		t.Errorf("Legacy props parsing failed: %v", comp1.Props)
	}
	if comp1.Props[0].TypeHint != "" || comp1.Props[1].TypeHint != "" {
		t.Errorf("Legacy props should have no TypeHint")
	}

	// Typed
	comp2 := ast[1]
	if len(comp2.Props) != 2 || comp2.Props[0].Name != "text" || comp2.Props[1].Name != "count" {
		t.Errorf("Typed props parsing failed: %v", comp2.Props)
	}
	if comp2.Props[0].TypeHint != "String" || comp2.Props[1].TypeHint != "Int" {
		t.Errorf("Typed props TypeHint failed: %v", comp2.Props)
	}

	// Defaulted
	comp3 := ast[2]
	if len(comp3.Props) != 2 || comp3.Props[0].Name != "text" || comp3.Props[1].Name != "flag" {
		t.Errorf("Defaulted props parsing failed: %v", comp3.Props)
	}
	if comp3.Props[0].TypeHint != "String" || comp3.Props[1].TypeHint != "Bool" {
		t.Errorf("Defaulted props TypeHint failed: %v", comp3.Props)
	}
	if comp3.Props[0].Default != `"Submit"` || comp3.Props[1].Default != "true" {
		t.Errorf("Defaulted props Default failed: %v", comp3.Props)
	}
}
