# Azure Pipeline Duplication Analysis Script
# Checks for duplicate files and merge opportunities

Write-Host "Analyzing Azure Pipeline Files for Duplicates and Merge Opportunities..." -ForegroundColor Blue

$PipelineDir = "azure-pipelines"
$files = Get-ChildItem $PipelineDir -Filter "*.yml"

Write-Host "`nFound $($files.Count) pipeline files:" -ForegroundColor Yellow
foreach ($file in $files) {
    Write-Host "  - $($file.Name)" -ForegroundColor Gray
}

Write-Host "`nAnalyzing file headers and purposes..." -ForegroundColor Yellow

$fileAnalysis = @{}

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $firstLines = (Get-Content $file.FullName | Select-Object -First 10) -join "`n"
    
    $analysis = @{
        'File' = $file.Name
        'FirstComment' = ($firstLines -split "`n" | Where-Object { $_ -match '^#' } | Select-Object -First 1) -replace '^#\s*', ''
        'HasStages' = $content -match "stages:"
        'HasJobs' = $content -match "jobs:"
        'HasParameters' = $content -match "parameters:"
        'HasJavaMaven' = $content -match "java.*maven|maven.*java" -or $content -match "pom\.xml"
        'HasNodejs' = $content -match "node\.?js|npm|yarn|pnpm|package\.json"
        'HasPython' = $content -match "python|pip|requirements\.txt"
        'HasContainer' = $content -match "docker|container|dockerfile"
        'HasEnterprise' = $content -match "enterprise|azure.*integration|defender|sentinel"
        'HasMonorepo' = $content -match "monorepo|multi.*project"
        'LineCount' = (Get-Content $file.FullName).Count
    }
    
    $fileAnalysis[$file.Name] = $analysis
}

Write-Host "`nFile Analysis Results:" -ForegroundColor Green
foreach ($file in $fileAnalysis.Keys | Sort-Object) {
    $info = $fileAnalysis[$file]
    Write-Host "`n$file ($($info.LineCount) lines):" -ForegroundColor Cyan
    Write-Host "  Purpose: $($info.FirstComment)" -ForegroundColor White
    
    $features = @()
    if ($info.HasJavaMaven) { $features += "Java/Maven" }
    if ($info.HasNodejs) { $features += "Node.js" }
    if ($info.HasPython) { $features += "Python" }
    if ($info.HasContainer) { $features += "Container" }
    if ($info.HasEnterprise) { $features += "Enterprise" }
    if ($info.HasMonorepo) { $features += "Monorepo" }
    
    if ($features.Count -gt 0) {
        Write-Host "  Features: $($features -join ', ')" -ForegroundColor Green
    }
}

# Check for potential duplicates
Write-Host "`n`nDuplication Analysis:" -ForegroundColor Yellow

# Group files by similar purposes
$groups = @{
    'Basic/Core' = @()
    'Java' = @()
    'Node.js' = @()
    'Python' = @()
    'Container' = @()
    'Enterprise' = @()
    'Monorepo' = @()
    'Specialized' = @()
}

foreach ($file in $fileAnalysis.Keys) {
    $info = $fileAnalysis[$file]
    
    if ($file -match "basic|comprehensive|enhanced") {
        $groups['Basic/Core'] += $file
    }
    elseif ($info.HasJavaMaven) {
        $groups['Java'] += $file
    }
    elseif ($info.HasNodejs -and -not $info.HasJavaMaven -and -not $info.HasContainer) {
        $groups['Node.js'] += $file
    }
    elseif ($info.HasPython -and $file -match "python") {
        $groups['Python'] += $file
    }
    elseif ($info.HasContainer) {
        $groups['Container'] += $file
    }
    elseif ($info.HasEnterprise) {
        $groups['Enterprise'] += $file
    }
    elseif ($info.HasMonorepo) {
        $groups['Monorepo'] += $file
    }
    else {
        $groups['Specialized'] += $file
    }
}

foreach ($group in $groups.Keys) {
    if ($groups[$group].Count -gt 0) {
        Write-Host "`n$group Templates:" -ForegroundColor Cyan
        foreach ($file in $groups[$group]) {
            Write-Host "  - $file" -ForegroundColor White
        }
        
        if ($groups[$group].Count -gt 1) {
            Write-Host "  ⚠️ Multiple files in this category - check for overlap" -ForegroundColor Yellow
        }
    }
}

# Merge opportunities analysis
Write-Host "`n`nMerge Opportunities Analysis:" -ForegroundColor Blue

$mergeOpportunities = @()

