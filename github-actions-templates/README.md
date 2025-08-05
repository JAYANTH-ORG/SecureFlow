# SecureFlow-Core GitHub Actions Integration

This directory contains GitHub Actions workflows and templates for integrating SecureFlow-Core into your CI/CD pipelines.

## 🚀 Quick Start

### 1. Copy a Template

Choose the appropriate template for your project:

- **Basic Security**: `github-actions-templates/basic-security.yml` - Essential security scanning with auto-detection
- **Java Maven**: `github-actions-templates/java-maven-security.yml` - Optimized for Maven Java projects with SecureFlow
- **Node.js Projects**: `github-actions-templates/nodejs-security.yml` - Optimized for npm/yarn/pnpm Node.js projects
- **Python Projects**: `github-actions-templates/python-security.yml` - Python-specific security analysis
- **Container Security**: `github-actions-templates/container-security.yml` - Docker/container security scanning

Copy the template to `.github/workflows/` in your repository.

### 2. Update the GitHub Repository Reference

Replace `your-org/secureflow-core` with the actual GitHub repository where SecureFlow-Core is hosted:

```yaml
- name: Install SecureFlow-Core from GitHub
  run: |
    pip install git+https://github.com/your-org/secureflow-core.git
```

### 3. Configure Permissions

Ensure your workflow has the necessary permissions:

```yaml
permissions:
  security-events: write  # For uploading SARIF results
  contents: read         # For checking out code
  pull-requests: write   # For PR comments
```

## 📋 Available Workflows

### Basic Security Workflow

**File**: `.github/workflows/security-basic.yml`

**Features**:
- ✅ Multi-language SAST scanning
- ✅ Dependency vulnerability scanning
- ✅ Secrets detection
- ✅ SARIF upload to GitHub Security tab
- ✅ PR comments with results
- ✅ Configurable scan types via workflow dispatch

**Triggers**:
- Push to main/develop branches
- Pull requests
- Daily schedule (2 AM UTC)
- Manual dispatch

### Comprehensive Security Workflow

**File**: `.github/workflows/security-comprehensive.yml`

**Features**:
- ✅ Multi-language security scanning matrix
- ✅ Infrastructure as Code (IaC) scanning
- ✅ Container security analysis
- ✅ Compliance reporting (SOC 2, PCI DSS, HIPAA)
- ✅ Executive dashboard generation
- ✅ GitHub Pages deployment
- ✅ Automatic issue creation for critical findings
- ✅ Parallel scanning for performance

**Triggers**:
- Weekly schedule (Sundays at 3 AM UTC)
- Manual dispatch with parameters

## 📋 Template Quick Reference

| Project Type | Template File | Package Manager | Key Features |
|-------------|---------------|-----------------|--------------|
| **Multi-language** | `basic-security.yml` | Auto-detected | 🔍 Auto project detection, basic security scans |
| **Java Maven** | `java-maven-security.yml` | Maven | ☕ SecureFlow integration, SAST, dependency scanning, SARIF output |
| **Node.js** | `nodejs-security.yml` | npm/yarn/pnpm | 📦 Package manager detection, license compliance, TypeScript support |
| **Python** | `python-security.yml` | pip/poetry/pipenv | 🐍 Python-specific tools, virtual environment support |
| **Container** | `container-security.yml` | Docker | 🐳 Multi-stage scanning, registry integration |

## 🔧 Custom Action: setup-secureflow

**Location**: `.github/actions/setup-secureflow/action.yml`

**Purpose**: Reusable action for installing and configuring SecureFlow-Core

**Inputs**:
- `python-version`: Python version (default: '3.11')
- `secureflow-version`: SecureFlow version (default: 'latest')
- `config-file`: Configuration file path (default: '.secureflow.yaml')
- `install-tools`: Install additional tools (default: 'true')

**Outputs**:
- `secureflow-version`: Installed version
- `config-path`: Configuration file path

**Usage**:
```yaml
- name: Setup SecureFlow
  uses: ./path/to/.github/actions/setup-secureflow
  with:
    python-version: '3.11'
    install-tools: 'true'
```

