# PowerShell script to create deployment ZIP file
# Excludes .venv, .git, __pycache__ folders and other unnecessary files

$zipFileName = "month_end_automator_deploy.zip"
$excludePatterns = @(
    ".git",
    ".venv",
    "venv",
    "env",
    "ENV",
    "__pycache__",
    "*.pyc",
    "*.csv",
    "*.xlsx",
    "*.xls",
    "test_*",
    "deploy*.zip",
    "month_end_automator_deploy.zip",
    ".azure",
    "*.log",
    ".vscode",
    ".idea"
)

# Remove existing ZIP if present
if (Test-Path $zipFileName) {
    Remove-Item $zipFileName -Force
    Write-Host "Removed existing ZIP file"
}

# Get all files and filter exclusions
$allFiles = Get-ChildItem -Path . -Recurse -File

$filesToInclude = @()
foreach ($file in $allFiles) {
    $shouldExclude = $false
    $relativePath = $file.FullName.Substring((Get-Location).Path.Length + 1)
    
    foreach ($pattern in $excludePatterns) {
        if ($relativePath -like "*\$pattern" -or 
            $relativePath -like "*\$pattern\*" -or 
            $relativePath -like "$pattern\*" -or
            $relativePath -eq $pattern) {
            $shouldExclude = $true
            break
        }
        # Also check if file name matches pattern
        if ($file.Name -like $pattern) {
            $shouldExclude = $true
            break
        }
    }
    
    if (-not $shouldExclude) {
        $filesToInclude += $file
    }
}

Write-Host "`nIncluding $($filesToInclude.Count) files in ZIP..."

# Create ZIP file
try {
    Compress-Archive -Path ($filesToInclude | Select-Object -ExpandProperty FullName) -DestinationPath $zipFileName -Force
    Write-Host "`nZIP file created successfully: $zipFileName" -ForegroundColor Green
    
    $zipInfo = Get-Item $zipFileName
    $sizeMB = [math]::Round($zipInfo.Length / 1MB, 2)
    Write-Host "  Size: $sizeMB MB" -ForegroundColor Cyan
    
    # Verify required files
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($zipInfo.FullName)
    $entries = $zip.Entries | Select-Object -ExpandProperty FullName
    $zip.Dispose()
    
    Write-Host "`nVerifying required files:" -ForegroundColor Yellow
    $required = @('main.py', 'requirements.txt', 'processor.py', 'reporter.py', 'errors.py')
    $allPresent = $true
    foreach ($file in $required) {
        if ($entries -contains $file) {
            Write-Host "  [OK] $file" -ForegroundColor Green
        } else {
            Write-Host "  [MISSING] $file" -ForegroundColor Red
            $allPresent = $false
        }
    }
    
    # Check folders
    Write-Host "`nVerifying folders:" -ForegroundColor Yellow
    $folders = @('templates', 'services')
    foreach ($folder in $folders) {
        $hasFolder = $entries | Where-Object { $_ -like "$folder/*" }
        if ($hasFolder) {
            Write-Host "  [OK] $folder/" -ForegroundColor Green
        } else {
            Write-Host "  [MISSING] $folder/" -ForegroundColor Red
            $allPresent = $false
        }
    }
    
    if ($allPresent) {
        Write-Host "`nAll required files and folders are present!" -ForegroundColor Green
    } else {
        Write-Host "`nWarning: Some required files are missing. Check above." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "`nError creating ZIP file: $_" -ForegroundColor Red
    exit 1
}
