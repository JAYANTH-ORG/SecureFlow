# SecureFlow GitHub Actions

This directory contains reusable GitHub Actions for integrating SecureFlow-Core into your CI/CD pipelines.

## 🎯 Available Actions

### 1. setup-secureflow

**Purpose**: Install and configure SecureFlow-Core from GitHub repository

**Location**: `.github/actions/setup-secureflow/action.yml`

**Inputs**:
- `python-version`: Python version to use (default: '3.11')
- `secureflow-repo`: GitHub repository (default: 'your-org/secureflow-core')
- `secureflow-ref`: Repository reference - branch, tag, or commit (default: 'main')
- `config-file`: Configuration file path (default: '.secureflow.yaml')
- `install-tools`: Install additional security tools (default: 'true')

**Outputs**:
- `secureflow-version`: Installed SecureFlow version
- `config-path`: Path to configuration file

**Usage**:
```yaml
- name: Setup SecureFlow
  uses: ./.github/actions/setup-secureflow
  with:
    python-version: '3.11'
    secureflow-repo: 'my-org/secureflow-core'
    secureflow-ref: 'v1.0.0'
    install-tools: 'true'
```

### 2. secureflow-scan

**Purpose**: Run comprehensive security scanning with SecureFlow-Core

**Location**: `.github/actions/secureflow-scan/action.yml`

**Inputs**:
- `target`: Target directory or file to scan (default: '.')
- `project-type`: Project type - auto, java-maven, nodejs, python, etc. (default: 'auto')
- `scan-types`: Comma-separated scan types (default: 'sast,secrets,dependencies')
- `severity-threshold`: Minimum severity - low, medium, high, critical (default: 'medium')
- `output-format`: Output format - sarif, json, html, text (default: 'sarif')
- `output-file`: Output file path (default: 'security-results.sarif')
- `config-file`: Configuration file path (default: '.secureflow.yaml')
- `fail-on-findings`: Fail action on security findings (default: 'false')
- `java-version`: Java version for Java projects
- `node-version`: Node.js version for Node.js projects

**Outputs**:
- `results-file`: Path to the results file
- `findings-count`: Total number of security findings
- `critical-count`: Number of critical severity findings
- `high-count`: Number of high severity findings
- `scan-status`: Overall scan status (success, failed, completed-with-findings)

**Usage**:
```yaml
- name: Run Security Scan
  id: scan
  uses: ./.github/actions/secureflow-scan
  with:
    target: '.'
    project-type: 'java-maven'
    scan-types: 'sast,secrets,dependencies,containers'
    severity-threshold: 'medium'
    java-version: '17'
    fail-on-findings: 'true'
```

## 🚀 Complete Workflow Examples

### Java Maven Project

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
      pull-requests: write
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up JDK
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
        cache: maven
    
    - name: Setup SecureFlow
      uses: ./.github/actions/setup-secureflow
      with:
        secureflow-repo: 'my-org/secureflow-core'
    
    - name: Run Security Scan
      id: scan
      uses: ./.github/actions/secureflow-scan
      with:
        project-type: 'java-maven'
        java-version: '17'
        fail-on-findings: 'true'
    
    - name: Upload SARIF
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: ${{ steps.scan.outputs.results-file }}
```

### Node.js Project

```yaml
- name: Setup SecureFlow
  uses: ./.github/actions/setup-secureflow
  with:
    secureflow-repo: 'my-org/secureflow-core'

- name: Run Security Scan
  uses: ./.github/actions/secureflow-scan
  with:
    project-type: 'nodejs'
    scan-types: 'sast,secrets,dependencies'
    node-version: '18'
```

### Python Project

```yaml
- name: Setup SecureFlow
  uses: ./.github/actions/setup-secureflow
  with:
    secureflow-repo: 'my-org/secureflow-core'

- name: Run Security Scan
  uses: ./.github/actions/secureflow-scan
  with:
    project-type: 'python'
    scan-types: 'sast,secrets,dependencies,bandit'
```

## 🔧 Configuration

### Default Configuration File

The setup action creates a default `.secureflow.yaml` if none exists:

```yaml
project:
  name: "my-project"
  description: "GitHub Actions Security Scan"
  team: "my-team"

scanning:
  sast_tool: "semgrep"
  sca_tool: "safety"
  secrets_tool: "trufflehog"
  severity_threshold: "medium"
  
  exclude_paths:
    - ".git/"
    - ".github/"
    - "node_modules/"
    - "__pycache__/"
    - "*.pyc"
    - "*.log"
    - "test_data/"
    - "tests/fixtures/"

github:
  repository: "${{ github.repository }}"
  token: "${{ github.token }}"

reporting:
  formats: ["json", "sarif"]
  include_remediation: true

advanced:
  parallel_scans: true
  max_workers: 2
```

### Repository Setup

1. **Copy the actions** to your repository:
   ```
   .github/
   └── actions/
       ├── setup-secureflow/
       │   └── action.yml
       └── secureflow-scan/
           └── action.yml
   ```

2. **Update the repository reference** in your workflows:
   ```yaml
   secureflow-repo: 'your-org/secureflow-core'
   ```

3. **Set up permissions** in your workflow:
   ```yaml
   permissions:
     security-events: write  # For SARIF upload
     contents: read         # For code checkout
     pull-requests: write   # For PR comments
   ```

## 🎯 Benefits of Using Actions

✅ **Clean Workflows**: No embedded Python code in YAML
✅ **Reusable**: Actions can be used across multiple workflows
✅ **Maintainable**: Centralized logic in action files
✅ **Testable**: Actions can be tested independently
✅ **Configurable**: Rich input/output interface
✅ **Error Handling**: Built-in error handling and validation
✅ **Type Safety**: Proper input validation and outputs

## 🔄 Migration from Inline Scripts

**Before** (Inline Python):
```yaml
- name: Run Security Scan
  run: |
    python -c "
    import asyncio
    from secureflow_core import SecureFlow
    # ... lots of Python code ...
    "
```

**After** (Actions):
```yaml
- name: Setup SecureFlow
  uses: ./.github/actions/setup-secureflow

- name: Run Security Scan
  uses: ./.github/actions/secureflow-scan
  with:
    project-type: 'java-maven'
    java-version: '17'
```

## 📋 Available Templates

- `java-maven-security-actions.yml` - Clean Java Maven workflow using actions
- `nodejs-security-actions.yml` - Node.js workflow with actions (coming soon)
- `python-security-actions.yml` - Python workflow with actions (coming soon)

The actions-based approach provides a much cleaner, more maintainable way to integrate SecureFlow-Core into your GitHub Actions workflows!
