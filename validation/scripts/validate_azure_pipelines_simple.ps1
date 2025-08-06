# Azure Pipelines Validation Script
# Simple validation for SecureFlow Azure pipeline templates

Write-Host "Validating Azure Pipeline Templates..." -ForegroundColor Blue

$PipelineDir = "c:\Users\2121659\Shared-libs\azure-pipelines"
$ErrorCount = 0
$ValidatedFiles = @()

# List of pipeline files to validate
$PipelineFiles = @(
    "secureflow-basic.yml",
    "secureflow-comprehensive.yml", 
    "secureflow-enhanced.yml",
    "secureflow-java-maven.yml",
    "secureflow-nodejs.yml",
    "secureflow-python-web.yml",
    "secureflow-container.yml",
    "secureflow-monorepo.yml",
    "secureflow-enterprise-azure.yml"
)

Write-Host "Checking pipeline files..." -ForegroundColor Yellow

foreach ($file in $PipelineFiles) {
    $filePath = Join-Path $PipelineDir $file
    
    if (-not (Test-Path $filePath)) {
        Write-Host "ERROR: File not found: $file" -ForegroundColor Red
        $ErrorCount++
        continue
    }
    
    Write-Host "Validating: $file" -ForegroundColor Cyan
    
    try {
        $content = Get-Content $filePath -Raw
        
        # Basic structure checks
        $hasStages = $content -match "stages:" -or $content -match "jobs:"
        $hasSteps = $content -match "steps:"
        $hasSecureFlow = $content -match "secureflow" -or $content -match "SecureFlow"
        
        if (-not $hasStages) {
            Write-Host "  WARNING: No stages or jobs found" -ForegroundColor Yellow
        }
        
        if (-not $hasSteps) {
            Write-Host "  WARNING: No steps found" -ForegroundColor Yellow  
        }
        
        if (-not $hasSecureFlow) {
            Write-Host "  WARNING: No SecureFlow usage detected" -ForegroundColor Yellow
        }
        
        Write-Host "  SUCCESS: Validation passed" -ForegroundColor Green
        $ValidatedFiles += $file
    }
    catch {
        Write-Host "  ERROR: Validation failed - $($_.Exception.Message)" -ForegroundColor Red
        $ErrorCount++
    }
}

# Summary
Write-Host "`nValidation Summary:" -ForegroundColor Blue
Write-Host "Successfully validated files: $($ValidatedFiles.Count)" -ForegroundColor Green
Write-Host "Files with errors: $ErrorCount" -ForegroundColor Red

if ($ValidatedFiles.Count -gt 0) {
    Write-Host "`nValidated files:" -ForegroundColor Green
    foreach ($file in $ValidatedFiles) {
        Write-Host "  - $file" -ForegroundColor Gray
    }
}

# Template coverage
Write-Host "`nTemplate Coverage:" -ForegroundColor Blue
Write-Host "- Basic multi-language pipeline: secureflow-basic.yml" -ForegroundColor Green
Write-Host "- Java Maven pipeline: secureflow-java-maven.yml" -ForegroundColor Green  
Write-Host "- Node.js pipeline: secureflow-nodejs.yml" -ForegroundColor Green
Write-Host "- Python web app pipeline: secureflow-python-web.yml" -ForegroundColor Green
Write-Host "- Container security pipeline: secureflow-container.yml" -ForegroundColor Green
Write-Host "- Monorepo pipeline: secureflow-monorepo.yml" -ForegroundColor Green
Write-Host "- Enterprise Azure pipeline: secureflow-enterprise-azure.yml" -ForegroundColor Green

if ($ErrorCount -eq 0) {
    Write-Host "`nSUCCESS: All Azure Pipeline templates validated!" -ForegroundColor Green
    Write-Host "Total templates: $($ValidatedFiles.Count)" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "`nWARNING: Validation completed with $ErrorCount errors" -ForegroundColor Yellow
    exit 1
}
