package agent

import (
	"testing"
)

func TestAIContextProposeValid(t *testing.T) {
	api := setupTestContextAPI()

	// Initial source
	originalSource := `
import Shared from "shared.tin"

component Main():
    Shared()
`

	pParams := AIProposalParams{
		Operation:       "replace",
		URI:             "file://main.tin",
		ExpectedVersion: 1,
		Replacement: `
import Shared from "shared.tin"

component Main():
    Shared()
    Shared()
`,
	}

	res := api.ValidateProposal(pParams, originalSource)
	if !res.Valid {
		t.Fatalf("Expected valid proposal, got diagnostics: %v", res.Diagnostics)
	}
}

func TestAIContextProposeSyntaxError(t *testing.T) {
	api := setupTestContextAPI()

	originalSource := `
import Shared from "shared.tin"
component Main():
    Shared()
`

	pParams := AIProposalParams{
		Operation:       "replace",
		URI:             "file://main.tin",
		ExpectedVersion: 1,
		Replacement: `
import Shared from "shared.tin"
component Main():
    Shared()
    this is invalid syntax () !!
`,
	}

	res := api.ValidateProposal(pParams, originalSource)
	if res.Valid {
		t.Fatalf("Expected invalid proposal due to syntax error")
	}
	if len(res.Diagnostics) == 0 {
		t.Fatalf("Expected diagnostics")
	}
}

func TestAIContextProposeSemanticError(t *testing.T) {
	api := setupTestContextAPI()

	originalSource := `
import Shared from "shared.tin"
component Main():
    Shared()
`

	pParams := AIProposalParams{
		Operation:       "replace",
		URI:             "file://main.tin",
		ExpectedVersion: 1,
		Replacement: `
component Main():
    NonExistentComponent()
`,
	}

	res := api.ValidateProposal(pParams, originalSource)
	if res.Valid {
		t.Fatalf("Expected invalid proposal due to semantic error")
	}
	if len(res.Diagnostics) == 0 {
		t.Fatalf("Expected diagnostics")
	}
	found := false
	for _, msg := range res.Diagnostics {
		if msg == "Unresolved semantic reference in patch: tinpy://main.tin#NonExistentComponent" {
			found = true
		}
	}
	if !found {
		t.Fatalf("Expected Unresolved semantic reference error, got: %v", res.Diagnostics)
	}
}
