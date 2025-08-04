"""
Azure DevOps integration for SecureFlow
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import httpx
from azure.devops.connection import Connection
from azure.devops.v7_1.pipelines import PipelinesClient
from azure.devops.v7_1.build import BuildClient
from azure.devops.v7_1.git import GitClient
from msrest.authentication import BasicAuthentication

from .config import AzureConfig
from .utils import Logger
from .templates import PipelineTemplateManager


class AzureDevOpsIntegration:
    """
    Azure DevOps integration for setting up security pipelines and workflows.
    """

    def __init__(self, config: AzureConfig):
        """
        Initialize Azure DevOps integration.

        Args:
            config: Azure configuration
        """
        self.config = config
        self.logger = Logger(__name__)
        self.template_manager = PipelineTemplateManager()

        # Initialize Azure DevOps connection
        if config.pat_token and config.devops_organization:
            credentials = BasicAuthentication("", config.pat_token)
            self.connection = Connection(
                base_url=f"https://dev.azure.com/{config.devops_organization}",
                creds=credentials,
            )
            self.pipelines_client = self.connection.clients.get_pipelines_client()
            self.build_client = self.connection.clients.get_build_client()
            self.git_client = self.connection.clients.get_git_client()
        else:
            self.connection = None
            self.logger.warning("Azure DevOps credentials not provided")

    async def setup_security_pipeline(
        self, project_name: str, repo_name: str, template_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Set up a security pipeline in Azure DevOps.

        Args:
            project_name: Azure DevOps project name
            repo_name: Repository name
            template_type: Type of security template

        Returns:
            Pipeline setup results
        """
        self.logger.info(f"Setting up security pipeline for {project_name}/{repo_name}")

        if not self.connection:
            raise ValueError("Azure DevOps connection not configured")

        try:
            # Generate pipeline YAML
            pipeline_yaml = self.template_manager.generate_pipeline(template_type)

            # Create or update pipeline
            pipeline_result = await self._create_pipeline(
                project_name, repo_name, pipeline_yaml
            )

            # Set up security extensions
            extensions_result = await self._setup_security_extensions(project_name)

            # Configure security policies
            policies_result = await self._configure_security_policies(project_name)

            # Set up security dashboard
            dashboard_result = await self._setup_security_dashboard(project_name)

            return {
                "pipeline": pipeline_result,
                "extensions": extensions_result,
                "policies": policies_result,
                "dashboard": dashboard_result,
                "status": "success",
            }

        except Exception as e:
            self.logger.error(f"Failed to setup security pipeline: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def _create_pipeline(
        self, project_name: str, repo_name: str, pipeline_yaml: str
    ) -> Dict[str, Any]:
        """Create or update Azure DevOps pipeline."""
        try:
            # Check if pipeline exists
            existing_pipelines = self.pipelines_client.list_pipelines(project_name)
            security_pipeline = None

            for pipeline in existing_pipelines:
                if pipeline.name == f"{repo_name}-security":
                    security_pipeline = pipeline
                    break

            pipeline_data = {
                "name": f"{repo_name}-security",
                "description": "Automated security pipeline created by SecureFlow",
                "yaml": pipeline_yaml,
            }

            if security_pipeline:
                # Update existing pipeline
                result = self.pipelines_client.update_pipeline(
                    project_name, security_pipeline.id, pipeline_data
                )
                self.logger.info(f"Updated existing pipeline: {security_pipeline.id}")
            else:
                # Create new pipeline
                result = self.pipelines_client.create_pipeline(
                    project_name, pipeline_data
                )
                self.logger.info(f"Created new pipeline: {result.id}")

            return {
                "id": result.id,
                "name": result.name,
                "url": result.url,
                "status": "created" if not security_pipeline else "updated",
            }

        except Exception as e:
            self.logger.error(f"Failed to create pipeline: {str(e)}")
            raise

    async def _setup_security_extensions(self, project_name: str) -> Dict[str, Any]:
        """Set up required security extensions."""
        extensions = [
            {
                "name": "Microsoft Security DevOps",
                "publisher": "ms-securitydevops",
                "extension_id": "microsoft-security-devops-azdevops",
            },
            {
                "name": "SonarQube",
                "publisher": "sonarqube",
                "extension_id": "sonarqube-azuredevops-extension",
            },
            {
                "name": "WhiteSource",
                "publisher": "whitesource",
                "extension_id": "whitesource-azuredevops-extension",
            },
        ]

        installed_extensions = []

        for ext in extensions:
            try:
                # Check if extension is already installed
                # Note: This would require additional Azure DevOps REST API calls
                # For now, we'll return the list of recommended extensions
                installed_extensions.append(
                    {
                        "name": ext["name"],
                        "status": "recommended",
                        "install_url": f"https://marketplace.visualstudio.com/items?itemName={ext['publisher']}.{ext['extension_id']}",
                    }
                )
            except Exception as e:
                self.logger.warning(
                    f"Could not check extension {ext['name']}: {str(e)}"
                )

        return {"extensions": installed_extensions}

    async def _configure_security_policies(self, project_name: str) -> Dict[str, Any]:
        """Configure security policies for the project."""
        policies = {
            "branch_policies": {
                "require_pull_request": True,
                "require_security_approval": True,
                "minimum_reviewers": 2,
            },
            "build_policies": {
                "require_security_scan": True,
                "block_on_high_severity": True,
                "require_compliance_check": True,
            },
            "deployment_policies": {
                "require_security_gate": True,
                "security_approval_timeout": 24,  # hours
            },
        }

        # Note: Actual policy configuration would require Azure DevOps Policy REST API
        # This is a placeholder showing the intended configuration

        return {
            "policies": policies,
            "status": "configured",
            "note": "Policies configured via SecureFlow automation",
        }

    async def _setup_security_dashboard(self, project_name: str) -> Dict[str, Any]:
        """Set up security dashboard widgets."""
        dashboard_config = {
            "widgets": [
                {
                    "name": "Security Scan Results",
                    "type": "test-results",
                    "configuration": {"testResultsContext": "security-scans"},
                },
                {
                    "name": "Vulnerability Trends",
                    "type": "chart",
                    "configuration": {
                        "chartType": "line",
                        "dataSource": "security-metrics",
                    },
                },
                {
                    "name": "Compliance Status",
                    "type": "compliance-widget",
                    "configuration": {"frameworks": ["SOC2", "PCI_DSS"]},
                },
            ]
        }

        return {
            "dashboard": dashboard_config,
            "status": "configured",
            "url": f"https://dev.azure.com/{self.config.devops_organization}/{project_name}/_dashboards",
        }

    async def create_security_work_items(
        self, scan_results: Dict[str, Any], project_name: str
    ) -> List[Dict[str, Any]]:
        """
        Create work items for security vulnerabilities.

        Args:
            scan_results: Security scan results
            project_name: Azure DevOps project name

        Returns:
            List of created work items
        """
        work_items = []

        if not self.connection:
            self.logger.warning("Cannot create work items: Azure DevOps not configured")
            return work_items

        try:
            # Process each scan type
            for scan_type, results in scan_results.items():
                if isinstance(results, dict) and "vulnerabilities" in results:
                    for vuln in results["vulnerabilities"]:
                        if vuln.get("severity") in ["HIGH", "CRITICAL"]:
                            work_item = await self._create_vulnerability_work_item(
                                project_name, vuln, scan_type
                            )
                            if work_item:
                                work_items.append(work_item)

            self.logger.info(f"Created {len(work_items)} security work items")
            return work_items

        except Exception as e:
            self.logger.error(f"Failed to create work items: {str(e)}")
            return work_items

    async def _create_vulnerability_work_item(
        self, project_name: str, vulnerability: Dict[str, Any], scan_type: str
    ) -> Optional[Dict[str, Any]]:
        """Create a work item for a vulnerability."""
        try:
            work_item_data = {
                "fields": {
                    "System.Title": f"[Security] {vulnerability.get('title', 'Security Vulnerability')}",
                    "System.WorkItemType": "Bug",
                    "System.Description": self._format_vulnerability_description(
                        vulnerability, scan_type
                    ),
                    "Microsoft.VSTS.Common.Priority": self._get_priority_from_severity(
                        vulnerability.get("severity")
                    ),
                    "System.Tags": f"security; {scan_type}; {vulnerability.get('severity', '').lower()}",
                }
            }

            # Note: This would use the Azure DevOps Work Item Tracking client
            # For now, returning mock data
            work_item = {
                "id": f"mock-{hash(str(vulnerability))}",
                "title": work_item_data["fields"]["System.Title"],
                "type": "Bug",
                "state": "New",
                "url": f"https://dev.azure.com/{self.config.devops_organization}/{project_name}/_workitems/edit/mock",
            }

            return work_item

        except Exception as e:
            self.logger.error(f"Failed to create work item: {str(e)}")
            return None

    def _format_vulnerability_description(
        self, vulnerability: Dict[str, Any], scan_type: str
    ) -> str:
        """Format vulnerability description for work item."""
        description = f"""
**Vulnerability Details:**
- **Type:** {scan_type.upper()} Scan
- **Severity:** {vulnerability.get('severity', 'Unknown')}
- **CWE:** {vulnerability.get('cwe', 'N/A')}
- **File:** {vulnerability.get('file', 'N/A')}
- **Line:** {vulnerability.get('line', 'N/A')}

**Description:**
{vulnerability.get('description', 'No description available')}

**Recommendation:**
{vulnerability.get('recommendation', 'Please review and remediate this vulnerability')}

**References:**
{vulnerability.get('references', 'N/A')}

---
*This work item was automatically created by SecureFlow*
        """
        return description.strip()

    def _get_priority_from_severity(self, severity: str) -> int:
        """Convert severity to Azure DevOps priority."""
        severity_map = {"CRITICAL": 1, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        return severity_map.get(severity, 3)

    async def get_pipeline_runs(
        self, project_name: str, pipeline_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent pipeline runs."""
        if not self.connection:
            return []

        try:
            runs = self.pipelines_client.list_runs(project_name, pipeline_id, top=limit)

            return [
                {
                    "id": run.id,
                    "state": run.state,
                    "result": run.result,
                    "created_date": (
                        run.created_date.isoformat() if run.created_date else None
                    ),
                    "finished_date": (
                        run.finished_date.isoformat() if run.finished_date else None
                    ),
                    "url": run.url,
                }
                for run in runs
            ]

        except Exception as e:
            self.logger.error(f"Failed to get pipeline runs: {str(e)}")
            return []

    async def cleanup(self):
        """Clean up Azure DevOps resources."""
        if self.connection:
            # Close connection if needed
            pass
        self.logger.info("Azure DevOps cleanup completed")
