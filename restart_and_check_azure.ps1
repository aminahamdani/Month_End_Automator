# PowerShell script to restart Azure App Service and check health status

param(
    [Parameter(Mandatory=$false)]
    [string]$AppServiceName = "month-end-automator",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "month-end-automator-rg",
    
    [Parameter(Mandatory=$false)]
    [string]$AppUrl = "https://month-end-automator.azurewebsites.net"
)

Write-Host "=== Azure App Service Restart and Health Check ===" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
$azCliInstalled = Get-Command az -ErrorAction SilentlyContinue

if (-not $azCliInstalled) {
    Write-Host "Azure CLI is not installed." -ForegroundColor Red
    Write-Host "Please install Azure CLI first: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    exit 1
}

Write-Host "Azure CLI is installed" -ForegroundColor Green
Write-Host ""

# Check Azure login
Write-Host "Checking Azure login..." -ForegroundColor Yellow
try {
    $account = az account show 2>&1 | ConvertFrom-Json
    if ($account) {
        Write-Host "Logged in to Azure" -ForegroundColor Green
        Write-Host "  Subscription: $($account.name)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "Not logged in. Please login..." -ForegroundColor Yellow
    az login
}
Write-Host ""

# Get App Service details before restart
Write-Host "Getting App Service details..." -ForegroundColor Yellow
try {
    $webapp = az webapp show --name $AppServiceName --resource-group $ResourceGroup 2>&1 | ConvertFrom-Json
    
    if ($webapp) {
        Write-Host "App Service found" -ForegroundColor Green
        Write-Host "  Name: $($webapp.name)" -ForegroundColor Cyan
        Write-Host "  State: $($webapp.state)" -ForegroundColor Cyan
        Write-Host "  Location: $($webapp.location)" -ForegroundColor Cyan
        
        $actualUrl = if ($webapp.defaultHostName) { "https://$($webapp.defaultHostName)" } else { $AppUrl }
        Write-Host "  URL: $actualUrl" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host "App Service not found: $AppServiceName" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error getting App Service: $_" -ForegroundColor Red
    exit 1
}

# Restart App Service
Write-Host "Restarting App Service..." -ForegroundColor Yellow
Write-Host "  This may take a few moments..." -ForegroundColor Cyan
Write-Host ""

try {
    az webapp restart --name $AppServiceName --resource-group $ResourceGroup 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Restart command sent successfully" -ForegroundColor Green
    } else {
        Write-Host "Error restarting App Service" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error restarting: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Waiting for restart to complete (10 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host ""

# Check App Service status
Write-Host "Checking App Service status..." -ForegroundColor Yellow
try {
    $webapp = az webapp show --name $AppServiceName --resource-group $ResourceGroup 2>&1 | ConvertFrom-Json
    
    if ($webapp) {
        Write-Host "Current Status:" -ForegroundColor Green
        Write-Host "  State: $($webapp.state)" -ForegroundColor Cyan
        Write-Host "  Availability State: $($webapp.availabilityState)" -ForegroundColor Cyan
        Write-Host "  Usage State: $($webapp.usageState)" -ForegroundColor Cyan
        Write-Host ""
    }
} catch {
    Write-Host "Could not retrieve status: $_" -ForegroundColor Yellow
}

# Check health endpoint
$actualUrl = if ($webapp.defaultHostName) { "https://$($webapp.defaultHostName)" } else { $AppUrl }
Write-Host "Checking app health at: $actualUrl" -ForegroundColor Yellow
Write-Host ""

try {
    # Try to check the health endpoint (if available) or root URL
    $response = Invoke-WebRequest -Uri $actualUrl -Method Get -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
    
    Write-Host "App Health Check:" -ForegroundColor Green
    Write-Host "  Status Code: $($response.StatusCode)" -ForegroundColor Cyan
    Write-Host "  Status Description: $($response.StatusDescription)" -ForegroundColor Cyan
    Write-Host ""
    
    if ($response.StatusCode -eq 200) {
        Write-Host "App is LIVE and responding!" -ForegroundColor Green
    } elseif ($response.StatusCode -eq 302 -or $response.StatusCode -eq 301) {
        Write-Host "App is LIVE (redirecting to login)" -ForegroundColor Green
    } else {
        Write-Host "App responded with status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "Could not reach app: $errorMsg" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "This might be normal if the app is still starting up." -ForegroundColor Yellow
    Write-Host "Wait a few more seconds and try accessing: $actualUrl" -ForegroundColor Cyan
}

Write-Host ""

# Show App Service logs (recent)
Write-Host "Checking recent logs..." -ForegroundColor Yellow
try {
    $logs = az webapp log tail --name $AppServiceName --resource-group $ResourceGroup 2>&1 --timeout 5
    if ($logs) {
        Write-Host "Recent log entries (last 5 seconds):" -ForegroundColor Cyan
        # Logs might be empty or still streaming
    }
} catch {
    # Ignore log errors
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "App Service: $AppServiceName" -ForegroundColor White
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host "App URL: $actualUrl" -ForegroundColor White -BackgroundColor DarkGreen
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Visit the URL above to test your app" -ForegroundColor Cyan
Write-Host "  2. Login with: amina / amina0000" -ForegroundColor Cyan
Write-Host "  3. Check logs: az webapp log tail --name $AppServiceName --resource-group $ResourceGroup" -ForegroundColor Cyan
Write-Host ""

Write-Host "Done!" -ForegroundColor Green
