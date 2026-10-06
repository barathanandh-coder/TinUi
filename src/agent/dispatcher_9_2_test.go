package agent

import (
	"testing"
)

func TestPanicRecovery(t *testing.T) {
	req := RequestEnvelope{
		JSONRPC: "2.0",
		ID:      999,
		Method:  "test_panic_handler",
	}

	// Temporarily override the behavior just to test panic recovery.
	// The best way is to call dispatchRequest with a method that will panic.
	// Since we don't have a specific test_panic method in the real dispatcher, 
	// we can test runSyncHandler directly.

	var capturedResponse *ResponseEnvelope
	
	// Mock emitResponse just for this test
	originalEmit := emitResponse
	defer func() { emitResponse = originalEmit }()
	
	emitResponse = func(res ResponseEnvelope) {
		capturedResponse = &res
	}

	runSyncHandler(req, func(r RequestEnvelope) {
		panic("intentional test panic")
	})

	if capturedResponse == nil {
		t.Fatalf("Expected a response from panic recovery, got nil")
	}

	if capturedResponse.Error == nil {
		t.Fatalf("Expected an error response, got success")
	}

	if capturedResponse.Error.Code != -32603 {
		t.Fatalf("Expected error code -32603, got %d", capturedResponse.Error.Code)
	}

	// Now check if it works via recoverRequest directly which is used in goroutines
	capturedResponse = nil
	func() {
		defer recoverRequest(1000)
		panic("another test panic")
	}()

	if capturedResponse == nil {
		t.Fatalf("Expected a response from panic recovery, got nil")
	}

	if capturedResponse.ID != 1000 {
		t.Fatalf("Expected ID 1000, got %v", capturedResponse.ID)
	}
}
