<#
Restore script: busca los ZIPs creados por `backup_to_dropbox.ps1` en la carpeta de Dropbox
y los extrae en la raíz del proyecto restaurando `uploads/` y `outputs/`.

Uso:
  # Extraer todos los ZIPs encontrados
  .\restore_from_dropbox.ps1

  # Extraer sólo los ZIPs más recientes (por tipo)
  .\restore_from_dropbox.ps1 -Latest

  # Especificar ruta de Dropbox personalizada
  .\restore_from_dropbox.ps1 -DropboxPath "D:\Users\Usuario\Dropbox"
#>

Param(
    [string]$DropboxPath = "$env:USERPROFILE\Dropbox",
    [switch]$Latest
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

if (-not (Test-Path $DropboxPath)) {
    Write-Host "Dropbox path '$DropboxPath' no encontrado." -ForegroundColor Yellow
    $answer = Read-Host "¿Ruta alternativa? (enter para abortar / escribe ruta)"
    if ([string]::IsNullOrWhiteSpace($answer)) { Write-Host "Abortando."; exit 1 }
    $DropboxPath = $answer
    if (-not (Test-Path $DropboxPath)) { Write-Host "Ruta no válida. Abortando."; exit 1 }
}

Write-Host "Buscando ZIPs en: $DropboxPath" -ForegroundColor Cyan

$patterns = @('*uploads*.zip','*outputs*.zip')
$found = @()
foreach ($p in $patterns) { $found += Get-ChildItem -Path $DropboxPath -Filter $p -File -ErrorAction SilentlyContinue }

if ($found.Count -eq 0) { Write-Host "No se encontraron ZIPs de backup en la ruta indicada." -ForegroundColor Yellow; exit 0 }

if ($Latest) {
    # Agrupar por tipo (uploads/outputs) y escoger el más reciente
    $grouped = $found | Group-Object { if ($_.Name -match 'uploads') { 'uploads' } else { 'outputs' } }
    $toExtract = @()
    foreach ($g in $grouped) {
        $latest = $g.Group | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        $toExtract += $latest
    }
} else {
    $toExtract = $found | Sort-Object LastWriteTime
}

foreach ($zip in $toExtract) {
    if ($zip.Name -match 'uploads') { $dest = Join-Path $projectRoot 'uploads' }
    else { $dest = Join-Path $projectRoot 'outputs' }

    if (-not (Test-Path $dest)) { New-Item -ItemType Directory -Path $dest | Out-Null }

    Write-Host "Extrayendo '$($zip.Name)' -> '$dest'..." -ForegroundColor Green
    try {
        Expand-Archive -Path $zip.FullName -DestinationPath $dest -Force
        Write-Host "Extraído: $($zip.Name)" -ForegroundColor Green
    } catch {
        Write-Host "Error extrayendo $($zip.FullName): $_" -ForegroundColor Red
    }
}

Write-Host "Restauración completada." -ForegroundColor Cyan
