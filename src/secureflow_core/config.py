"""
Configuration management for SecureFlow
"""

import os
import json
import yaml
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class AzureConfig(BaseModel):
    """Azure-specific configuration"""

    tenant_id: Optional[str] = Field(None, description="Azure tenant ID")
    client_id: Optional[str] = Field(None, description="Azure client ID")
    client_secret: Optional[str] = Field(None, description="Azure client secret")
    subscription_id: Optional[str] = Field(None, description="Azure subscription ID")
    resource_group: Optional[str] = Field(None, description="Azure resource group")
    devops_organization: Optional[str] = Field(
        None, description="Azure DevOps organization"
    )
    pat_token: Optional[str] = Field(None, description="Personal Access Token")
    key_vault_url: Optional[str] = Field(None, description="Azure Key Vault URL")


class ScanningConfig(BaseModel):
    """Security scanning configuration"""

    enable_sast: bool = Field(True, description="Enable SAST scanning")
    enable_dast: bool = Field(True, description="Enable DAST scanning")
    enable_sca: bool = Field(True, description="Enable SCA scanning")
    enable_secrets: bool = Field(True, description="Enable secret scanning")
    enable_iac: bool = Field(True, description="Enable IaC scanning")
    enable_container: bool = Field(True, description="Enable container scanning")

    # Tool configurations
    sast_tool: str = Field("semgrep", description="SAST tool to use")
    dast_tool: str = Field("zap", description="DAST tool to use")
    sca_tool: str = Field("safety", description="SCA tool to use")
    secrets_tool: str = Field("trufflehog", description="Secret scanning tool")
    iac_tool: str = Field("checkov", description="IaC scanning tool")
    container_tool: str = Field("trivy", description="Container scanning tool")

    # Severity settings
    severity_threshold: str = Field("medium", description="Minimum severity to report")
    fail_on_high: bool = Field(True, description="Fail build on high severity issues")
    fail_on_critical: bool = Field(True, description="Fail build on critical issues")

    # Exclusions
    exclude_paths: List[str] = Field(
        default_factory=lambda: [
            ".git",
            ".venv",
            "node_modules",
            "__pycache__",
            "*.pyc",
            "*.log",
        ]
    )
    exclude_rules: List[str] = Field(
        default_factory=list, description="Rules to exclude"
    )


class ComplianceConfig(BaseModel):
    """Compliance framework configuration"""

    frameworks: List[str] = Field(
        default_factory=lambda: ["SOC2", "PCI_DSS"],
        description="Compliance frameworks to check",
    )
    custom_policies_path: Optional[str] = Field(
        None, description="Path to custom policies"
    )
    generate_reports: bool = Field(True, description="Generate compliance reports")
    report_format: str = Field("json", description="Report format (json, xml, pdf)")


class NotificationConfig(BaseModel):
    """Notification configuration"""

    enable_email: bool = Field(False, description="Enable email notifications")
    enable_slack: bool = Field(False, description="Enable Slack notifications")
    enable_teams: bool = Field(False, description="Enable Teams notifications")

    email_recipients: List[str] = Field(default_factory=list)
    slack_webhook: Optional[str] = Field(None)
    teams_webhook: Optional[str] = Field(None)

    notify_on_high: bool = Field(True, description="Notify on high severity issues")
    notify_on_critical: bool = Field(True, description="Notify on critical issues")
    notify_on_compliance_fail: bool = Field(
        True, description="Notify on compliance failures"
    )


