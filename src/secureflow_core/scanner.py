"""
Security scanning engine for SecureFlow
"""

import asyncio
import json
import subprocess
import tempfile
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import semver

from .config import ScanningConfig
from .utils import Logger


class Severity(Enum):
    """Security vulnerability severity levels"""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class Vulnerability:
    """Represents a security vulnerability"""

    id: str
    title: str
    description: str
    severity: Severity
    cwe: Optional[str] = None
    cvss_score: Optional[float] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    tool: Optional[str] = None
    rule_id: Optional[str] = None
    recommendation: Optional[str] = None
    references: List[str] = None

    def __post_init__(self):
        if self.references is None:
            self.references = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "cwe": self.cwe,
            "cvss_score": self.cvss_score,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "tool": self.tool,
            "rule_id": self.rule_id,
            "recommendation": self.recommendation,
            "references": self.references,
        }


@dataclass
class ScanResult:
    """Represents the result of a security scan"""

    tool: str
    target: str
    scan_type: str
    vulnerabilities: List[Vulnerability]
    scan_duration: float
    timestamp: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def get_vulnerability_count_by_severity(self) -> Dict[str, int]:
        """Get count of vulnerabilities by severity"""
        counts = {severity.value: 0 for severity in Severity}
        for vuln in self.vulnerabilities:
            counts[vuln.severity.value] += 1
        return counts

    def has_high_severity_issues(self) -> bool:
        """Check if scan has high or critical severity issues"""
        return any(
            vuln.severity in [Severity.HIGH, Severity.CRITICAL]
            for vuln in self.vulnerabilities
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "tool": self.tool,
            "target": self.target,
            "scan_type": self.scan_type,
            "vulnerabilities": [vuln.to_dict() for vuln in self.vulnerabilities],
            "scan_duration": self.scan_duration,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "by_severity": self.get_vulnerability_count_by_severity(),
                "has_high_severity": self.has_high_severity_issues(),
            },
        }


