# remove-zencoder-force.ps1 - Non-interactive
# Forcefully uninstall zencoder extension, remove global storage and settings entries

$ErrorActionPreference = 'Stop'

function Write-Status { param($m, $t = 'INFO'); $c = @{INFO = 'Cyan'; WARN = 'Yellow'; ERROR = 'Red'; SUCCESS = 'Green' }; Write-Host "[$t] $m" -ForegroundColor $c[$t] }

# Check if 'code' CLI is available
try { $n = code --version 2>$null; if ($LASTEXITCODE -ne 0) { throw } } catch { Write-Status "'code' CLI not available" 'ERROR'; exit 1 }

$extId = 'zencoderai.zencoder'
$installed = (code --list-extensions 2>$null) -contains $extId
if ($installed) {
  Write-Status "Uninstalling extension $extId" 'INFO'
  code --uninstall-extension $extId
  Write-Status "Uninstalled $extId" 'SUCCESS'
}
else {
  Write-Status "$extId not installed" 'INFO'
}

# Remove extension folder(s)
$extPattern = "$env:USERPROFILE\.vscode\extensions\$extId*"
$extDirs = Get-ChildItem "$env:USERPROFILE\.vscode\extensions" -Directory | Where-Object { $_.Name -like "$extId*" }
foreach ($d in $extDirs) {
  try { Remove-Item -Path $d.FullName -Recurse -Force; Write-Status "Removed extension folder: $($d.FullName)" 'SUCCESS' } catch { Write-Status "Failed to remove $($d.FullName): $_" 'WARN' }
}

# Remove global storage
$globalPath = "$env:APPDATA\Code\User\globalStorage\$extId"
if (Test-Path $globalPath) {
  try { Remove-Item -Path $globalPath -Recurse -Force; Write-Status "Removed ZenCoder global storage" 'SUCCESS' } catch { Write-Status "Failed to remove global storage: $_" 'WARN' }
}
else { Write-Status "No global storage path: $globalPath" 'INFO' }

# Backup and remove zencoder settings from settings.json
$settingsPath = "$env:APPDATA\Code\User\settings.json"
if (Test-Path $settingsPath) {
  $backup = "$settingsPath.bak.zencoder.$((Get-Date).ToString('yyyyMMdd_HHmmss'))"
  Copy-Item $settingsPath $backup -Force
  Write-Status "Backed up settings.json to $backup" 'INFO'
  $sj = Get-Content $settingsPath -Raw | ConvertFrom-Json
  $changed = $false

  $props = $sj | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
  foreach ($p in $props) {
    if ($p -like 'zencoder*') {
      $sj.PSObject.Properties.Remove($p)
      $changed = $true
      Write-Status "Removed settings key: $p" 'INFO'
    }
  }
  if ($changed) { $sj | ConvertTo-Json -Depth 20 | Set-Content $settingsPath -Force -Encoding UTF8; Write-Status "Saved settings.json (updated)" 'SUCCESS' }
  else { Write-Status "No zencoder settings keys found" 'INFO' }
}
else { Write-Status "settings.json not found at $settingsPath" 'WARN' }

Write-Status "ZenCoder removal complete. Reload VS Code to apply changes." 'SUCCESS'

