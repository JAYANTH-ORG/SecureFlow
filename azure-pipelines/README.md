# Azure DevOps Pipelines - SecureFlow Security Templates

This directory contains comprehensive Azure DevOps pipeline templates for security automation using SecureFlow-Core. Each template is designed for specific use cases and project types, providing enterprise-grade security scanning and compliance validation.

## 📋 Available Templates

### Core Templates

| Template | Purpose | Best For |
|----------|---------|----------|
| [secureflow-basic.yml](secureflow-basic.yml) | Multi-language basic security scanning | General projects, quick setup |
| [secureflow-comprehensive.yml](secureflow-comprehensive.yml) | Complete security coverage | Critical applications |
| [secureflow-enhanced.yml](secureflow-enhanced.yml) | Enhanced scanning with backward compatibility | Legacy Azure DevOps environments |

### Language-Specific Templates

| Template | Language/Framework | Features |
|----------|-------------------|----------|
| [secureflow-java-maven.yml](secureflow-java-maven.yml) | Java + Maven | Maven integration, OWASP dependency check, SpotBugs |
| [secureflow-nodejs.yml](secureflow-nodejs.yml) | Node.js | npm/yarn/pnpm support, license compliance, audit integration |
| [secureflow-python-web.yml](secureflow-python-web.yml) | Python Web Apps | Django/FastAPI/Flask, OWASP Top 10, API security, DAST |

### Specialized Templates

| Template | Specialization | Use Cases |
|----------|---------------|-----------|
| [secureflow-container.yml](secureflow-container.yml) | Container Security | Docker images, Kubernetes deployments, registry scanning |
| [secureflow-monorepo.yml](secureflow-monorepo.yml) | Monorepo Projects | Multi-project repos, differential scanning, dependency analysis |
| [secureflow-enterprise-azure.yml](secureflow-enterprise-azure.yml) | Enterprise Azure | Defender integration, Sentinel SIEM, Policy compliance |

## 🚀 Quick Start

### Basic Multi-Language Setup

```yaml
# azure-pipelines.yml
resources:
  repositories:
  - repository: secureflow-templates
    type: git
    name: your-org/secureflow-core
    ref: main

extends:
  template: azure-pipelines/secureflow-basic.yml@secureflow-templates
  parameters:
    project_type: 'auto-detect'  # Automatically detects Java, Node.js, Python, etc.
    scan_types: ['sast', 'sca', 'secrets']
    fail_on_high: true
```

### Java Maven Project

```yaml
extends:
  template: azure-pipelines/secureflow-java-maven.yml@secureflow-templates
  parameters:
    java_version: '17'
    maven_goals: 'clean compile test-compile'
    enable_owasp_check: true
    enable_spotbugs: true
    compliance_frameworks: ['SOC2', 'PCI-DSS']
```

### Node.js Application

```yaml
extends:
  template: azure-pipelines/secureflow-nodejs.yml@secureflow-templates
  parameters:
    node_version: '18'
    package_manager: 'auto-detect'  # Supports npm, yarn, pnpm
    enable_license_check: true
    audit_level: 'moderate'
```

### Python Web Application

```yaml
extends:
  template: azure-pipelines/secureflow-python-web.yml@secureflow-templates
  parameters:
    web_framework: 'auto-detect'  # Django, FastAPI, Flask
    enable_dast: true
    enable_api_security: true
    compliance_frameworks: ['OWASP-Top10', 'PCI-DSS']
```

### Container/Docker Projects

```yaml
extends:
  template: azure-pipelines/secureflow-container.yml@secureflow-templates
  parameters:
    dockerfile_path: 'Dockerfile'
    image_name: '$(Build.Repository.Name)'
    enable_trivy_scan: true
    enable_grype_scan: true
    enable_runtime_security: true
```

### Monorepo Projects

```yaml
extends:
  template: azure-pipelines/secureflow-monorepo.yml@secureflow-templates
  parameters:
    enable_differential_scan: true
    parallel_execution: true
    projects_config:
    - name: 'frontend'
      path: 'apps/frontend'
      type: 'nodejs'
      scan_types: ['sast', 'sca', 'secrets']
    - name: 'backend'
      path: 'apps/backend'
      type: 'java-maven'
      scan_types: ['sast', 'sca', 'secrets', 'dependencies']
```

