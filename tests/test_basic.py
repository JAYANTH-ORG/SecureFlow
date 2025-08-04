"""
Basic tests for SecureFlow core functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Import SecureFlow components
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from secureflow_core import SecureFlow, Config
from secureflow_core.scanner import Scanner, ScanResult, Vulnerability, Severity
from secureflow_core.config import ScanningConfig


class TestConfig:
    """Test configuration functionality"""

    def test_default_config(self):
        """Test default configuration creation"""
        config = Config()

        assert config.log_level == "INFO"
        assert config.output_format == "json"
        assert config.cache_enabled is True
        assert config.scanning.enable_sast is True
        assert config.scanning.sast_tool == "semgrep"

    def test_config_with_custom_values(self):
        """Test configuration with custom values"""
        scanning_config = ScanningConfig(
            sast_tool="bandit", severity_threshold="high", fail_on_high=False
        )

        config = Config(scanning=scanning_config)

        assert config.scanning.sast_tool == "bandit"
        assert config.scanning.severity_threshold == "high"
        assert config.scanning.fail_on_high is False

    def test_config_load_from_dict(self):
        """Test loading configuration from dictionary"""
        config_dict = {
            "log_level": "DEBUG",
            "scanning": {"sast_tool": "sonarqube", "enable_container": False},
        }

        config = Config(**config_dict)

        assert config.log_level == "DEBUG"
        assert config.scanning.sast_tool == "sonarqube"
        assert config.scanning.enable_container is False


class TestScanner:
    """Test security scanner functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = ScanningConfig()
        self.scanner = Scanner(self.config)

    @pytest.mark.asyncio
    async def test_scan_source_code(self):
        """Test source code scanning"""
        # Mock the command execution to simulate semgrep output
        mock_semgrep_output = {
            "returncode": 0,
            "stdout": '{"results": []}',
            "stderr": "",
        }

        with patch.object(self.scanner, "_run_command") as mock_command:
            mock_command.return_value = mock_semgrep_output

            result = await self.scanner.scan_source_code("test_target")

            assert result.tool == "semgrep"
            assert result.scan_type == "sast"
            assert result.target == "test_target"
            assert isinstance(result.vulnerabilities, list)
            mock_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_scan_dependencies(self):
        """Test dependency scanning"""
        # Mock finding dependency files and safety command execution
        from pathlib import Path

        with patch.object(Path, "rglob") as mock_rglob:
            # Mock that requirements.txt files are found
            mock_file = Path("test_target/requirements.txt")
            mock_rglob.return_value = [mock_file]

            mock_safety_output = {
                "returncode": 0,
                "stdout": "[]",  # No vulnerabilities found
                "stderr": "",
            }

            with patch.object(self.scanner, "_run_command") as mock_command:
                mock_command.return_value = mock_safety_output

                result = await self.scanner.scan_dependencies("test_target")

                assert result.tool == "safety"
                assert result.scan_type == "sca"
                assert result.target == "test_target"
                assert isinstance(result.vulnerabilities, list)
                mock_command.assert_called_once()

    def test_vulnerability_creation(self):
        """Test vulnerability object creation"""
        vuln = Vulnerability(
            id="test-vuln-1",
            title="Test Vulnerability",
            description="This is a test vulnerability",
            severity=Severity.HIGH,
            file_path="/path/to/file.py",
            line_number=42,
            tool="test-tool",
        )

        assert vuln.id == "test-vuln-1"
        assert vuln.severity == Severity.HIGH
        assert vuln.file_path == "/path/to/file.py"
        assert vuln.line_number == 42

        # Test dictionary conversion
        vuln_dict = vuln.to_dict()
        assert vuln_dict["id"] == "test-vuln-1"
        assert vuln_dict["severity"] == "HIGH"

    def test_scan_result_summary(self):
        """Test scan result summary functionality"""
        vulnerabilities = [
            Vulnerability("1", "Vuln 1", "Desc 1", Severity.HIGH, tool="test"),
            Vulnerability("2", "Vuln 2", "Desc 2", Severity.MEDIUM, tool="test"),
            Vulnerability("3", "Vuln 3", "Desc 3", Severity.HIGH, tool="test"),
        ]

        result = ScanResult(
            tool="test-tool",
            target="test-target",
            scan_type="test",
            vulnerabilities=vulnerabilities,
            scan_duration=1.0,
            timestamp="2024-01-01T00:00:00Z",
        )

        severity_counts = result.get_vulnerability_count_by_severity()
        assert severity_counts["HIGH"] == 2
        assert severity_counts["MEDIUM"] == 1
        assert severity_counts["CRITICAL"] == 0

        assert result.has_high_severity_issues() is True


