# SecureFlow Core - Shared DevSecOps Library

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Azure DevOps](https://img.shields.io/badge/Azure_DevOps-Ready-blue.svg)](https://azure.microsoft.com/en-us/services/devops/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Ready-green.svg)](https://github.com/features/actions)

A comprehensive, modern shared DevSecOps library that teams can integrate into any repository for automated security scanning, vulnerability management, compliance checking, and seamless CI/CD integration with Azure DevOps and GitHub Actions.

## 🚀 Features

### Core Security Capabilities
- **🔍 Vulnerability Scanning**: SAST, DAST, SCA, and container security
- **🛡️ Compliance Automation**: SOC 2, PCI DSS, HIPAA, and custom policies
- **🔧 Auto-Remediation**: Intelligent fix suggestions and automated patching
- **📊 Security Metrics**: Real-time dashboards and reporting
- **🔐 Secret Management**: Azure Key Vault integration and secret scanning

### CI/CD Platform Integration
- **📋 Pipeline Templates**: Ready-to-use YAML templates for Azure DevOps and GitHub Actions
- **🔄 Automated Workflows**: CI/CD security integration for multiple platforms
- **📈 Dashboard Integration**: Security metrics in Azure DevOps and GitHub Pages
- **🚪 Quality Gates**: Automated security approval processes
- **🐙 GitHub Actions**: Comprehensive workflows, reusable actions, and SARIF integration

### Modern Architecture
- **🐍 Python 3.8+**: Modern Python with type hints
- **⚡ Async Support**: High-performance async operations
- **🧩 Plugin System**: Extensible architecture
- **📦 Easy Integration**: Simple pip install and configuration
- **🎯 CLI Tools**: Command-line interface for all operations

## 📦 Installation

```bash
# Install the core library
pip install secureflow-core

# Install with development dependencies
pip install secureflow-core[dev]

# Install with documentation dependencies
pip install secureflow-core[docs]
```

## 🚀 Quick Start

### 1. Basic Setup

```python
from secureflow_core import SecureFlow, Config

# Initialize with default configuration
sf = SecureFlow()

# Or with custom configuration
config = Config(
    azure_tenant_id="your-tenant-id",
    azure_client_id="your-client-id",
    azure_subscription_id="your-subscription-id"
)
sf = SecureFlow(config)
```

### 2. Security Scanning

```python
# Scan source code for vulnerabilities
results = await sf.scan.source_code("./src")

# Scan dependencies
dependency_results = await sf.scan.dependencies("requirements.txt")

# Scan Docker images
container_results = await sf.scan.container("myapp:latest")

# Generate security report
report = sf.report.generate(results, dependency_results, container_results)
```

### 3. Azure DevOps Integration

```python
# Create security pipeline
pipeline = sf.azure.create_security_pipeline(
    project="MyProject",
    repository="MyRepo",
    template="comprehensive-security"
)

# Add security gates
sf.azure.add_security_gate(
    pipeline_id=pipeline.id,
    stage="production",
    policies=["high-severity-block", "compliance-check"]
)
```

### 4. CLI Usage

```bash
# Initialize in a repository
secureflow init

# Run security scan
secureflow scan --all

# Generate compliance report
secureflow report --format json --output compliance.json

# Deploy Azure DevOps templates
secureflow azure deploy-templates --project MyProject
```

## 🎯 What Can SecureFlow Scan?

SecureFlow-Core supports a wide range of application types and technologies:

### **Application Types**
🌐 **Web Apps** (React, Vue, Angular, APIs)  
📱 **Mobile Apps** (iOS, Android, React Native, Flutter)  
🖥️ **Desktop Apps** (Electron, Native)  
☁️ **Cloud-Native** (Containers, Serverless, Kubernetes)  
🏗️ **Infrastructure** (Terraform, CloudFormation, ARM)  

### **Programming Languages**  
🐍 Python • 🟨 JavaScript/TypeScript • ☕ Java • 🔷 C#/.NET • 🐹 Go • 💎 Ruby • 🐘 PHP • and more...

### **Security Scan Types**
🔍 **SAST** - Source code vulnerabilities  
📦 **SCA** - Dependency vulnerabilities  
🔐 **Secrets** - Hardcoded credentials  
🏗️ **IaC** - Infrastructure misconfigurations  
🐳 **Container** - Image & runtime security  

## 📚 Documentation

### **Quick Access**
- 📋 **[Complete Documentation Index](./DOCUMENTATION_INDEX.md)** - Navigate all documentation by role
- 🎯 **[Quick Reference](./QUICK_REFERENCE.md)** - Commands and scan types
- 📊 **[Comprehensive Analysis](./COMPREHENSIVE_ANALYSIS.md)** - Technical deep-dive and roadmap
- 📚 **[Usage Guide](./USAGE_GUIDE.md)** - Detailed scenarios and examples

### **By Role**
- 👩‍💻 **Developers**: [README.md](./README.md) → [Quick Reference](./QUICK_REFERENCE.md) → [Examples](./examples/)
- 🔧 **DevOps**: [Azure DevOps](./azure-pipelines/) | [GitHub Actions](./github-actions-templates/) → [Compatibility Guide](./COMPATIBILITY_GUIDE.md)
- 🏢 **Technical Leaders**: [Comprehensive Analysis](./COMPREHENSIVE_ANALYSIS.md) → [Project Summary](./PROJECT_SUMMARY.md)
- 🛡️ **Security Teams**: [Supported Applications](./SUPPORTED_APPLICATIONS.md) → [Usage Guide](./USAGE_GUIDE.md)

**See the complete list**: [📋 Supported Applications](./SUPPORTED_APPLICATIONS.md) | [🎯 Quick Reference](./QUICK_REFERENCE.md) | [📊 Comprehensive Analysis](./COMPREHENSIVE_ANALYSIS.md)

## 🏗️ Azure DevOps Pipeline Integration

### Example Pipeline Template

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
    - main
    - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  - template: variables/security-vars.yml

stages:
  - template: templates/security-scan-stage.yml
  - template: templates/build-stage.yml
  - template: templates/security-test-stage.yml
  - template: templates/deploy-stage.yml
```

### Security Scan Stage Template

```yaml
# templates/security-scan-stage.yml
parameters:
  - name: scanTypes
    type: object
    default:
      - sast
      - dast
      - sca
      - secrets

stages:
- stage: SecurityScan
  displayName: 'Security Scanning'
  jobs:
  - job: SecurityAnalysis
    displayName: 'Security Analysis'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.11'
        
    - script: |
        pip install secureflow-core
        secureflow scan --types ${{ join(',', parameters.scanTypes) }}
      displayName: 'Run Security Scans'
      
    - task: PublishTestResults@2
      inputs:
        testResultsFiles: 'security-results.xml'
        testRunTitle: 'Security Scan Results'
```

## 🔄 Azure DevOps Pipeline Integration

SecureFlow provides ready-to-use Azure DevOps pipeline templates for comprehensive security scanning.

### Basic Security Pipeline

Add this to your `azure-pipelines.yml`:

```yaml
# Basic security scanning pipeline
resources:
  repositories:
  - repository: secureflow-templates
    type: git
    name: secureflow-core
    ref: main

stages:
- template: azure-pipelines/secureflow-basic.yml@secureflow-templates
  parameters:
    repository_path: '$(Build.SourcesDirectory)'
    scan_types: ['sast', 'sca', 'secrets']
    fail_on_high: true
```

### Comprehensive Security Pipeline

For advanced security scanning with compliance reporting:

```yaml
# Comprehensive security pipeline
resources:
  repositories:
  - repository: secureflow-templates
    type: git
    name: secureflow-core
    ref: main

stages:
- template: azure-pipelines/secureflow-comprehensive.yml@secureflow-templates
  parameters:
    repository_path: '$(Build.SourcesDirectory)'
    container_image: 'myapp:latest'
    compliance_frameworks: ['SOC2', 'PCI-DSS']
    notification_email: 'security@company.com'
```

### Custom Pipeline Integration

You can also integrate SecureFlow into existing pipelines:

```yaml
# In your existing azure-pipelines.yml
stages:
- stage: Security
  displayName: 'Security Scanning'
  jobs:
  - job: SecureFlowScan
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.11'
    
    - script: |
        pip install secureflow-core
        secureflow scan all $(Build.SourcesDirectory) --output-format sarif
      displayName: 'Run Security Scans'
    
    - task: PublishTestResults@2
      inputs:
        testResultsFormat: 'SARIF'
        testResultsFiles: '**/*.sarif'
      displayName: 'Publish Security Results'
```

### Environment Variables

Configure these Azure DevOps variables for full functionality:

```yaml
variables:
  # Required for Azure DevOps integration
  AZURE_DEVOPS_PAT: $(AZURE_DEVOPS_PAT)  # Personal Access Token
  
  # Optional notification webhooks
  TEAMS_WEBHOOK_URL: $(TEAMS_WEBHOOK_URL)
  SLACK_WEBHOOK_URL: $(SLACK_WEBHOOK_URL)
  
  # External service tokens
  GITHUB_TOKEN: $(GITHUB_TOKEN)
  JIRA_TOKEN: $(JIRA_TOKEN)
```

### Service Connections

Set up these service connections in Azure DevOps:

1. **Azure Key Vault** - For secret management
2. **Container Registry** - For container scanning
3. **External Services** - For third-party integrations

## 🐙 GitHub Actions Integration

SecureFlow provides comprehensive GitHub Actions workflows and reusable actions for seamless CI/CD security integration.

### Quick Setup

1. **Copy a workflow template** to `.github/workflows/` in your repository:
   - [`github-actions-templates/basic-security.yml`](./github-actions-templates/basic-security.yml) - Essential security scanning
   - [`github-actions-templates/python-security.yml`](./github-actions-templates/python-security.yml) - Python-specific security
   - [`github-actions-templates/container-security.yml`](./github-actions-templates/container-security.yml) - Container security

2. **Update the action reference** in your workflow:
   ```yaml
   - name: Setup SecureFlow
     uses: your-org/secureflow-core/.github/actions/setup-secureflow@main
   ```

3. **Configure repository permissions**:
   ```yaml
   permissions:
     security-events: write  # For SARIF upload
     contents: read         # For checkout
     pull-requests: write   # For PR comments
   ```

### Basic GitHub Actions Workflow

```yaml
name: 🛡️ Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
      pull-requests: write
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup SecureFlow
      uses: your-org/secureflow-core/.github/actions/setup-secureflow@main
    
    - name: Run security scans
      run: |
        secureflow scan all . \
          --output-format sarif \
          --output-file security-results.sarif
    
    - name: Upload SARIF results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: security-results.sarif
```

### Advanced Features

- **🔄 Matrix scanning** across multiple languages and environments
- **📊 Executive dashboards** deployed to GitHub Pages
- **🚨 Automatic issue creation** for critical security findings
- **💬 PR comments** with security scan summaries
- **🏗️ Infrastructure scanning** (Terraform, Kubernetes, Docker)
- **📋 Compliance reporting** (SOC 2, PCI DSS, HIPAA)

For detailed GitHub Actions documentation, see [`github-actions-templates/README.md`](./github-actions-templates/README.md).

## ⚙️ Configuration

### Quick Configuration

Initialize SecureFlow in your repository:

```bash
# Initialize with interactive setup
secureflow init

# Initialize with defaults
secureflow init --project-type auto-detect

# Initialize for specific project type
secureflow init --project-type python-web-app
```

### Configuration File

Create a `.secureflow.yaml` file in your repository root:

```yaml
# Minimal configuration
project:
  name: "my-project"
  team: "development"

scanning:
  sast_tool: "semgrep"
  sca_tool: "safety"
  severity_threshold: "medium"
  
azure:
  organization: "your-org"
  project: "your-project"
  
reporting:
  formats: ["html", "json", "sarif"]
```

For a complete configuration example, see [`.secureflow.example.yaml`](./.secureflow.example.yaml).

### Environment-Specific Configuration

Use environment variables for sensitive data:

```bash
# Azure DevOps
export AZURE_DEVOPS_PAT="your-pat-token"
export AZURE_DEVOPS_ORG="your-organization"

# External Services
export GITHUB_TOKEN="your-github-token"
export SLACK_WEBHOOK_URL="your-slack-webhook"

# Security Tools
export SEMGREP_API_TOKEN="your-semgrep-token"
```

### Configuration Example

```python
# config.py or environment variables
SECUREFLOW_CONFIG = {
    "azure": {
        "tenant_id": "your-tenant-id",
        "client_id": "your-client-id",
        "subscription_id": "your-subscription-id"
    },
    "scanning": {
        "tools": {
            "sast": "semgrep",
            "dast": "zap",
            "sca": "safety"
        },
        "severity_threshold": "medium",
        "fail_on_high": True
    },
    "compliance": {
        "frameworks": ["SOC2", "PCI_DSS"],
        "custom_policies": "./policies/"
    }
}
```

### Plugin Development

```python
from secureflow_core.plugins import BasePlugin

class CustomScannerPlugin(BasePlugin):
    name = "custom-scanner"
    version = "1.0.0"
    
    async def scan(self, target: str) -> ScanResult:
        # Implement your custom scanning logic
        return ScanResult(
            tool=self.name,
            target=target,
            vulnerabilities=vulnerabilities
        )
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/codevibe/secureflow-core.git
cd secureflow-core

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=secureflow_core

# Run specific test file
pytest tests/test_scanner.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [Azure DevOps CLI](https://docs.microsoft.com/en-us/azure/devops/cli/)
- [Microsoft Security DevOps](https://github.com/microsoft/security-devops)
- [Azure Security Center](https://azure.microsoft.com/en-us/services/security-center/)

## 📞 Support

- 📧 Email: support@codevibe.com
- 💬 Discussions: [GitHub Discussions](https://github.com/codevibe/secureflow-core/discussions)
- 🐛 Issues: [GitHub Issues](https://github.com/codevibe/secureflow-core/issues)

---

Made with ❤️ by the CodeVibe Team

### Backward Compatibility

SecureFlow supports multiple environment configurations:

- **Modern Environments** - Use standard workflows with latest action versions
- **Legacy Environments** - Use `.github/workflows/security-compatible.yml` for:
  - GitHub Enterprise Server 3.4-3.5
  - Self-hosted runners with older Node.js versions
  - Environments requiring older action versions

For detailed compatibility information and troubleshooting, see [COMPATIBILITY_GUIDE.md](./COMPATIBILITY_GUIDE.md).
