package main

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func createProject(projectName string) {
	reader := bufio.NewReader(os.Stdin)

	fmt.Printf("\n\033[1;36m+==============================================================================+\033[0m\n")
	fmt.Printf("\033[1;36m|   \033[1;97m[*] TinPyUI v1.6.1 Project Scaffolding Wizard\033[1;36m                              |\033[0m\n")
	fmt.Printf("\033[1;36m+==============================================================================+\033[0m\n\n")

	// 1. Project Name prompt if empty
	if strings.TrimSpace(projectName) == "" {
		fmt.Print("\033[1;36m>> Enter project name/directory \033[1;97m[default: my-cyber-app]\033[0m: \033[1;33m")
		input, _ := reader.ReadString('\n')
		fmt.Print("\033[0m")
		projectName = strings.TrimSpace(input)
		if projectName == "" {
			projectName = "my-cyber-app"
		}
	}

	// 2. Target Device Architecture Selection
	fmt.Printf("\n\033[1;97mSelect target device architecture for your project:\033[0m\n")
	fmt.Printf("  \033[1;36m[1]\033[0m \033[1;97m🌐 Universal Omni-Platform\033[0m  \033[0;36m(All Devices: Android Mobile + iOS Mobile + Tablet + Web WASM)\033[0m\n")
	fmt.Printf("  \033[1;32m[2]\033[0m \033[1;97m💻 Native Desktop Specified\033[0m \033[0;32m(Windows / macOS / Linux C-FFI Vector Surface)\033[0m\n")
	fmt.Printf("  \033[1;94m[3]\033[0m \033[1;97m📱 Mobile Touch Specified\033[0m   \033[0;94m(Android & iOS Touch-First with Haptics)\033[0m\n")
	fmt.Printf("  \033[1;35m[4]\033[0m \033[1;97m📱 Tablet / iPad Specified\033[0m  \033[0;35m(Adaptive Dual-Column Split View)\033[0m\n")
	fmt.Printf("  \033[1;33m[5]\033[0m \033[1;97m🌐 WebAssembly Specified\033[0m   \033[0;33m(Zero-DOM WebGL / WebGPU Browser App)\033[0m\n\n")

	fmt.Print("\033[1;36m>> Select device mode \033[1;97m(1-5)\033[0m \033[90m[default: 1]\033[0m: \033[1;33m")
	devChoiceInput, _ := reader.ReadString('\n')
	fmt.Print("\033[0m")
	devChoice := strings.TrimSpace(devChoiceInput)
	if devChoice == "" {
		devChoice = "1"
	}

	devTitle := "Universal (Mobile + Tablet + Web WASM)"
	devSlug := "universal"
	switch devChoice {
	case "2":
		devTitle = "Native Desktop Specified"
		devSlug = "desktop"
	case "3":
		devTitle = "Mobile Touch Specified"
		devSlug = "mobile"
	case "4":
		devTitle = "Tablet / iPad Specified"
		devSlug = "tablet"
	case "5":
		devTitle = "WebAssembly Specified"
		devSlug = "web"
	}

	// 3. Confirmation Prompt Before Creating
	absPath, _ := filepath.Abs(projectName)
	fmt.Printf("\n\033[1;97mReady to scaffold:\033[0m\n")
	fmt.Printf("  • Target Directory:  \033[1;36m%s\033[0m\n", absPath)
	fmt.Printf("  • Device Target:     \033[1;32m%s\033[0m\n", devTitle)

	fmt.Print("\n\033[1;36m>> Proceed with creating project? \033[1;97m(Y/n)\033[0m \033[90m[default: Y]\033[0m: \033[1;33m")
	confirmInput, _ := reader.ReadString('\n')
	fmt.Print("\033[0m")
	confirm := strings.ToLower(strings.TrimSpace(confirmInput))
	if confirm != "" && confirm != "y" && confirm != "yes" {
		fmt.Printf("\n\033[1;33m[!] Project creation aborted by user.\033[0m\n\n")
		return
	}

	fmt.Printf("\n\033[1;32m[+] Initializing Matrix in: %s...\033[0m\n", projectName)

	// Create root directory
	if err := os.MkdirAll(projectName, 0755); err != nil {
		fmt.Printf("Error creating project directory: %v\n", err)
		os.Exit(1)
	}

	dirs := []string{
		"public",
		"scenes",
		"shaders",
		"database",
		"backend",
	}

	for _, dir := range dirs {
		if err := os.MkdirAll(filepath.Join(projectName, dir), 0755); err != nil {
			fmt.Printf("Error creating directory %s: %v\n", dir, err)
			os.Exit(1)
		}
	}

	fmt.Println("[+] Assembling Pythonic lexer & hardware engine environment...")

	// 1. Copy wasm_exec.js and engine wasm binaries to public/
	copyFile("wasm_exec.js", filepath.Join(projectName, "public", "wasm_exec.js"))
	if _, err := os.Stat("tinui_engine.wasm"); err == nil {
		copyFile("tinui_engine.wasm", filepath.Join(projectName, "public", "tinui_engine.wasm"))
		copyFile("tinui_engine.wasm", filepath.Join(projectName, "public", "app.wasm"))
	} else if _, err := os.Stat(filepath.Join("wasm_engine", "tinui_engine.wasm")); err == nil {
		copyFile(filepath.Join("wasm_engine", "tinui_engine.wasm"), filepath.Join(projectName, "public", "tinui_engine.wasm"))
		copyFile(filepath.Join("wasm_engine", "tinui_engine.wasm"), filepath.Join(projectName, "public", "app.wasm"))
	}

	// 2. Write main.tin
	mainTinContent := fmt.Sprintf(`component Main():
    AnimatedBackground(effect="cyber-wave", primaryColor="neon-purple", secondaryColor="neon-cyan"):
        Navbar(padding=20, blur=True):
            Row(align="center", justify="space-between", width="full"):
                Text(text="%s (%s)", color="neon-cyan", weight="bold")
                Row(gap=30, color="white"):
                    NavLink(text="Live Matrix", href="/")
                    NavLink(text="Docs", href="/docs")
        Router(transition="cinematic", duration="smooth"):
            Route(path="/", scene="Dashboard", default_route="true")
`, projectName, devTitle)
	writeFile(filepath.Join(projectName, "main.tin"), mainTinContent)

	// 3. Write scenes/dashboard.tin
	dashboardTin := fmt.Sprintf(`component Dashboard():
    Container(align="center", justify="center", width="full", padding=40):
        GradientText(text="Welcome to %s", size="hero")
        Spacer(height=20)
        Text(text="Configured Architecture: %s", size="large", color="white", weight="bold")
        Spacer(height=15)
        Text(text="Your Zero-DOM Wasm engine and C-FFI surface are active.", color="muted")
        Spacer(height=30)
        Row(gap=20, align="center", justify="center"):
            Button(text="📳 Haptic Pulse", variant="solid", glow="neon-cyan", radius="pill")
            Button(text="⚡ Spring Physics", variant="outline", glow="neon-purple", radius="pill")
`, projectName, devTitle)
	writeFile(filepath.Join(projectName, "scenes", "dashboard.tin"), dashboardTin)

	// 4. Write shaders/background.frag
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

	// 5. Write tinpy.toml
	tomlConfig := fmt.Sprintf(`[project]
name = "%s"
version = "1.0.0"
target_device = "%s"

[dev]
port = 8080
watch = true
`, projectName, devSlug)
	writeFile(filepath.Join(projectName, "tinpy.toml"), tomlConfig)

	// 6. Write tinpyui.config.json
	configJSON := fmt.Sprintf(`{
  "name": "%s",
  "version": "1.0.0",
  "targetDevice": "%s",
  "compilerSettings": {
    "entry": "main.tin",
    "output": "public/app.ir.json"
  }
}`, projectName, devSlug)
	writeFile(filepath.Join(projectName, "tinpyui.config.json"), configJSON)

	// 7. Write main.py
	mainPy := fmt.Sprintf(`import tinpyui as tin

class App(tin.App):
    def __init__(self):
        super().__init__(title="%s — %s", width=1280, height=820)
        self.count = tin.Signal(0)

    def build(self):
        with tin.LayoutWindow(title="%s") as root:
            with tin.Column(width="full", padding=24, gap=16):
                tin.GradientText("🚀 %s", gradient=["neon-cyan", "neon-purple"], size="hero")
                tin.Badge("Target: %s", variant="neon-cyan")
                tin.Text(text=lambda: f"Reactive Counter: {self.count.value}", color="white")
                with tin.Row(gap=12):
                    tin.Button("Increment Counter", on_click=lambda: self.count.set(self.count.value + 1))
                    tin.Button("📳 Haptic Pulse", on_click=lambda: tin.haptics.vibrate(60))
        return root

if __name__ == "__main__":
    app = App()
    app.run(prompt_target=True)
`, projectName, devTitle, projectName, projectName, devTitle)
	writeFile(filepath.Join(projectName, "main.py"), mainPy)

	writeFile(filepath.Join(projectName, "backend", ".gitkeep"), "")
	writeFile(filepath.Join(projectName, "database", ".gitkeep"), "")

	fmt.Printf("\n\033[1;32m✔ [TinPyUI Scaffold] Successfully created project '%s'!\033[0m\n\n", projectName)
	fmt.Printf("\033[1;97mNext steps:\033[0m\n")
	fmt.Printf("  \033[1;36mcd %s\033[0m\n", projectName)
	fmt.Printf("  \033[1;36mpython main.py\033[0m      \033[90m# Run multi-device interactive launcher\033[0m\n")
	fmt.Printf("  \033[1;36mtinpy dev\033[0m           \033[90m# Start WebAssembly live dev server\033[0m\n\n")
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
		return
	}
	_ = os.WriteFile(dst, data, 0644)
}
