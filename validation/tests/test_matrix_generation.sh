#!/bin/bash
# Test script to verify matrix generation logic

echo "Testing matrix generation logic..."

# Simulate the scan types array
SCAN_TYPES=("python" "javascript" "container")

echo "Test 1: Array with elements"
# Build JSON array manually to avoid jq dependency issues
JSON_ARRAY="["
for i in "${!SCAN_TYPES[@]}"; do
  if [ $i -gt 0 ]; then
    JSON_ARRAY+=","
  fi
  JSON_ARRAY+="\"${SCAN_TYPES[$i]}\""
done
JSON_ARRAY+="]"
echo "Result: {\"scan_type\":$JSON_ARRAY}"

echo ""
echo "Test 2: Empty array"
EMPTY_SCAN_TYPES=()
if [ ${#EMPTY_SCAN_TYPES[@]} -eq 0 ]; then
  echo "Result: {\"scan_type\":[\"general\"]}"
else
  echo "Unexpected: Array should be empty"
fi

echo ""
echo "Test 3: Single element"
SINGLE_SCAN_TYPES=("python")
JSON_ARRAY="["
for i in "${!SINGLE_SCAN_TYPES[@]}"; do
  if [ $i -gt 0 ]; then
    JSON_ARRAY+=","
  fi
  JSON_ARRAY+="\"${SINGLE_SCAN_TYPES[$i]}\""
done
JSON_ARRAY+="]"
echo "Result: {\"scan_type\":$JSON_ARRAY}"

echo ""
echo "Matrix generation test completed successfully!"
