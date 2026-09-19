$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = 'python'
$backupScript = Join-Path $scriptDir 'backup_db.py'

if (-not (Test-Path $backupScript)) {
    Write-Error "Backup script not found: $backupScript"
    exit 1
}

$logFile = Join-Path $scriptDir '..', '..', 'backups', 'backup.log'

try {
    & $python $backupScript *>> $logFile
    Write-Host "Backup completed."
} catch {
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "[$timestamp] ERROR: $_" | Out-File -FilePath $logFile -Append
    exit 1
}
