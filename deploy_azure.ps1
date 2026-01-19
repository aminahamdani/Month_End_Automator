# PowerShell script to deploy Month-End Automator to Azure App Service
# Deploys month_end_automator_deploy.zip to Azure App Service

param(
    [Parameter(Mandatory=$false)]
    [string]$ZipFile = "month_end_automator_deploy.zip",
    
    [Parameter(Mandatory=$false)]
    [string]$AppServiceName = "month-end-automator",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "month-end-automator-rg"
)

Write-Host "=== Azure App Service Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
Write-Host "Checking Azure CLI..." -ForegroundColor Yellow
$azCliInstalled = Get-Command az -ErrorAction SilentlyContinue

if (-not $azCliInstalled) {
    Write-Host "✗ Azure CLI is not installed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Azure CLI first:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://aka.ms/installazurecliwindows" -ForegroundColor Cyan
    Write-Host "  2. Or run: winget install -e --id Microsoft.AzureCLI" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After installation, restart PowerShell and run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Azure CLI is installed" -ForegroundColor Green
Write-Host ""

# Check if ZIP file exists
Write-Host "Checking ZIP file: $ZipFile" -ForegroundColor Yellow
if (-not (Test-Path $ZipFile)) {
    Write-Host "✗ ZIP file not found: $ZipFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create the ZIP file first using create_deploy_zip.ps1" -ForegroundColor Yellow
    Write-Host "Or manually zip the required files." -ForegroundColor Yellow
    exit 1
}

$zipInfo = Get-Item $ZipFile
$sizeMB = [math]::Round($zipInfo.Length / 1MB, 2)
Write-Host "✓ ZIP file found: $($zipInfo.Name)" -ForegroundColor Green
Write-Host "  Size: $sizeMB MB" -ForegroundColor Cyan
Write-Host ""

# Check Azure login
Write-Host "Checking Azure login..." -ForegroundColor Yellow
try {
    $account = az account show 2>&1 | ConvertFrom-Json
    if ($account) {
        Write-Host "✓ Logged in to Azure" -ForegroundColor Green
        Write-Host "  Subscription: $($account.name)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠ Not logged in. Please login..." -ForegroundColor Yellow
    Write-Host "Running: az login" -ForegroundColor Cyan
    az login
    $account = az account show 2>&1 | ConvertFrom-Json
    if ($account) {
        Write-Host "✓ Login successful" -ForegroundColor Green
    } else {
        Write-Host "✗ Login failed" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Check resource group
Write-Host "Checking resource group: $ResourceGroup" -ForegroundColor Yellow
try {
    $rg = az group show --name $ResourceGroup 2>&1 | ConvertFrom-Json
    if ($rg) {
        Write-Host "✓ Resource group found" -ForegroundColor Green
    } else {
        Write-Host "✗ Resource group not found: $ResourceGroup" -ForegroundColor Red
        Write-Host "  Please create the resource group first or check the name." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "✗ Error checking resource group: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check App Service
Write-Host "Checking App Service: $AppServiceName" -ForegroundColor Yellow
try {
    $webapp = az webapp show --name $AppServiceName --resource-group $ResourceGroup 2>&1 | ConvertFrom-Json
    if ($webapp) {
        Write-Host "✓ App Service found" -ForegroundColor Green
        Write-Host "  Current state: $($webapp.state)" -ForegroundColor Cyan
    } else {
        Write-Host "✗ App Service not found: $AppServiceName" -ForegroundColor Red
        Write-Host "  Please create the App Service first in Azure Portal." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "✗ Error checking App Service: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Deploy ZIP file
Write-Host "Deploying ZIP file to App Service..." -ForegroundColor Yellow
Write-Host "  App Service: $AppServiceName" -ForegroundColor Cyan
Write-Host "  Resource Group: $ResourceGroup" -ForegroundColor Cyan
Write-Host "  ZIP File: $ZipFile" -ForegroundColor Cyan
Write-Host ""

try {
    Write-Host "Running: az webapp deployment source config-zip ..." -ForegroundColor Cyan
    $deployOutput = az webapp deployment source config-zip `
        --resource-group $ResourceGroup `
        --name $AppServiceName `
        --src $ZipFile `
        2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Deployment successful!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "✗ Deployment failed" -ForegroundColor Red
        Write-Host "Error: $deployOutput" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "✗ Deployment error: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Get App Service URL
Write-Host "Getting App Service URL..." -ForegroundColor Yellow
try {
    $webapp = az webapp show --name $AppServiceName --resource-group $ResourceGroup | ConvertFrom-Json
    if ($webapp.defaultHostName) {
        $appUrl = "https://$($webapp.defaultHostName)"
        Write-Host ""
        Write-Host "=== Deployment Complete ===" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your app is live at:" -ForegroundColor Cyan
        Write-Host "  $appUrl" -ForegroundColor White -BackgroundColor DarkGreen
        Write-Host ""
        Write-Host "Login credentials:" -ForegroundColor Yellow
        Write-Host "  Username: amina" -ForegroundColor Cyan
        Write-Host "  Password: amina0000" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host "⚠ Could not retrieve App Service URL" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Error retrieving App Service URL: $_" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can find your App Service URL in Azure Portal:" -ForegroundColor Cyan
    Write-Host "  https://portal.azure.com" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