### Enterprise Azure Integration

```yaml
extends:
  template: azure-pipelines/secureflow-enterprise-azure.yml@secureflow-templates
  parameters:
    azure_subscription_id: '$(AZURE_SUBSCRIPTION_ID)'
    key_vault_name: '$(KEY_VAULT_NAME)'
    enable_defender_integration: true
    enable_sentinel_integration: true
    compliance_frameworks: ['SOC2', 'PCI-DSS', 'ISO27001', 'NIST']
```

## 🔧 Configuration Options

### Common Parameters

All templates support these common parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repository_path` | string | `$(Build.SourcesDirectory)` | Path to scan |
| `scan_types` | array | `['sast', 'sca', 'secrets']` | Security scan types |
| `fail_on_high` | boolean | `true` | Fail pipeline on high severity issues |
| `enable_compliance_scan` | boolean | `false` | Enable compliance framework checks |

### Project Type Detection

The `secureflow-basic.yml` template automatically detects:

- **Java**: Maven (`pom.xml`) or Gradle (`build.gradle`)
- **Node.js**: Package.json with npm/yarn/pnpm detection
- **Python**: `requirements.txt`, `pyproject.toml`, or `setup.py`
- **.NET**: `*.csproj` or `*.sln` files
- **Go**: `go.mod` files
- **Rust**: `Cargo.toml` files
- **Generic**: Fallback for other project types

### Scan Types

Available scan types across templates:

- `sast`: Static Application Security Testing
- `sca`: Software Composition Analysis (dependencies)
- `secrets`: Secret/credential scanning
- `dast`: Dynamic Application Security Testing
- `container`: Container image vulnerability scanning
- `infrastructure`: Infrastructure as Code scanning
- `compliance`: Compliance framework validation

## 📊 Reports and Artifacts

All templates generate:

- **HTML Security Reports**: Comprehensive security analysis
- **JSON Results**: Machine-readable scan results
- **Compliance Reports**: Framework-specific compliance status
- **Executive Summaries**: High-level security overview

## 🔒 Security Best Practices

### Secrets Management

```yaml
# Use Azure Key Vault for sensitive configuration
variables:
- group: security-secrets  # Variable group linked to Key Vault
- name: API_KEY
  value: $(api-key-secret)  # Retrieved from Key Vault
```

### Service Connections

Configure these service connections in Azure DevOps:

- **Enterprise-Security-Connection**: Azure Resource Manager connection
- **Container-Registry-Connection**: Docker registry access
- **Security-Tools-Connection**: Third-party security tool APIs

### Variable Groups

Create variable groups for:

- `enterprise-security-secrets`: Key Vault-backed secrets
- `security-configuration`: Security tool configurations
- `compliance-settings`: Compliance framework settings

## 🚦 Security Gates

### Basic Gate Configuration

```yaml
# Security gate with customizable thresholds
- script: |
    secureflow gate check \
      --input-dir . \
      --fail-on-severity high \
      --max-high-issues 0 \
      --max-critical-issues 0
  displayName: 'Security Gate Check'
```

### Advanced Enterprise Gates

```yaml
# Enterprise security gate with multiple frameworks
- script: |
    secureflow gate check \
      --input-dir . \
      --fail-on-severity critical \
      --compliance-frameworks SOC2,PCI-DSS \
      --require-license-compliance \
      --max-critical-issues 0
  displayName: 'Enterprise Security Gate'
```

## 🔗 Integration Examples

### Microsoft Defender for DevOps

```yaml
# Automatic integration with Microsoft Defender
- task: AzureCLI@2
  inputs:
    azureSubscription: 'Enterprise-Security-Connection'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      secureflow integration defender \
        --subscription-id "$(AZURE_SUBSCRIPTION_ID)" \
        --workspace "$(SECURITY_CENTER_WORKSPACE)" \
        --input-dir . \
        --repository "$(Build.Repository.Name)"
