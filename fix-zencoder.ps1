# Fix-ZenCoder: Diagnostic & Helper script for Zencoder in VS Code
# NOTE: This file has been archived; an identical copy lives in `scripts/legacy/` for historical reasons.
# Use the `scripts/legacy/fix-zencoder.ps1` copy when possible.
# Usage: .\fix-zencoder.ps1 [-DryRun] [-DisableConflicts] [-Reinstall] [-ClearCache] [-SignIn]

param(
    [switch]$DryRun,
    [switch]$DisableConflicts,
    [switch]$Reinstall,
    [switch]$ClearCache,
    [switch]$SignIn
)

$ErrorActionPreference = 'Stop'

function Write-Status { param($msg, $lvl='INFO'); $p = @{ INFO='Cyan'; WARN='Yellow'; ERROR='Red'; SUCCESS='Green'}; Write-Host "[$lvl] $msg" -ForegroundColor $p[$lvl] }

Write-Host "\nðŸ” Zencoder Diagnostic & Fix Script" -ForegroundColor Cyan
Write-Host "===================================\n" -ForegroundColor Cyan

# Ensure 'code' CLI available
try { $codeVersion = code --version 2>$null; if ($LASTEXITCODE -ne 0) { throw } } catch { Write-Status "'code' CLI not found. Install VS Code and add 'code' to PATH (Command Palette -> Shell Command: Install 'code' command)." 'ERROR'; exit 1 }
Write-Status "VS Code CLI detected" 'SUCCESS'

function Get-VSCodeExtension { param($id) $list = code --list-extensions 2>$null; return $list -contains $id }
function Get-ExtensionPath { param($id) $exts = Get-ChildItem "$env:USERPROFILE\.vscode\extensions" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "$id*" }; return $exts[0] }

# Step 1: Check installation
Write-Status "Step 1: Checking Zencoder extension installation..." 'INFO'
$installed = Get-VSCodeExtension 'zencoderai.zencoder'
if ($installed) { Write-Status "ZenCoder (zencoderai.zencoder) is installed" 'SUCCESS' } else { Write-Status "ZenCoder not installed" 'WARN' }

$path = Get-ExtensionPath 'zencoderai.zencoder'
if ($path) { Write-Status "Extension folder: $($path.FullName)" 'INFO' } else { Write-Status "Can't find extension folder" 'WARN' }

# Step 2: Check user settings for conflicts
$settingsPath = "$env:APPDATA\Code\User\settings.json"
if (-not (Test-Path $settingsPath)) { Write-Status "Settings.json not found at $settingsPath" 'ERROR'; exit 1 }
$settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
Write-Status "Loaded settings.json" 'SUCCESS'

$conflicts = @()
# Possible conflicts: GitHub Copilot, Continue, Tabnine, CopilotLabs etc.
if ($settings.'github.copilot.enable' -ne $null) { if (($settings.'github.copilot.enable' -is [hashtable] -and $settings.'github.copilot.enable'.'*' -eq $true) -or $settings.'github.copilot.enable' -eq $true) { $conflicts += 'GitHub Copilot' }}
if ($settings.'continue.enableTabAutocomplete' -eq $true) { $conflicts += 'Continue' }
if ($settings.'tabnine.experimentalAutoImports' -eq $true) { $conflicts += 'Tabnine (Experimental)' }
if ($conflicts.Count -gt 0) { Write-Status "Potential conflicts: $($conflicts -join ', ')" 'WARN' } else { Write-Status "No obvious conflicts detected" 'SUCCESS' }

# Step 3: Check sign-in state (globalStorage)
$zencoderStatePath = "$env:APPDATA\Code\User\globalStorage\zencoderai.zencoder"
if (Test-Path $zencoderStatePath) { $files = Get-ChildItem -Path $zencoderStatePath -File 2>$null; if ($files -and $files.Count -gt 0) { Write-Status "ZenCoder sign-in state data found" 'SUCCESS' } else { Write-Status "ZenCoder global state folder exists but no sign-in data found" 'WARN' } } else { Write-Status "No ZenCoder global state folder found" 'WARN' }

# Step 4: Verify available commands
$allExts = code --list-extensions 2>$null
$zCmds = code --list-extensions --show-versions 2>$null | Select-String 'zencoder' 2>$null
if ($zCmds) { Write-Status "Zencoder extension command listing found in 'code --list-extensions'" 'SUCCESS' } else { Write-Status "Zencoder extension not listed in code --list-extensions" 'WARN' }

