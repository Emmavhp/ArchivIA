<#
Backup script: copia o comprime las carpetas `uploads` y `outputs` a la carpeta de Dropbox.

Uso:
  # Copiar carpetas con timestamp
  .\backup_to_dropbox.ps1

  # Comprimir en ZIP en la carpeta de Dropbox
  .\backup_to_dropbox.ps1 -Zip

  # Especificar ruta de Dropbox personalizada
  .\backup_to_dropbox.ps1 -DropboxPath "D:\Users\Usuario\Dropbox" -Zip

El script detecta la carpeta del repo (donde está el script) y busca `uploads` y `outputs` dentro.
#>

Param(
    [string[]]$SourcePaths = @("uploads", "outputs"),
    [string]$DropboxPath = "$env:USERPROFILE\Dropbox",
    [switch]$Zip
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")

#if Dropbox path doesn't exist, offer to create it
if (-not (Test-Path $DropboxPath)) {
    Write-Host "Dropbox path '$DropboxPath' not found." -ForegroundColor Yellow
    $answer = Read-Host "¿Crear la carpeta de destino en esa ruta? (y/n)"
    if ($answer -ne 'y') { Write-Host "Abortando."; exit 1 }
    New-Item -ItemType Directory -Path $DropboxPath | Out-Null
}

foreach ($rel in $SourcePaths) {
    $src = Join-Path $scriptDir $rel
    if (-not (Test-Path $src)) {
        Write-Host "Fuente no encontrada: $src — se omite." -ForegroundColor Yellow
        continue
    }

    if ($Zip) {
        $safeName = ($rel -replace '[\\/:*?"<>| ]','_').TrimEnd('_')
        $zipName = "${safeName}_${timestamp}.zip"
        $zipPath = Join-Path $DropboxPath $zipName
        Write-Host "Comprimiendo '$src' -> '$zipPath'..."
        Compress-Archive -Path (Join-Path $src '*') -DestinationPath $zipPath -Force
        Write-Host "Guardado: $zipPath"
    } else {
        $dest = Join-Path $DropboxPath ("${rel}_${timestamp}")
        Write-Host "Copiando '$src' -> '$dest'..."
        Copy-Item -Path $src -Destination $dest -Recurse -Force
        Write-Host "Copiado a: $dest"
    }
}

Write-Host "Backup completado." -ForegroundColor Green