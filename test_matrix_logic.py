#!/usr/bin/env python3
"""
Test script to simulate the exact matrix generation logic from the workflow
"""

def simulate_matrix_generation():
    """Simulate the bash script logic for matrix generation"""
    
    # Simulate different scenarios
    test_cases = [
        {
            "name": "Python project",
            "files": ["main.py", "requirements.txt"],
            "expected": ["python"]
        },
        {
            "name": "JavaScript project", 
            "files": ["package.json"],
            "expected": ["javascript"]
        },
        {
            "name": "Mixed project",
            "files": ["main.py", "package.json", "Dockerfile"],
            "expected": ["python", "javascript", "container"]
        },
        {
            "name": "Empty project",
            "files": [],
            "expected": ["general"]
        }
    ]
    
    for test in test_cases:
        print(f"\n🧪 Test: {test['name']}")
        print(f"Files: {test['files']}")
        
        # Simulate the detection logic
        scan_types = []
        
        # Check for Python
        if any(f.endswith('.py') for f in test['files']) or 'requirements.txt' in test['files'] or 'pyproject.toml' in test['files']:
            scan_types.append("python")
        
        # Check for JavaScript
        if 'package.json' in test['files'] or 'yarn.lock' in test['files'] or 'package-lock.json' in test['files']:
            scan_types.append("javascript")
        
        # Check for containers
        if 'Dockerfile' in test['files'] or 'docker-compose.yml' in test['files']:
            scan_types.append("container")
        
        # Generate matrix JSON
        if len(scan_types) == 0:
            matrix_json = '{"scan_type":["general"]}'
        else:
            json_array = "[" + ",".join(f'"{scan_type}"' for scan_type in scan_types) + "]"
            matrix_json = f'{{"scan_type":{json_array}}}'
        
        print(f"Generated matrix: {matrix_json}")
        print(f"Expected scan types: {test['expected']}")
        print(f"Actual scan types: {scan_types}")
        
        # Verify
        if scan_types == test['expected'] or (len(scan_types) == 0 and test['expected'] == ["general"]):
            print("✅ PASS")
        else:
            print("❌ FAIL")

if __name__ == "__main__":
    print("🔍 Testing Matrix Generation Logic")
    print("=" * 50)
    simulate_matrix_generation()
    print("\n" + "=" * 50)
    print("✅ Matrix generation testing complete!")
