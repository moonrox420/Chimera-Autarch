#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Diagnose ZenCoder extension issues
    
  NOTE: This file has been archived and a copy is present in `scripts/legacy/diagnose-zencoder.ps1`.
  The root-level copy is kept for backwards compatibility, but prefer using `scripts/legacy` scripts.
#>

Write-Host ""
Write-Host "ðŸ” ZenCoder Diagnostic Tool" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Check VS Code
$VSCodeVersion = code --version 2>$null
if ($LASTEXITCODE -eq 0) {
  Write-Host "âœ… VS Code: $(($VSCodeVersion -split '\n')[0])" -ForegroundColor Green
}
else {
  Write-Host "âŒ VS Code not found in PATH" -ForegroundColor Red
  exit 1
}

Write-Host ""

# Check installed extensions
Write-Host "ðŸ“¦ Checking Extensions..." -ForegroundColor Yellow
$Extensions = code --list-extensions 2>$null

if ($Extensions -match "zencoderai.zencoder") {
  Write-Host "âœ… ZenCoder is installed" -ForegroundColor Green
    
  # Get extension info
  $ExtInfo = code --show-versions --list-extensions 2>$null | Select-String "zencoderai.zencoder"
  if ($ExtInfo) {
    Write-Host "   Version: $ExtInfo" -ForegroundColor Cyan
  }
}
else {
  Write-Host "âŒ ZenCoder NOT installed" -ForegroundColor Red
  Write-Host ""
  Write-Host "To install:" -ForegroundColor Yellow
  Write-Host "  code --install-extension zencoderai.zencoder" -ForegroundColor White
  exit 1
}

Write-Host ""

# Check extension directory
$ExtDir = "$env:USERPROFILE\.vscode\extensions"
if (Test-Path $ExtDir) {
  $ZencoderDirs = Get-ChildItem $ExtDir -Directory | Where-Object { $_.Name -like "*zencoder*" }
    
  if ($ZencoderDirs) {
    Write-Host "âœ… Extension files found:" -ForegroundColor Green
    foreach ($Dir in $ZencoderDirs) {
      Write-Host "   $($Dir.Name)" -ForegroundColor Cyan
    }
  }
  else {
    Write-Host "âš ï¸  No extension files found (may need reinstall)" -ForegroundColor Yellow
  }
}
else {
  Write-Host "âš ï¸  Extensions directory not found" -ForegroundColor Yellow
}

Write-Host ""

# Check for common issues
Write-Host "ðŸ” Common Issues Check:" -ForegroundColor Yellow
Write-Host ""

# Check internet connection
try {
  $null = Test-Connection -ComputerName api.zencoder.ai -Count 1 -ErrorAction Stop
  Write-Host "âœ… Internet connection OK" -ForegroundColor Green
}
catch {
  Write-Host "âŒ Cannot reach ZenCoder API" -ForegroundColor Red
  Write-Host "   Check firewall/proxy settings" -ForegroundColor Yellow
}

# Check VS Code settings
$SettingsPath = "$env:APPDATA\Code\User\settings.json"
if (Test-Path $SettingsPath) {
  Write-Host "âœ… VS Code settings found" -ForegroundColor Green
    
  $Settings = Get-Content $SettingsPath -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
  if ($Settings) {
    # Check for ZenCoder settings
    $ZencoderSettings = $Settings | Get-Member -MemberType NoteProperty | Where-Object { $_.Name -like "*zencoder*" }
    if ($ZencoderSettings) {
      Write-Host "   ZenCoder settings configured" -ForegroundColor Cyan
    }
  }
}

Write-Host ""
Write-Host "ðŸ“‹ Troubleshooting Steps:" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Reload VS Code Window:" -ForegroundColor White
Write-Host "   Ctrl+Shift+P â†’ 'Developer: Reload Window'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Sign in to ZenCoder:" -ForegroundColor White
Write-Host "   Ctrl+Shift+P â†’ 'Zencoder: Sign In'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Check Output Panel:" -ForegroundColor White
Write-Host "   View â†’ Output â†’ Select 'Zencoder' from dropdown" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Reinstall Extension:" -ForegroundColor White
Write-Host "   Extensions â†’ Zencoder â†’ Uninstall â†’ Reinstall" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Contact Support:" -ForegroundColor White
Write-Host "   https://zencoder.ai/support" -ForegroundColor Gray
Write-Host ""

