param(
  [Parameter(Mandatory=$true)][string]$InstallerPath,
  [string]$InstallDirectory = "$env:LOCALAPPDATA\Programs\Music Production Workstation",
  [switch]$RunInstall,
  [switch]$RunUninstall
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
function Assert-File([string]$Path, [string]$Label) {
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "$Label fehlt: $Path" }
  if ((Get-Item -LiteralPath $Path).Length -le 0) { throw "$Label ist leer: $Path" }
}
Assert-File $InstallerPath 'Installer'
$installer = (Resolve-Path -LiteralPath $InstallerPath).Path
$exe = Join-Path $InstallDirectory 'MPW.exe'
$report = [ordered]@{
  Installer = $installer
  SHA256 = (Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash
  InstallDirectory = $InstallDirectory
  InstallExecuted = $false
  ExecutableSelfTest = 'not_run'
  UninstallExecuted = $false
  DataRetention = 'manual_check_required'
}
if ($RunUninstall -and -not $RunInstall) { throw 'RunUninstall erfordert RunInstall.' }
if ($RunInstall) {
  if (Test-Path -LiteralPath $InstallDirectory) {
    throw 'Installationsziel existiert bereits. Zur Sicherheit kein automatischer Installationsversuch.'
  }
  $proc = Start-Process -FilePath $installer -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',"/DIR=$InstallDirectory") -Wait -PassThru
  if ($proc.ExitCode -ne 0) { throw "Installer fehlgeschlagen: $($proc.ExitCode)" }
  $report.InstallExecuted = $true
  Assert-File $exe 'Installierte MPW.exe'
  & $exe --self-test
  if ($LASTEXITCODE -ne 0) { throw "EXE-Selbsttest fehlgeschlagen: $LASTEXITCODE" }
  $report.ExecutableSelfTest = 'passed'
  if ($RunUninstall) {
    $uninstaller = Join-Path $InstallDirectory 'unins000.exe'
    Assert-File $uninstaller 'Uninstaller'
    $unproc = Start-Process -FilePath $uninstaller -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -Wait -PassThru
    if ($unproc.ExitCode -ne 0) { throw "Uninstaller fehlgeschlagen: $($unproc.ExitCode)" }
    $report.UninstallExecuted = $true
    if (Test-Path -LiteralPath $exe) { throw 'MPW.exe nach Deinstallation noch vorhanden.' }
  }
}
$report | ConvertTo-Json -Depth 3
Write-Warning 'GUI-Sprachwechsel, Upgrade mit bestehenden Daten und Benutzerdaten-Erhalt muessen unter Windows manuell geprueft werden.'
