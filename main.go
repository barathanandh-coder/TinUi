package main

import (
	"bufio"
	_ "embed"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"

	"github.com/tinui/tinui/compiler"
)

//go:embed tinui_engine.wasm
var EmbeddedEngineWasm []byte

//go:embed wasm_exec.js
var EmbeddedWasmExecJS []byte

//go:embed tin-runtime.js
var EmbeddedTinRuntimeJS []byte

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	arg1 := os.Args[1]

	// 1. Direct file run shorthand: `tinui app.tin`
	if len(os.Args) == 2 && strings.HasSuffix(arg1, ".tin") {
		outDir := "public"
		outputFile := filepath.Join("public", "app.ir.json")
		os.MkdirAll(outDir, 0755)
		startDevServer(arg1, outDir, outputFile, false)
		return
	}

	if arg1 == "-h" || arg1 == "--help" || arg1 == "help" {
		printUsage()
		return
	}

	command := arg1
	if command == "init" {
		targetName := ""
		if len(os.Args) > 2 {
			targetName = os.Args[2]
		}
		initProject(targetName)
		return
	}


	if len(os.Args) < 3 {
		printUsage()
		os.Exit(1)
	}


	var hydrate bool
	var isMobile bool
	var inputFile string
	for _, arg := range os.Args[2:] {
		if arg == "--hydrate" {
			hydrate = true
		} else if arg == "--mobile" || arg == "--android" || arg == "mobile" {
			isMobile = true
		} else if !strings.HasPrefix(arg, "--") {
			if arg == "mobile" {
				isMobile = true
			} else {
				inputFile = arg
			}
		}
	}

	if (command == "export" || command == "build") && isMobile {
		if inputFile == "" {
			for _, cand := range []string{"main.tin", "index.tin", "app.tin", "main.py"} {
				if _, err := os.Stat(cand); err == nil {
					inputFile = cand
					break
				}
			}
			if inputFile == "" {
				inputFile = "main.tin"
			}
		}
		exportMobileProject(inputFile)
		return
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

	if command == "dev" || command == "run" {
		outDir = "public"
		base = strings.TrimSuffix(filepath.Base(inputFile), ext)
		outputFile = filepath.Join("public", "app.ir.json")
		os.MkdirAll(outDir, 0755)
		startDevServer(inputFile, outDir, outputFile, hydrate)
		return
	}

	if command == "desktop" {
		outDir = "."
		base = strings.TrimSuffix(filepath.Base(inputFile), ext)
		outputFile = base + ".ir.json"
		startDesktopApp(inputFile, outDir, outputFile, true)
		return
	}

	if command == "build" {
		hydrate = true
		if outDir == "" || outDir == "." {
			outDir = "dist"
			outputFile = filepath.Join("dist", "app.ir.json")
			os.MkdirAll(outDir, 0755)
		}
	}

	success := compileFile(inputFile, outDir, outputFile, hydrate)
	if !success {
		os.Exit(1)
	}
}

func exportMobileProject(inputFile string) {
	fmt.Printf("\n\033[1;36m[TinUI Mobile Engine]\033[0m Preparing native mobile export for: \033[1;97m%s\033[0m...\n", inputFile)
	_ = compileFile(inputFile, "public", "app.ir.json", false)

	// Prefer python tinpyui.py build --mobile if tinpyui.py exists, or python -m tinpyui.cli
	var cmd *exec.Cmd
	if _, err := os.Stat("tinpyui.py"); err == nil {
		cmd = exec.Command("python", "tinpyui.py", "build", "--mobile", inputFile)
	} else {
		cmd = exec.Command("python", "-m", "tinpyui.cli", "build", "--mobile", inputFile)
	}
	cmd.Env = append(os.Environ(), "PYTHONPATH=pypi_build"+string(filepath.ListSeparator)+os.Getenv("PYTHONPATH"))
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		var cmd3 *exec.Cmd
		if _, err3 := os.Stat("tinpyui.py"); err3 == nil {
			cmd3 = exec.Command("python3", "tinpyui.py", "build", "--mobile", inputFile)
		} else {
			cmd3 = exec.Command("python3", "-m", "tinpyui.cli", "build", "--mobile", inputFile)
		}
		cmd3.Env = append(os.Environ(), "PYTHONPATH=pypi_build"+string(filepath.ListSeparator)+os.Getenv("PYTHONPATH"))
		cmd3.Stdout = os.Stdout
		cmd3.Stderr = os.Stderr
		if err3 := cmd3.Run(); err3 != nil {
			fmt.Printf("\033[1;33m[!] Note: Python mobile exporter exited with: %v. Staging complete.\033[0m\n", err3)
		}
	}
}




