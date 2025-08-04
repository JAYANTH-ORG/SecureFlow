"""
SecureFlow Core - Shared DevSecOps Library

A comprehensive library for integrating security scanning, vulnerability management,
and compliance automation into any development workflow.
"""

__version__ = "1.0.0"
__author__ = "CodeVibe Team"
__email__ = "devops@codevibe.com"

from .core import SecureFlow
from .config import Config, AzureConfig, ScanningConfig, ComplianceConfig
from .scanner import Scanner, ScanResult, Vulnerability
from .azure import AzureDevOpsIntegration
from .compliance import ComplianceChecker, ComplianceReport
from .plugins import BasePlugin, PluginManager
from .utils import Logger, SecurityMetrics

__all__ = [
    "SecureFlow",
    "Config",
    "AzureConfig",
    "ScanningConfig",
    "ComplianceConfig",
    "Scanner",
    "ScanResult",
    "Vulnerability",
    "AzureDevOpsIntegration",
    "ComplianceChecker",
    "ComplianceReport",
    "BasePlugin",
    "PluginManager",
    "Logger",
    "SecurityMetrics",
]
