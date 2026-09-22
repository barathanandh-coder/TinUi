@echo off
setlocal enabledelayedexpansion

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="test" goto test
if "%1"=="test-py" goto test_py
if "%1"=="test-go" goto test_go
if "%1"=="vet" goto vet
if "%1"=="wasm" goto wasm
if "%1"=="build" goto build
if "%1"=="clean" goto clean

echo [!] Unknown command: %1
goto help

:help
echo ==============================================================================
echo   TinPyUI Windows Developer Helper Script (dev.bat)
echo ==============================================================================
echo   dev.bat test         Run all Python and Go test suites
echo   dev.bat test-py      Run Python unittest suite
echo   dev.bat test-go      Run Go compiler and engine test suite
echo   dev.bat vet          Run Go static analysis (go vet ./...)
echo   dev.bat wasm         Compile wasm_engine to WebAssembly binary
echo   dev.bat build        Build local tinui.exe binary
echo   dev.bat clean        Remove temporary test databases and caches
echo ==============================================================================
exit /b 0

:test
echo [*] Running Python unit tests...
python -m unittest discover tests -v
if %errorlevel% neq 0 exit /b %errorlevel%

echo [*] Running Go tests...
go test -v ./...
if %errorlevel% neq 0 exit /b %errorlevel%
echo [+] All tests passed successfully!
exit /b 0

:test_py
echo [*] Running Python unit tests...
python -m unittest discover tests -v
exit /b %errorlevel%

:test_go
echo [*] Running Go test suite...
go test -v ./...
exit /b %errorlevel%

:vet
echo [*] Running Go static analyzer...
go vet ./...
if %errorlevel% equ 0 (
    echo [+] Go vet passed with 0 warnings!
)
exit /b %errorlevel%

:wasm
echo [*] Compiling WebAssembly Engine...
if not exist "public" mkdir public
set GOOS=js
set GOARCH=wasm
go build -ldflags="-s -w" -o public/tinui_engine.wasm ./wasm_engine
if %errorlevel% equ 0 (
    echo [+] Successfully generated public\tinui_engine.wasm
)
exit /b %errorlevel%

:build
echo [*] Compiling TinUI CLI binary...
go build -o tinui.exe .
if %errorlevel% equ 0 (
    echo [+] Successfully generated tinui.exe
)
exit /b %errorlevel%

:clean
echo [*] Cleaning temporary files and caches...
if exist "test.db" del /f /q test.db
if exist "test.db-journal" del /f /q test.db-journal
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo [+] Clean completed.
exit /b 0