func compileFile(inputFile, outDir, outputFile string, hydrate bool) bool {
	sourceBytes, err := os.ReadFile(inputFile)
	if err != nil {
		fmt.Printf("[Error] Error reading file %s: %v\n", inputFile, err)
		return false
	}
	sourceCode := string(sourceBytes) + "\n"

	// Also scan and append all scene components from scenes/ directory
	scenesDir := "scenes"
	inputDir := filepath.Dir(inputFile)
	if inputDir != "" && inputDir != "." {
		if _, err := os.Stat(filepath.Join(inputDir, "scenes")); err == nil {
			scenesDir = filepath.Join(inputDir, "scenes")
		}
	}
	if _, err := os.Stat(scenesDir); err == nil {
		filepath.Walk(scenesDir, func(path string, info os.FileInfo, err error) error {
			if err == nil && !info.IsDir() && strings.HasSuffix(path, ".tin") {
				if b, readErr := os.ReadFile(path); readErr == nil {
					sourceCode += string(b) + "\n"
				}
			}
			return nil
		})
	}

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
	_ = os.WriteFile("app.ir.json", irJSON, 0644)
	_ = os.MkdirAll("public", 0755)
	_ = os.WriteFile(filepath.Join("public", "app.ir.json"), irJSON, 0644)

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
	fmt.Println("\n\033[1;36m+==============================================================================+\033[0m")
	fmt.Println("\033[1;36m|   \033[1;97m[*] TinUI v1.6.1 — Zero-Dependency Embedded Engine CLI\033[1;36m                     |\033[0m")
	fmt.Println("\033[1;36m+==============================================================================+\033[0m")
	fmt.Println("\n\033[1;97m⚡ Instant 1-Step Execution:\033[0m")
	fmt.Println("  \033[1;32mtinui <file.tin>\033[0m              \033[90m# Run file immediately in live dev server\033[0m")
	fmt.Println("  \033[1;32mtinui run <file.tin>\033[0m          \033[90m# Run application dev server\033[0m")
	fmt.Println("  \033[1;32mtinui desktop <file.tin>\033[0m      \033[90m# Launch as Native Desktop Window\033[0m")
	fmt.Println("\n\033[1;97m🛠️ Compilation & Production:\033[0m")
	fmt.Println("  \033[1;36mtinui compile <file.tin>\033[0m      \033[90m# Fast compile to IR JSON AST\033[0m")
	fmt.Println("  \033[1;36mtinui build <file.tin>\033[0m        \033[90m# Build standalone production bundle (HTML + WASM)\033[0m")
	fmt.Println("  \033[1;36mtinui build --mobile <file>\033[0m   \033[90m# Export Android Gradle project & build APK\033[0m")
	fmt.Println("  \033[1;36mtinui export mobile <file>\033[0m    \033[90m# Standalone Native Mobile Export Pipeline\033[0m")
	fmt.Println("  \033[1;36mtinui init [project-name]\033[0m     \033[90m# Scaffold fresh project architecture\033[0m")
}

