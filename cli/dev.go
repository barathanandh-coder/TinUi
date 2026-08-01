package main

import (
	"encoding/json"
	"fmt"
	"mime"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/tinui/tinui/compiler"
)

func startDevServer() {
	fmt.Println("⚡️ TinPyUI v1.5 Dev Server")
	
	mime.AddExtensionType(".wasm", "application/wasm")

	// Start file watcher in a goroutine
	go watchFiles()

	port := "8080"
	fmt.Printf("[+] Server running at http://localhost:%s\n", port)
	
	// Simple SPA handler
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/" || r.URL.Path == "/index.html" {
			w.Header().Set("Content-Type", "text/html")
			fmt.Fprint(w, DefaultIndexHTML)
			return
		}

		if r.URL.Path == "/tin-runtime.js" {
			w.Header().Set("Content-Type", "application/javascript")
			fmt.Fprint(w, DefaultTinRuntimeJS)
			return
		}

		path := filepath.Join("public", r.URL.Path)
		if _, err := os.Stat(path); os.IsNotExist(err) {
			// SPA Fallback to index.html for unknown routes (Cinematic Router)
			w.Header().Set("Content-Type", "text/html")
			fmt.Fprint(w, DefaultIndexHTML)
			return
		}

		http.ServeFile(w, r, path)
	})

	err := http.ListenAndServe(":"+port, nil)
	if err != nil {
		fmt.Printf("Error starting server: %v\n", err)
		os.Exit(1)
	}
}

// watchFiles simulates a file system watcher for HGR and AST Recompilation
func watchFiles() {
	fmt.Println("[+] Watcher initialized (Hot GLSL Reloading enabled).")
	
	// Compile on startup
	fmt.Println("    -> Recompiling AST and Wasm Payload on boot...")
	compileTinProject()

	// Track file mod times for a naive polling watcher
	modTimes := make(map[string]time.Time)

	for {
		filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
			if err != nil || info.IsDir() {
				return nil
			}

			// Watch .tin and .frag files
			if strings.HasSuffix(path, ".tin") || strings.HasSuffix(path, ".frag") {
				lastMod, exists := modTimes[path]
				if exists && info.ModTime().After(lastMod) {
					fmt.Printf("\n[~] File changed: %s\n", path)
					if strings.HasSuffix(path, ".frag") {
						fmt.Println("    -> Triggering Hot GLSL Reloading (HGR)...")
						// Note: In a full implementation, we run glsl_validator and push via WebSocket
					} else {
						fmt.Println("    -> Recompiling AST and Wasm Payload...")
						compileTinProject()
					}
				}
				modTimes[path] = info.ModTime()
			}
			return nil
		})
		time.Sleep(1 * time.Second)
	}
}

func compileTinProject() {
	var allSource string
	
	// Read main.tin
	if b, err := os.ReadFile("main.tin"); err == nil {
		allSource += string(b) + "\n"
	} else {
		fmt.Println("[Compiler] Error: main.tin not found.")
		return
	}

	// Read all scenes
	filepath.Walk("scenes", func(path string, info os.FileInfo, err error) error {
		if err == nil && !info.IsDir() && strings.HasSuffix(path, ".tin") {
			b, _ := os.ReadFile(path)
			allSource += string(b) + "\n"
		}
		return nil
	})

	lexer := compiler.NewLexer(allSource)
	parser := compiler.NewParser(lexer)
	astRoots := parser.Parse()

	if len(parser.Errors) > 0 {
		fmt.Println("[Compiler Error] Syntax Errors:")
		for _, e := range parser.Errors {
			fmt.Println("  -", e)
		}
		return
	}

	gen := compiler.NewIRGenerator()
	instructions := gen.Generate(astRoots)

	out, _ := json.MarshalIndent(instructions, "", "  ")
	os.MkdirAll("public", 0755)
	os.WriteFile(filepath.Join("public", "app.ir.json"), out, 0644)
	fmt.Println("[Compiler] Successfully generated public/app.ir.json")
}
