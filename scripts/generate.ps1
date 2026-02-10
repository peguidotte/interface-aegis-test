# Aegis Test Interfaces Generator - PowerShell Wrapper
# Windows-friendly script to run the Python generator

param()

try {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $pythonScript = Join-Path -Path $scriptDir -ChildPath "generate.py"
    
    Write-Host "Running Aegis Test Generator..." -ForegroundColor Cyan
    
    python3 $pythonScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Generation completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Generation failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}
catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}
