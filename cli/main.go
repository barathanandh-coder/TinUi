package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	command := os.Args[1]

	switch command {
	case "create":
		if len(os.Args) < 3 {
			fmt.Println("Error: Missing project name.")
			fmt.Println("Usage: tinpy create <project-name>")
			os.Exit(1)
		}
		createProject(os.Args[2])
	case "dev":
		startDevServer()
	default:
		fmt.Printf("Unknown command: %s\n", command)
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println("⚡️ TinPyUI v1.5 - The Zero-DOM Wasm Engine")
	fmt.Println("\nUsage:")
	fmt.Println("  tinpy create <project-name>   Scaffold a new TinPyUI project")
	fmt.Println("  tinpy dev                     Start the development server with HGR")
}