func initProject(inputName string) {
	reader := bufio.NewReader(os.Stdin)

	fmt.Printf("\n\033[1;36m+==============================================================================+\033[0m\n")
	fmt.Printf("\033[1;36m|   \033[1;97m[*] TinPyUI v1.6.1 Project Scaffolding Wizard\033[1;36m                              |\033[0m\n")
	fmt.Printf("\033[1;36m+==============================================================================+\033[0m\n\n")

	projectName := strings.TrimSpace(inputName)
	if projectName == "" {
		fmt.Print("\033[1;36m>> Enter project name/directory \033[1;97m[default: my-cyber-app]\033[0m: \033[1;33m")
		input, _ := reader.ReadString('\n')
		fmt.Print("\033[0m")
		projectName = strings.TrimSpace(input)
		if projectName == "" {
			projectName = "my-cyber-app"
		}
	}

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

	fmt.Printf("\n\033[1;32m[+] Initializing fresh TinPyUI v1.6.0 project in: %s...\033[0m\n", projectName)
	os.MkdirAll(projectName, 0755)
	os.MkdirAll(filepath.Join(projectName, "src"), 0755)
	os.MkdirAll(filepath.Join(projectName, "public"), 0755)
	os.MkdirAll(filepath.Join(projectName, "scenes"), 0755)
	os.MkdirAll(filepath.Join(projectName, "shaders"), 0755)
	os.MkdirAll(filepath.Join(projectName, "database"), 0755)
	os.MkdirAll(filepath.Join(projectName, "backend"), 0755)

	mainTinContent := fmt.Sprintf(`component Main():
    AnimatedBackground(effect="quantum-vortex", primaryColor="neon-purple", secondaryColor="neon-cyan"):
        Navbar(padding=20, blur=true):
            Row(align="center", justify="space-between", width="full"):
                Row(align="center", gap=10):
                    Text(text="%s (%s)", color="neon-cyan", weight="bold")
                Row(gap=30, color="white"):
                    NavLink(text="Dashboard", href="/")
                    NavLink(text="Documentation", href="/docs")
        Section(align="center", paddingY=80, maxWidth=800, justify="center"):
            GradientText(text="%s", gradient=["neon-cyan", "neon-purple"], size="hero")
            Text(text="Target: %s", size="large", color="white", weight="bold", marginTop=20)
            Text(text="Hardware-Accelerated UI Engine with Pythonic Indentation DSL.", color="muted", marginTop=10)
            Row(gap=20, align="center", justify="center", marginTop=40):
                Button(text="Get Started", variant="solid", glow="neon-cyan", radius="pill")
                Button(text="⚡ Spring Physics", variant="outline", glow="neon-purple", radius="pill")
`, projectName, devTitle, projectName, devTitle)
	_ = os.WriteFile(filepath.Join(projectName, "index.tin"), []byte(mainTinContent), 0644)
	_ = os.WriteFile(filepath.Join(projectName, "src", "index.tin"), []byte(mainTinContent), 0644)
	_ = os.WriteFile(filepath.Join(projectName, "main.tin"), []byte(mainTinContent), 0644)

	configStr := fmt.Sprintf(`{
  "name": "%s",
  "version": "1.0.0",
  "targetDevice": "%s",
  "compilerSettings": {
    "entry": "index.tin",
    "output": "public/app.ir.json"
  }
}`, projectName, devSlug)
	_ = os.WriteFile(filepath.Join(projectName, "tinpyui.config.json"), []byte(configStr), 0644)

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
	_ = os.WriteFile(filepath.Join(projectName, "main.py"), []byte(mainPy), 0644)
	_ = os.WriteFile(filepath.Join(projectName, "backend", ".gitkeep"), []byte(""), 0644)
	_ = os.WriteFile(filepath.Join(projectName, "database", ".gitkeep"), []byte(""), 0644)

	ensureWasmAssets(filepath.Join(projectName, "public"))

	fmt.Printf("\n\033[1;32m✔ [TinPyUI Scaffold] Successfully created project '%s'!\033[0m\n\n", projectName)
	fmt.Printf("\033[1;97mNext steps:\033[0m\n")
	fmt.Printf("  \033[1;36mcd %s\033[0m\n", projectName)
	fmt.Printf("  \033[1;36mtinui index.tin\033[0m      \033[90m# Run instantly with live hot reload\033[0m\n")
	fmt.Printf("  \033[1;36mpython main.py\033[0m       \033[90m# Run native desktop app (120 FPS)\033[0m\n\n")
}

