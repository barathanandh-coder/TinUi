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
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	command := os.Args[1]
	if command != "compile" && command != "build" && command != "dev" && command != "init" {
		printUsage()
		os.Exit(1)
	}

	if command == "init" {
		initProject()
		return
	}

	if len(os.Args) < 3 {
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

	ext := filepath.Ext(inputFile)
	base := strings.TrimSuffix(inputFile, ext)
	outputFile := base + ".ir.json"

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

	outDir := filepath.Dir(outputFile)
	if outDir != "" && outDir != "." {
		os.MkdirAll(outDir, 0755)
	}

	if command == "dev" {
		// Zero-DOM: Always compile IR into public/ so all Wasm assets are co-located
		outDir = "public"
		base = strings.TrimSuffix(filepath.Base(inputFile), ext)
		outputFile = filepath.Join("public", "app.ir.json")
		os.MkdirAll(outDir, 0755)
		startDevServer(inputFile, outDir, outputFile, hydrate)
		return
	}

	success := compileFile(inputFile, outDir, outputFile, hydrate)
	if !success {
		os.Exit(1)
	}
}

func compileFile(inputFile, outDir, outputFile string, hydrate bool) bool {
	sourceBytes, err := os.ReadFile(inputFile)
	if err != nil {
		fmt.Printf("[Error] Error reading file %s: %v\n", inputFile, err)
		return false
	}
	sourceCode := string(sourceBytes)

	fmt.Printf("Compiling %s...\n", inputFile)

	lexer := compiler.NewLexer(sourceCode)
	parser := compiler.NewParser(lexer)

	astRoots := parser.Parse()

	if len(parser.Errors) > 0 {
		fmt.Println("\x1b[1;31m[Error] Syntax Errors found:\x1b[0m")
		for _, msg := range parser.Errors {
			fmt.Printf("  \x1b[31m✗\x1b[0m \x1b[33m%s\x1b[0m\n", msg)
		}
		return false
	}

	generator := compiler.NewIRGenerator()
	instructions := generator.Generate(astRoots)

	irJSON, err := json.MarshalIndent(instructions, "", "  ")
	if err != nil {
		fmt.Printf("[Error] Error generating IR JSON: %v\n", err)
		return false
	}

	err = os.WriteFile(outputFile, irJSON, 0644)
	if err != nil {
		fmt.Printf("[Error] Error writing output file: %v\n", err)
		return false
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

		runtimeJsFile := filepath.Join(outDir, "tin-runtime.js")
		err = os.WriteFile(runtimeJsFile, []byte(DefaultTinRuntimeJS), 0644)
		if err != nil {
			fmt.Printf("[Error] Error writing tin-runtime.js: %v\n", err)
		} else {
			fmt.Printf("Success! Generated Runtime JS at: %s\n", runtimeJsFile)
		}

		ensureWasmAssets(outDir)
		fmt.Printf("Success! Copied WebAssembly assets to: %s\n", outDir)
	}

	fmt.Printf("Success! Generated Intermediate Representation at: %s\n", outputFile)
	return true
}

func printUsage() {
	fmt.Println("TinUI Compiler CLI")
	fmt.Println("Usage: tinui [compile|dev|init] <filename>.tin")
}

func initProject() {
	fmt.Println("Initializing new TinPyUI project...")
	
	// Create main.tin
	if _, err := os.Stat("main.tin"); os.IsNotExist(err) {
		err := os.WriteFile("main.tin", []byte(DefaultStarterTin), 0644)
		if err != nil {
			fmt.Println("[Error] Could not create main.tin:", err)
		} else {
			fmt.Println("Created main.tin")
		}
	} else {
		fmt.Println("main.tin already exists, skipping.")
	}

	// Create public dir
	os.MkdirAll("public", 0755)

	// Create config
	if _, err := os.Stat("tinpyui.config.json"); os.IsNotExist(err) {
		configStr := `{
  "compilerSettings": {
    "output": "public/app.ir.json"
  }
}`
		err := os.WriteFile("tinpyui.config.json", []byte(configStr), 0644)
		if err != nil {
			fmt.Println("[Error] Could not create config:", err)
		} else {
			fmt.Println("Created tinpyui.config.json")
		}
	} else {
		fmt.Println("tinpyui.config.json already exists, skipping.")
	}

	fmt.Println("\nProject initialized! Run 'go run . dev main.tin' to start the dev server.")
}
