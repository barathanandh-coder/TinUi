package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/tinui/tinui/compiler"
)

func main() {
	// 1. Handle Command Line Arguments
	if len(os.Args) < 3 {
		printUsage()
		os.Exit(1)
	}

	command := os.Args[1]
	if command != "compile" && command != "build" {
		printUsage()
		os.Exit(1)
	}

	inputFile := os.Args[2]

	// 2. Read the .tin Source File
	sourceBytes, err := os.ReadFile(inputFile)
	if err != nil {
		fmt.Printf("❌ Error reading file %s: %v\n", inputFile, err)
		os.Exit(1)
	}
	sourceCode := string(sourceBytes)

	fmt.Printf("⏳ Compiling %s...\n", inputFile)

	// 3. The Compilation Pipeline
	lexer := compiler.NewLexer(sourceCode)
	parser := compiler.NewParser(lexer)
	
	astRoots := parser.Parse()

	if len(parser.Errors) > 0 {
		fmt.Println("❌ Syntax Errors found:")
		for _, msg := range parser.Errors {
			fmt.Printf("  - %s\n", msg)
		}
		os.Exit(1)
	}

	generator := compiler.NewIRGenerator()
	instructions := generator.Generate(astRoots)

	// 4. Serialize to JSON
	irJSON, err := json.MarshalIndent(instructions, "", "  ")
	if err != nil {
		fmt.Printf("❌ Error generating IR JSON: %v\n", err)
		os.Exit(1)
	}

	// 5. Write the Output File
	ext := filepath.Ext(inputFile)
	base := strings.TrimSuffix(inputFile, ext)
	outputFile := base + ".ir.json"

	err = os.WriteFile(outputFile, irJSON, 0644)
	if err != nil {
		fmt.Printf("❌ Error writing output file: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("✅ Success! Generated Intermediate Representation at: %s\n", outputFile)
}

func printUsage() {
	fmt.Println("TinUI Compiler CLI")
	fmt.Println("Usage: tinui compile <filename>.tin")
}
