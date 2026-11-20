param(
  [Parameter(Mandatory=$true)][string[]]$DataPaths,
  [Parameter(Mandatory=$true)][string]$ManifestPath,
  [switch]$Verify
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
# Read-only snapshot/verification. No copy, remove, restore or installer execution.
if (-not $DataPaths -or $DataPaths.Count -eq 0) { throw 'Mindestens ein Datenpfad erforderlich.' }
$manifestFull=[IO.Path]::GetFullPath($ManifestPath)
$items=@()
$seen=@{}
foreach ($rawPath in $DataPaths) {
  if (-not (Test-Path -LiteralPath $rawPath)) { throw "Datenpfad fehlt: $rawPath" }
  $resolved=(Resolve-Path -LiteralPath $rawPath).Path
  if (-not (Test-Path -LiteralPath $resolved -PathType Container)) { throw "Kein Datenverzeichnis: $resolved" }
  $files=@(Get-ChildItem -LiteralPath $resolved -Recurse -File -Force -ErrorAction Stop)
  foreach ($file in $files) {
    if (($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse Point im Datenbestand: $($file.FullName)" }
    $full=$file.FullName
    if ([string]::Equals($full,$manifestFull,[StringComparison]::OrdinalIgnoreCase)) { throw 'Manifest darf nicht im Datenbestand liegen.' }
    if ($seen.ContainsKey($full)) { throw "Doppelt erfasste Datei: $full" }
    $seen[$full]=$true
    $items+= [ordered]@{ Path=$full; Length=[int64]$file.Length; SHA256=(Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash }
  }
}
$items=@($items | Sort-Object { $_.Path })
if ($Verify) {
  if (-not (Test-Path -LiteralPath $manifestFull -PathType Leaf)) { throw 'Vergleichsmanifest fehlt.' }
  $before=Get-Content -LiteralPath $manifestFull -Raw -Encoding UTF8 | ConvertFrom-Json
  if ($before.Schema -ne 1) { throw 'Unbekanntes Manifestformat.' }
  $old=@($before.Files)
  if ($old.Count -ne $items.Count) { throw "Dateianzahl veraendert: vorher $($old.Count), nachher $($items.Count)" }
  for($i=0;$i -lt $old.Count;$i++) {
    if ($old[$i].Path -cne $items[$i].Path -or [int64]$old[$i].Length -ne $items[$i].Length -or $old[$i].SHA256 -cne $items[$i].SHA256) {
      throw "Datei geaendert: $($items[$i].Path)"
    }
  }
  Write-Host "OK: $($items.Count) Dateien unveraendert."
} else {
  if (Test-Path -LiteralPath $manifestFull) { throw 'Manifest existiert bereits; kein Ueberschreiben.' }
  $parent=Split-Path -Parent $manifestFull
  if (-not (Test-Path -LiteralPath $parent -PathType Container)) { throw 'Manifest-Zielordner fehlt.' }
  $result=[ordered]@{ Schema=1; CreatedUtc=[DateTime]::UtcNow.ToString('o'); Files=$items }
  $result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestFull -Encoding UTF8 -NoNewline
  Write-Host "Baseline erstellt: $($items.Count) Dateien."
}
