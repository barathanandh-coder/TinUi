$ErrorActionPreference = "Stop"

$Platforms = @(
    @{ OS = "windows"; Arch = "amd64"; Ext = ".exe" },
    @{ OS = "linux"; Arch = "amd64"; Ext = "" },
    @{ OS = "darwin"; Arch = "amd64"; Ext = "" },
    @{ OS = "darwin"; Arch = "arm64"; Ext = "" }
)

$OutDir = "src\tinpyui\bin"
if (-not (Test-Path -Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

Write-Host "Compiling Go Native Executables for PyPI Distribution..." -ForegroundColor Cyan

foreach ($platform in $Platforms) {
    $os = $platform.OS
    $arch = $platform.Arch
    $ext = $platform.Ext
    
    $binName = "tinui-$os-$arch$ext"
    $binPath = Join-Path $OutDir $binName
    
    Write-Host "Building for $os/$arch -> $binPath"
    
    $env:GOOS = $os
    $env:GOARCH = $arch
    
    go build -o $binPath main.go
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to build for $os/$arch" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Done! The Python wheel will now package these native compilers." -ForegroundColor Green
