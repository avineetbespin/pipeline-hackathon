# PowerShell script to store Fivetran credentials in Secret Manager
# Usage: .\scripts\store_secrets.ps1

$env:CLOUDSDK_PYTHON = "C:\Python313\python.exe"

Write-Host "========================================"
Write-Host "Fivetran Secret Manager Setup"
Write-Host "========================================"
Write-Host ""

# Get credentials
$API_KEY = Read-Host "Enter Fivetran API Key"
$API_SECRET = Read-Host "Enter Fivetran API Secret"

if ([string]::IsNullOrWhiteSpace($API_KEY) -or [string]::IsNullOrWhiteSpace($API_SECRET)) {
    Write-Host "Error: Both API Key and Secret are required!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "API Key length: $($API_KEY.Length) characters"
Write-Host "API Secret length: $($API_SECRET.Length) characters"
Write-Host ""

# Create temporary files (no newlines)
$tempKeyFile = [System.IO.Path]::GetTempFileName()
$tempSecretFile = [System.IO.Path]::GetTempFileName()

try {
    # Write without newlines and without BOM
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($tempKeyFile, $API_KEY, $utf8NoBom)
    [System.IO.File]::WriteAllText($tempSecretFile, $API_SECRET, $utf8NoBom)

    Write-Host "Storing credentials in Secret Manager..."

    # Store API Key
    & gcloud secrets create fivetran-api-key --data-file=$tempKeyFile --replication-policy=automatic --project=bgus-genai-poc2
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Stored fivetran-api-key" -ForegroundColor Green
    } else {
        throw "Failed to store fivetran-api-key"
    }

    # Store API Secret
    & gcloud secrets create fivetran-api-secret --data-file=$tempSecretFile --replication-policy=automatic --project=bgus-genai-poc2
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Stored fivetran-api-secret" -ForegroundColor Green
    } else {
        throw "Failed to store fivetran-api-secret"
    }

    Write-Host ""
    Write-Host "========================================"
    Write-Host "✓ Secrets stored successfully!" -ForegroundColor Green
    Write-Host "========================================"

} finally {
    # Clean up temp files
    Remove-Item $tempKeyFile -ErrorAction SilentlyContinue
    Remove-Item $tempSecretFile -ErrorAction SilentlyContinue
}
