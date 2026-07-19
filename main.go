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

	var hydrate bool
	var inputFile string
	for _, arg := range os.Args[2:] {
		if arg == "--hydrate" {
			hydrate = true
		} else if !strings.HasPrefix(arg, "--") {
			inputFile = arg
		}
	}
	
	if inputFile == "" {
		fmt.Println("[Error] No input file specified.")
		printUsage()
		os.Exit(1)
	}

	// 2. Read the .tin Source File
	sourceBytes, err := os.ReadFile(inputFile)
	if err != nil {
		fmt.Printf("[Error] Error reading file %s: %v\n", inputFile, err)
		os.Exit(1)
	}
	sourceCode := string(sourceBytes)

	fmt.Printf("Compiling %s...\n", inputFile)

	// 3. The Compilation Pipeline
	lexer := compiler.NewLexer(sourceCode)
	parser := compiler.NewParser(lexer)
	
	astRoots := parser.Parse()

	if len(parser.Errors) > 0 {
		fmt.Println("[Error] Syntax Errors found:")
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
		fmt.Printf("[Error] Error generating IR JSON: %v\n", err)
		os.Exit(1)
	}

	// 5. Write the Output File
	ext := filepath.Ext(inputFile)
	base := strings.TrimSuffix(inputFile, ext)
	outputFile := base + ".ir.json"

	// Check for config
	configBytes, configErr := os.ReadFile("tinpyui.config.json")
	if configErr == nil {
		var config struct {
			CompilerSettings struct {
				Output string `json:"output"`
			} `json:"compilerSettings"`
		}
		if err := json.Unmarshal(configBytes, &config); err == nil && config.CompilerSettings.Output != "" {
			outputFile = config.CompilerSettings.Output
		}
	}

	// Ensure output directory exists
	outDir := filepath.Dir(outputFile)
	if outDir != "" && outDir != "." {
		os.MkdirAll(outDir, 0755)
	}

	err = os.WriteFile(outputFile, irJSON, 0644)
	if err != nil {
		fmt.Printf("[Error] Error writing output file: %v\n", err)
		os.Exit(1)
	}
	
	if hydrate {
		htmlShell := compiler.GenerateHydrationShell(instructions)
		htmlOutputFile := filepath.Join(outDir, "index.html")
		err = os.WriteFile(htmlOutputFile, []byte(htmlShell), 0644)
		if err != nil {
			fmt.Printf("[Error] Error writing hydration HTML: %v\n", err)
		} else {
			fmt.Printf("Success! Generated Static SEO Hydration Shell at: %s\n", htmlOutputFile)
		}
	}

	fmt.Printf("Success! Generated Intermediate Representation at: %s\n", outputFile)
}

func printUsage() {
	fmt.Println("TinUI Compiler CLI")
	fmt.Println("Usage: tinui compile <filename>.tin")
}
