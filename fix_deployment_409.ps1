# PowerShell script to fix Azure App Service 409 Conflict deployment error
param(
    [Parameter(Mandatory=$false)]
    [string]$AppServiceName = "month-end-automator",
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "month-end-automator-rg"
)

Write-Host "=== Fixing Azure Deployment 409 Conflict Error ===" -ForegroundColor Cyan
Write-Host ""

# Check Azure CLI
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "Azure CLI not found. Please install it first." -ForegroundColor Red
    exit 1
}

# Check login
Write-Host "Checking Azure login..." -ForegroundColor Yellow
try {
    $account = az account show 2>&1 | ConvertFrom-Json
    Write-Host "Logged in: $($account.name)" -ForegroundColor Green
} catch {
    Write-Host "Logging in..." -ForegroundColor Yellow
    az login
}
Write-Host ""

# Stop App Service
Write-Host "Step 1: Stopping App Service..." -ForegroundColor Yellow
az webapp stop --name $AppServiceName --resource-group $ResourceGroup 2>&1 | Out-Null
Start-Sleep -Seconds 5
Write-Host "Stopped" -ForegroundColor Green
Write-Host ""

# Restart App Service
Write-Host "Step 2: Restarting App Service..." -ForegroundColor Yellow
az webapp restart --name $AppServiceName --resource-group $ResourceGroup 2>&1 | Out-Null
Start-Sleep -Seconds 15
Write-Host "Restarted" -ForegroundColor Green
Write-Host ""

# Check status
Write-Host "Step 3: Checking status..." -ForegroundColor Yellow
$webapp = az webapp show --name $AppServiceName --resource-group $ResourceGroup 2>&1 | ConvertFrom-Json
Write-Host "State: $($webapp.state)" -ForegroundColor Cyan
Write-Host "Availability: $($webapp.availabilityState)" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== Fix Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Wait 30-60 seconds" -ForegroundColor White
Write-Host "2. Go to GitHub Actions and click 'Re-run jobs' on the failed workflow" -ForegroundColor White
Write-Host "3. Or push a new commit to trigger deployment" -ForegroundColor White
Write-Host ""
