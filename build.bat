@echo off
echo [TinUI] Compiling WebAssembly Engine...
set GOOS=js
set GOARCH=wasm

if exist "dist_wasm\tin_wasm_engine_bg.wasm" if not "%1"=="--go-wasm" (
    echo [TinUI] Using ultra-compact Rust WebAssembly Core Engine ~213KB...
    copy dist_wasm\tin_wasm_engine_bg.wasm tinui_engine.wasm >nul
    copy dist_wasm\tin_wasm_engine.js tin_wasm_engine.js >nul
) else (
    where tinygo >nul 2>nul
    if "%1"=="--tinygo" (
        echo [TinUI] Building ultra-compact WebAssembly using TinyGo ~350KB...
        tinygo build -o tinui_engine.wasm -target=wasm -no-debug ./wasm_engine
    ) else (
        echo [TinUI] Building WebAssembly using standard Go toolchain...
        go build -ldflags="-s -w" -o tinui_engine.wasm ./wasm_engine
    )
)

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
    if not exist public mkdir public
    copy "%WASM_EXEC_PATH%" public\ >nul
    if not exist pypi_build\tinpyui mkdir pypi_build\tinpyui
    copy "%WASM_EXEC_PATH%" pypi_build\tinpyui\ >nul
)

copy tinui_engine.wasm static\ >nul
copy tinui_engine.wasm tinui-npm\bin\ >nul
if not exist public mkdir public
copy tinui_engine.wasm public\ >nul
if not exist pypi_build\tinpyui mkdir pypi_build\tinpyui
copy tinui_engine.wasm pypi_build\tinpyui\ >nul
copy tin-runtime.js pypi_build\tinpyui\ >nul
copy index.tin pypi_build\tinpyui\ >nul
if exist dist_wasm\tin_wasm_engine_bg.wasm (
    copy dist_wasm\tin_wasm_engine_bg.wasm tinpyui\ >nul
    copy dist_wasm\tin_wasm_engine_bg.wasm pypi_build\tinpyui\ >nul
    copy dist_wasm\tin_wasm_engine.js tinpyui\ >nul
    copy dist_wasm\tin_wasm_engine.js pypi_build\tinpyui\ >nul
    copy dist_wasm\tin_wasm_engine.js public\ >nul
)

echo [TinUI] Building Embedded CLI Compiler (Single Standalone Binary)...
set GOOS=windows
set GOARCH=amd64
go build -ldflags="-s -w" -o tinui.exe .
go build -ldflags="-s -w" -o tinui-npm/bin/tinui-win.exe .

echo [TinUI] Building Cross-Platform Embedded Binaries...
set GOOS=linux
go build -ldflags="-s -w" -o tinui-npm/bin/tinui-linux .

set GOOS=darwin
go build -ldflags="-s -w" -o tinui-npm/bin/tinui-macos .

echo [TinUI] Build Complete! Everything is embedded. You can now run:
echo • CLI: .\tinui.exe index.tin