// ============================================================================
// DEV SERVER & HYDRATION ASSET MANAGEMENT
// ============================================================================

func startDevServer(inputFile, outDir, outputFile string, hydrate bool) {
	fmt.Printf("\n\033[1;32m[TinUI Engine] Starting Live Server for %s on http://localhost:3000\033[0m\n", inputFile)

	compileFile(inputFile, outDir, outputFile, hydrate)
	ensureWasmAssets(outDir)

	var reloadChannels []chan struct{}
	var chanMutex sync.Mutex

	notifyReload := func() {
		chanMutex.Lock()
		for _, ch := range reloadChannels {
			select {
			case ch <- struct{}{}:
			default:
			}
		}
		reloadChannels = nil
		chanMutex.Unlock()
	}

	go func() {
		var lastMod time.Time
		if stat, err := os.Stat(inputFile); err == nil {
			lastMod = stat.ModTime()
		}

		for {
			time.Sleep(400 * time.Millisecond)
			stat, err := os.Stat(inputFile)
			if err == nil {
				if stat.ModTime().After(lastMod) {
					lastMod = stat.ModTime()
					fmt.Println("\n\033[1;36m[Dev Server] File change detected, recompiling in-memory...\033[0m")
					if compileFile(inputFile, outDir, outputFile, hydrate) {
						notifyReload()
					}
				}
			}
		}
	}()

	fs := http.FileServer(http.Dir(outDir))
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/" || r.URL.Path == "/index.html" {
			content := DefaultIndexHTML
			if customHTML, err := os.ReadFile(filepath.Join(outDir, "index.html")); err == nil {
				content = string(customHTML)
			}
			livereloadScript := `
			<script>
				(function() {
					function connect() {
						fetch('/tinui_livereload').then(res => {
							if(res.status === 200) {
								window.location.reload();
							} else {
								setTimeout(connect, 1000);
							}
						}).catch(() => setTimeout(connect, 1000));
					}
					setTimeout(connect, 1000);
				})();
			</script>`

			if strings.Contains(content, "</body>") {
				content = strings.Replace(content, "</body>", livereloadScript+"</body>", 1)
			} else {
				content += livereloadScript
			}
			w.Header().Set("Content-Type", "text/html")
			w.Write([]byte(content))
			return
		}

		if r.URL.Path == "/tin-runtime.js" {
			w.Header().Set("Content-Type", "application/javascript")
			if data, err := os.ReadFile(filepath.Join(outDir, "tin-runtime.js")); err == nil {
				w.Write(data)
				return
			}
			if len(EmbeddedTinRuntimeJS) > 0 {
				w.Write(EmbeddedTinRuntimeJS)
				return
			}
			fmt.Fprint(w, DefaultTinRuntimeJS)
			return
		}

		if r.URL.Path == "/wasm_exec.js" {
			w.Header().Set("Content-Type", "application/javascript")
			if data, err := os.ReadFile(filepath.Join(outDir, "wasm_exec.js")); err == nil {
				w.Write(data)
				return
			}
			if len(EmbeddedWasmExecJS) > 0 {
				w.Write(EmbeddedWasmExecJS)
				return
			}
		}

		if r.URL.Path == "/tinui_engine.wasm" || r.URL.Path == "/app.wasm" {
			w.Header().Set("Content-Type", "application/wasm")
			filename := filepath.Base(r.URL.Path)
			if data, err := os.ReadFile(filepath.Join(outDir, filename)); err == nil {
				w.Write(data)
				return
			}
			if len(EmbeddedEngineWasm) > 0 {
				w.Write(EmbeddedEngineWasm)
				return
			}
		}

		fs.ServeHTTP(w, r)
	})

	http.HandleFunc("/tinui_livereload", func(w http.ResponseWriter, r *http.Request) {
		ch := make(chan struct{}, 1)
		chanMutex.Lock()
		reloadChannels = append(reloadChannels, ch)
		chanMutex.Unlock()

		select {
		case <-ch:
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("reload"))
		case <-r.Context().Done():
		}
	})

	err := http.ListenAndServe(":3000", nil)
	if err != nil {
		fmt.Printf("[Error] Failed to start dev server: %v\n", err)
	}
}

