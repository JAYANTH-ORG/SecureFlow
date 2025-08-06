#!/usr/bin/env python3
"""
Verify the project structure organization
"""

import os
import glob

def check_folder_structure():
    """Check if the folder structure is organized correctly"""
    
    print("🔍 Verifying Project Structure Organization")
    print("=" * 50)
    
    base_path = "c:\\Users\\2121659\\Shared-libs"
    
    # Expected folder structure
    expected_structure = {
        "validation/scripts": ["validate_workflows.py", "analyze_actions.py"],
        "validation/tests": ["test_matrix_logic.py", "test_echo_json.py", "test_json_generation.py"],
        "docs/analysis": ["COMPATIBILITY_ANALYSIS.md", "COMPREHENSIVE_ANALYSIS.md"],
        "docs/summaries": ["PROJECT_SUMMARY.md", "BACKWARD_COMPATIBILITY_SUMMARY.md"],
        "docs/validation": ["WORKFLOW_VALIDATION_SUMMARY.md", "JSON_FIX_COMPLETE.md"]
    }
    
    all_good = True
    
    for folder, expected_files in expected_structure.items():
        folder_path = os.path.join(base_path, folder)
        print(f"\n📁 Checking {folder}/")
        
        if not os.path.exists(folder_path):
            print(f"   ❌ Folder does not exist: {folder_path}")
            all_good = False
            continue
        
        for expected_file in expected_files:
            file_path = os.path.join(folder_path, expected_file)
            if os.path.exists(file_path):
                print(f"   ✅ {expected_file}")
            else:
                print(f"   ❌ Missing: {expected_file}")
                all_good = False
    
    # Check root files are still there
    print(f"\n📁 Checking root directory files...")
    root_files = ["README.md", "pyproject.toml", "PROJECT_STRUCTURE.md"]
    for file in root_files:
        file_path = os.path.join(base_path, file)
        if os.path.exists(file_path):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ Missing: {file}")
            all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 Project structure organization completed successfully!")
    else:
        print("⚠️  Some files may not have been moved correctly.")
    
    return all_good

def show_new_structure():
    """Show the new organized structure"""
    
    print("\n📂 New Project Structure:")
    print("=" * 30)
    
    base_path = "c:\\Users\\2121659\\Shared-libs"
    
    # Show organized folders
    for root, dirs, files in os.walk(base_path):
        level = root.replace(base_path, '').count(os.sep)
        indent = ' ' * 2 * level
        folder_name = os.path.basename(root)
        if level == 0:
            print(f"{indent}📁 SecureFlow-Core/")
        else:
            print(f"{indent}📁 {folder_name}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith(('.py', '.md', '.yml', '.yaml', '.toml')):
                if file.endswith('.py'):
                    icon = "🐍"
                elif file.endswith('.md'):
                    icon = "📄"
                elif file.endswith(('.yml', '.yaml')):
                    icon = "⚙️"
                elif file.endswith('.toml'):
                    icon = "🔧"
                else:
                    icon = "📄"
                print(f"{subindent}{icon} {file}")

if __name__ == "__main__":
    check_folder_structure()
    show_new_structure()
