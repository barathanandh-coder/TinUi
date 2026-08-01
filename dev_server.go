package main

import (
	"fmt"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)

func startDevServer(inputFile, outDir, outputFile string, hydrate bool) {
	fmt.Printf("Starting Dev Server for %s on http://localhost:3000\n", inputFile)

	compileFile(inputFile, outDir, outputFile, hydrate)

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

	// File watcher (Polling)
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

	// Serve Static Files
	fs := http.FileServer(http.Dir(outDir))
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// Serve index.html explicitly to inject livereload script
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

	// Livereload endpoint (Long Polling)
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
			// Client disconnected
		}
	})

	err := http.ListenAndServe(":3000", nil)
	if err != nil {
		fmt.Printf("[Error] Failed to start dev server: %v\n", err)
	}
}