class TestSecureFlow:
    """Test main SecureFlow class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = Config()
        self.secureflow = SecureFlow(self.config)

    @pytest.mark.asyncio
    async def test_scan_repository(self):
        """Test repository scanning"""
        with patch.object(
            self.secureflow.scanner, "scan_source_code"
        ) as mock_sast, patch.object(
            self.secureflow.scanner, "scan_dependencies"
        ) as mock_sca, patch.object(
            self.secureflow.scanner, "scan_secrets"
        ) as mock_secrets:

            # Mock scan results
            mock_sast.return_value = ScanResult(
                "semgrep", ".", "sast", [], 1.0, "2024-01-01T00:00:00Z"
            )
            mock_sca.return_value = ScanResult(
                "safety", ".", "sca", [], 0.5, "2024-01-01T00:00:00Z"
            )
            mock_secrets.return_value = ScanResult(
                "truffhog", ".", "secrets", [], 0.8, "2024-01-01T00:00:00Z"
            )

            results = await self.secureflow.scan_repository(".")

            assert "sast" in results
            assert "sca" in results
            assert "secrets" in results

            mock_sast.assert_called_once_with(".")
            mock_sca.assert_called_once_with(".")
            mock_secrets.assert_called_once_with(".")

    @pytest.mark.asyncio
    async def test_generate_security_report(self):
        """Test security report generation"""
        scan_results = {
            "sast": {"tool": "semgrep", "vulnerabilities": [], "scan_duration": 1.0}
        }

        with patch.object(
            self.secureflow.report, "generate_comprehensive_report"
        ) as mock_report:
            mock_report.return_value = "test_report.html"

            report_path = await self.secureflow.generate_security_report(scan_results)

            assert report_path == "test_report.html"
            mock_report.assert_called_once_with(scan_results, None)

    def test_get_security_metrics(self):
        """Test security metrics retrieval"""
        metrics = self.secureflow.get_security_metrics()

        assert isinstance(metrics, dict)
        assert "scans_completed" in metrics
        assert "vulnerabilities_found" in metrics


class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_end_to_end_scan_workflow(self):
        """Test complete scan workflow"""
        config = Config()
        secureflow = SecureFlow(config)

        # Create a temporary test file
        test_file = Path("test_file.py")
        test_file.write_text(
            """
# Test Python file
password = "hardcoded_password"  # This should be detected
"""
        )

        try:
            # This would run actual scans in a real scenario
            # For testing, we'll mock the scanner behavior
            with patch.object(secureflow.scanner, "scan_source_code") as mock_scan:
                mock_vuln = Vulnerability(
                    id="test-hardcoded-password",
                    title="Hardcoded password detected",
                    description="Found hardcoded password in source code",
                    severity=Severity.HIGH,
                    file_path=str(test_file),
                    line_number=3,
                    tool="test-scanner",
                )

                mock_result = ScanResult(
                    tool="test-scanner",
                    target=".",
                    scan_type="sast",
                    vulnerabilities=[mock_vuln],
                    scan_duration=1.0,
                    timestamp="2024-01-01T00:00:00Z",
                )
                mock_scan.return_value = mock_result

                # Run scan
                results = await secureflow.scan_repository(".")

                # Verify results
                assert "sast" in results
                sast_result = results["sast"]
                assert len(sast_result.vulnerabilities) == 1
                assert sast_result.vulnerabilities[0].severity == Severity.HIGH

        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
            await secureflow.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
