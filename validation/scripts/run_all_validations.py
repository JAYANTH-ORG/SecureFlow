#!/usr/bin/env python3
"""
Complete Project Validation Suite
Runs all validation scripts and provides comprehensive status report
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_script(script_path, script_name):
    """Run a script and capture its output"""
    print(f"\nRunning {script_name}...")
    print("=" * 50)
    
    try:
        # Change to the script's directory
        script_dir = os.path.dirname(script_path)
        original_dir = os.getcwd()
        
        if script_dir:
            os.chdir(script_dir)
        
        # Run the script
        result = subprocess.run([sys.executable, os.path.basename(script_path)], 
                              capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        # Restore directory
        os.chdir(original_dir)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Run all validation scripts"""
    print("SecureFlow-Core Complete Validation Suite")
    print("=" * 60)
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Define all validation scripts
    validation_scripts = [
        {
            'path': project_root / 'validation' / 'scripts' / 'validate_workflows.py',
            'name': 'Workflow Validation',
            'description': 'Validates GitHub Actions workflow files'
        },
        {
            'path': project_root / 'validation' / 'scripts' / 'analyze_actions.py',
            'name': 'Action Analysis',
            'description': 'Analyzes GitHub Actions for deprecated versions'
        },
        {
            'path': project_root / 'validation' / 'tests' / 'test_matrix_logic.py',
            'name': 'Matrix Logic Test',
            'description': 'Tests matrix generation logic'
        },
        {
            'path': project_root / 'validation' / 'tests' / 'test_echo_json.py',
            'name': 'Echo JSON Test',
            'description': 'Tests echo-based JSON generation'
        },
        {
            'path': project_root / 'validation' / 'tests' / 'test_json_generation.py',
            'name': 'JSON Generation Test',
            'description': 'Tests JSON generation from workflow logic'
        }
    ]
    
    # Run all scripts
    results = {}
    for script in validation_scripts:
        if script['path'].exists():
            success = run_script(str(script['path']), script['name'])
            results[script['name']] = {
                'success': success,
                'description': script['description']
            }
        else:
            print(f"❌ Script not found: {script['path']}")
            results[script['name']] = {
                'success': False,
                'description': f"Script not found: {script['description']}"
            }
    
    # Print summary
    print("\n" + "=" * 60)
    print("\nVALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, result in results.items():
        status = "PASS" if result['success'] else "FAIL"
        print(f"{status} - {name}")
        print(f"     {result['description']}")
        if not result['success']:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL VALIDATIONS PASSED!")
        print("Project is ready for production use")
    else:
        print("SOME VALIDATIONS FAILED")
        print("Review failed tests above")
    
    print("\nProject Structure:")
    print(f"   Root: {project_root}")
    print("   Validation scripts: validation/scripts/")
    print("   Validation tests: validation/tests/")
    print("   Documentation: docs/")
    print("   Workflows: .github/workflows/")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
