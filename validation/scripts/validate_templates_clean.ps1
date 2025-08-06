# Template Validation Script for Windows PowerShell
# Validates GitHub Actions templates

Write-Host "Validating GitHub Actions templates..." -ForegroundColor Cyan

$TEMPLATES_DIR = "github-actions-templates"
$ACTIONS_DIR = ".github/actions"

# Check if templates exist
$templates = @("basic-security.yml", "java-maven-security.yml", "nodejs-security.yml", "python-security.yml", "container-security.yml")

Write-Host "Checking template files..." -ForegroundColor Yellow
foreach ($template in $templates) {
    $templatePath = Join-Path $TEMPLATES_DIR $template
    if (Test-Path $templatePath) {
        Write-Host "  Template found: $template" -ForegroundColor Green
    } else {
        Write-Host "  Template missing: $template" -ForegroundColor Red
    }
}

# Validate setup action
Write-Host "Checking setup action..." -ForegroundColor Yellow
$setupActionPath = Join-Path $ACTIONS_DIR "setup-secureflow/action.yml"
if (Test-Path $setupActionPath) {
    Write-Host "  Setup action found" -ForegroundColor Green
    
    # Check for Python dependency detection
    $content = Get-Content $setupActionPath -Raw
    if ($content -match "detect-deps") {
        Write-Host "  Python dependency detection implemented" -ForegroundColor Green
    } else {
        Write-Host "  Python dependency detection missing" -ForegroundColor Red
    }
} else {
    Write-Host "  Setup action missing" -ForegroundColor Red
}

# Basic YAML syntax validation
Write-Host "Performing basic YAML validation..." -ForegroundColor Yellow

foreach ($template in $templates) {
    $templatePath = Join-Path $TEMPLATES_DIR $template
    if (Test-Path $templatePath) {
        try {
            $content = Get-Content $templatePath -Raw
            if ($content -match "^name:" -and $content -match "on:" -and $content -match "jobs:") {
                Write-Host "  YAML structure valid: $template" -ForegroundColor Green
            } else {
                Write-Host "  YAML structure incomplete: $template" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  YAML read error: $template" -ForegroundColor Red
        }
    }
}

# Check workspace integration
Write-Host "Checking workspace integration..." -ForegroundColor Yellow

$workspaceFiles = @(
    "src/secureflow_core/__init__.py",
    "pyproject.toml", 
    "README.md",
    "tests/test_core.py"
)

foreach ($file in $workspaceFiles) {
    if (Test-Path $file) {
        Write-Host "  Workspace file exists: $file" -ForegroundColor Green
    } else {
        Write-Host "  Workspace file missing: $file" -ForegroundColor Red
    }
}

Write-Host "Template validation complete!" -ForegroundColor Green