```

### Azure Sentinel SIEM

```yaml
# Send security events to Azure Sentinel
- task: AzureCLI@2
  inputs:
    azureSubscription: 'Enterprise-Security-Connection'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      secureflow integration sentinel \
        --subscription-id "$(AZURE_SUBSCRIPTION_ID)" \
        --workspace "$(SENTINEL_WORKSPACE)" \
        --input-dir . \
        --event-type "DevSecOps-Scan"
```

### Teams Notifications

```yaml
# Teams webhook notification on completion
- script: |
    curl -H "Content-Type: application/json" \
      -d '{
        "@type": "MessageCard",
        "summary": "Security Scan Complete",
        "themeColor": "0076D7",
        "sections": [{
          "activityTitle": "Security Scan Completed",
          "activitySubtitle": "Repository: $(Build.Repository.Name)",
          "facts": [{"name": "Status", "value": "$(Agent.JobStatus)"}]
        }]
      }' \
      "$(TEAMS_WEBHOOK_URL)"
  displayName: 'Teams Notification'
  condition: always()
```

## 📈 Performance Optimization

### Caching Strategies

Templates include intelligent caching for:

- **Maven**: `$(Pipeline.Workspace)/.m2/repository`
- **Node.js**: `$(Pipeline.Workspace)/.npm`
- **Python**: `$(Pipeline.Workspace)/.pip`
- **Security Tools**: `$(Pipeline.Workspace)/.security-cache`

### Parallel Execution

```yaml
# Enable parallel scanning for monorepos
parameters:
  parallel_execution: true

strategy:
  parallel: 5  # Scan up to 5 projects simultaneously
```

### Differential Scanning

```yaml
# Only scan changed projects in monorepos
parameters:
  enable_differential_scan: true
```

## 🔧 Troubleshooting

### Common Issues

1. **Tool Installation Failures**
   ```yaml
   # Add error handling for tool installation
   - script: |
       pip install secureflow-core[all] || {
         echo "Primary installation failed, trying alternative..."
         pip install --index-url https://pypi.org/simple/ secureflow-core[all]
       }
   ```

2. **Permission Issues**
   ```yaml
   # Ensure proper permissions for security tools
   - script: |
       sudo chmod +x /usr/local/bin/security-tool
       sudo chown $(whoami) /tmp/security-cache
   ```

3. **Memory Constraints**
   ```yaml
   # Increase memory for large scans
   variables:
     MAVEN_OPTS: '-Xmx4g'
     NODE_OPTIONS: '--max-old-space-size=4096'
   ```

### Debug Mode

Enable debug logging:

```yaml
variables:
  SECUREFLOW_DEBUG: 'true'
  SYSTEM_DEBUG: 'true'
```

## 📚 Advanced Configuration

### Custom Security Rules

```yaml
# Use custom security rulesets
- script: |
    secureflow scan sast \
      --target . \
      --ruleset custom \
      --rules-file .secureflow/custom-rules.yaml
```

### Multi-Environment Scanning

```yaml
# Environment-specific configurations
- script: |
    case "$(ENVIRONMENT)" in
      "production")
        COMPLIANCE_FRAMEWORKS="SOC2,PCI-DSS,ISO27001"
        FAIL_ON_SEVERITY="medium"
        ;;
      "staging")
        COMPLIANCE_FRAMEWORKS="OWASP-Top10"
        FAIL_ON_SEVERITY="high"
        ;;
      "development")
        COMPLIANCE_FRAMEWORKS="OWASP-Top10"
        FAIL_ON_SEVERITY="critical"
        ;;
    esac
    
    secureflow scan comprehensive \
      --compliance-frameworks "$COMPLIANCE_FRAMEWORKS" \
      --fail-on-severity "$FAIL_ON_SEVERITY"
```

## 🤝 Contributing

To contribute new templates or improve existing ones:

1. Follow the template naming convention: `secureflow-{purpose}.yml`
2. Include comprehensive parameter documentation
3. Add example usage in this README
4. Test with multiple project types
5. Ensure compatibility with Azure DevOps versions 2019+

## 📄 License

These pipeline templates are part of the SecureFlow-Core project and are licensed under the same terms.

---

For more information, see the [SecureFlow-Core documentation](../README.md) and [usage guide](../docs/USAGE_GUIDE.md).