class Config(BaseModel):
    """Main configuration class for SecureFlow"""

    azure: Optional[AzureConfig] = Field(None, description="Azure configuration")
    scanning: ScanningConfig = Field(default_factory=ScanningConfig)
    compliance: ComplianceConfig = Field(default_factory=ComplianceConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)

    # General settings
    log_level: str = Field("INFO", description="Logging level")
    output_format: str = Field("json", description="Default output format")
    cache_enabled: bool = Field(True, description="Enable result caching")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")

    # Parallel execution
    max_concurrent_scans: int = Field(4, description="Maximum concurrent scans")
    scan_timeout: int = Field(1800, description="Scan timeout in seconds")

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """
        Load configuration from file or environment variables.

        Args:
            config_path: Path to configuration file

        Returns:
            Config instance
        """
        config_data = {}

        # Try to load from file
        if config_path:
            config_data = cls._load_from_file(config_path)
        else:
            # Try default locations
            for default_path in [
                ".secureflow.yml",
                ".secureflow.yaml",
                ".secureflow.json",
                "secureflow.config.yml",
                "secureflow.config.yaml",
                "secureflow.config.json",
            ]:
                if Path(default_path).exists():
                    config_data = cls._load_from_file(default_path)
                    break

        # Merge with environment variables
        env_config = cls._load_from_env()
        config_data = cls._merge_configs(config_data, env_config)

        return cls(**config_data)

    @staticmethod
    def _load_from_file(file_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        path = Path(file_path)
        if not path.exists():
            return {}

        content = path.read_text()

        if path.suffix in [".yml", ".yaml"]:
            return yaml.safe_load(content) or {}
        elif path.suffix == ".json":
            return json.loads(content)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")

    @staticmethod
    def _load_from_env() -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}

        # Azure configuration
        azure_config = {}
        if os.getenv("AZURE_TENANT_ID"):
            azure_config["tenant_id"] = os.getenv("AZURE_TENANT_ID")
        if os.getenv("AZURE_CLIENT_ID"):
            azure_config["client_id"] = os.getenv("AZURE_CLIENT_ID")
        if os.getenv("AZURE_CLIENT_SECRET"):
            azure_config["client_secret"] = os.getenv("AZURE_CLIENT_SECRET")
        if os.getenv("AZURE_SUBSCRIPTION_ID"):
            azure_config["subscription_id"] = os.getenv("AZURE_SUBSCRIPTION_ID")
        if os.getenv("AZURE_DEVOPS_ORG"):
            azure_config["devops_organization"] = os.getenv("AZURE_DEVOPS_ORG")
        if os.getenv("AZURE_DEVOPS_PAT"):
            azure_config["pat_token"] = os.getenv("AZURE_DEVOPS_PAT")
        if os.getenv("AZURE_KEY_VAULT_URL"):
            azure_config["key_vault_url"] = os.getenv("AZURE_KEY_VAULT_URL")

        if azure_config:
            config["azure"] = azure_config

        # Scanning configuration
        scanning_config = {}
        if os.getenv("SECUREFLOW_SAST_TOOL"):
            scanning_config["sast_tool"] = os.getenv("SECUREFLOW_SAST_TOOL")
        if os.getenv("SECUREFLOW_SEVERITY_THRESHOLD"):
            scanning_config["severity_threshold"] = os.getenv(
                "SECUREFLOW_SEVERITY_THRESHOLD"
            )
        if os.getenv("SECUREFLOW_FAIL_ON_HIGH"):
            scanning_config["fail_on_high"] = (
                os.getenv("SECUREFLOW_FAIL_ON_HIGH").lower() == "true"
            )

        if scanning_config:
            config["scanning"] = scanning_config

        # General settings
        if os.getenv("SECUREFLOW_LOG_LEVEL"):
            config["log_level"] = os.getenv("SECUREFLOW_LOG_LEVEL")
        if os.getenv("SECUREFLOW_OUTPUT_FORMAT"):
            config["output_format"] = os.getenv("SECUREFLOW_OUTPUT_FORMAT")

        return config

    @staticmethod
    def _merge_configs(
        base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two configuration dictionaries."""
        merged = base.copy()

        for key, value in override.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = Config._merge_configs(merged[key], value)
            else:
                merged[key] = value

        return merged

    def save(self, file_path: str):
        """Save configuration to file."""
        path = Path(file_path)
        config_dict = self.model_dump(exclude_none=True)

        if path.suffix in [".yml", ".yaml"]:
            with open(path, "w") as f:
                yaml.dump(config_dict, f, default_flow_style=False)
        elif path.suffix == ".json":
            with open(path, "w") as f:
                json.dump(config_dict, f, indent=2)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")

    def get_azure_credentials(self) -> Dict[str, str]:
        """Get Azure credentials for authentication."""
        if not self.azure:
            raise ValueError("Azure configuration not provided")

        credentials = {}
        if self.azure.tenant_id:
            credentials["tenant_id"] = self.azure.tenant_id
        if self.azure.client_id:
            credentials["client_id"] = self.azure.client_id
        if self.azure.client_secret:
            credentials["client_secret"] = self.azure.client_secret

        return credentials