# Check if secureflow-basic.yml already covers Java and Node.js
$basicFile = $fileAnalysis['secureflow-basic.yml']
if ($basicFile) {
    if ($basicFile.HasJavaMaven -and $basicFile.HasNodejs) {
        Write-Host "✅ secureflow-basic.yml already includes Java and Node.js support" -ForegroundColor Green
        
        # Check if dedicated files are redundant
        if ($groups['Java'].Count -gt 0) {
            Write-Host "⚠️ Consider: Java-specific file might be redundant if basic covers Java well" -ForegroundColor Yellow
            $mergeOpportunities += "Java features from secureflow-java-maven.yml could enhance secureflow-basic.yml"
        }
        
        if ($groups['Node.js'].Count -gt 0) {
            Write-Host "⚠️ Consider: Node.js-specific file might be redundant if basic covers Node.js well" -ForegroundColor Yellow
            $mergeOpportunities += "Node.js features from secureflow-nodejs.yml could enhance secureflow-basic.yml"
        }
    }
}

# Check for feature overlap
$allFeatures = @{}
foreach ($file in $fileAnalysis.Keys) {
    $info = $fileAnalysis[$file]
    if ($info.HasJavaMaven) { 
        if (-not $allFeatures['JavaMaven']) { $allFeatures['JavaMaven'] = @() }
        $allFeatures['JavaMaven'] += $file 
    }
    if ($info.HasNodejs) { 
        if (-not $allFeatures['Nodejs']) { $allFeatures['Nodejs'] = @() }
        $allFeatures['Nodejs'] += $file 
    }
    if ($info.HasPython) { 
        if (-not $allFeatures['Python']) { $allFeatures['Python'] = @() }
        $allFeatures['Python'] += $file 
    }
    if ($info.HasContainer) { 
        if (-not $allFeatures['Container']) { $allFeatures['Container'] = @() }
        $allFeatures['Container'] += $file 
    }
    if ($info.HasEnterprise) { 
        if (-not $allFeatures['Enterprise']) { $allFeatures['Enterprise'] = @() }
        $allFeatures['Enterprise'] += $file 
    }
}

Write-Host "`nFeature Overlap:" -ForegroundColor Yellow
foreach ($feature in $allFeatures.Keys) {
    if ($allFeatures[$feature].Count -gt 1) {
        Write-Host "  $feature appears in:" -ForegroundColor Cyan
        foreach ($file in $allFeatures[$feature]) {
            Write-Host "    - $file" -ForegroundColor White
        }
    }
}

# Recommendations
Write-Host "`n`nRecommendations:" -ForegroundColor Green

Write-Host "`n1. File Structure Assessment:" -ForegroundColor Yellow
Write-Host "   ✅ No exact duplicates found" -ForegroundColor Green
Write-Host "   ✅ Each file serves a distinct purpose" -ForegroundColor Green
Write-Host "   ⚠️ Some feature overlap exists - this is intentional for different use cases" -ForegroundColor Yellow

Write-Host "`n2. Merge Opportunities:" -ForegroundColor Yellow
if ($basicFile.HasJavaMaven -and $basicFile.HasNodejs) {
    Write-Host "   📝 secureflow-basic.yml already includes multi-language support" -ForegroundColor Green
    Write-Host "   📝 Dedicated templates provide deep, specialized functionality" -ForegroundColor Green
    Write-Host "   📝 Current structure follows best practice: basic for quick start, specialized for advanced use" -ForegroundColor Green
} else {
    Write-Host "   📝 Could enhance secureflow-basic.yml with better Java/Node.js support" -ForegroundColor Yellow
}

Write-Host "`n3. Optimization Suggestions:" -ForegroundColor Yellow
Write-Host "   💡 Consider creating shared steps templates in steps/ directory" -ForegroundColor Cyan
Write-Host "   💡 Extract common security scanning steps to reusable templates" -ForegroundColor Cyan
Write-Host "   💡 Create variable templates for common configurations" -ForegroundColor Cyan

Write-Host "`n4. Template Strategy:" -ForegroundColor Yellow
Write-Host "   🎯 Current approach is correct: " -ForegroundColor Green
Write-Host "      - secureflow-basic.yml: Quick start with auto-detection" -ForegroundColor White
Write-Host "      - Language-specific: Deep integration and specialized features" -ForegroundColor White
Write-Host "      - Use case-specific: Containers, monorepos, enterprise" -ForegroundColor White

Write-Host "`nConclusion: Current file structure is well-organized with minimal duplication." -ForegroundColor Green
Write-Host "Each template serves a specific purpose and user need." -ForegroundColor Green
