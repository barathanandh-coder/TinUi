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

set "WASM_EXEC_PATH="
if exist "%GOROOT%\lib\wasm\wasm_exec.js" (
    set "WASM_EXEC_PATH=%GOROOT%\lib\wasm\wasm_exec.js"
) else if exist "%GOROOT%\misc\wasm\wasm_exec.js" (
    set "WASM_EXEC_PATH=%GOROOT%\misc\wasm\wasm_exec.js"
)

if not "%WASM_EXEC_PATH%"=="" (
    copy "%WASM_EXEC_PATH%" . >nul
    if not exist static mkdir static
    copy "%WASM_EXEC_PATH%" static\ >nul
    if not exist tinui-npm\bin mkdir tinui-npm\bin
    copy "%WASM_EXEC_PATH%" tinui-npm\bin\ >nul
) else (
    echo [ERROR] Could not find wasm_exec.js in GOROOT
)

copy tinui_engine.wasm static\ >nul
copy tinui_engine.wasm tinui-npm\bin\ >nul


echo [TinUI] Build Complete! You can now run:
echo .\tinui.exe compile task_manager.tin