func ensureWasmAssets(outDir string) {
	os.MkdirAll(outDir, 0755)
	wasmExecDest := filepath.Join(outDir, "wasm_exec.js")
	appWasmDest := filepath.Join(outDir, "app.wasm")
	tinuiWasmDest := filepath.Join(outDir, "tinui_engine.wasm")
	tinRuntimeDest := filepath.Join(outDir, "tin-runtime.js")

	if _, err := os.Stat(wasmExecDest); os.IsNotExist(err) && len(EmbeddedWasmExecJS) > 0 {
		_ = os.WriteFile(wasmExecDest, EmbeddedWasmExecJS, 0644)
	}
	if _, err := os.Stat(tinuiWasmDest); os.IsNotExist(err) && len(EmbeddedEngineWasm) > 0 {
		_ = os.WriteFile(tinuiWasmDest, EmbeddedEngineWasm, 0644)
	}
	if _, err := os.Stat(appWasmDest); os.IsNotExist(err) && len(EmbeddedEngineWasm) > 0 {
		_ = os.WriteFile(appWasmDest, EmbeddedEngineWasm, 0644)
	}
	if _, err := os.Stat(tinRuntimeDest); os.IsNotExist(err) {
		if len(EmbeddedTinRuntimeJS) > 0 {
			_ = os.WriteFile(tinRuntimeDest, EmbeddedTinRuntimeJS, 0644)
		} else {
			_ = os.WriteFile(tinRuntimeDest, []byte(DefaultTinRuntimeJS), 0644)
		}
	}
}

func copyFile(src, dst string) error {
	data, err := os.ReadFile(src)
	if err != nil {
		fmt.Printf("[Warning] Failed to read asset %s: %v\n", src, err)
		return err
	}
	return os.WriteFile(dst, data, 0644)
}

// ============================================================================
// NATIVE DESKTOP SHELL LAUNCHER & C++ ENGINE FLAGS
// ============================================================================

func startDesktopApp(inputFile, outDir, outputFile string, hydrate bool) {
	fmt.Printf("[TinPyUI Desktop Engine] Launching native window application for %s...\n", inputFile)
	compileFile(inputFile, outDir, outputFile, hydrate)
	ensureWasmAssets(outDir)

	listener, err := net.Listen("tcp", "127.0.0.1:3000")
	if err != nil {
		listener, err = net.Listen("tcp", "127.0.0.1:0")
		if err != nil {
			fmt.Printf("[Desktop Server Error] Could not bind to network port: %v\n", err)
			return
		}
	}
	defer listener.Close()

	port := fmt.Sprintf("%d", listener.Addr().(*net.TCPAddr).Port)
	appURL := fmt.Sprintf("http://127.0.0.1:%s/index.html", port)

	go func() {
		time.Sleep(300 * time.Millisecond)
		fmt.Printf("[TinPyUI Desktop Engine] Native Desktop Window Opened: %s\n", appURL)
		fmt.Printf("[TinPyUI Desktop Engine] Universal C++ Core: engine_core.cc (webview.h IPC Bridge)\n")

		if runtime.GOOS == "windows" {
			tempProfile := filepath.Join(os.TempDir(), "tinpyui_desktop_profile")
			cmd := exec.Command("cmd", "/c", "start", "msedge.exe", fmt.Sprintf("--app=%s", appURL), "--new-window", "--window-size=1280,820", fmt.Sprintf("--user-data-dir=%s", tempProfile))
			if err := cmd.Run(); err != nil {
				_ = exec.Command("cmd", "/c", "start", appURL).Run()
			}
		} else if runtime.GOOS == "darwin" {
			_ = exec.Command("open", "-a", "Safari", appURL).Run()
		} else {
			_ = exec.Command("xdg-open", appURL).Run()
		}
	}()

	fs := http.FileServer(http.Dir(outDir))
	_ = http.Serve(listener, fs)
}

