#!/usr/bin/env python3
"""
GitHub Actions Workflow Validator
Validates YAML syntax and checks for common GitHub Actions issues
"""

import yaml
import os
import sys
import re

def check_github_actions_expressions(content, file_path):
    """Check for common GitHub Actions expression issues"""
    issues = []
    
    # Check for hashFiles usage
    hashfiles_pattern = r"hashFiles\s*\([^)]*\)"
    matches = re.finditer(hashfiles_pattern, content)
    
    for match in matches:
        line_num = content[:match.start()].count('\n') + 1
        matched_text = match.group()
        
        # Check if it's in an if condition and properly formatted
        line_start = content.rfind('\n', 0, match.start()) + 1
        line_end = content.find('\n', match.end())
        if line_end == -1:
            line_end = len(content)
        line_content = content[line_start:line_end].strip()
        
        if 'if:' in line_content:
            # Check for proper syntax
            if '${{' in line_content and '}}' in line_content:
                # If wrapped in ${{}}, check if it's correctly formatted
                if not re.search(r'\$\{\{.*hashFiles.*\}\}', line_content):
                    issues.append(f"Line {line_num}: Potentially malformed expression: {line_content}")
            # If not wrapped, check if it follows the simple pattern
            elif not re.match(r'\s*if:\s*[^$]*$', line_content):
                pass  # This might be OK for simple expressions
        
        print(f"Found hashFiles at line {line_num}: {matched_text}")
    
    return issues

def validate_workflow_file(file_path):
    """Validate a GitHub Actions workflow file"""
    print(f"Validating: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML
        yaml_content = yaml.safe_load(content)
        
        # Basic structure validation
        if not isinstance(yaml_content, dict):
            print(f"❌ Invalid structure: {file_path}")
            return False
        
        # Check for GitHub Actions specific issues
        issues = check_github_actions_expressions(content, file_path)
        
        if issues:
            print(f"⚠️  Potential issues in {file_path}:")
            for issue in issues:
                print(f"   {issue}")
        
        # Check for required GitHub Actions fields
        if 'on' not in yaml_content:
            print(f"⚠️  Warning: No 'on' trigger found in {file_path}")
        
        if 'jobs' in yaml_content:
            job_count = len(yaml_content['jobs'])
            print(f"✅ {file_path} - Valid YAML with {job_count} jobs")
        else:
            print(f"✅ {file_path} - Valid YAML (no jobs section)")
        
        return len(issues) == 0
        
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
