package agent

import (
	"encoding/json"
	"testing"
)

func TestAIContextAPI8_3(t *testing.T) {
	api := setupTestContextAPI()

	// 1. context.architecture
	// In setupTestContextAPI, Main renders Shared and Missing.
	mainID := "tinpy://main.tin#Main"
	arch := api.GetArchitecture(mainID)
	if arch == nil {
		t.Fatalf("Expected architecture for Main")
	}
	if len(arch.Children) != 2 {
		t.Fatalf("Expected 2 children for Main architecture, got %d", len(arch.Children))
	}
	// Missing might be one of them, Shared is the other.
	foundShared := false
	for _, child := range arch.Children {
		if child.ID == "tinpy://shared.tin#Shared" {
			foundShared = true
			if len(child.Children) != 2 {
				t.Fatalf("Expected Shared to have 2 children (Button renders), got %d", len(child.Children))
			}
		}
	}
	if !foundShared {
		t.Errorf("Expected Shared in Main architecture")
	}

	// 2. context.impact
	// Shared impacts Main (because Main renders Shared). Shared also impacts Main via imports, but impact graph usually follows dependents.
	sharedID := "tinpy://shared.tin#Shared"
	impact := api.GetImpact(sharedID)
	if impact == nil {
		t.Fatalf("Expected impact for Shared")
	}
	if len(impact.Children) == 0 {
		t.Fatalf("Expected Shared to impact Main")
	}
	foundMain := false
	for _, child := range impact.Children {
		if child.ID == "tinpy://main.tin#Main" {
			foundMain = true
		}
	}
	if !foundMain {
		t.Errorf("Expected Shared to impact Main")
	}

	// 3. context.dependencies
	deps := api.GetDependencies(mainID)
	if deps == nil {
		t.Fatalf("Expected dependencies for Main")
	}
	// Main depends on Shared and Missing
	if len(deps.Children) != 2 {
		t.Fatalf("Expected 2 dependencies for Main, got %d", len(deps.Children))
	}

	// 4. context.related
	// Find related for Shared. toggle is a related symbol in the same file.
	// Actually, get_related uses GetSymbolsForFile which grabs all symbols in the file.
	related := api.GetRelated(sharedID)
	if len(related) == 0 {
		t.Fatalf("Expected related symbols for Shared")
	}

	// 5. context.search
	// Search for 'Main'
	searchRes := api.SearchSymbols("Main")
	if len(searchRes) != 1 {
		t.Fatalf("Expected 1 search result for 'Main', got %d", len(searchRes))
	}
	if searchRes[0].Name != "Main" {
		t.Errorf("Expected result to be Main")
	}
	
	// Case-insensitive search
	searchRes = api.SearchSymbols("main")
	if len(searchRes) != 1 {
		t.Errorf("Expected case-insensitive search to match Main")
	}
	
	// Verify serialization
	_, err := json.Marshal(arch)
	if err != nil {
		t.Fatalf("Failed to serialize architecture: %v", err)
	}
}