# Provide recommendations
Write-Host "\nRecommendations:" -ForegroundColor Cyan
Write-Host "  â€¢ Reload VS Code: Ctrl+Shift+P -> 'Developer: Reload Window'" -ForegroundColor Gray
Write-Host "  â€¢ If command 'Zencoder: Sign In' missing -> Reinstall extension" -ForegroundColor Gray
Write-Host "  â€¢ If you want one AI agent, disable other AI extensions (Copilot/Continue/Tabnine) and keep ZenCoder on" -ForegroundColor Gray

# Offer to make changes if the user asked for auto-fix
if ($DryRun) { Write-Status "Dry run enabled - no changes will be made." 'INFO' }

# If user asked to disable conflicts
if ($DisableConflicts) {
    Write-Status "-- DisableConflicts flagged: preparing to update settings.json" 'INFO'
    # Ask for confirmation
    $confirm = Read-Host "This will update your User settings to disable known competing AI assistants. Continue? (y/n)"
    if ($confirm -ne 'y') { Write-Status "User declined to modify settings" 'INFO' } else {
        # Modify settings object
        # GitHub Copilot
        if ($settings.'github.copilot.enable' -ne $null -or $settings.'github.copilot.editor.enableAutoCompletions' -ne $null) {
            if (-not $DryRun) {
                $settings.'github.copilot.enable' = @{ "*" = $false }
                $settings.'github.copilot.editor.enableAutoCompletions' = $false
                $settings.'github.copilot.nextEditSuggestions.enabled' = $false
                Write-Status "GitHub Copilot disabled in settings" 'SUCCESS'
            } else { Write-Status "Would set GitHub Copilot to disabled in settings (dry run)" 'INFO' }
        }
        # Continue
        if ($settings.'continue.enableTabAutocomplete' -eq $true) {
            if (-not $DryRun) { $settings.'continue.enableTabAutocomplete' = $false; Write-Status "Continue tabu disabled" 'SUCCESS' } else { Write-Status "Would disable Continue (dry run)" 'INFO' }
        }
        # Tabnine
        if ($settings.'tabnine.experimentalAutoImports' -eq $true) { if (-not $DryRun) { $settings.'tabnine.experimentalAutoImports' = $false; Write-Status "Tabnine experimental features disabled" 'SUCCESS' } else { Write-Status "Would disable Tabnine experimental features (dry run)" 'INFO' } }

        if (-not $DryRun) {
            $settings | ConvertTo-Json -Depth 20 | Set-Content -Path $settingsPath -Force -Encoding UTF8
            Write-Status "Applied changes to settings.json" 'SUCCESS'
        }
    }
}

# If user asked to reinstall extension
if ($Reinstall) {
    Write-Status "-- Reinstall flagged: will try to uninstall then install Zencoder" 'INFO'
    $confirm = Read-Host "Reinstall Zencoder extension now? (y/n)"
    if ($confirm -ne 'y') { Write-Status "User canceled reinstallation" 'INFO' } else {
        if (-not $DryRun) {
            code --uninstall-extension zencoderai.zencoder
            Start-Sleep -Seconds 2
            code --install-extension zencoderai.zencoder
            Write-Status "ZenCoder reinstalled" 'SUCCESS'
        } else { Write-Status "Would uninstall and reinstall ZenCoder (dry run)" 'INFO' }
    }
}

# Clear cache
if ($ClearCache) {
    $confirm = Read-Host "This will delete the Zencoder globalStorage folder and remove caches. Continue? (y/n)"
    if ($confirm -ne 'y') { Write-Status "User canceled cache clearing" 'INFO' } else {
        if (Test-Path $zencoderStatePath) {
            if (-not $DryRun) { Remove-Item -Path $zencoderStatePath -Recurse -Force; Write-Status "Zencoder globalStorage removed" 'SUCCESS' } else { Write-Status "Would remove Zencoder globalStorage (dry run)" 'INFO' }
        } else { Write-Status "No Zencoder globalStorage folder found" 'WARN' }
    }
}

# Sign-in
if ($SignIn) {
    Write-Status "Opening sign-in page for Zencoder in default browser" 'INFO'
    Start-Process "https://zencoder.ai/login"
}

Write-Host "\nDiagnostics complete. If you need me to apply fixes run this script with -DisableConflicts or -Reinstall (without -DryRun)." -ForegroundColor Cyan

