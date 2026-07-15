@echo off
echo [TinUI] Building CLI Compiler for local testing...
go build -o tinui.exe main.go

echo [TinUI] Building NPM CLI Binaries...
set GOOS=linux
set GOARCH=amd64
go build -o tinui-npm/bin/tinui-linux main.go

set GOOS=darwin
set GOARCH=amd64
go build -o tinui-npm/bin/tinui-macos main.go

set GOOS=windows
set GOARCH=amd64
go build -o tinui-npm/bin/tinui-win.exe main.go

echo [TinUI] Compiling WebAssembly Engine...
set GOOS=js
set GOARCH=wasm
go build -o tinui_engine.wasm ./wasm_engine

echo [TinUI] Copying WebAssembly assets...
for /f "delims=" %%i in ('go env GOROOT') do set "GOROOT=%%i"
copy "%GOROOT%\misc\wasm\wasm_exec.js" . >nul
if not exist static mkdir static
copy "%GOROOT%\misc\wasm\wasm_exec.js" static\ >nul
copy tinui_engine.wasm static\ >nul

echo [TinUI] Build Complete! You can now run:
echo .\tinui.exe compile task_manager.tin
