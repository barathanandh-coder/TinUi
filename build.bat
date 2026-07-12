@echo off
echo [TinUI] Building CLI Compiler...
go build -o tinui.exe main.go

echo [TinUI] Compiling WebAssembly Engine...
set GOOS=js
set GOARCH=wasm
go build -o tinui_engine.wasm ./wasm_engine

echo [TinUI] Build Complete! You can now run:
echo .\tinui.exe compile task_manager.tin
