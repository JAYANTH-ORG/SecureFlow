"""
Core SecureFlow class - Main entry point for the library
"""

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

from .config import Config
from .scanner import Scanner
from .azure import AzureDevOpsIntegration
from .compliance import ComplianceChecker
from .plugins import PluginManager
from .utils import Logger, SecurityMetrics
from .report import ReportGenerator


class SecureFlow:
    """
    Main SecureFlow class that orchestrates all security operations.

    This is the primary interface for teams to interact with the SecureFlow
    shared library for DevSecOps automation.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize SecureFlow with configuration.

        Args:
            config: Configuration object. If None, loads from environment/file.
        """
        self.config = config or Config.load()
        self.logger = Logger(__name__)

        # Initialize core components
        self.scanner = Scanner(self.config.scanning)
        self.azure = (
            AzureDevOpsIntegration(self.config.azure) if self.config.azure else None
        )
        self.compliance = ComplianceChecker(self.config.compliance)
        self.plugins = PluginManager()
        self.metrics = SecurityMetrics()
        self.report = ReportGenerator(self.config)

        self.logger.info("SecureFlow initialized successfully")

    async def scan_repository(self, repo_path: str = ".") -> Dict[str, Any]:
        """
        Perform comprehensive security scanning on a repository.

        Args:
            repo_path: Path to the repository to scan

        Returns:
            Dictionary containing all scan results
        """
        self.logger.info(f"Starting repository scan: {repo_path}")

        results = {}

        # Source code analysis (SAST)
        if self.config.scanning.enable_sast:
            self.logger.info("Running SAST scan...")
            results["sast"] = await self.scanner.scan_source_code(repo_path)

        # Dependency scanning (SCA)
        if self.config.scanning.enable_sca:
            self.logger.info("Running dependency scan...")
            results["sca"] = await self.scanner.scan_dependencies(repo_path)

        # Secret scanning
        if self.config.scanning.enable_secrets:
            self.logger.info("Running secret scan...")
            results["secrets"] = await self.scanner.scan_secrets(repo_path)

        # Infrastructure as Code scanning
        if self.config.scanning.enable_iac:
            self.logger.info("Running IaC scan...")
            results["iac"] = await self.scanner.scan_infrastructure(repo_path)

        # Container scanning (if Dockerfile present)
        dockerfile_path = Path(repo_path) / "Dockerfile"
        if dockerfile_path.exists() and self.config.scanning.enable_container:
            self.logger.info("Running container scan...")
            results["container"] = await self.scanner.scan_container(
                str(dockerfile_path)
            )

        # Update metrics
        self.metrics.record_scan_completion(results)

        self.logger.info("Repository scan completed")
        return results

    async def generate_security_report(
        self, scan_results: Dict[str, Any], output_path: Optional[str] = None
    ) -> str:
        """
        Generate a comprehensive security report from scan results.

        Args:
            scan_results: Results from security scans
            output_path: Optional path to save the report

        Returns:
            Path to the generated report
        """
        return await self.report.generate_comprehensive_report(
            scan_results, output_path
        )

    async def check_compliance(
        self, frameworks: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Check compliance against security frameworks.

        Args:
            frameworks: List of frameworks to check against

        Returns:
            Compliance check results
        """
        frameworks = frameworks or self.config.compliance.frameworks
        return await self.compliance.check_compliance(frameworks)

    async def setup_azure_pipeline(
        self, project_name: str, repo_name: str, template_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Set up Azure DevOps pipeline with security integration.

        Args:
            project_name: Azure DevOps project name
            repo_name: Repository name
            template_type: Type of security template to use

        Returns:
            Pipeline setup results
        """
        if not self.azure:
            raise ValueError("Azure configuration not provided")

        return await self.azure.setup_security_pipeline(
            project_name, repo_name, template_type
        )

    def get_security_metrics(self) -> Dict[str, Any]:
        """
        Get current security metrics and statistics.

        Returns:
            Dictionary containing security metrics
        """
        return self.metrics.get_metrics()

    async def auto_remediate(
        self, scan_results: Dict[str, Any], auto_apply: bool = False
    ) -> Dict[str, Any]:
        """
        Attempt automatic remediation of security issues.

        Args:
            scan_results: Results from security scans
            auto_apply: Whether to automatically apply fixes

        Returns:
            Remediation results and suggested fixes
        """
        remediation_results = {}

        for scan_type, results in scan_results.items():
            if hasattr(self.scanner, f"remediate_{scan_type}"):
                remediate_func = getattr(self.scanner, f"remediate_{scan_type}")
                remediation_results[scan_type] = await remediate_func(
                    results, auto_apply
                )

        return remediation_results

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

    async def cleanup(self):
        """Clean up resources."""
        if self.azure:
            await self.azure.cleanup()
        self.logger.info("SecureFlow cleanup completed")
