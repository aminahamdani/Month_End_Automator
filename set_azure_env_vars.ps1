# PowerShell script to set environment variables (app settings) in Azure App Service

param(
    [Parameter(Mandatory=$false)]
    [string]$AppServiceName = "month-end-automator",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "month-end-automator-rg"
)

Write-Host "=== Setting Azure App Service Environment Variables ===" -ForegroundColor Cyan
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

# Define environment variables to set
# Note: These are example values - update with your actual values
$envVars = @{
    "DB_URL" = "your_database_url_here"
    "SECRET_KEY" = "your_secret_key_here"
    "EMAIL_SENDER" = "noreply@example.com"
}

Write-Host "Setting environment variables..." -ForegroundColor Yellow
Write-Host "  App Service: $AppServiceName" -ForegroundColor Cyan
Write-Host "  Resource Group: $ResourceGroup" -ForegroundColor Cyan
Write-Host ""

# Build settings string for az command
$settingsList = @()
foreach ($key in $envVars.Keys) {
    $value = $envVars[$key]
    $settingsList += "$key=$value"
}

$settingsString = $settingsList -join " "

Write-Host "Environment variables to set:" -ForegroundColor Yellow
foreach ($key in $envVars.Keys) {
    $displayValue = if ($key -eq "SECRET_KEY") { "***" } else { $envVars[$key] }
    Write-Host "  $key = $displayValue" -ForegroundColor Cyan
}
Write-Host ""

# Set app settings
try {
    Write-Host "Running: az webapp config appsettings set ..." -ForegroundColor Cyan
    $result = az webapp config appsettings set `
        --resource-group $ResourceGroup `
        --name $AppServiceName `
        --settings $settingsString `
        2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Environment variables set successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Error setting environment variables: $result" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Verify app settings
Write-Host "Verifying environment variables..." -ForegroundColor Yellow
try {
    $appSettings = az webapp config appsettings list `
        --resource-group $ResourceGroup `
        --name $AppServiceName `
        2>&1 | ConvertFrom-Json
    
    if ($appSettings) {
        Write-Host ""
        Write-Host "Current App Settings:" -ForegroundColor Green
        Write-Host ""
        
        $foundVars = @{}
        foreach ($setting in $appSettings) {
            if ($envVars.ContainsKey($setting.name)) {
                $foundVars[$setting.name] = $true
                $displayValue = if ($setting.name -eq "SECRET_KEY") { "***" } else { $setting.value }
                Write-Host "  [OK] $($setting.name) = $displayValue" -ForegroundColor Green
            }
        }
        
        # Check for missing variables
        Write-Host ""
        $allFound = $true
        foreach ($key in $envVars.Keys) {
            if (-not $foundVars.ContainsKey($key)) {
                Write-Host "  [MISSING] $key" -ForegroundColor Red
                $allFound = $false
            }
        }
        
        if ($allFound) {
            Write-Host ""
            Write-Host "All environment variables are set correctly!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "Some environment variables are missing." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Could not retrieve app settings" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error verifying settings: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
