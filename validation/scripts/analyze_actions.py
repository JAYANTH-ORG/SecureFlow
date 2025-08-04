#!/usr/bin/env python3
"""
Extract and analyze all GitHub Actions used in workflow files
"""

import yaml
import re
import os

def extract_actions_from_workflow(file_path):
    """Extract all GitHub Actions used in a workflow file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML
        yaml_content = yaml.safe_load(content)
        
        actions = []
        
        # Extract actions from jobs
        if 'jobs' in yaml_content:
            for job_name, job_config in yaml_content['jobs'].items():
                if 'steps' in job_config:
                    for step in job_config['steps']:
                        if isinstance(step, dict) and 'uses' in step:
                            actions.append({
                                'job': job_name,
                                'action': step['uses'],
                                'step_name': step.get('name', 'Unnamed step')
                            })
        
        return actions
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def main():
    """Main function to analyze all workflow files"""
    workflow_files = [
        '.github/workflows/security-comprehensive.yml',
        '.github/workflows/security-basic.yml', 
        '.github/workflows/security-compatible.yml'
    ]
    
    print("🔍 Analyzing GitHub Actions in workflow files...")
    print("=" * 70)
    
    all_actions = {}
    
    for file_path in workflow_files:
        if os.path.exists(file_path):
            print(f"\n📄 File: {file_path}")
            actions = extract_actions_from_workflow(file_path)
            
            for action_info in actions:
                action = action_info['action']
                if action not in all_actions:
                    all_actions[action] = []
                all_actions[action].append(f"{file_path} ({action_info['job']})")
                
                # Check for deprecated versions
                if '@v3' in action and 'upload-artifact' in action:
                    print(f"  ⚠️  DEPRECATED: {action} in {action_info['step_name']}")
                elif '@v4' in action or '@v5' in action:
                    print(f"  ✅ CURRENT: {action}")
                else:
                    print(f"  ℹ️  {action}")
    
    print("\n" + "=" * 70)
    print("📊 Summary of all actions used:")
    
    deprecated_found = False
    for action, locations in sorted(all_actions.items()):
        print(f"\n🔧 {action}")
        for location in locations:
            print(f"   └─ {location}")
        
        if '@v3' in action and 'upload-artifact' in action:
            print("   ⚠️  DEPRECATED - NEEDS UPDATE!")
            deprecated_found = True
    
    print("\n" + "=" * 70)
    if deprecated_found:
        print("❌ DEPRECATED ACTIONS FOUND - Update required!")
        return 1
    else:
        print("✅ All actions are using current versions!")
        return 0

if __name__ == "__main__":
    exit(main())
