.PHONY: help test test-py test-go vet wasm build clean lint format

# Default target
help:
	@echo "TinPyUI Developer CLI & Build Automation"
	@echo "========================================="
	@echo "  make test        Run both Python and Go test suites"
	@echo "  make test-py     Run Python unittest test suite"
	@echo "  make test-go     Run Go test suite"
	@echo "  make vet         Run Go static analyzer (go vet)"
	@echo "  make wasm        Compile wasm_engine to WebAssembly binary"
	@echo "  make build       Build tinui CLI binary"
	@echo "  make lint        Run all linting and validation checks"
	@echo "  make format      Format Go and Python code"
	@echo "  make clean       Remove caches, build artifacts, and test DBs"

test: test-py test-go

test-py:
	python -m unittest discover tests -v

test-go:
	go test -v ./...

vet:
	go vet ./...

wasm:
	@mkdir -p public
	GOOS=js GOARCH=wasm go build -ldflags="-s -w" -o public/tinui_engine.wasm ./wasm_engine
	@echo "Successfully compiled WebAssembly Engine to public/tinui_engine.wasm"

wasm-tinygo:
	@mkdir -p public
	tinygo build -o public/tinui_engine.wasm -target=wasm -no-debug ./wasm_engine
	@echo "Successfully compiled TinyGo WebAssembly Engine to public/tinui_engine.wasm"

build:
	go build -o tinui .
	@echo "Successfully built TinUI CLI binary"

lint: vet
	@echo "Go static checks passed."

format:
	gofmt -s -w .

clean:
	rm -f tinui tinui.exe
	rm -f public/tinui_engine.wasm
	rm -f test.db test.db-journal *.ir.json public/*.ir.json
	rm -rf __pycache__ tests/__pycache__ database/__pycache__ backend/__pycache__
	rm -rf dist build *.egg-info
	@echo "Cleaned build artifacts and temporary files."
