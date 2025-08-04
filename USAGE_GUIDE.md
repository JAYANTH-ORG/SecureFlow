# SecureFlow-Core Usage Guide

This comprehensive guide provides step-by-step instructions for using SecureFlow-Core in various scenarios, from basic security scanning to advanced Azure DevOps integration.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Usage Scenarios](#basic-usage-scenarios)
3. [Azure DevOps Integration](#azure-devops-integration)
4. [Advanced Use Cases](#advanced-use-cases)
5. [Custom Plugin Development](#custom-plugin-development)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install secureflow-core

# With development tools
pip install secureflow-core[dev]

# With all optional dependencies
pip install secureflow-core[all]
```

### First Steps

```bash
# 1. Initialize SecureFlow in your project
cd /path/to/your/project
secureflow init

# 2. Run a quick security scan
secureflow scan all .

# 3. Generate a security report
secureflow report generate --input scan-results.json --format html
```

---

## 📝 Basic Usage Scenarios

### Scenario 1: Python Web Application Security Scan

**Use Case**: You have a Python Flask/Django application and want to scan for security vulnerabilities.

#### Step 1: Setup Configuration

Create `.secureflow.yaml` in your project root:

```yaml
project:
  name: "my-web-app"
  description: "Python web application"
  team: "backend-team"

scanning:
  sast_tool: "semgrep"
  sca_tool: "safety"
  secrets_tool: "trufflehog"
  severity_threshold: "medium"
  
  exclude_paths:
    - "venv/"
    - "migrations/"
    - "static/"
    - "tests/fixtures/"

reporting:
  formats: ["html", "json"]
  include_remediation: true
```

#### Step 2: Run Security Scans

```bash
# Scan for code vulnerabilities (SAST)
secureflow scan sast . --tool semgrep --severity medium

# Scan dependencies for known vulnerabilities
secureflow scan sca . --tool safety

# Check for exposed secrets
secureflow scan secrets . --tool trufflehog

# Run all scans at once
secureflow scan all . --output-format json --output-file security-results.json
```

#### Step 3: Generate and View Reports

```bash
# Generate HTML report
secureflow report generate \
  --input security-results.json \
  --format html \
  --output-dir reports/ \
  --include-charts

# Open the report
open reports/security-report.html
```

#### Step 4: Python Integration

```python
#!/usr/bin/env python3
"""
Example: Integrating SecureFlow into your Python application
"""
import asyncio
from secureflow_core import SecureFlow, Config

async def main():
    # Load configuration
    config = Config.from_file(".secureflow.yaml")
    
    # Initialize SecureFlow
    secureflow = SecureFlow(config)
    
    # Run security scans
    print("🔍 Running security scans...")
    
    # SAST scan
    sast_results = await secureflow.scan_source_code(".")
    print(f"SAST: Found {len(sast_results.vulnerabilities)} issues")
    
    # Dependency scan
    sca_results = await secureflow.scan_dependencies(".")
    print(f"SCA: Found {len(sca_results.vulnerabilities)} vulnerable dependencies")
    
    # Generate report
    from secureflow_core.report import ReportGenerator
    report_gen = ReportGenerator(config)
    
    report = await report_gen.generate_html_report([sast_results, sca_results])
    
    with open("security-report.html", "w") as f:
        f.write(report)
    
    print("✅ Security scan completed! Check security-report.html")

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Scenario 2: Container Security Scanning

**Use Case**: You have a Docker application and want to scan container images for vulnerabilities.

#### Step 1: Build and Scan Container

```bash
# Build your container
docker build -t myapp:latest .

# Scan the container image
secureflow scan container myapp:latest \
  --tool trivy \
  --severity HIGH,CRITICAL \
  --output-format json \
  --output-file container-scan.json
```

#### Step 2: Dockerfile Security Scan

```bash
# Scan Dockerfile for best practices
secureflow scan iac . \
  --tool checkov \
  --framework dockerfile \
  --output-format json
```

#### Step 3: Automated Container Pipeline

```python
#!/usr/bin/env python3
"""
Example: Container security scanning in CI/CD
"""
import asyncio
import sys
from secureflow_core import SecureFlow, Config

async def container_security_check(image_name: str):
    """Run comprehensive container security checks"""
    
    config = Config()
    secureflow = SecureFlow(config)
    
    print(f"🐳 Scanning container: {image_name}")
    
    # Scan container image
    container_results = await secureflow.scan_container(image_name)
    
    # Check for critical vulnerabilities
    critical_vulns = [
        v for v in container_results.vulnerabilities 
        if v.severity == "critical"
    ]
    
    if critical_vulns:
        print(f"❌ CRITICAL: Found {len(critical_vulns)} critical vulnerabilities!")
        for vuln in critical_vulns[:5]:  # Show first 5
            print(f"  - {vuln.title} ({vuln.cve_id})")
        return False
    
    print(f"✅ Container scan passed: {len(container_results.vulnerabilities)} total issues")
    return True

async def main():
    if len(sys.argv) != 2:
        print("Usage: python container_check.py <image_name>")
        sys.exit(1)
    
    image_name = sys.argv[1]
    success = await container_security_check(image_name)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Scenario 3: Infrastructure as Code (IaC) Security

**Use Case**: You have Terraform configurations and want to scan for security misconfigurations.

#### Step 1: Terraform Security Scan

```bash
# Scan Terraform files
secureflow scan iac ./terraform/ \
  --tool checkov \
  --framework terraform \
  --output-format json \
  --output-file iac-results.json

# Scan with specific policies
secureflow scan iac ./terraform/ \
  --tool tfsec \
  --policies CKV_AWS_20,CKV_AWS_23 \
  --exclude-paths terraform/modules/legacy/
```

#### Step 2: Multi-Cloud IaC Scanning

```python
#!/usr/bin/env python3
"""
Example: Multi-cloud infrastructure security scanning
"""
import asyncio
from pathlib import Path
from secureflow_core import SecureFlow, Config

async def scan_infrastructure():
    """Scan infrastructure configurations for multiple cloud providers"""
    
    config = Config()
    secureflow = SecureFlow(config)
    
    iac_paths = {
        "aws": "./terraform/aws/",
        "azure": "./terraform/azure/", 
        "gcp": "./terraform/gcp/",
        "kubernetes": "./k8s/"
    }
    
    results = {}
    
    for cloud, path in iac_paths.items():
        if Path(path).exists():
            print(f"🔍 Scanning {cloud.upper()} infrastructure...")
            
            scan_result = await secureflow.scan_infrastructure(path)
            results[cloud] = scan_result
            
            # Filter high severity issues
            high_issues = [
                v for v in scan_result.vulnerabilities 
                if v.severity in ["high", "critical"]
            ]
            
            print(f"  {cloud.upper()}: {len(high_issues)} high/critical issues")
    
    # Generate consolidated report
    from secureflow_core.report import ReportGenerator
    report_gen = ReportGenerator(config)
    
    all_results = list(results.values())
    report = await report_gen.generate_html_report(
        all_results,
        title="Multi-Cloud Infrastructure Security Report"
    )
    
    with open("infrastructure-security-report.html", "w") as f:
        f.write(report)
    
    print("✅ Infrastructure scan completed!")
    return results

if __name__ == "__main__":
    asyncio.run(scan_infrastructure())
```

---

## 🔄 Azure DevOps Integration

### Scenario 4: Basic Azure DevOps Pipeline Integration

**Use Case**: Add security scanning to your existing Azure DevOps pipeline.

#### Step 1: Add SecureFlow to Pipeline

Create `azure-pipelines-security.yml`:

```yaml
# Basic security pipeline
trigger:
  branches:
    include:
    - main
    - develop
  paths:
    exclude:
    - docs/*
    - README.md

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'

stages:
- stage: SecurityScan
  displayName: 'Security Scanning'
  jobs:
  - job: CodeSecurity
    displayName: 'Code Security Analysis'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
        addToPath: true

    - script: |
        python -m pip install --upgrade pip
        pip install secureflow-core
      displayName: 'Install SecureFlow'

    - script: |
        # Initialize SecureFlow
        secureflow init --project-type auto-detect
        
        # Run security scans
        secureflow scan all $(Build.SourcesDirectory) \
          --output-format sarif \
          --output-file $(Agent.TempDirectory)/security-results.sarif \
          --severity-threshold medium
      displayName: 'Run Security Scans'

    - task: PublishTestResults@2
      inputs:
        testResultsFormat: 'SARIF'
        testResultsFiles: '$(Agent.TempDirectory)/security-results.sarif'
        mergeTestResults: true
        failTaskOnFailedTests: true
        testRunTitle: 'Security Scan Results'
      displayName: 'Publish Security Results'
      condition: always()
```

#### Step 2: Advanced Pipeline with Work Items

```yaml
# Advanced security pipeline with Azure DevOps integration
stages:
- stage: SecurityScan
  displayName: 'Security Scanning'
  jobs:
  - job: ComprehensiveSecurity
    displayName: 'Comprehensive Security Analysis'
    steps:
    - template: azure-pipelines/steps/setup-secureflow.yml
    
    - script: |
        # Run comprehensive security scan
        secureflow scan all $(Build.SourcesDirectory) \
          --output-format json \
          --output-file $(Agent.TempDirectory)/security-results.json \
          --include-metrics \
          --parallel
      displayName: 'Comprehensive Security Scan'

    - script: |
        # Generate security report
        secureflow report generate \
          --input $(Agent.TempDirectory)/security-results.json \
          --format html,json,sarif \
          --output-dir $(Agent.TempDirectory)/reports \
          --include-charts \
          --include-remediation
      displayName: 'Generate Security Reports'

    - script: |
        # Create work items for high/critical issues
        secureflow azure create-work-items \
          --input $(Agent.TempDirectory)/security-results.json \
          --severity high,critical \
          --project $(System.TeamProject) \
          --area-path "Security/Vulnerabilities" \
          --assign-to "security@company.com"
      displayName: 'Create Security Work Items'
      env:
        AZURE_DEVOPS_PAT: $(AZURE_DEVOPS_PAT)

    - task: PublishHtmlReport@1
      inputs:
        reportDir: '$(Agent.TempDirectory)/reports'
        tabName: 'Security Dashboard'
      displayName: 'Publish Security Dashboard'
```

---

### Scenario 5: Multi-Stage Security Pipeline

**Use Case**: Implement security scanning across development, staging, and production environments.

#### Pipeline Configuration

```yaml
# Multi-environment security pipeline
trigger: none

pr:
  branches:
    include:
    - main

parameters:
- name: environment
  displayName: 'Target Environment'
  type: string
  default: 'development'
  values:
  - development
  - staging
  - production

variables:
- template: variables/${{ parameters.environment }}.yml

stages:
- stage: PreDeploymentSecurity
  displayName: 'Pre-Deployment Security'
  jobs:
  - job: StaticAnalysis
    displayName: 'Static Code Analysis'
    steps:
    - template: azure-pipelines/steps/setup-secureflow.yml
    
    - script: |
        # Environment-specific security configuration
        cat > .secureflow.yaml << EOF
        project:
          name: "$(Build.Repository.Name)"
          environment: "${{ parameters.environment }}"
        
        scanning:
          severity_threshold: "${{ variables.securityThreshold }}"
          sast_tool: "semgrep"
          sca_tool: "safety"
        
        azure:
          organization: "$(System.CollectionUri)"
          project: "$(System.TeamProject)"
        EOF
      displayName: 'Configure Environment Security'

    - script: |
        secureflow scan sast . --tool semgrep
        secureflow scan sca . --tool safety
        secureflow scan secrets . --tool trufflehog
      displayName: 'Static Security Scans'

- stage: RuntimeSecurity
  displayName: 'Runtime Security'
  dependsOn: PreDeploymentSecurity
  condition: and(succeeded(), ne('${{ parameters.environment }}', 'development'))
  jobs:
  - job: DynamicAnalysis
    displayName: 'Dynamic Security Testing'
    steps:
    - script: |
        # DAST scanning for staging/production
        secureflow scan dast "${{ variables.applicationUrl }}" \
          --tool zap \
          --auth-type oauth \
          --timeout 1800
      displayName: 'Dynamic Application Security Testing'
```

#### Environment Variables Files

Create `variables/development.yml`:

```yaml
variables:
  securityThreshold: 'low'
  applicationUrl: 'https://dev.myapp.com'
  notificationLevel: 'info'
```

Create `variables/production.yml`:

```yaml
variables:
  securityThreshold: 'high'
  applicationUrl: 'https://myapp.com'
  notificationLevel: 'critical'
```

---

## 🔧 Advanced Use Cases

### Scenario 6: Custom Security Dashboard

**Use Case**: Create a custom security dashboard that aggregates data from multiple repositories.

```python
#!/usr/bin/env python3
"""
Example: Custom security dashboard aggregating multiple repositories
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from secureflow_core import SecureFlow, Config
from secureflow_core.azure import AzureDevOpsClient

class SecurityDashboard:
    def __init__(self, azure_config: Dict[str, str]):
        self.azure_client = AzureDevOpsClient(azure_config)
        self.repositories = []
        self.scan_results = []
    
    async def add_repository(self, repo_path: str, config_path: str = None):
        """Add a repository to monitor"""
        config = Config.from_file(config_path) if config_path else Config()
        secureflow = SecureFlow(config)
        
        self.repositories.append({
            'path': repo_path,
            'secureflow': secureflow,
            'config': config
        })
    
    async def scan_all_repositories(self) -> List[Dict[str, Any]]:
        """Scan all registered repositories"""
        results = []
        
        for repo in self.repositories:
            print(f"🔍 Scanning {repo['path']}...")
            
            # Run comprehensive scan
            scan_result = await repo['secureflow'].scan_repository(repo['path'])
            
            # Aggregate metrics
            metrics = {
                'repository': repo['path'],
                'timestamp': datetime.now().isoformat(),
                'total_vulnerabilities': len(scan_result.vulnerabilities),
                'critical_count': len([v for v in scan_result.vulnerabilities if v.severity == 'critical']),
                'high_count': len([v for v in scan_result.vulnerabilities if v.severity == 'high']),
                'scan_duration': scan_result.scan_duration,
                'tools_used': list(set([v.tool for v in scan_result.vulnerabilities]))
            }
            
            results.append({
                'metrics': metrics,
                'scan_result': scan_result
            })
        
        self.scan_results = results
        return results
    
    async def generate_dashboard_report(self) -> str:
        """Generate HTML dashboard report"""
        if not self.scan_results:
            await self.scan_all_repositories()
        
        # Calculate dashboard metrics
        total_repos = len(self.scan_results)
        total_vulns = sum(r['metrics']['total_vulnerabilities'] for r in self.scan_results)
        critical_vulns = sum(r['metrics']['critical_count'] for r in self.scan_results)
        
        # Generate HTML report
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metric-card { 
                    border: 1px solid #ddd; 
                    padding: 20px; 
                    margin: 10px; 
                    border-radius: 5px; 
                    display: inline-block; 
                    min-width: 200px;
                }
                .critical { border-left: 5px solid #ff4444; }
                .warning { border-left: 5px solid #ffaa00; }
                .info { border-left: 5px solid #4444ff; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>🛡️ Security Dashboard</h1>
            <p>Generated: {timestamp}</p>
            
            <div class="metrics">
                <div class="metric-card info">
                    <h3>Total Repositories</h3>
                    <h2>{total_repos}</h2>
                </div>
                <div class="metric-card warning">
                    <h3>Total Vulnerabilities</h3>
                    <h2>{total_vulns}</h2>
                </div>
                <div class="metric-card critical">
                    <h3>Critical Issues</h3>
                    <h2>{critical_vulns}</h2>
                </div>
            </div>
            
            <h2>📊 Repository Details</h2>
            <table>
                <tr>
                    <th>Repository</th>
                    <th>Total Issues</th>
                    <th>Critical</th>
                    <th>High</th>
                    <th>Scan Duration</th>
                    <th>Tools Used</th>
                </tr>
                {repo_rows}
            </table>
            
            <canvas id="vulnerabilityChart" width="400" height="200"></canvas>
            
            <script>
                // Create vulnerability trend chart
                const ctx = document.getElementById('vulnerabilityChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: {repo_labels},
                        datasets: [{{
                            label: 'Critical',
                            data: {critical_data},
                            backgroundColor: 'rgba(255, 68, 68, 0.6)'
                        }}, {{
                            label: 'High',
                            data: {high_data},
                            backgroundColor: 'rgba(255, 170, 0, 0.6)'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        title: {{
                            display: true,
                            text: 'Vulnerability Distribution by Repository'
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        # Build repository rows
        repo_rows = ""
        repo_labels = []
        critical_data = []
        high_data = []
        
        for result in self.scan_results:
            metrics = result['metrics']
            repo_name = metrics['repository'].split('/')[-1]  # Get repo name
            repo_labels.append(repo_name)
            critical_data.append(metrics['critical_count'])
            high_data.append(metrics['high_count'])
            
            repo_rows += f"""
                <tr>
                    <td>{repo_name}</td>
                    <td>{metrics['total_vulnerabilities']}</td>
                    <td>{metrics['critical_count']}</td>
                    <td>{metrics['high_count']}</td>
                    <td>{metrics['scan_duration']:.2f}s</td>
                    <td>{', '.join(metrics['tools_used'])}</td>
                </tr>
            """
        
        return html_template.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_repos=total_repos,
            total_vulns=total_vulns,
            critical_vulns=critical_vulns,
            repo_rows=repo_rows,
            repo_labels=json.dumps(repo_labels),
            critical_data=json.dumps(critical_data),
            high_data=json.dumps(high_data)
        )
    
    async def update_azure_dashboard(self):
        """Update Azure DevOps dashboard with latest metrics"""
        if not self.scan_results:
            await self.scan_all_repositories()
        
        # Create dashboard data
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'repositories': len(self.scan_results),
            'total_vulnerabilities': sum(r['metrics']['total_vulnerabilities'] for r in self.scan_results),
            'critical_vulnerabilities': sum(r['metrics']['critical_count'] for r in self.scan_results),
            'scan_results': self.scan_results
        }
        
        # Update Azure DevOps dashboard
        await self.azure_client.update_dashboard(
            project="YourProject",
            dashboard_name="Security Overview",
            data=dashboard_data
        )

async def main():
    # Initialize dashboard
    azure_config = {
        'organization': 'your-org',
        'pat_token': 'your-pat-token'
    }
    
    dashboard = SecurityDashboard(azure_config)
    
    # Add repositories to monitor
    await dashboard.add_repository('/path/to/repo1', '.secureflow-repo1.yaml')
    await dashboard.add_repository('/path/to/repo2', '.secureflow-repo2.yaml')
    await dashboard.add_repository('/path/to/repo3')
    
    # Generate reports
    print("🔍 Scanning all repositories...")
    await dashboard.scan_all_repositories()
    
    print("📊 Generating dashboard...")
    html_report = await dashboard.generate_dashboard_report()
    
    with open('security-dashboard.html', 'w') as f:
        f.write(html_report)
    
    print("🔄 Updating Azure DevOps dashboard...")
    await dashboard.update_azure_dashboard()
    
    print("✅ Security dashboard updated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Scenario 7: Compliance Automation

**Use Case**: Automate compliance checking and reporting for SOC 2, PCI DSS, and HIPAA.

```python
#!/usr/bin/env python3
"""
Example: Automated compliance checking and reporting
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from secureflow_core import SecureFlow, Config
from secureflow_core.compliance import ComplianceChecker

async def compliance_audit_pipeline():
    """Run comprehensive compliance audit"""
    
    # Initialize compliance checker
    config = Config.from_file('.secureflow.yaml')
    compliance_checker = ComplianceChecker(config)
    secureflow = SecureFlow(config)
    
    print("🔍 Starting compliance audit...")
    
    # Run security scans first
    scan_results = await secureflow.scan_repository('.')
    
    # Check compliance for different frameworks
    frameworks = ['SOC2', 'PCI-DSS', 'HIPAA', 'NIST']
    compliance_results = {}
    
    for framework in frameworks:
        print(f"📋 Checking {framework} compliance...")
        
        result = await compliance_checker.check_compliance(
            framework=framework,
            scan_results=[scan_results],
            include_evidence=True
        )
        
        compliance_results[framework] = result
        
        # Print summary
        passed = sum(1 for check in result.checks if check.status == 'pass')
        failed = sum(1 for check in result.checks if check.status == 'fail')
        
        print(f"  {framework}: {passed} passed, {failed} failed")
    
    # Generate compliance reports
    print("📄 Generating compliance reports...")
    
    for framework, result in compliance_results.items():
        report_html = await compliance_checker.generate_compliance_report(
            result, 
            format='html',
            include_remediation=True
        )
        
        with open(f'compliance-{framework.lower()}.html', 'w') as f:
            f.write(report_html)
    
    # Generate executive summary
    executive_summary = generate_executive_summary(compliance_results)
    
    with open('compliance-executive-summary.html', 'w') as f:
        f.write(executive_summary)
    
    print("✅ Compliance audit completed!")
    return compliance_results

def generate_executive_summary(compliance_results: Dict[str, Any]) -> str:
    """Generate executive summary of compliance status"""
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Compliance Executive Summary</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
            .framework {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .pass {{ border-left: 5px solid #28a745; }}
            .fail {{ border-left: 5px solid #dc3545; }}
            .warning {{ border-left: 5px solid #ffc107; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .status-pass {{ color: #28a745; font-weight: bold; }}
            .status-fail {{ color: #dc3545; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ Compliance Executive Summary</h1>
            <p><strong>Generated:</strong> {timestamp}</p>
            <p><strong>Organization:</strong> Your Organization</p>
        </div>
        
        <h2>📊 Compliance Overview</h2>
        <table>
            <tr>
                <th>Framework</th>
                <th>Total Checks</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Compliance Rate</th>
                <th>Status</th>
            </tr>
            {framework_rows}
        </table>
        
        <h2>🎯 Key Findings</h2>
        {key_findings}
        
        <h2>🚀 Recommendations</h2>
        {recommendations}
        
        <h2>📈 Trend Analysis</h2>
        <p>This section would contain compliance trends over time when historical data is available.</p>
    </body>
    </html>
    """
    
    framework_rows = ""
    key_findings = ""
    
    for framework, result in compliance_results.items():
        total_checks = len(result.checks)
        passed = sum(1 for check in result.checks if check.status == 'pass')
        failed = total_checks - passed
        compliance_rate = (passed / total_checks * 100) if total_checks > 0 else 0
        
        status_class = "status-pass" if compliance_rate >= 90 else "status-fail"
        status_text = "✅ Compliant" if compliance_rate >= 90 else "❌ Non-Compliant"
        
        framework_rows += f"""
            <tr>
                <td>{framework}</td>
                <td>{total_checks}</td>
                <td>{passed}</td>
                <td>{failed}</td>
                <td>{compliance_rate:.1f}%</td>
                <td class="{status_class}">{status_text}</td>
            </tr>
        """
        
        # Add key findings for failed frameworks
        if compliance_rate < 90:
            failed_checks = [check for check in result.checks if check.status == 'fail']
            key_findings += f"""
            <div class="framework fail">
                <h3>{framework} - Critical Issues</h3>
                <ul>
            """
            for check in failed_checks[:3]:  # Show top 3 failures
                key_findings += f"<li>{check.title}: {check.description}</li>"
            key_findings += "</ul></div>"
    
    recommendations = """
    <div class="framework warning">
        <h3>Priority Actions</h3>
        <ol>
            <li><strong>Address Critical Security Issues:</strong> Focus on fixing high and critical severity vulnerabilities first.</li>
            <li><strong>Implement Access Controls:</strong> Ensure proper authentication and authorization mechanisms are in place.</li>
            <li><strong>Data Encryption:</strong> Implement encryption for data at rest and in transit.</li>
            <li><strong>Monitoring and Logging:</strong> Set up comprehensive security monitoring and audit logging.</li>
            <li><strong>Regular Security Reviews:</strong> Establish regular security assessments and code reviews.</li>
        </ol>
    </div>
    """
    
    return html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        framework_rows=framework_rows,
        key_findings=key_findings,
        recommendations=recommendations
    )

if __name__ == "__main__":
    asyncio.run(compliance_audit_pipeline())
```

---

## 🔌 Custom Plugin Development

### Scenario 8: Creating a Custom Security Plugin

**Use Case**: Develop a custom plugin to integrate with your organization's proprietary security tool.

```python
#!/usr/bin/env python3
"""
Example: Custom security plugin for proprietary tools
"""
from typing import List, Dict, Any, Optional
import asyncio
import json
from secureflow_core.plugins import ScannerPlugin
from secureflow_core.models import ScanResult, Vulnerability

class CustomSecurityPlugin(ScannerPlugin):
    """Custom plugin for proprietary security scanner"""
    
    name = "custom-security-scanner"
    version = "1.0.0"
    description = "Integration with CustomCorp Security Scanner"
    scan_type = "custom"
    
    def __init__(self):
        super().__init__()
        self.api_endpoint = None
        self.api_token = None
        self.timeout = 300
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration"""
        try:
            plugin_config = config.get('plugins', {}).get('custom-security-scanner', {})
            
            self.api_endpoint = plugin_config.get('api_endpoint')
            self.api_token = plugin_config.get('api_token')
            self.timeout = plugin_config.get('timeout', 300)
            
            if not self.api_endpoint or not self.api_token:
                self.logger.error("API endpoint and token are required")
                return False
            
            # Test connection
            test_result = await self._test_connection()
            if test_result:
                self.logger.info("Custom security scanner plugin initialized successfully")
                return True
            else:
                self.logger.error("Failed to connect to custom security scanner")
                return False
                
        except Exception as e:
            self.logger.error(f"Plugin initialization failed: {str(e)}")
            return False
    
    async def scan(self, target: str) -> ScanResult:
        """Run custom security scan"""
        import time
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting custom security scan on {target}")
            
            # Prepare scan request
            scan_request = {
                'target': target,
                'scan_type': 'comprehensive',
                'options': {
                    'deep_scan': True,
                    'include_dependencies': True,
                    'timeout': self.timeout
                }
            }
            
            # Submit scan to custom API
            scan_id = await self._submit_scan(scan_request)
            
            # Wait for scan completion
            scan_results = await self._wait_for_scan_completion(scan_id)
            
            # Parse results
            vulnerabilities = await self._parse_scan_results(scan_results)
            
            return ScanResult(
                tool=self.name,
                target=target,
                scan_type=self.scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                metadata={
                    'scan_id': scan_id,
                    'scanner_version': scan_results.get('scanner_version'),
                    'custom_metrics': scan_results.get('metrics', {})
                }
            )
            
        except Exception as e:
            self.logger.error(f"Custom security scan failed: {str(e)}")
            return self._create_error_result(target, str(e), start_time)
    
    async def _test_connection(self) -> bool:
        """Test connection to custom security scanner API"""
        try:
            import httpx
            
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_endpoint}/health",
                    headers=headers,
                    timeout=10
                )
                return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
    
    async def _submit_scan(self, scan_request: Dict[str, Any]) -> str:
        """Submit scan to custom API and return scan ID"""
        import httpx
        
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_endpoint}/scans",
                headers=headers,
                json=scan_request,
                timeout=30
            )
            
            if response.status_code != 201:
                raise Exception(f"Failed to submit scan: {response.text}")
            
            result = response.json()
            return result['scan_id']
    
    async def _wait_for_scan_completion(self, scan_id: str) -> Dict[str, Any]:
        """Wait for scan to complete and return results"""
        import httpx
        
        headers = {
            'Authorization': f'Bearer {self.api_token}'
        }
        
        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(
                    f"{self.api_endpoint}/scans/{scan_id}",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code != 200:
                    raise Exception(f"Failed to get scan status: {response.text}")
                
                result = response.json()
                status = result['status']
                
                if status == 'completed':
                    return result
                elif status == 'failed':
                    raise Exception(f"Scan failed: {result.get('error', 'Unknown error')}")
                elif status in ['queued', 'running']:
                    await asyncio.sleep(10)  # Wait 10 seconds before checking again
                else:
                    raise Exception(f"Unknown scan status: {status}")
    
    async def _parse_scan_results(self, scan_results: Dict[str, Any]) -> List[Vulnerability]:
        """Parse custom scanner results into SecureFlow format"""
        vulnerabilities = []
        
        for issue in scan_results.get('vulnerabilities', []):
            vuln = Vulnerability(
                id=issue.get('id', ''),
                title=issue.get('title', 'Unknown Vulnerability'),
                description=issue.get('description', ''),
                severity=self._map_severity(issue.get('severity', 'medium')),
                confidence=issue.get('confidence', 'medium'),
                file_path=issue.get('file_path', ''),
                line_number=issue.get('line_number', 0),
                column_number=issue.get('column_number', 0),
                cwe_id=issue.get('cwe_id', ''),
                cve_id=issue.get('cve_id', ''),
                tool=self.name,
                category=issue.get('category', 'security'),
                remediation=issue.get('remediation', ''),
                references=issue.get('references', []),
                metadata={
                    'custom_rule_id': issue.get('rule_id'),
                    'impact_score': issue.get('impact_score'),
                    'exploitability': issue.get('exploitability')
                }
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _map_severity(self, custom_severity: str) -> str:
        """Map custom severity levels to standard levels"""
        severity_mapping = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low',
            'info': 'info',
            # Custom mappings
            'severe': 'critical',
            'moderate': 'medium',
            'minor': 'low'
        }
        
        return severity_mapping.get(custom_severity.lower(), 'medium')
    
    def _create_error_result(self, target: str, error_message: str, start_time: float) -> ScanResult:
        """Create error result for failed scans"""
        import time
        
        return ScanResult(
            tool=self.name,
            target=target,
            scan_type=self.scan_type,
            vulnerabilities=[],
            scan_duration=time.time() - start_time,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            metadata={
                'error': error_message,
                'status': 'failed'
            }
        )

# Plugin registration and usage example
async def main():
    """Example of using the custom plugin"""
    from secureflow_core import SecureFlow, Config
    from secureflow_core.plugins import PluginManager
    
    # Load configuration
    config = Config.from_dict({
        'plugins': {
            'custom-security-scanner': {
                'api_endpoint': 'https://security-scanner.company.com/api/v1',
                'api_token': 'your-api-token-here',
                'timeout': 600
            }
        }
    })
    
    # Initialize plugin manager and register custom plugin
    plugin_manager = PluginManager()
    custom_plugin = CustomSecurityPlugin()
    
    await plugin_manager.register_plugin(custom_plugin)
    await plugin_manager.initialize_plugins(config.model_dump())
    
    # Use the plugin
    scan_result = await custom_plugin.scan('/path/to/code')
    
    print(f"Scan completed: {len(scan_result.vulnerabilities)} vulnerabilities found")
    for vuln in scan_result.vulnerabilities[:5]:  # Show first 5
        print(f"- {vuln.title} ({vuln.severity})")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Command not found" errors

**Problem**: Security tools (semgrep, safety, etc.) not installed

**Solution**:
```bash
# Install required security tools
pip install semgrep safety bandit

# For container scanning
sudo apt-get install docker.io
docker pull aquasec/trivy

# For IaC scanning
pip install checkov
```

#### Issue 2: Permission denied errors

**Problem**: Insufficient permissions for file access or tool execution

**Solution**:
```bash
# Fix file permissions
chmod +x /path/to/secureflow
chmod -R 755 /path/to/project

# For Docker scanning
sudo usermod -aG docker $USER
# Log out and log back in
```

#### Issue 3: Azure DevOps authentication failures

**Problem**: Invalid or expired PAT tokens

**Solution**:
```bash
# Set environment variables
export AZURE_DEVOPS_PAT="your-new-pat-token"
export AZURE_DEVOPS_ORG="your-organization"

# Test connection
secureflow azure test-connection
```

#### Issue 4: Scan timeouts

**Problem**: Large repositories causing scan timeouts

**Solution**:
```yaml
# In .secureflow.yaml
advanced:
  scan_timeout: 3600  # Increase to 1 hour
  parallel_scans: true
  max_workers: 8

scanning:
  exclude_paths:
    - "node_modules/"
    - "vendor/"
    - "*.min.js"
```

#### Issue 5: High false positive rates

**Problem**: Too many false positive security alerts

**Solution**:
```yaml
# Fine-tune scanning configuration
scanning:
  severity_threshold: "medium"  # Filter out low severity
  
  # Custom ignore patterns
  ignore_patterns:
    - "test/**"
    - "docs/**"
    - "*.test.js"
  
  # Tool-specific configurations
  tool_configs:
    semgrep:
      rules: "p/security-audit"
      exclude_rules: "generic.secrets"
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# CLI debug mode
secureflow --verbose scan all .

# Environment variable
export SECUREFLOW_LOG_LEVEL=DEBUG
secureflow scan all .
```

```python
# Python debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

from secureflow_core import SecureFlow, Config
config = Config(log_level="DEBUG")
```

### Support and Help

For additional help:

1. **Check logs**: Look in `.secureflow.log` for detailed error messages
2. **Validate configuration**: Use `secureflow config validate` to check your setup
3. **Test tools**: Run `secureflow doctor` to verify all dependencies
4. **Community**: Check GitHub issues and discussions
5. **Documentation**: Refer to the complete API documentation

---

This usage guide covers the most common scenarios for using SecureFlow-Core in real-world applications. Each example includes complete, working code that you can adapt to your specific needs.
