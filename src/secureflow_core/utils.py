"""
Utility modules for SecureFlow
"""

import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json


class Logger:
    """Enhanced logger for SecureFlow"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        """Set up logger with appropriate handlers and formatting"""
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)

            # File handler (optional)
            log_dir = Path(".secureflow-logs")
            if not log_dir.exists():
                log_dir.mkdir(exist_ok=True)

            file_handler = logging.FileHandler(log_dir / "secureflow.log")
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(file_formatter)

            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.INFO)

    def set_level(self, level: str):
        """Set logging level"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        self.logger.setLevel(level_map.get(level.upper(), logging.INFO))

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)


class SecurityMetrics:
    """Security metrics collection and analysis"""

    def __init__(self):
        self.metrics = {
            "scans_completed": 0,
            "vulnerabilities_found": 0,
            "vulnerabilities_by_severity": {
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
                "INFO": 0,
            },
            "scan_types": {"sast": 0, "sca": 0, "secrets": 0, "iac": 0, "container": 0},
            "tools_used": {},
            "scan_durations": [],
            "compliance_checks": 0,
            "compliance_failures": 0,
            "last_updated": None,
        }
        self.logger = Logger(__name__)

    def record_scan_completion(self, scan_results: Dict[str, Any]):
        """Record completion of security scans"""
        self.metrics["scans_completed"] += 1
        self.metrics["last_updated"] = datetime.now().isoformat()

        for scan_type, result in scan_results.items():
            # Update scan type count
            if scan_type in self.metrics["scan_types"]:
                self.metrics["scan_types"][scan_type] += 1

            # Process scan result
            if isinstance(result, dict):
                # Update tool usage
                tool = result.get("tool", "unknown")
                self.metrics["tools_used"][tool] = (
                    self.metrics["tools_used"].get(tool, 0) + 1
                )

                # Update vulnerability counts
                vulnerabilities = result.get("vulnerabilities", [])
                self.metrics["vulnerabilities_found"] += len(vulnerabilities)

                for vuln in vulnerabilities:
                    severity = vuln.get("severity", "INFO")
                    if severity in self.metrics["vulnerabilities_by_severity"]:
                        self.metrics["vulnerabilities_by_severity"][severity] += 1

                # Record scan duration
                duration = result.get("scan_duration", 0)
                if duration > 0:
                    self.metrics["scan_durations"].append(duration)

        self.logger.info(f"Recorded metrics for scan completion")

    def record_compliance_check(self, results: Dict[str, Any]):
        """Record compliance check results"""
        self.metrics["compliance_checks"] += 1

        for framework, result in results.items():
            if not result.get("compliant", True):
                self.metrics["compliance_failures"] += 1

        self.metrics["last_updated"] = datetime.now().isoformat()
        self.logger.info(f"Recorded compliance check metrics")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        metrics = self.metrics.copy()

        # Calculate additional metrics
        if self.metrics["scan_durations"]:
            metrics["average_scan_duration"] = sum(
                self.metrics["scan_durations"]
            ) / len(self.metrics["scan_durations"])
            metrics["total_scan_time"] = sum(self.metrics["scan_durations"])
        else:
            metrics["average_scan_duration"] = 0
            metrics["total_scan_time"] = 0

        # Calculate compliance rate
        if self.metrics["compliance_checks"] > 0:
            success_rate = (
                self.metrics["compliance_checks"] - self.metrics["compliance_failures"]
            ) / self.metrics["compliance_checks"]
            metrics["compliance_success_rate"] = round(success_rate * 100, 2)
        else:
            metrics["compliance_success_rate"] = 0

        # Calculate vulnerability density
        if self.metrics["scans_completed"] > 0:
            metrics["average_vulnerabilities_per_scan"] = round(
                self.metrics["vulnerabilities_found"] / self.metrics["scans_completed"],
                2,
            )
        else:
            metrics["average_vulnerabilities_per_scan"] = 0

        return metrics

    def export_metrics(self, file_path: str, format: str = "json"):
        """Export metrics to file"""
        metrics = self.get_metrics()

        if format.lower() == "json":
            with open(file_path, "w") as f:
                json.dump(metrics, f, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

        self.logger.info(f"Exported metrics to {file_path}")

    def reset_metrics(self):
        """Reset all metrics"""
        self.__init__()
        self.logger.info("Reset all security metrics")


class CacheManager:
    """Cache manager for scan results and other data"""

    def __init__(self, cache_dir: str = ".secureflow-cache", ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl  # Time to live in seconds
        self.logger = Logger(__name__)

    def get_cache_key(self, scan_type: str, target: str, tool: str) -> str:
        """Generate cache key for scan results"""
        import hashlib

        key_string = f"{scan_type}:{target}:{tool}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cache file is still valid based on TTL"""
        if not cache_file.exists():
            return False

        file_age = datetime.now().timestamp() - cache_file.stat().st_mtime
        return file_age < self.ttl

    def get_cached_result(
        self, scan_type: str, target: str, tool: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached scan result if available and valid"""
        cache_key = self.get_cache_key(scan_type, target, tool)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if self.is_cache_valid(cache_file):
            try:
                with open(cache_file, "r") as f:
                    result = json.load(f)
                self.logger.debug(f"Retrieved cached result for {scan_type}:{tool}")
                return result
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Failed to read cache file {cache_file}: {str(e)}")
                # Remove corrupted cache file
                cache_file.unlink(missing_ok=True)

        return None

    def cache_result(
        self, scan_type: str, target: str, tool: str, result: Dict[str, Any]
    ):
        """Cache scan result"""
        cache_key = self.get_cache_key(scan_type, target, tool)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, "w") as f:
                json.dump(result, f, indent=2)
            self.logger.debug(f"Cached result for {scan_type}:{tool}")
        except IOError as e:
            self.logger.warning(f"Failed to cache result: {str(e)}")

    def clear_cache(self):
        """Clear all cached results"""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except OSError as e:
                self.logger.warning(
                    f"Failed to delete cache file {cache_file}: {str(e)}"
                )

        self.logger.info("Cleared all cached results")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.json"))
        valid_files = [f for f in cache_files if self.is_cache_valid(f)]

        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            "total_files": len(cache_files),
            "valid_files": len(valid_files),
            "expired_files": len(cache_files) - len(valid_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_directory": str(self.cache_dir),
        }


class FileUtils:
    """File and directory utilities"""

    @staticmethod
    def find_files_by_extension(directory: str, extensions: list) -> list:
        """Find files with specific extensions in directory"""
        directory_path = Path(directory)
        files = []

        for ext in extensions:
            # Normalize extension (ensure it starts with .)
            if not ext.startswith("."):
                ext = f".{ext}"

            files.extend(directory_path.rglob(f"*{ext}"))

        return [str(f) for f in files]

    @staticmethod
    def get_project_type(directory: str) -> Optional[str]:
        """Detect project type based on files present"""
        directory_path = Path(directory)

        # Python
        if (
            (directory_path / "requirements.txt").exists()
            or (directory_path / "setup.py").exists()
            or (directory_path / "pyproject.toml").exists()
        ):
            return "python"

        # Node.js
        if (directory_path / "package.json").exists():
            return "node"

        # Java
        if (directory_path / "pom.xml").exists() or (
            directory_path / "build.gradle"
        ).exists():
            return "java"

        # .NET
        if list(directory_path.rglob("*.csproj")) or list(
            directory_path.rglob("*.sln")
        ):
            return "dotnet"

        # Go
        if (directory_path / "go.mod").exists():
            return "go"

        # Terraform
        if list(directory_path.rglob("*.tf")):
            return "terraform"

        # Docker
        if (directory_path / "Dockerfile").exists():
            return "docker"

        return None

    @staticmethod
    def create_backup(file_path: str) -> str:
        """Create backup of file"""
        original_path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = original_path.with_suffix(
            f".{timestamp}.backup{original_path.suffix}"
        )

        import shutil

        shutil.copy2(original_path, backup_path)

        return str(backup_path)

    @staticmethod
    def ensure_directory(directory_path: str):
        """Ensure directory exists"""
        Path(directory_path).mkdir(parents=True, exist_ok=True)


class ConfigValidator:
    """Configuration validation utilities"""

    @staticmethod
    def validate_azure_config(azure_config) -> list:
        """Validate Azure configuration"""
        errors = []

        if not azure_config:
            return ["Azure configuration is missing"]

        required_fields = ["devops_organization", "pat_token"]
        for field in required_fields:
            if not getattr(azure_config, field, None):
                errors.append(f"Azure {field} is required")

        return errors

    @staticmethod
    def validate_scanning_config(scanning_config) -> list:
        """Validate scanning configuration"""
        errors = []

        valid_tools = {
            "sast": ["semgrep", "bandit", "sonarqube"],
            "sca": ["safety", "pip-audit", "npm-audit"],
            "secrets": ["trufflehog", "gitleaks", "detect-secrets"],
            "iac": ["checkov", "tfsec", "terrascan"],
            "container": ["trivy", "clair", "anchore"],
        }

        if scanning_config.sast_tool not in valid_tools["sast"]:
            errors.append(f"Invalid SAST tool: {scanning_config.sast_tool}")

        if scanning_config.sca_tool not in valid_tools["sca"]:
            errors.append(f"Invalid SCA tool: {scanning_config.sca_tool}")

        # Add more validation as needed

        return errors
