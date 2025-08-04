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

def check_action_versions(content, file_path):
    """Check for deprecated action versions"""
    issues = []
    
    # Check for deprecated action versions
    deprecated_actions = {
        'actions/upload-artifact@v3': 'actions/upload-artifact@v4',
        'actions/download-artifact@v3': 'actions/download-artifact@v4',
        'actions/setup-python@v4': 'actions/setup-python@v5',
        'github/codeql-action@v2': 'github/codeql-action@v3'
    }
    
    for deprecated, recommended in deprecated_actions.items():
        if deprecated in content:
            line_num = content[:content.find(deprecated)].count('\n') + 1
            issues.append(f"Line {line_num}: Deprecated action '{deprecated}' should use '{recommended}'")
    
    return issues

def check_matrix_syntax(content, file_path):
    """Check for matrix syntax issues"""
    issues = []
    
    # Look for matrix configurations
    if 'matrix:' in content:
        # Check for any jq usage that could cause issues
        if 'jq -c .' in content:
            line_num = content[:content.find('jq -c .')].count('\n') + 1
            issues.append(f"Line {line_num}: Using 'jq -c .' for JSON compaction - consider removing if JSON is already valid")
        
        if 'jq -R . | jq -s .' in content:
            line_num = content[:content.find('jq -R . | jq -s .')].count('\n') + 1
            issues.append(f"Line {line_num}: Complex jq pipeline - consider manual JSON generation for better reliability")
        
        # Check for potentially problematic printf patterns
        if 'printf \'"%s"\\n\'' in content:
            line_num = content[:content.find('printf \'"%s"\\n\'')].count('\n') + 1
            issues.append(f"Line {line_num}: Potentially malformed JSON in matrix generation - double quotes issue")
    
    return issues

def check_transitive_dependencies(content, file_path):
    """Check for potential transitive action dependencies"""
    issues = []
    warnings = []
    
    # Check for custom actions that might use deprecated versions
    if 'uses:' in content and ('your-org/' in content or 'local/' in content):
        warnings.append("Custom actions detected - ensure they don't use deprecated action versions")
    
    # Check for workflow_call or reusable workflows
    if 'uses:' in content and '.github/workflows/' in content:
        warnings.append("Reusable workflow detected - verify it doesn't use deprecated actions")
    
    # Check for any embedded YAML or dynamic action generation
    if 'run:' in content and ('upload-artifact' in content):
        warnings.append("Script contains upload-artifact reference - check for dynamic action usage")
    
    return issues, warnings

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
        issues += check_action_versions(content, file_path)
        issues += check_matrix_syntax(content, file_path)
        issues, warnings = check_transitive_dependencies(content, file_path)
        issues += issues  # Add any issues from transitive dependency checks
        
        if issues:
            print(f"⚠️  Potential issues in {file_path}:")
            for issue in issues:
                print(f"   {issue}")
        
        if warnings:
            print(f"⚠️  Warnings in {file_path}:")
            for warning in warnings:
                print(f"   {warning}")
        
        # Check for required GitHub Actions fields
        # Note: YAML parser interprets 'on:' as boolean True, not string 'on'
        if 'on' not in yaml_content and True not in yaml_content:
            print(f"⚠️  Warning: No 'on' trigger found in {file_path}")
        elif True in yaml_content:
            # YAML interpreted 'on:' as boolean True - this is expected
            print(f"ℹ️  Found 'on' trigger (parsed as boolean True due to YAML 1.1 spec)")
        
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
