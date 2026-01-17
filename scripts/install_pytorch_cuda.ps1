# PowerShell script to install PyTorch with CUDA support
# Run this script when you have stable internet connection

$ErrorActionPreference = "Stop"

Write-Host "Installing PyTorch with CUDA 12.6 support..." -ForegroundColor Cyan

# Activate venv
$venvPath = Join-Path $PSScriptRoot "..\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    . $venvPath
    Write-Host "Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    py -3.11 -m venv ..\venv
    . $venvPath
}

# Uninstall existing torch if present
Write-Host "Removing existing PyTorch installation..." -ForegroundColor Yellow
pip uninstall torch torchvision torchaudio -y 2>$null

# Clear pip cache
pip cache purge

# Install PyTorch with CUDA
Write-Host "Installing PyTorch with CUDA 12.6..." -ForegroundColor Cyan
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Cyan
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}')"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nPyTorch with CUDA installed successfully!" -ForegroundColor Green
} else {
    Write-Host "`nInstallation failed. Try using a VPN or download wheels manually." -ForegroundColor Red
}
