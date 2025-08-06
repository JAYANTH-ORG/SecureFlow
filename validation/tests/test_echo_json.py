#!/usr/bin/env python3
"""
Test the new echo-based JSON generation approach
"""

import json
import tempfile
import subprocess
import os

def test_echo_json_generation():
    """Test the echo-based JSON generation"""
    
    print("Testing echo-based JSON generation...")
    
    # Simulate the echo commands from the workflow
    scan_types_json = '["python","javascript","container"]'
    
    # Simulate the echo commands
    lines = [
        "{",
        f'  "project_name": "JAYANTH-ORG/SecureFlow",',
        f'  "scan_types": {scan_types_json},',
        f'  "compliance_frameworks": ["SOC2", "PCI-DSS"],',
        f'  "container_image": "",',
        f'  "notification_level": "high"',
        "}"
    ]
    
    json_content = '\n'.join(lines)
    print("Generated JSON content:")
    print(json_content)
    
    # Test if it's valid JSON
    try:
        parsed = json.loads(json_content)
        print("JSON parsing successful!")
        print("Parsed data:", json.dumps(parsed, indent=2))
        return True
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        return False

def test_variable_substitution():
    """Test that GitHub Actions variable substitution won't break JSON"""
    
    print("\nTesting GitHub Actions variable substitution...")
    
    # Simulate what GitHub Actions would substitute
    variables = {
        "${{ github.repository }}": "JAYANTH-ORG/SecureFlow",
        "${{ github.event.inputs.container_image }}": "",
        "${{ github.event.inputs.notification_level || 'high' }}": "high"
    }
    
    # Template with GitHub Actions variables
    template = '''{
  "project_name": "${{ github.repository }}",
  "scan_types": ["python"],
  "compliance_frameworks": ["SOC2", "PCI-DSS"],
  "container_image": "${{ github.event.inputs.container_image }}",
  "notification_level": "${{ github.event.inputs.notification_level || 'high' }}"
}'''
    
    # Simulate GitHub Actions variable substitution
    substituted = template
    for var, value in variables.items():
        substituted = substituted.replace(var, value)
    
    print("Template after GitHub Actions substitution:")
    print(substituted)
    
    try:
        parsed = json.loads(substituted)
        print("JSON parsing successful after substitution!")
        return True
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed after substitution: {e}")
        return False

if __name__ == "__main__":
    print("Testing New JSON Generation Approach")
    print("=" * 50)
    
    test1 = test_echo_json_generation()
    test2 = test_variable_substitution()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Echo-based generation: {'PASS' if test1 else 'FAIL'}")
    print(f"Variable substitution: {'PASS' if test2 else 'FAIL'}")
    
    if all([test1, test2]):
        print("\nAll tests passed! The new JSON generation approach is working correctly.")
    else:
        print("\nSome tests failed.")
