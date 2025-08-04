#!/usr/bin/env python3
"""
GitHub Actions Workflow Validator
Validates YAML syntax and basic GitHub Actions structure
"""

import yaml
import os
import sys

def validate_workflow_file(file_path):
    """Validate a GitHub Actions workflow file"""
    print(f"Validating: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
        
        # Basic structure validation
        if not isinstance(content, dict):
            print(f"❌ Invalid structure: {file_path}")
            return False
        
        # Check for required GitHub Actions fields
        if 'on' not in content and 'true' not in str(content.get('on', '')):
            print(f"⚠️  Warning: No 'on' trigger found in {file_path}")
        
        if 'jobs' in content:
            job_count = len(content['jobs'])
            print(f"✅ {file_path} - Valid YAML with {job_count} jobs")
        else:
            print(f"✅ {file_path} - Valid YAML (no jobs section)")
        
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ YAML Error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def main():
    """Main validation function"""
    workflow_files = [
        '.github/workflows/security-comprehensive.yml',
        '.github/workflows/security-basic.yml', 
        '.github/workflows/security-compatible.yml',
        'github-actions-templates/container-security.yml',
        'github-actions-templates/basic-security.yml',
        'github-actions-templates/python-security.yml'
    ]
    
    print("🔍 Validating GitHub Actions workflow files...")
    print("=" * 50)
    
    all_valid = True
    for file_path in workflow_files:
        if not validate_workflow_file(file_path):
            all_valid = False
        print()
    
    print("=" * 50)
    if all_valid:
        print("🎉 All workflow files are valid!")
        return 0
    else:
        print("❌ Some workflow files have issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
