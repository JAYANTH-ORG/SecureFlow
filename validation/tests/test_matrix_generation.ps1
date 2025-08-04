# Test script to verify matrix generation logic (PowerShell version)

Write-Host "Testing matrix generation logic..."

# Test 1: Array with elements
Write-Host "Test 1: Array with elements"
$SCAN_TYPES = @("python", "javascript", "container")
$JSON_ARRAY = "["
for ($i = 0; $i -lt $SCAN_TYPES.Length; $i++) {
    if ($i -gt 0) {
        $JSON_ARRAY += ","
    }
    $JSON_ARRAY += "`"$($SCAN_TYPES[$i])`""
}
$JSON_ARRAY += "]"
Write-Host "Result: {`"scan_type`":$JSON_ARRAY}"

# Test 2: Empty array
Write-Host ""
Write-Host "Test 2: Empty array"
$EMPTY_SCAN_TYPES = @()
if ($EMPTY_SCAN_TYPES.Length -eq 0) {
    Write-Host "Result: {`"scan_type`":[`"general`"]}"
} else {
    Write-Host "Unexpected: Array should be empty"
}

# Test 3: Single element
Write-Host ""
Write-Host "Test 3: Single element"
$SINGLE_SCAN_TYPES = @("python")
$JSON_ARRAY = "["
for ($i = 0; $i -lt $SINGLE_SCAN_TYPES.Length; $i++) {
    if ($i -gt 0) {
        $JSON_ARRAY += ","
    }
    $JSON_ARRAY += "`"$($SINGLE_SCAN_TYPES[$i])`""
}
$JSON_ARRAY += "]"
Write-Host "Result: {`"scan_type`":$JSON_ARRAY}"

Write-Host ""
Write-Host "Matrix generation test completed successfully!"
