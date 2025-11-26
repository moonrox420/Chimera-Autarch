#!/usr/bin/env pwsh
try {
  python .\scripts\guard_source.py
  if ($LastExitCode -ne 0) {
    Write-Error "Pre-commit: source guard failed. Please fix the reported issues and try again."
    exit $LastExitCode
  }
}
catch {
  Write-Error $_.Exception.Message
  exit 1
}
exit 0