## 📖 Templates Usage Guide

### For Python Projects

1. Copy `github-actions-templates/python-security.yml` to `.github/workflows/python-security.yml`
2. Update the action reference
3. Customize scan tools if needed:

```yaml
- name: Run SAST with Semgrep
  run: |
    secureflow scan sast . \
      --tool semgrep \
      --rules "p/python" \
      --exclude-paths "tests/,docs/"
```

### For Node.js Projects

1. Copy `github-actions-templates/nodejs-security.yml` to `.github/workflows/nodejs-security.yml`
2. Update the action reference
3. The template automatically detects your package manager (npm, yarn, or pnpm)

**Key Features**:
- 🔍 **Package Manager Detection**: Automatically detects npm, yarn, or pnpm
- 📦 **Dependency Auditing**: Runs security audits with your package manager
- 🔧 **TypeScript Support**: Auto-detects and configures TypeScript scanning
- 📋 **License Compliance**: Checks for problematic licenses
- 🚨 **Known Vulnerabilities**: Cross-references with CVE databases
- 🔨 **Build Integration**: Attempts to build project for better analysis

**Customization Example**:
```yaml
- name: Run Node.js security scan
  run: |
    secureflow scan all . \
      --nodejs-project \
      --typescript \
      --package-manager npm \
      --severity-threshold medium \
      --include-build-files
```

**Package Manager Support**:
- **npm**: Uses `npm ci` and `npm audit`
- **Yarn**: Uses `yarn install --frozen-lockfile` and `yarn audit`
- **pnpm**: Uses `pnpm install --frozen-lockfile` and `pnpm audit`

### For Java Maven Projects

1. Copy `github-actions-templates/java-maven-security.yml` to `.github/workflows/java-security.yml`
2. Update the GitHub repository reference:

```yaml
- name: Install SecureFlow-Core from GitHub
  run: |
    pip install git+https://github.com/your-org/secureflow-core.git
```

3. The workflow will automatically:
   - Detect Java/Maven project structure
   - Compile the project for better analysis
   - Run comprehensive security scans (SAST, secrets, dependencies, containers)
   - Generate SARIF output for GitHub Security tab
   - Upload scan artifacts

**Java Version Support**: The workflow supports Java 8-21 and will use the configured Maven local repository.

**Scan Types**:
- **SAST**: Static analysis with Semgrep for Java-specific vulnerability patterns
- **Secret Detection**: TruffleHog for hardcoded credentials and API keys
- **Dependency Scanning**: Maven dependency vulnerability analysis
- **Container Scanning**: Docker image security if Dockerfile present

### For Container Projects

1. Copy `github-actions-templates/container-security.yml` to `.github/workflows/container-security.yml`
2. Update the action reference
3. Customize container scanning:

```yaml
- name: Scan container image
  run: |
    secureflow scan container myapp:latest \
      --tool trivy \
      --severity HIGH,CRITICAL \
      --output-format sarif
```

### For Infrastructure Projects

Use the comprehensive workflow which includes IaC scanning for:
- Terraform configurations
- Kubernetes manifests
- Docker configurations
- CloudFormation templates

## ⚙️ Configuration

### Environment Variables

Set these in your repository settings:

```yaml
env:
  # Optional: Custom SecureFlow configuration
  SECUREFLOW_CONFIG: '.secureflow.yaml'
  
  # Optional: Tool-specific tokens
  SEMGREP_API_TOKEN: ${{ secrets.SEMGREP_API_TOKEN }}
  SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

### Repository Secrets

Add these secrets in your repository settings:

- `GITHUB_TOKEN`: Automatically provided
- `SEMGREP_API_TOKEN`: For Semgrep Pro features (optional)
- `SNYK_TOKEN`: For Snyk scanning (optional)

### SecureFlow Configuration

Create a `.secureflow.yaml` file in your repository root:

```yaml
project:
  name: "my-project"
  team: "development"

