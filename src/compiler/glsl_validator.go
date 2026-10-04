package compiler

import (
	"fmt"
	"strings"
)

// ValidateGLSL performs a fast, static-analysis check on GLSL fragment code.
// It catches common errors like missing semicolons and missing main() function.
func ValidateGLSL(code string) []error {
	var errs []error
	lines := strings.Split(code, "\n")
	hasMain := false
	inMain := false

	for i, line := range lines {
		trimmed := strings.TrimSpace(line)
		
		// Skip empty lines and comments
		if trimmed == "" || strings.HasPrefix(trimmed, "//") {
			continue
		}

		if strings.Contains(trimmed, "void main()") {
			hasMain = true
			inMain = true
			continue
		}

		// Simple semicolon check inside blocks
		if inMain {
			if strings.HasSuffix(trimmed, "}") {
				inMain = false // basic block exit tracking
				continue
			}
			
			if !strings.HasSuffix(trimmed, ";") && !strings.HasSuffix(trimmed, "{") {
				// Avoid throwing errors on multiline statements or macros, but catch basic syntax errors
				if !strings.HasPrefix(trimmed, "#") && !strings.HasPrefix(trimmed, "if") && !strings.HasPrefix(trimmed, "else") && !strings.HasPrefix(trimmed, "for") {
					errs = append(errs, fmt.Errorf("GLSL Syntax Error (Line %d): Missing semicolon at the end of statement: '%s'", i+1, trimmed))
				}
			}
		}
	}

	if !hasMain {
		errs = append(errs, fmt.Errorf("GLSL Syntax Error: Missing 'void main()' entry point"))
	}

	return errs
}
