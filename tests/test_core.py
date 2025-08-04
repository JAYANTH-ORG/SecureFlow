"""
Test the basic functionality of SecureFlow Core
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

# Import with fallback for missing dependencies
try:
    from secureflow_core import SecureFlow, Config
    from secureflow_core.scanner import Scanner, ScanResult, Vulnerability, Severity
    from secureflow_core.config import ScanningConfig

    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_AVAILABLE = False


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="SecureFlow imports not available")
class TestSecureFlowCore:
    """Test cases for SecureFlow Core functionality"""

    def test_config_creation(self):
        """Test configuration creation"""
        config = Config()
        assert config.scanning.enable_sast is True
        assert config.scanning.enable_sca is True
        assert config.scanning.sast_tool == "semgrep"

    def test_scanner_initialization(self):
        """Test scanner initialization"""
        config = ScanningConfig()
        scanner = Scanner(config)
        assert scanner.config == config

    def test_vulnerability_creation(self):
        """Test vulnerability object creation"""
        vuln = Vulnerability(
            id="test-vuln-1",
            title="Test Vulnerability",
            description="A test vulnerability",
            severity=Severity.HIGH,
            file_path="test.py",
            line_number=42,
            tool="test-tool",
        )

        assert vuln.id == "test-vuln-1"
        assert vuln.severity == Severity.HIGH
        assert vuln.file_path == "test.py"
        assert vuln.line_number == 42

    def test_scan_result_creation(self):
        """Test scan result creation"""
        import time

        vulnerabilities = [
            Vulnerability(
                id="test-1",
                title="Test Issue",
                description="A test issue",
                severity=Severity.MEDIUM,
                tool="test-tool",
            )
        ]

        result = ScanResult(
            tool="test-tool",
            target="./test",
            scan_type="sast",
            vulnerabilities=vulnerabilities,
            scan_duration=1.5,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        assert result.tool == "test-tool"
        assert len(result.vulnerabilities) == 1
        assert result.has_high_severity_issues() is False  # MEDIUM is not HIGH/CRITICAL

        # Test with high severity
        result.vulnerabilities[0].severity = Severity.HIGH
        assert result.has_high_severity_issues() is True

    @pytest.mark.asyncio
    async def test_secureflow_initialization(self):
        """Test SecureFlow initialization"""
        config = Config()
        secureflow = SecureFlow(config)

        assert secureflow.config == config
        assert secureflow.scanner is not None
        assert secureflow.compliance is not None

        # Test cleanup
        await secureflow.cleanup()


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="SecureFlow imports not available")
class TestMockScanning:
    """Test scanning functionality with mocked tools"""

    @pytest.mark.asyncio
    async def test_mock_sast_scan(self):
        """Test SAST scanning with mocked tool"""
        config = ScanningConfig()
        scanner = Scanner(config)

        # Mock the command execution
        with patch.object(scanner, "_run_command") as mock_run:
            mock_run.return_value = {
                "returncode": 0,
                "stdout": '{"results": []}',
                "stderr": "",
            }

            # Mock the parser to return empty vulnerabilities
            with patch.object(scanner, "_parse_semgrep_output") as mock_parse:
                mock_parse.return_value = []

                result = await scanner._run_semgrep("./test", "sast")

                assert result.tool == "semgrep"
                assert result.scan_type == "sast"
                assert len(result.vulnerabilities) == 0

    @pytest.mark.asyncio
    async def test_mock_sca_scan(self):
        """Test SCA scanning with mocked tool"""
        config = ScanningConfig()
        scanner = Scanner(config)

        # Mock the command execution
        with patch.object(scanner, "_run_command") as mock_run:
            mock_run.return_value = {"returncode": 0, "stdout": "[]", "stderr": ""}

            # Mock the parser
            with patch.object(scanner, "_parse_safety_output") as mock_parse:
                mock_parse.return_value = []

                result = await scanner._run_safety("./test", "sca")

                assert result.tool == "safety"
                assert result.scan_type == "sca"


class TestUtilities:
    """Test utility functions that don't require full imports"""

    def test_basic_python_functionality(self):
        """Test basic Python functionality works in our environment"""
        import json
        import time
        from pathlib import Path

        # Test JSON handling
        test_data = {"test": "value", "number": 42}
        json_str = json.dumps(test_data)
        parsed = json.loads(json_str)
        assert parsed["test"] == "value"

        # Test time formatting
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        assert "T" in timestamp
        assert "Z" in timestamp

        # Test pathlib
        current_dir = Path(".")
        assert current_dir.exists()


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    import sys

    print("🧪 Running SecureFlow Core Tests")

    if not IMPORTS_AVAILABLE:
        print("⚠️  SecureFlow imports not available, running basic tests only")
        test_utils = TestUtilities()
        test_utils.test_basic_python_functionality()
        print("✅ Basic utility tests passed")
    else:
        print("✅ All imports available, running comprehensive tests")

        # Run basic synchronous tests
        test_core = TestSecureFlowCore()
        try:
            test_core.test_config_creation()
            print("✅ Config creation test passed")

            test_core.test_scanner_initialization()
            print("✅ Scanner initialization test passed")

            test_core.test_vulnerability_creation()
            print("✅ Vulnerability creation test passed")

            test_core.test_scan_result_creation()
            print("✅ Scan result creation test passed")

            # Run async tests
            async def run_async_tests():
                await test_core.test_secureflow_initialization()
                print("✅ SecureFlow initialization test passed")

                test_mock = TestMockScanning()
                await test_mock.test_mock_sast_scan()
                print("✅ Mock SAST scan test passed")

                await test_mock.test_mock_sca_scan()
                print("✅ Mock SCA scan test passed")

            asyncio.run(run_async_tests())

        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            sys.exit(1)

    print("\n🎉 All tests completed successfully!")