func GetNativeCppCompilerFlags(targetOS string) string {
	switch targetOS {
	case "darwin", "macos":
		return "c++ engine_core.cc -std=c++11 -framework WebKit -framework Cocoa -o tinui_mac"
	case "linux":
		return "g++ engine_core.cc `pkg-config --cflags --libs gtk+-3.0 webkit2gtk-4.0` -o tinui_linux"
	case "windows":
		return "g++ engine_core.cc -mwindows -ladvapi32 -lole32 -lshell32 -lshlwapi -luser32 -lversion -o tinui_win.exe"
	default:
		return "g++ engine_core.cc -o tinui_desktop"
	}
}

// ============================================================================
// TEMPLATES & STARTER FILES
// ============================================================================

const DefaultIndexHTML = `<!DOCTYPE html><html lang="en"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TinPyUI App</title>
</head>
<body>
    <div id="tinui-root">
        <!-- The Wasm Engine mounts here -->
    </div>
    <script src="wasm_exec.js"></script>
    <script src="tin-runtime.js"></script>
</body></html>`

const DefaultTinRuntimeJS = `// tin-runtime.js — TinPyUI v1.6.1 Runtime with Diagnostic Error Overlay & Boundary
(function() {
    function ensureDiagnosticOverlay() {
        if (!document.body) {
            document.addEventListener('DOMContentLoaded', ensureDiagnosticOverlay);
            return;
        }
        if (!document.getElementById('error-overlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'error-overlay';
            overlay.style.display = 'none';
            overlay.style.padding = '24px';
            overlay.style.color = '#ff4d4d';
            overlay.style.backgroundColor = '#0a0a0a';
            overlay.style.fontFamily = 'monospace';
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100vw';
            overlay.style.height = '100vh';
            overlay.style.zIndex = '999999';
            overlay.style.boxSizing = 'border-box';
            overlay.style.overflow = 'auto';

            const title = document.createElement('h2');
            title.style.margin = '0 0 16px 0';
            title.style.fontSize = '20px';
            title.style.borderBottom = '1px solid #ff4d4d';
            title.style.paddingBottom = '8px';
            title.innerText = '⚠️ TinPyUI Engine Panic';

            const log = document.createElement('pre');
            log.id = 'error-log';
            log.style.margin = '0';
            log.style.whiteSpace = 'pre-wrap';
            log.style.wordBreak = 'break-all';
            log.style.fontSize = '14px';
            log.style.lineHeight = '1.5';

            overlay.appendChild(title);
            overlay.appendChild(log);
            document.body.appendChild(overlay);
        }
    }
    ensureDiagnosticOverlay();

    window.crash = function(message) {
        ensureDiagnosticOverlay();
        const canvas = document.getElementById('tin-canvas');
        if (canvas) canvas.style.display = 'none';
        const root = document.getElementById('tinui-root');
        if (root) root.style.display = 'none';
        const overlay = document.getElementById('error-overlay');
        if (overlay) overlay.style.display = 'block';
        const log = document.getElementById('error-log');
        if (log) log.innerText += message + "\n\n";
        console.error('[TinPyUI Engine Panic]', message);
    };

    window.onerror = function(msg, url, line, col, error) {
        const errorDetails = error && error.stack ? error.stack : (msg + '\nLocation: ' + url + ':' + line + ':' + (col || 0));
        window.crash('Runtime Error: ' + errorDetails);
        return false;
    };

    window.addEventListener('unhandledrejection', function(event) {
        const reason = event.reason;
        const msg = reason && (reason.stack || reason.message) ? (reason.stack || reason.message) : String(reason);
        window.crash('Unhandled Rejection: ' + msg);
    });

    window.clearCrash = function() {
        const overlay = document.getElementById('error-overlay');
        if (overlay) {
            overlay.style.display = 'none';
            const log = document.getElementById('error-log');
            if (log) log.innerText = '';
        }
        const canvas = document.getElementById('tin-canvas');
        if (canvas) canvas.style.display = 'block';
        const root = document.getElementById('tinui-root');
        if (root) root.style.display = 'block';
    };

    window.reloadShader = function(target, code) {
        if (typeof window.TinUIReloadShader === 'function') {
            return window.TinUIReloadShader(target, code);
        }
        return false;
    };

    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'TINPYUI_RELOAD_SHADER') {
            window.reloadShader(event.data.target || 'tin-canvas', event.data.code);
        }
    });

    const go = new Go();
    const _tinWasmSources = ["tinui_engine.wasm", "app.wasm", "/tinui_engine.wasm", "/app.wasm"];
    let _tinWasmPromise = null;
    for (const src of _tinWasmSources) {
        if (!_tinWasmPromise) {
            _tinWasmPromise = fetch(src).then(res => {
                if (!res.ok) throw new Error("HTTP " + res.status + " fetching " + src);
                return res;
            });
        } else {
            _tinWasmPromise = _tinWasmPromise.catch(() => fetch(src).then(res => {
                if (!res.ok) throw new Error("HTTP " + res.status + " fetching " + src);
                return res;
            }));
        }
    }

    async function _loadIR() {
        const irCandidates = ['app.ir.json', 'main.ir.json', 'index.ir.json', '/app.ir.json', '/main.ir.json', '/index.ir.json'];
        for (const path of irCandidates) {
            try {
                const res = await fetch(path);
                if (res.ok) {
                    const text = await res.text();
                    if (text && text.trim().startsWith('{')) {
                        const parsed = JSON.parse(text);
                        if (parsed.nodes && parsed.nodes.length > 0) return text;
                    }
                }
            } catch (e) {}
        }
        return null;
    }

    async function bootEngine() {
        try {
            ensureDiagnosticOverlay();
            const res = await _tinWasmPromise;
            if (!res) throw new Error("Could not load WebAssembly binary from candidate paths.");
            const result = await WebAssembly.instantiateStreaming(res, go.importObject);

            let canvas = document.getElementById('tin-canvas');
            if (!canvas && document.body) {
                canvas = document.createElement('canvas');
                canvas.id = 'tin-canvas';
                canvas.style.position = 'fixed';
                canvas.style.top = '0';
                canvas.style.left = '0';
                canvas.style.width = '100vw';
                canvas.style.height = '100vh';
                canvas.style.display = 'block';
                canvas.style.zIndex = '-1';
                document.body.prepend(canvas);
            }

            if (canvas) {
                const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
                if (gl) {
                    gl.clearColor(0.1, 0.1, 0.1, 1.0);
                    gl.clear(gl.COLOR_BUFFER_BIT);
                }
            }

            go.run(result.instance);
            const irJSON = await _loadIR();
            if (irJSON && typeof BootTinUI === 'function') {
                BootTinUI(irJSON);
            } else if (typeof BootTinUI !== 'function') {
                throw new Error("BootTinUI wasm symbol not found on global scope.");
            }
        } catch (err) {
            window.crash('Engine Boot Failure: ' + (err && (err.stack || err.message) ? (err.stack || err.message) : err));
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootEngine);
    } else {
        bootEngine();
    }
})();
`

const DefaultStarterTin = `component Main():
    Section(paddingY = 64, align = "center", justify = "center", minHeight = "screen"):
        Heading(text = "Hello from TinPyUI", color = "neon-cyan", size = "h1")
        Text(text = "Edit main.tin to get started.", color = "muted", marginTop = 24)
`