class Scanner:
    """
    Main security scanner class that orchestrates different security scanning tools.
    """

    def __init__(self, config: ScanningConfig):
        """
        Initialize scanner with configuration.

        Args:
            config: Scanning configuration
        """
        self.config = config
        self.logger = Logger(__name__)
        self._scan_tools = {
            "sast": {
                "semgrep": self._run_semgrep,
                "bandit": self._run_bandit,
                "sonarqube": self._run_sonarqube,
            },
            "sca": {
                "safety": self._run_safety,
                "pip-audit": self._run_pip_audit,
                "npm-audit": self._run_npm_audit,
            },
            "secrets": {
                "truffhog": self._run_truffhog,
                "gitleaks": self._run_gitleaks,
                "detect-secrets": self._run_detect_secrets,
            },
            "iac": {
                "checkov": self._run_checkov,
                "tfsec": self._run_tfsec,
                "terrascan": self._run_terrascan,
            },
            "container": {
                "trivy": self._run_trivy,
                "clair": self._run_clair,
                "anchore": self._run_anchore,
            },
        }

    async def scan_source_code(self, target_path: str) -> ScanResult:
        """
        Perform Static Application Security Testing (SAST).

        Args:
            target_path: Path to source code

        Returns:
            SAST scan results
        """
        self.logger.info(f"Running SAST scan on {target_path}")
        tool = self.config.sast_tool

        if tool not in self._scan_tools["sast"]:
            raise ValueError(f"Unsupported SAST tool: {tool}")

        scan_func = self._scan_tools["sast"][tool]
        return await scan_func(target_path, "sast")

    async def scan_dependencies(self, target_path: str) -> ScanResult:
        """
        Perform Software Composition Analysis (SCA).

        Args:
            target_path: Path to project

        Returns:
            SCA scan results
        """
        self.logger.info(f"Running SCA scan on {target_path}")
        tool = self.config.sca_tool

        if tool not in self._scan_tools["sca"]:
            raise ValueError(f"Unsupported SCA tool: {tool}")

        scan_func = self._scan_tools["sca"][tool]
        return await scan_func(target_path, "sca")

    async def scan_secrets(self, target_path: str) -> ScanResult:
        """
        Perform secret scanning.

        Args:
            target_path: Path to scan for secrets

        Returns:
            Secret scan results
        """
        self.logger.info(f"Running secret scan on {target_path}")
        tool = self.config.secrets_tool

        if tool not in self._scan_tools["secrets"]:
            raise ValueError(f"Unsupported secrets tool: {tool}")

        scan_func = self._scan_tools["secrets"][tool]
        return await scan_func(target_path, "secrets")

    async def scan_infrastructure(self, target_path: str) -> ScanResult:
        """
        Perform Infrastructure as Code (IaC) scanning.

        Args:
            target_path: Path to IaC files

        Returns:
            IaC scan results
        """
        self.logger.info(f"Running IaC scan on {target_path}")
        tool = self.config.iac_tool

        if tool not in self._scan_tools["iac"]:
            raise ValueError(f"Unsupported IaC tool: {tool}")

        scan_func = self._scan_tools["iac"][tool]
        return await scan_func(target_path, "iac")

    async def scan_container(self, image_or_dockerfile: str) -> ScanResult:
        """
        Perform container security scanning.

        Args:
            image_or_dockerfile: Container image name or Dockerfile path

        Returns:
            Container scan results
        """
        self.logger.info(f"Running container scan on {image_or_dockerfile}")
        tool = self.config.container_tool

        if tool not in self._scan_tools["container"]:
            raise ValueError(f"Unsupported container tool: {tool}")

        scan_func = self._scan_tools["container"][tool]
        return await scan_func(image_or_dockerfile, "container")

    # SAST Tool Implementations
    async def _run_semgrep(self, target_path: str, scan_type: str) -> ScanResult:
        """Run Semgrep SAST scan"""
        import time

        start_time = time.time()

        try:
            cmd = [
                "semgrep",
                "--config=auto",
                "--json",
                "--exclude",
                " ".join(self.config.exclude_paths),
                target_path,
            ]

            result = await self._run_command(cmd)
            vulnerabilities = self._parse_semgrep_output(result.get("stdout", ""))

            return ScanResult(
                tool="semgrep",
                target=target_path,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                metadata={"command": " ".join(cmd)},
            )

        except Exception as e:
            self.logger.error(f"Semgrep scan failed: {str(e)}")
            return self._create_error_result(
                "semgrep", target_path, scan_type, str(e), start_time
            )

    async def _run_bandit(self, target_path: str, scan_type: str) -> ScanResult:
        """Run Bandit Python security scanner"""
        import time

        start_time = time.time()

        try:
            cmd = [
                "bandit",
                "-r",
                target_path,
                "-f",
                "json",
                "--skip",
                ",".join(self.config.exclude_paths),
            ]

            result = await self._run_command(cmd)
            vulnerabilities = self._parse_bandit_output(result.get("stdout", ""))

            return ScanResult(
                tool="bandit",
                target=target_path,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                metadata={"command": " ".join(cmd)},
            )

        except Exception as e:
            self.logger.error(f"Bandit scan failed: {str(e)}")
            return self._create_error_result(
                "bandit", target_path, scan_type, str(e), start_time
            )

    async def _run_sonarqube(self, target_path: str, scan_type: str) -> ScanResult:
        """Run SonarQube scanner"""
        # Placeholder implementation
        import time

        start_time = time.time()

        self.logger.info("SonarQube scan would be implemented with sonar-scanner CLI")

        return ScanResult(
            tool="sonarqube",
            target=target_path,
            scan_type=scan_type,
            vulnerabilities=[],
            scan_duration=time.time() - start_time,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            metadata={"status": "placeholder", "note": "SonarQube integration pending"},
        )

    # SCA Tool Implementations
    async def _run_safety(self, target_path: str, scan_type: str) -> ScanResult:
        """Run Safety dependency scanner"""
        import time

        start_time = time.time()

        try:
            # Look for requirements files
            req_files = list(Path(target_path).rglob("requirements*.txt"))
            if not req_files:
                req_files = list(Path(target_path).rglob("Pipfile"))

            if not req_files:
                self.logger.warning("No dependency files found for Safety scan")
                return self._create_empty_result(
                    "safety", target_path, scan_type, start_time
                )

            cmd = ["safety", "check", "--json", "--file", str(req_files[0])]
            result = await self._run_command(cmd)
            vulnerabilities = self._parse_safety_output(result.get("stdout", ""))

            return ScanResult(
                tool="safety",
                target=target_path,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                metadata={"requirements_file": str(req_files[0])},
            )

        except Exception as e:
            self.logger.error(f"Safety scan failed: {str(e)}")
            return self._create_error_result(
                "safety", target_path, scan_type, str(e), start_time
            )

    async def _run_pip_audit(self, target_path: str, scan_type: str) -> ScanResult:
        """Run pip-audit dependency scanner"""
        import time

        start_time = time.time()

        try:
            cmd = ["pip-audit", "--format=json", "--desc"]
            result = await self._run_command(cmd, cwd=target_path)
            vulnerabilities = self._parse_pip_audit_output(result.get("stdout", ""))

            return ScanResult(
                tool="pip-audit",
                target=target_path,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        except Exception as e:
            self.logger.error(f"pip-audit scan failed: {str(e)}")
            return self._create_error_result(
                "pip-audit", target_path, scan_type, str(e), start_time
            )

    async def _run_npm_audit(self, target_path: str, scan_type: str) -> ScanResult:
        """Run npm audit for Node.js dependencies"""
        import time

        start_time = time.time()

        try:
            package_json = Path(target_path) / "package.json"
            if not package_json.exists():
                self.logger.warning("No package.json found for npm audit")
                return self._create_empty_result(
                    "npm-audit", target_path, scan_type, start_time
                )

            cmd = ["npm", "audit", "--json"]
            result = await self._run_command(cmd, cwd=target_path)
            vulnerabilities = self._parse_npm_audit_output(result.get("stdout", ""))

            return ScanResult(
                tool="npm-audit",
                target=target_path,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        except Exception as e:
            self.logger.error(f"npm audit failed: {str(e)}")
            return self._create_error_result(
                "npm-audit", target_path, scan_type, str(e), start_time
            )

    # Secret Scanning Tool Implementations
    async def _run_truffhog(self, target_path: str, scan_type: str) -> ScanResult:
        """Run TruffleHog secret scanner"""
        import time

        start_time = time.time()

        try:
            cmd = ["trufflehog", "--json", "filesystem", target_path]
            result = await self._run_command(cmd)
            vulnerabilities = self._parse_truffhog_output(result.get("stdout", ""))

            return ScanResult(
                tool="trufflehog",
                target=target_path,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        except Exception as e:
            self.logger.error(f"TruffleHog scan failed: {str(e)}")
            return self._create_error_result(
                "trufflehog", target_path, scan_type, str(e), start_time
            )

    async def _run_gitleaks(self, target_path: str, scan_type: str) -> ScanResult:
        """Run Gitleaks secret scanner"""
        import time

        start_time = time.time()

        try:
            cmd = [
                "gitleaks",
                "detect",
                "--source",
                target_path,
                "--report-format",
                "json",
            ]
            result = await self._run_command(cmd)
            vulnerabilities = self._parse_gitleaks_output(result.get("stdout", ""))

            return ScanResult(
                tool="gitleaks",
                target=target_path,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        except Exception as e:
            self.logger.error(f"Gitleaks scan failed: {str(e)}")
            return self._create_error_result(
                "gitleaks", target_path, scan_type, str(e), start_time
            )

    async def _run_detect_secrets(self, target_path: str, scan_type: str) -> ScanResult:
        """Run detect-secrets scanner"""
        import time

        start_time = time.time()

        try:
            cmd = ["detect-secrets", "scan", "--force-use-all-plugins", target_path]
            result = await self._run_command(cmd)
            vulnerabilities = self._parse_detect_secrets_output(
                result.get("stdout", "")
            )

            return ScanResult(
                tool="detect-secrets",
                target=target_path,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        except Exception as e:
            self.logger.error(f"detect-secrets scan failed: {str(e)}")
            return self._create_error_result(
                "detect-secrets", target_path, scan_type, str(e), start_time
            )

    # IaC Tool Implementations
    async def _run_checkov(self, target_path: str, scan_type: str) -> ScanResult:
        """Run Checkov IaC scanner"""
        import time

        start_time = time.time()

        try:
            cmd = ["checkov", "-d", target_path, "--output", "json", "--quiet"]
            result = await self._run_command(cmd)
            vulnerabilities = self._parse_checkov_output(result.get("stdout", ""))

            return ScanResult(
                tool="checkov",
                target=target_path,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        except Exception as e:
            self.logger.error(f"Checkov scan failed: {str(e)}")
            return self._create_error_result(
                "checkov", target_path, scan_type, str(e), start_time
            )

    async def _run_tfsec(self, target_path: str, scan_type: str) -> ScanResult:
        """Run tfsec Terraform scanner"""
        import time

        start_time = time.time()

        try:
            cmd = ["tfsec", target_path, "--format", "json"]
            result = await self._run_command(cmd)
            vulnerabilities = self._parse_tfsec_output(result.get("stdout", ""))

            return ScanResult(
                tool="tfsec",
                target=target_path,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        except Exception as e:
            self.logger.error(f"tfsec scan failed: {str(e)}")
            return self._create_error_result(
                "tfsec", target_path, scan_type, str(e), start_time
            )

    async def _run_terrascan(self, target_path: str, scan_type: str) -> ScanResult:
        """Run Terrascan IaC scanner"""
        import time

        start_time = time.time()

        try:
            cmd = ["terrascan", "scan", "-d", target_path, "-o", "json"]
            result = await self._run_command(cmd)
            vulnerabilities = self._parse_terrascan_output(result.get("stdout", ""))

            return ScanResult(
                tool="terrascan",
                target=target_path,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        except Exception as e:
            self.logger.error(f"Terrascan scan failed: {str(e)}")
            return self._create_error_result(
                "terrascan", target_path, scan_type, str(e), start_time
            )

    # Container Tool Implementations
    async def _run_trivy(self, target: str, scan_type: str) -> ScanResult:
        """Run Trivy container scanner"""
        import time

        start_time = time.time()

        try:
            # Determine if target is image or filesystem
            if Path(target).exists():
                cmd = ["trivy", "fs", "--format", "json", target]
            else:
                cmd = ["trivy", "image", "--format", "json", target]

            result = await self._run_command(cmd)
            vulnerabilities = self._parse_trivy_output(result.get("stdout", ""))

            return ScanResult(
                tool="trivy",
                target=target,
                scan_type=scan_type,
                vulnerabilities=vulnerabilities,
                scan_duration=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

        except Exception as e:
            self.logger.error(f"Trivy scan failed: {str(e)}")
            return self._create_error_result(
                "trivy", target, scan_type, str(e), start_time
            )

    async def _run_clair(self, target: str, scan_type: str) -> ScanResult:
        """Run Clair container scanner"""
        # Placeholder implementation
        import time

        start_time = time.time()

        self.logger.info("Clair scanner would require Clair server setup")

        return ScanResult(
            tool="clair",
            target=target,
            scan_type=scan_type,
            vulnerabilities=[],
            scan_duration=time.time() - start_time,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            metadata={"status": "placeholder", "note": "Clair integration pending"},
        )

    async def _run_anchore(self, target: str, scan_type: str) -> ScanResult:
        """Run Anchore container scanner"""
        # Placeholder implementation
        import time

        start_time = time.time()

        self.logger.info("Anchore scanner would require Anchore Engine setup")

        return ScanResult(
            tool="anchore",
            target=target,
            scan_type=scan_type,
            vulnerabilities=[],
            scan_duration=time.time() - start_time,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            metadata={"status": "placeholder", "note": "Anchore integration pending"},
        )

    # Utility Methods
    async def _run_command(
        self, cmd: List[str], cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

            stdout, stderr = await process.communicate()

            return {
                "returncode": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
            }

        except Exception as e:
            self.logger.error(f"Command execution failed: {' '.join(cmd)}: {str(e)}")
            return {"returncode": -1, "stdout": "", "stderr": str(e)}

    def _create_error_result(
        self, tool: str, target: str, scan_type: str, error: str, start_time: float
    ) -> ScanResult:
        """Create error scan result"""
        import time

        return ScanResult(
            tool=tool,
            target=target,
            scan_type=scan_type,
            vulnerabilities=[],
            scan_duration=time.time() - start_time,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            metadata={"error": error, "status": "failed"},
        )

    def _create_empty_result(
        self, tool: str, target: str, scan_type: str, start_time: float
    ) -> ScanResult:
        """Create empty scan result"""
        import time

        return ScanResult(
            tool=tool,
            target=target,
            scan_type=scan_type,
            vulnerabilities=[],
            scan_duration=time.time() - start_time,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            metadata={"status": "no_issues_found"},
        )

    # Parser methods (simplified implementations)
    def _parse_semgrep_output(self, output: str) -> List[Vulnerability]:
        """Parse Semgrep JSON output"""
        vulnerabilities = []
        try:
            if not output.strip():
                return vulnerabilities

            data = json.loads(output)
            for result in data.get("results", []):
                vuln = Vulnerability(
                    id=result.get("check_id", "unknown"),
                    title=result.get("message", "Security issue detected"),
                    description=result.get("extra", {}).get("message", ""),
                    severity=self._map_severity(
                        result.get("extra", {}).get("severity", "INFO")
                    ),
                    file_path=result.get("path"),
                    line_number=result.get("start", {}).get("line"),
                    tool="semgrep",
                    rule_id=result.get("check_id"),
                    references=result.get("extra", {}).get("references", []),
                )
                vulnerabilities.append(vuln)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse Semgrep output")

        return vulnerabilities

    def _parse_bandit_output(self, output: str) -> List[Vulnerability]:
        """Parse Bandit JSON output"""
        vulnerabilities = []
        try:
            if not output.strip():
                return vulnerabilities

            data = json.loads(output)
            for result in data.get("results", []):
                vuln = Vulnerability(
                    id=f"bandit-{result.get('test_id', 'unknown')}",
                    title=result.get("test_name", "Security issue"),
                    description=result.get("issue_text", ""),
                    severity=self._map_severity(result.get("issue_severity", "LOW")),
                    file_path=result.get("filename"),
                    line_number=result.get("line_number"),
                    tool="bandit",
                    rule_id=result.get("test_id"),
                    recommendation=result.get("more_info"),
                )
                vulnerabilities.append(vuln)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse Bandit output")

        return vulnerabilities

    def _parse_safety_output(self, output: str) -> List[Vulnerability]:
        """Parse Safety JSON output"""
        vulnerabilities = []
        try:
            if not output.strip():
                return vulnerabilities

            # Safety output can be a list of vulnerabilities
            data = (
                json.loads(output) if output.startswith("[") else [json.loads(output)]
            )

            for result in data:
                vuln = Vulnerability(
                    id=result.get("id", "unknown"),
                    title=f"Vulnerable package: {result.get('package', 'unknown')}",
                    description=result.get("advisory", ""),
                    severity=self._map_severity(
                        "HIGH"
                    ),  # Safety reports are generally high severity
                    tool="safety",
                    recommendation=f"Update {result.get('package')} to version {result.get('safe_version', 'latest')}",
                )
                vulnerabilities.append(vuln)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse Safety output")

        return vulnerabilities

    # Additional parser methods would be implemented similarly...
    def _parse_pip_audit_output(self, output: str) -> List[Vulnerability]:
        """Parse pip-audit output - placeholder"""
        return []

    def _parse_npm_audit_output(self, output: str) -> List[Vulnerability]:
        """Parse npm audit output - placeholder"""
        return []

    def _parse_truffhog_output(self, output: str) -> List[Vulnerability]:
        """Parse TruffleHog output - placeholder"""
        return []

    def _parse_gitleaks_output(self, output: str) -> List[Vulnerability]:
        """Parse Gitleaks output - placeholder"""
        return []

    def _parse_detect_secrets_output(self, output: str) -> List[Vulnerability]:
        """Parse detect-secrets output - placeholder"""
        return []

    def _parse_checkov_output(self, output: str) -> List[Vulnerability]:
        """Parse Checkov output - placeholder"""
        return []

    def _parse_tfsec_output(self, output: str) -> List[Vulnerability]:
        """Parse tfsec output - placeholder"""
        return []

    def _parse_terrascan_output(self, output: str) -> List[Vulnerability]:
        """Parse Terrascan output - placeholder"""
        return []

    def _parse_trivy_output(self, output: str) -> List[Vulnerability]:
        """Parse Trivy output - placeholder"""
        return []

    def _map_severity(self, severity_str: str) -> Severity:
        """Map string severity to Severity enum"""
        severity_map = {
            "CRITICAL": Severity.CRITICAL,
            "HIGH": Severity.HIGH,
            "MEDIUM": Severity.MEDIUM,
            "LOW": Severity.LOW,
            "INFO": Severity.INFO,
            "WARNING": Severity.MEDIUM,
            "ERROR": Severity.HIGH,
        }

        return severity_map.get(severity_str.upper(), Severity.INFO)
