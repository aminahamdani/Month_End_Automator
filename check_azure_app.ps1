# PowerShell script to check Azure App Service
# This script checks if Azure CLI is installed and helps verify your App Service

Write-Host "Checking Azure CLI installation..." -ForegroundColor Yellow

# Check if Azure CLI is installed
$azCliInstalled = Get-Command az -ErrorAction SilentlyContinue

if (-not $azCliInstalled) {
    Write-Host "`nAzure CLI is not installed." -ForegroundColor Red
    Write-Host "`nPlease install Azure CLI first:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://aka.ms/installazurecliwindows" -ForegroundColor Cyan
    Write-Host "  2. Or run: winget install -e --id Microsoft.AzureCLI" -ForegroundColor Cyan
    Write-Host "`nAfter installation, restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Azure CLI is installed" -ForegroundColor Green

# Check if logged in
Write-Host "`nChecking Azure login status..." -ForegroundColor Yellow
$account = $null
try {
    $accountOutput = az account show 2>&1
    if ($LASTEXITCODE -eq 0) {
        $account = $accountOutput | ConvertFrom-Json
    }
} catch {
    # Ignore errors
}

if ($account) {
    Write-Host "✓ Already logged in" -ForegroundColor Green
    Write-Host "  Subscription: $($account.name)" -ForegroundColor Cyan
    Write-Host "  Subscription ID: $($account.id)" -ForegroundColor Cyan
} else {
    Write-Host "⚠ Not logged in. Please login..." -ForegroundColor Yellow
    Write-Host "`nRunning: az login" -ForegroundColor Cyan
    az login
    
    # Get account after login
    try {
        $account = az account show | ConvertFrom-Json
        if ($account) {
            Write-Host "`n✓ Login successful" -ForegroundColor Green
            Write-Host "  Subscription: $($account.name)" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "⚠ Login failed" -ForegroundColor Red
    }
}

# Select Azure for Students subscription if multiple subscriptions exist
Write-Host "`nChecking subscriptions..." -ForegroundColor Yellow
$subscriptions = az account list | ConvertFrom-Json

if ($subscriptions.Count -gt 1) {
    Write-Host "Multiple subscriptions found:" -ForegroundColor Yellow
    foreach ($sub in $subscriptions) {
        $marker = if ($sub.name -like "*Student*" -or $sub.name -like "*Student*") { " ← Students" } else { "" }
        Write-Host "  - $($sub.name)$marker" -ForegroundColor Cyan
    }
    
    # Find Azure for Students subscription
    $studentSub = $subscriptions | Where-Object { $_.name -like "*Student*" }
    if ($studentSub) {
        Write-Host "`nSetting subscription to: $($studentSub.name)" -ForegroundColor Yellow
        az account set --subscription $studentSub.id
        Write-Host "✓ Subscription set" -ForegroundColor Green
    }
}

# Check resource group
$resourceGroup = "month-end-automator-rg"
Write-Host "`nChecking resource group: $resourceGroup" -ForegroundColor Yellow

try {
    $rg = az group show --name $resourceGroup 2>$null | ConvertFrom-Json
    if ($rg) {
        Write-Host "✓ Resource group found" -ForegroundColor Green
        Write-Host "  Location: $($rg.location)" -ForegroundColor Cyan
    } else {
        Write-Host "⚠ Resource group not found: $resourceGroup" -ForegroundColor Yellow
        Write-Host "`nAvailable resource groups:" -ForegroundColor Yellow
        $allRGs = az group list | ConvertFrom-Json
        foreach ($rgItem in $allRGs) {
            Write-Host "  - $($rgItem.name)" -ForegroundColor Cyan
        }
    }
} catch {
    Write-Host "⚠ Error checking resource group" -ForegroundColor Red
}

# Check App Service
$appServiceName = "month-end-automator"
Write-Host "`nChecking App Service: $appServiceName" -ForegroundColor Yellow

try {
    $webapp = az webapp show --name $appServiceName --resource-group $resourceGroup 2>$null | ConvertFrom-Json
    if ($webapp) {
        Write-Host "✓ App Service found!" -ForegroundColor Green
        Write-Host "  Name: $($webapp.name)" -ForegroundColor Cyan
        Write-Host "  State: $($webapp.state)" -ForegroundColor Cyan
        Write-Host "  Location: $($webapp.location)" -ForegroundColor Cyan
        Write-Host "  URL: https://$($webapp.defaultHostName)" -ForegroundColor Cyan
        Write-Host "  Resource Group: $($webapp.resourceGroup)" -ForegroundColor Cyan
    } else {
        Write-Host "⚠ App Service not found: $appServiceName" -ForegroundColor Yellow
        Write-Host "`nAvailable App Services in ${resourceGroup}:" -ForegroundColor Yellow
        $webapps = az webapp list --resource-group $resourceGroup 2>$null | ConvertFrom-Json
        if ($webapps -and $webapps.Count -gt 0) {
            foreach ($app in $webapps) {
                Write-Host "  - $($app.name)" -ForegroundColor Cyan
            }
        } else {
            Write-Host "  (No App Services found in this resource group)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "⚠ Error checking App Service. Resource group might not exist." -ForegroundColor Yellow
}

Write-Host "`nDone!" -ForegroundColor Green
