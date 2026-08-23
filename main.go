package main

import (
	"bufio"
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

func main() {
	// 1. Handle Command Line Arguments
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	command := os.Args[1]
	if command != "compile" && command != "build" && command != "dev" && command != "init" && command != "desktop" {
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
	fmt.Println("Usage: tinui [compile|dev|init|desktop] <filename>.tin")
}

func initProject() {
	reader := bufio.NewReader(os.Stdin)

	fmt.Printf("\n\033[1;36m+==============================================================================+\033[0m\n")
	fmt.Printf("\033[1;36m|   \033[1;97m[*] TinPyUI v1.6.0 Project Scaffolding Wizard\033[1;36m                              |\033[0m\n")
	fmt.Printf("\033[1;36m+==============================================================================+\033[0m\n\n")

	fmt.Print("\033[1;36m>> Enter project name/directory \033[1;97m[default: my-cyber-app]\033[0m: \033[1;33m")
	inputName, _ := reader.ReadString('\n')
	fmt.Print("\033[0m")
	projectName := strings.TrimSpace(inputName)
	if projectName == "" {
		projectName = "my-cyber-app"
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
	os.MkdirAll(filepath.Join(projectName, "public"), 0755)
	os.MkdirAll(filepath.Join(projectName, "scenes"), 0755)
	os.MkdirAll(filepath.Join(projectName, "shaders"), 0755)
	os.MkdirAll(filepath.Join(projectName, "database"), 0755)
	os.MkdirAll(filepath.Join(projectName, "backend"), 0755)

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
	_ = os.WriteFile(filepath.Join(projectName, "main.tin"), []byte(mainTinContent), 0644)

	configStr := fmt.Sprintf(`{
  "name": "%s",
  "version": "1.0.0",
  "targetDevice": "%s",
  "compilerSettings": {
    "entry": "main.tin",
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
	fmt.Printf("  \033[1;36mpython main.py\033[0m      \033[90m# Run multi-device interactive launcher\033[0m\n")
	fmt.Printf("  \033[1;36mtinui dev main.tin\033[0m  \033[90m# Start WebAssembly live dev server\033[0m\n\n")
}

// ============================================================================
// DEV SERVER & HYDRATION ASSET MANAGEMENT
// ============================================================================

func startDevServer(inputFile, outDir, outputFile string, hydrate bool) {
	fmt.Printf("Starting Dev Server for %s on http://localhost:3000\n", inputFile)

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
			time.Sleep(500 * time.Millisecond)
			stat, err := os.Stat(inputFile)
			if err == nil {
				if stat.ModTime().After(lastMod) {
					lastMod = stat.ModTime()
					fmt.Println("\n[Dev Server] File change detected, recompiling...")
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

			content = strings.Replace(content, "</body>", livereloadScript+"</body>", 1)
			w.Header().Set("Content-Type", "text/html")
			w.Write([]byte(content))
			return
		}

		if r.URL.Path == "/tin-runtime.js" {
			w.Header().Set("Content-Type", "application/javascript")
			fmt.Fprint(w, DefaultTinRuntimeJS)
			return
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
	wasmExecDest := filepath.Join(outDir, "wasm_exec.js")
	appWasmDest := filepath.Join(outDir, "app.wasm")
	tinuiWasmDest := filepath.Join(outDir, "tinui_engine.wasm")

	exePath, _ := os.Executable()
	exeDir := filepath.Dir(exePath)

	if _, err := os.Stat(wasmExecDest); os.IsNotExist(err) {
		if _, err := os.Stat("wasm_exec.js"); err == nil {
			copyFile("wasm_exec.js", wasmExecDest)
		} else if _, err := os.Stat(filepath.Join(exeDir, "wasm_exec.js")); err == nil {
			copyFile(filepath.Join(exeDir, "wasm_exec.js"), wasmExecDest)
		}
	}

	wasmSrc := ""
	if _, err := os.Stat("tinui_engine.wasm"); err == nil {
		wasmSrc = "tinui_engine.wasm"
	} else if _, err := os.Stat(filepath.Join("wasm_engine", "tinui_engine.wasm")); err == nil {
		wasmSrc = filepath.Join("wasm_engine", "tinui_engine.wasm")
	} else if _, err := os.Stat(filepath.Join(exeDir, "tinui_engine.wasm")); err == nil {
		wasmSrc = filepath.Join(exeDir, "tinui_engine.wasm")
	} else if _, err := os.Stat(filepath.Join(outDir, "tinui_engine.wasm")); err == nil {
		wasmSrc = filepath.Join(outDir, "tinui_engine.wasm")
	} else if _, err := os.Stat(filepath.Join(outDir, "app.wasm")); err == nil {
		wasmSrc = filepath.Join(outDir, "app.wasm")
	}

	if wasmSrc != "" {
		if _, err := os.Stat(appWasmDest); os.IsNotExist(err) {
			copyFile(wasmSrc, appWasmDest)
		}
		if _, err := os.Stat(tinuiWasmDest); os.IsNotExist(err) {
			copyFile(wasmSrc, tinuiWasmDest)
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

const DefaultTinRuntimeJS = `// tin-runtime.js — TinPyUI v1.6.0 Runtime
const go = new Go();
const _tinWasmSources = ["tinui_engine.wasm", "app.wasm", "/tinui_engine.wasm", "/app.wasm"];
let _tinWasmPromise = null;
for (const src of _tinWasmSources) {
    if (!_tinWasmPromise) {
        _tinWasmPromise = fetch(src).then(res => {
            if (!res.ok) throw new Error("Status " + res.status);
            return res;
        });
    } else {
        _tinWasmPromise = _tinWasmPromise.catch(() => fetch(src).then(res => {
            if (!res.ok) throw new Error("Status " + res.status);
            return res;
        }));
    }
}
_tinWasmPromise.then(res => WebAssembly.instantiateStreaming(res, go.importObject))
.then((result) => {
    go.run(result.instance);
    fetch('app.ir.json').then(r => r.text()).then(json => {
        if (typeof BootTinUI === 'function') {
            BootTinUI(json);
        }
    });
}).catch(err => {
    console.error('[TinPyUI Runtime] Failed to initialize WebAssembly engine:', err);
});
`

const DefaultStarterTin = `component Main():
    Section(paddingY = 64, align = "center", justify = "center", minHeight = "screen"):
        Heading(text = "Hello from TinPyUI", color = "neon-cyan", size = "h1")
        Text(text = "Edit main.tin to get started.", color = "muted", marginTop = 24)
`
