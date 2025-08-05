#!/bin/bash
# Validation script for GitHub Actions templates

echo "🔍 Validating GitHub Actions templates..."

TEMPLATES_DIR="github-actions-templates"
ACTIONS_DIR=".github/actions"

# Check if templates exist
for template in "basic-security.yml" "java-maven-security.yml" "nodejs-security.yml" "python-security.yml" "container-security.yml"; do
    if [ -f "$TEMPLATES_DIR/$template" ]; then
        echo "✅ Template found: $template"
    else
        echo "❌ Template missing: $template"
    fi
done

# Validate setup action
if [ -f "$ACTIONS_DIR/setup-secureflow/action.yml" ]; then
    echo "✅ Setup action found"
    
    # Check for Python dependency detection
    if grep -q "detect-deps" "$ACTIONS_DIR/setup-secureflow/action.yml"; then
        echo "✅ Python dependency detection implemented"
    else
        echo "❌ Python dependency detection missing"
    fi
else
    echo "❌ Setup action missing"
fi

# Validate YAML syntax (if yamllint is available)
if command -v yamllint &> /dev/null; then
    echo "🔍 Validating YAML syntax..."
    for file in $TEMPLATES_DIR/*.yml $ACTIONS_DIR/setup-secureflow/action.yml; do
        if [ -f "$file" ]; then
            if yamllint "$file" > /dev/null 2>&1; then
                echo "✅ YAML valid: $(basename $file)"
            else
                echo "❌ YAML invalid: $(basename $file)"
            fi
        fi
    done
else
    echo "ℹ️ yamllint not available - skipping YAML validation"
fi

echo "🎉 Template validation complete!"
