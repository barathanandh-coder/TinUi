package compiler

import (
	"testing"
)

func TestInferLiteral(t *testing.T) {
	tests := []struct {
		value    string
		expected TypeKind
	}{
		{`"hello"`, TypeString},
		{`'hello'`, TypeString},
		{`42`, TypeInt},
		{`-10`, TypeInt},
		{`3.14`, TypeFloat},
		{`-0.5`, TypeFloat},
		{`true`, TypeBool},
		{`false`, TypeBool},
		{`null`, TypeNull},
		{`something_unquoted`, TypeUnknown},
	}

	for _, tc := range tests {
		res := InferLiteral(tc.value, Range{})
		if res.Type.Kind != tc.expected {
			t.Errorf("InferLiteral(%s) expected %s, got %s", tc.value, tc.expected, res.Type.Kind)
		}
	}
}

func TestAssignmentCompatibility(t *testing.T) {
	res1 := CheckAssignmentCompatibility(TinType{Kind: TypeFloat}, TinType{Kind: TypeInt})
	if !res1 {
		t.Errorf("Expected Int to be assignable to Float (widening)")
	}

	res2 := CheckAssignmentCompatibility(TinType{Kind: TypeInt}, TinType{Kind: TypeFloat})
	if res2 {
		t.Errorf("Expected Float NOT to be assignable to Int (narrowing)")
	}

	res3 := CheckAssignmentCompatibility(TinType{Kind: TypeInt}, TinType{Kind: TypeNull})
	if !res3 {
		t.Errorf("Expected Null to be assignable to Int")
	}
}

func TestInferExpression(t *testing.T) {
	left := TypeResult{Type: TinType{Kind: TypeInt}, Confidence: ConfidenceLiteral}
	right := TypeResult{Type: TinType{Kind: TypeFloat}, Confidence: ConfidenceLiteral}
	
	res1 := InferExpression(left, "+", right, Range{})
	if res1.Type.Kind != TypeFloat {
		t.Errorf("Expected Int + Float = Float, got %s", res1.Type.Kind)
	}
	
	strLeft := TypeResult{Type: TinType{Kind: TypeString}, Confidence: ConfidenceLiteral}
	res2 := InferExpression(strLeft, "+", right, Range{})
	if res2.Type.Kind != TypeString {
		t.Errorf("Expected String + Float = String, got %s", res2.Type.Kind)
	}

	res3 := InferExpression(left, "+", strLeft, Range{})
	if res3.Type.Kind != TypeString {
		t.Errorf("Expected Int + String = String, got %s", res3.Type.Kind)
	}
	
	res4 := InferExpression(left, "-", strLeft, Range{})
	if res4.Type.Kind != TypeConflict {
		t.Errorf("Expected Int - String = TypeConflict, got %s", res4.Type.Kind)
	}
}