scanning:
  sast_tool: "semgrep"
  sca_tool: "safety"
  severity_threshold: "medium"
  
  exclude_paths:
    - "tests/"
    - "docs/"
    - "vendor/"

github:
  repository: "${{ github.repository }}"
  create_issues: true
  comment_on_pr: true

reporting:
  formats: ["html", "sarif"]
  include_remediation: true
```

## 🔍 Understanding Results

### SARIF Upload

Results are automatically uploaded to GitHub's Security tab where you can:
- View vulnerabilities in context
- Track remediation progress
- Set up security alerts
- Review historical trends

### Artifact Reports

Detailed HTML reports are uploaded as workflow artifacts:
- Executive summary
- Detailed vulnerability listings
- Remediation guidance
- Compliance status

### PR Comments

Automated comments on pull requests include:
- Security scan summary
- Critical/high issue counts
- Links to detailed reports
- Blocking recommendations for critical issues

## 🚨 Security Gates

### Failing Builds

Workflows will fail the build if:
- Critical severity vulnerabilities are found
- Scan tools fail to execute
- Configuration is invalid

### Customizing Failure Conditions

```yaml
- name: Custom security gate
  run: |
    # Fail on 5+ high severity issues
    HIGH_COUNT=$(python -c "...")
    if [ "$HIGH_COUNT" -gt 5 ]; then
      echo "Too many high severity issues: $HIGH_COUNT"
      exit 1
    fi
```

## 📊 GitHub Pages Dashboard

The comprehensive workflow automatically deploys a security dashboard to GitHub Pages:

1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions"
3. Dashboard will be available at `https://your-org.github.io/your-repo`

Dashboard includes:
- Executive summary
- Vulnerability trends
- Compliance status
- Interactive charts

## 🔄 Integration with Existing Workflows

### Adding to Existing CI/CD

```yaml
jobs:
  # Your existing jobs
  test:
    runs-on: ubuntu-latest
    steps:
      # Your test steps
      
  # Add security scanning
  security:
    needs: test
    uses: ./.github/workflows/security-basic.yml
    
  # Only deploy if security passes
  deploy:
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      # Your deployment steps
```

### Matrix Builds with Security

```yaml
strategy:
  matrix:
    python-version: [3.8, 3.9, 3.10, 3.11]
    
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v4
    with:
      python-version: ${{ matrix.python-version }}
  
  # Run tests
  - run: pytest
  
  # Run security scan (only on one Python version)
  - name: Security scan
    if: matrix.python-version == '3.11'
    uses: your-org/secureflow-core/.github/actions/setup-secureflow@main
  - run: secureflow scan all .
    if: matrix.python-version == '3.11'
```

## 🛠️ Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure workflow has `security-events: write` permission
2. **Tool Not Found**: Use `install-tools: 'true'` in setup-secureflow action
3. **SARIF Upload Failed**: Check file paths and ensure SARIF format is valid
4. **Configuration Error**: Validate `.secureflow.yaml` syntax

### Debug Mode

Enable debug logging:

```yaml
- name: Setup SecureFlow
  uses: ./path/to/.github/actions/setup-secureflow
  env:
    SECUREFLOW_LOG_LEVEL: DEBUG
```

### Custom Tool Installation

```yaml
- name: Install custom tools
  run: |
    # Install additional security tools
    pip install custom-scanner
    npm install -g security-tool
    
- name: Setup SecureFlow
  uses: ./path/to/.github/actions/setup-secureflow
  with:
    install-tools: 'false'  # Skip default tools
```

## 📚 Examples

See the `examples/` directory for complete working examples:
- Python web application
- Node.js API
- Docker multi-stage builds
- Terraform infrastructure
- Kubernetes applications

## 🔗 Related Links

- [SecureFlow-Core Documentation](../../README.md)
- [Usage Guide](../../USAGE_GUIDE.md)
- [Azure DevOps Integration](../../azure-pipelines/)
- [GitHub Security Features](https://docs.github.com/en/code-security)

---

*For more information about SecureFlow-Core, see the [main documentation](../../README.md).*
