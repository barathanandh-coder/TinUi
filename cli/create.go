package main

import (
	"fmt"
	"os"
	"path/filepath"
)

func createProject(projectName string) {
	fmt.Printf("\n⚡️ TinPyUI v1.5 - The Zero-DOM Wasm Engine\n\n")
	fmt.Printf("[+] Initializing Matrix: %s\n", projectName)

	// Create root directory
	if err := os.MkdirAll(projectName, 0755); err != nil {
		fmt.Printf("Error creating project directory: %v\n", err)
		os.Exit(1)
	}

	dirs := []string{
		"public",
		"scenes",
		"shaders",
	}

	for _, dir := range dirs {
		if err := os.MkdirAll(filepath.Join(projectName, dir), 0755); err != nil {
			fmt.Printf("Error creating directory %s: %v\n", dir, err)
			os.Exit(1)
		}
	}

	fmt.Println("[+] Assembling Pythonic lexer environment...")

	// 1. & 2. Zero-DOM: index.html and tin-runtime.js are no longer written to disk.
	// They are served dynamically from memory by the dev server.

	// Copy wasm_exec.js and tinui_engine.wasm if they exist in the root (for dev testing)
	copyFile("wasm_exec.js", filepath.Join(projectName, "public", "wasm_exec.js"))
	copyFile(filepath.Join("wasm_engine", "tinui_engine.wasm"), filepath.Join(projectName, "public", "app.wasm"))

	// 3. Write main.tin
	writeFile(filepath.Join(projectName, "main.tin"), DefaultMainTin)

	// 4. Write scenes/dashboard.tin
	dashboardTin := `component Dashboard():
    Container(align="center", justify="center", width="full", padding=50):
        GradientText(text="Welcome to the Matrix", size="hero")
        Spacer(height=20)
        Text(text="Your Zero-DOM Wasm engine is running.", color="muted")
`
	writeFile(filepath.Join(projectName, "scenes", "dashboard.tin"), dashboardTin)

	// 5. Write shaders/background.frag
	bgFrag := `precision highp float;
uniform float u_time;
uniform vec2 u_resolution;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    float color = 0.5 + 0.5 * sin(u_time + uv.x * 10.0);
    gl_FragColor = vec4(0.0, color, 1.0, 1.0);
}
`
	writeFile(filepath.Join(projectName, "shaders", "background.frag"), bgFrag)

	// 6. Write tinpy.toml
	fmt.Println("[+] Writing tinpy.toml configuration...")
	tomlConfig := `[project]
name = "` + projectName + `"
version = "0.1.0"

[dev]
port = 8080
watch = true
`
	writeFile(filepath.Join(projectName, "tinpy.toml"), tomlConfig)

	fmt.Printf("\n🚀 Matrix initialized.\n\nNext steps:\n  cd %s\n  tinpy dev\n", projectName)
}

func writeFile(path, content string) {
	err := os.WriteFile(path, []byte(content), 0644)
	if err != nil {
		fmt.Printf("Error writing %s: %v\n", path, err)
		os.Exit(1)
	}
}

func copyFile(src, dst string) {
	data, err := os.ReadFile(src)
	if err != nil {
		fmt.Printf("Warning: Could not copy %s (ensure you are running from repo root during dev): %v\n", src, err)
		return
	}
	err = os.WriteFile(dst, data, 0644)
	if err != nil {
		fmt.Printf("Error writing %s: %v\n", dst, err)
	}
}
