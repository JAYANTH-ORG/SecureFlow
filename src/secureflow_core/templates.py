"""
Azure DevOps pipeline templates for SecureFlow
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml

from .utils import Logger


class PipelineTemplateManager:
    """Manages Azure DevOps pipeline templates"""

    def __init__(self):
        self.logger = Logger(__name__)
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize built-in pipeline templates"""
        return {
            "basic": self._get_basic_template(),
            "comprehensive": self._get_comprehensive_template(),
            "compliance": self._get_compliance_template(),
        }

    def generate_pipeline(self, template_type: str, **kwargs) -> str:
        """Generate pipeline YAML for specified template type"""
        if template_type not in self.templates:
            raise ValueError(f"Unknown template type: {template_type}")

        template = self.templates[template_type]

        # Convert to YAML
        return yaml.dump(template, default_flow_style=False, sort_keys=False)

    def _get_basic_template(self) -> Dict[str, Any]:
        """Basic security pipeline template"""
        return {
            "trigger": {"branches": {"include": ["main", "develop"]}},
            "pool": {"vmImage": "ubuntu-latest"},
            "variables": [{"template": "variables/security-vars.yml"}],
            "stages": [
                {
                    "stage": "SecurityScan",
                    "displayName": "Security Scanning",
                    "jobs": [
                        {
                            "job": "SAST",
                            "displayName": "Static Analysis",
                            "steps": [
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "3.11"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": "secureflow scan --types sast --output sast-results.json --format json",
                                    "displayName": "Run SAST Scan",
                                },
                                {
                                    "task": "PublishTestResults@2",
                                    "inputs": {
                                        "testResultsFiles": "sast-results.xml",
                                        "testRunTitle": "SAST Results",
                                    },
                                    "condition": "always()",
                                },
                            ],
                        }
                    ],
                }
            ],
        }

    def _get_comprehensive_template(self) -> Dict[str, Any]:
        """Comprehensive security pipeline template"""
        return {
            "trigger": {"branches": {"include": ["main", "develop", "release/*"]}},
            "pr": {"branches": {"include": ["main", "develop"]}},
            "pool": {"vmImage": "ubuntu-latest"},
            "variables": [
                {"template": "variables/security-vars.yml"},
                {"name": "SECUREFLOW_LOG_LEVEL", "value": "INFO"},
                {"name": "SECUREFLOW_FAIL_ON_HIGH", "value": "true"},
            ],
            "stages": [
                {
                    "stage": "SecurityPreCheck",
                    "displayName": "Security Pre-Check",
                    "jobs": [
                        {
                            "job": "PreFlightCheck",
                            "displayName": "Pre-flight Security Check",
                            "steps": [
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "3.11"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": "secureflow scan --types secrets --fail-on high",
                                    "displayName": "Secret Scan (Fail Fast)",
                                },
                            ],
                        }
                    ],
                },
                {
                    "stage": "ComprehensiveScan",
                    "displayName": "Comprehensive Security Scan",
                    "dependsOn": "SecurityPreCheck",
                    "condition": "succeeded()",
                    "jobs": [
                        {
                            "job": "StaticAnalysis",
                            "displayName": "Static Application Security Testing",
                            "steps": [
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "3.11"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": "secureflow scan --types sast --output $(Agent.TempDirectory)/sast-results.json --format json",
                                    "displayName": "Run SAST Scan",
                                },
                                {
                                    "task": "PublishBuildArtifacts@1",
                                    "inputs": {
                                        "pathToPublish": "$(Agent.TempDirectory)/sast-results.json",
                                        "artifactName": "sast-results",
                                    },
                                },
                            ],
                        },
                        {
                            "job": "DependencyAnalysis",
                            "displayName": "Software Composition Analysis",
                            "steps": [
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "3.11"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": "secureflow scan --types sca --output $(Agent.TempDirectory)/sca-results.json --format json",
                                    "displayName": "Run SCA Scan",
                                },
                                {
                                    "task": "PublishBuildArtifacts@1",
                                    "inputs": {
                                        "pathToPublish": "$(Agent.TempDirectory)/sca-results.json",
                                        "artifactName": "sca-results",
                                    },
                                },
                            ],
                        },
                        {
                            "job": "InfrastructureAnalysis",
                            "displayName": "Infrastructure as Code Security",
                            "steps": [
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "3.11"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": "secureflow scan --types iac --output $(Agent.TempDirectory)/iac-results.json --format json",
                                    "displayName": "Run IaC Scan",
                                },
                                {
                                    "task": "PublishBuildArtifacts@1",
                                    "inputs": {
                                        "pathToPublish": "$(Agent.TempDirectory)/iac-results.json",
                                        "artifactName": "iac-results",
                                    },
                                },
                            ],
                        },
                        {
                            "job": "ContainerSecurity",
                            "displayName": "Container Security Scan",
                            "condition": "and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))",
                            "steps": [
                                {
                                    "task": "Docker@2",
                                    "displayName": "Build Docker Image",
                                    "inputs": {
                                        "command": "build",
                                        "dockerfile": "Dockerfile",
                                        "tags": "$(Build.Repository.Name):$(Build.BuildId)",
                                    },
                                },
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "3.11"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": "secureflow scan --types container --target $(Build.Repository.Name):$(Build.BuildId) --output $(Agent.TempDirectory)/container-results.json --format json",
                                    "displayName": "Run Container Scan",
                                },
                                {
                                    "task": "PublishBuildArtifacts@1",
                                    "inputs": {
                                        "pathToPublish": "$(Agent.TempDirectory)/container-results.json",
                                        "artifactName": "container-results",
                                    },
                                },
                            ],
                        },
                    ],
                },
                {
                    "stage": "SecurityReporting",
                    "displayName": "Security Report Generation",
                    "dependsOn": "ComprehensiveScan",
                    "condition": "always()",
                    "jobs": [
                        {
                            "job": "GenerateReport",
                            "displayName": "Generate Security Report",
                            "steps": [
                                {
                                    "task": "DownloadBuildArtifacts@0",
                                    "inputs": {
                                        "downloadType": "current",
                                        "downloadPath": "$(Agent.TempDirectory)",
                                    },
                                },
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "3.11"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": """
python -c "
import json
import glob
import os

# Combine all scan results
results = {}
for result_file in glob.glob('$(Agent.TempDirectory)/*-results/*.json'):
    scan_type = os.path.basename(result_file).replace('-results.json', '')
    with open(result_file, 'r') as f:
        results[scan_type] = json.load(f)

# Save combined results
with open('combined-results.json', 'w') as f:
    json.dump(results, f, indent=2)
"
                                    """,
                                    "displayName": "Combine Scan Results",
                                },
                                {
                                    "script": "secureflow report --scan-results combined-results.json --output security-report.html --format html",
                                    "displayName": "Generate HTML Report",
                                },
                                {
                                    "task": "PublishBuildArtifacts@1",
                                    "inputs": {
                                        "pathToPublish": "security-report.html",
                                        "artifactName": "security-report",
                                    },
                                },
                                {
                                    "task": "PublishTestResults@2",
                                    "inputs": {
                                        "testResultsFormat": "JUnit",
                                        "testResultsFiles": "**/*-results.xml",
                                        "testRunTitle": "Security Scan Results",
                                    },
                                    "condition": "always()",
                                },
                            ],
                        }
                    ],
                },
                {
                    "stage": "SecurityGates",
                    "displayName": "Security Quality Gates",
                    "dependsOn": "ComprehensiveScan",
                    "condition": "and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))",
                    "jobs": [
                        {
                            "job": "QualityGateCheck",
                            "displayName": "Security Quality Gate",
                            "steps": [
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "3.11"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": "secureflow scan --all --fail-on high",
                                    "displayName": "Security Quality Gate Check",
                                },
                            ],
                        }
                    ],
                },
            ],
        }

    def _get_compliance_template(self) -> Dict[str, Any]:
        """Compliance-focused pipeline template"""
        return {
            "trigger": {
                "branches": {"include": ["main"]},
                "schedules": [
                    {
                        "cron": "0 2 * * 0",  # Weekly on Sunday at 2 AM
                        "displayName": "Weekly Compliance Check",
                        "branches": {"include": ["main"]},
                    }
                ],
            },
            "pool": {"vmImage": "ubuntu-latest"},
            "variables": [{"template": "variables/compliance-vars.yml"}],
            "stages": [
                {
                    "stage": "ComplianceCheck",
                    "displayName": "Compliance Validation",
                    "jobs": [
                        {
                            "job": "SOC2Compliance",
                            "displayName": "SOC 2 Compliance Check",
                            "steps": [
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "3.11"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": "secureflow compliance --framework SOC2 --output soc2-compliance.json --format json",
                                    "displayName": "Run SOC 2 Compliance Check",
                                },
                                {
                                    "task": "PublishBuildArtifacts@1",
                                    "inputs": {
                                        "pathToPublish": "soc2-compliance.json",
                                        "artifactName": "soc2-compliance",
                                    },
                                },
                            ],
                        },
                        {
                            "job": "PCIDSSCompliance",
                            "displayName": "PCI DSS Compliance Check",
                            "steps": [
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "3.11"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": "secureflow compliance --framework PCI_DSS --output pci-compliance.json --format json",
                                    "displayName": "Run PCI DSS Compliance Check",
                                },
                                {
                                    "task": "PublishBuildArtifacts@1",
                                    "inputs": {
                                        "pathToPublish": "pci-compliance.json",
                                        "artifactName": "pci-compliance",
                                    },
                                },
                            ],
                        },
                    ],
                },
                {
                    "stage": "ComplianceReporting",
                    "displayName": "Compliance Reporting",
                    "dependsOn": "ComplianceCheck",
                    "condition": "always()",
                    "jobs": [
                        {
                            "job": "GenerateComplianceReport",
                            "displayName": "Generate Compliance Report",
                            "steps": [
                                {
                                    "task": "DownloadBuildArtifacts@0",
                                    "inputs": {
                                        "downloadType": "current",
                                        "downloadPath": "$(Agent.TempDirectory)",
                                    },
                                },
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "3.11"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": """
python -c "
import json
import glob

# Combine compliance results
compliance_results = {}
for result_file in glob.glob('$(Agent.TempDirectory)/*-compliance/*.json'):
    framework = result_file.split('-compliance')[0].split('/')[-1]
    with open(result_file, 'r') as f:
        compliance_results[framework] = json.load(f)

# Generate comprehensive compliance report
# This would use the SecureFlow compliance reporting functionality
print('Compliance results processed')
"
                                    """,
                                    "displayName": "Process Compliance Results",
                                },
                                {
                                    "task": "PublishBuildArtifacts@1",
                                    "inputs": {
                                        "pathToPublish": "compliance-report.html",
                                        "artifactName": "compliance-report",
                                    },
                                },
                            ],
                        }
                    ],
                },
            ],
        }

    def create_variable_templates(self, output_dir: str):
        """Create variable template files"""
        output_path = Path(output_dir)
        variables_dir = output_path / "variables"
        variables_dir.mkdir(parents=True, exist_ok=True)

        # Security variables
        security_vars = {
            "variables": {
                "SECUREFLOW_LOG_LEVEL": "INFO",
                "SECUREFLOW_OUTPUT_FORMAT": "json",
                "SECUREFLOW_FAIL_ON_HIGH": "true",
                "SECUREFLOW_CACHE_ENABLED": "true",
                "PYTHON_VERSION": "3.11",
            }
        }

        with open(variables_dir / "security-vars.yml", "w") as f:
            yaml.dump(security_vars, f, default_flow_style=False)

        # Compliance variables
        compliance_vars = {
            "variables": {
                "COMPLIANCE_FRAMEWORKS": "SOC2,PCI_DSS",
                "COMPLIANCE_REPORT_FORMAT": "json",
                "COMPLIANCE_OUTPUT_DIR": "$(Agent.TempDirectory)/compliance",
            }
        }

        with open(variables_dir / "compliance-vars.yml", "w") as f:
            yaml.dump(compliance_vars, f, default_flow_style=False)

        self.logger.info(f"Created variable templates in {variables_dir}")

    def create_pipeline_templates(self, output_dir: str):
        """Create pipeline template files"""
        output_path = Path(output_dir)
        templates_dir = output_path / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)

        # Security scan stage template
        security_stage = {
            "parameters": [
                {
                    "name": "scanTypes",
                    "type": "object",
                    "default": ["sast", "sca", "secrets"],
                },
                {"name": "failOnHigh", "type": "boolean", "default": True},
            ],
            "stages": [
                {
                    "stage": "SecurityScan",
                    "displayName": "Security Scanning",
                    "jobs": [
                        {
                            "job": "RunSecurityScans",
                            "displayName": "Run Security Scans",
                            "steps": [
                                {
                                    "task": "UsePythonVersion@0",
                                    "inputs": {"versionSpec": "$(PYTHON_VERSION)"},
                                },
                                {
                                    "script": "pip install secureflow-core",
                                    "displayName": "Install SecureFlow",
                                },
                                {
                                    "script": "secureflow scan --types ${{ join(',', parameters.scanTypes) }} ${{ parameters.failOnHigh and '--fail-on high' or '' }}",
                                    "displayName": "Run Security Scans",
                                },
                            ],
                        }
                    ],
                }
            ],
        }

        with open(templates_dir / "security-scan-stage.yml", "w") as f:
            yaml.dump(security_stage, f, default_flow_style=False)

        self.logger.info(f"Created pipeline templates in {templates_dir}")

    def save_all_templates(self, output_dir: str):
        """Save all templates to directory"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save main pipeline templates
        for template_name, template_content in self.templates.items():
            filename = f"azure-pipelines-{template_name}.yml"
            with open(output_path / filename, "w") as f:
                yaml.dump(
                    template_content, f, default_flow_style=False, sort_keys=False
                )

        # Create supporting templates
        self.create_variable_templates(str(output_path))
        self.create_pipeline_templates(str(output_path))

        self.logger.info(f"Saved all templates to {output_path}")
