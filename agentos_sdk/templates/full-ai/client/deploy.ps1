$GhcrUser = (Read-Host "GHCR Username").ToLower()
$GhcrPat  = Read-Host "GHCR PAT"

# Login securely via stdin
$GhcrPat | docker login ghcr.io -u $GhcrUser --password-stdin
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker login failed."
    exit 1
}


# Create network if missing
docker network create agentos-net 2>$null

# Pull with retry
$maxRetries = 3
$retryCount = 0
$success = $false

while (-not $success -and $retryCount -lt $maxRetries) {
    docker compose -f docker-compose.prod.yml pull
    if ($LASTEXITCODE -eq 0) {
        $success = $true
    } else {
        $retryCount++
        Write-Host "Pull failed (attempt $retryCount of $maxRetries). Retrying in 5 seconds..."
        Start-Sleep -Seconds 5
    }
}

if (-not $success) {
    Write-Error "Docker compose pull failed after $maxRetries attempts."
    exit 1
}

# Down and clean up orphans to prevent dirty recreation states
docker compose -f docker-compose.prod.yml down --remove-orphans
# Start backend (which starts db via depends_on) and migrate single-writer
docker compose -f docker-compose.prod.yml up -d backend
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate --noinput
# Start remaining services (worker, beat, connector, frontend, watchtower)
docker compose -f docker-compose.prod.yml up -d

# Write to .env securely if not present, replacing if they are empty
$envFile = ".env"
if (-not (Test-Path $envFile)) {
    New-Item -Path $envFile -ItemType File | Out-Null
}

$envContent = Get-Content $envFile -Raw
if ($envContent -notmatch "GHCR_USER=") {
    Add-Content $envFile "`nGHCR_USER=$ghcrUser"
} else {
    (Get-Content $envFile) -replace "^GHCR_USER=.*", "GHCR_USER=$ghcrUser" | Set-Content $envFile
}

if ($envContent -notmatch "GHCR_PAT=") {
    Add-Content $envFile "`nGHCR_PAT=$ghcrPat"
} else {
    (Get-Content $envFile) -replace "^GHCR_PAT=.*", "GHCR_PAT=$ghcrPat" | Set-Content $envFile
}

Write-Host "Deployment completed."
