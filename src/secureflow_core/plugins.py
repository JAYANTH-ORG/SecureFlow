"""
Plugin system for SecureFlow
"""

import asyncio
import importlib
import inspect
import importlib.util
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from pathlib import Path
from datetime import datetime

from .utils import Logger
from .scanner import ScanResult


class BasePlugin(ABC):
    """Base class for all SecureFlow plugins"""

    name: str = "base_plugin"
    version: str = "1.0.0"
    description: str = "Base plugin"
    author: str = "SecureFlow"

    def __init__(self):
        self.logger = Logger(f"plugin.{self.name}")
        self.config = {}

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with configuration.

        Args:
            config: Plugin configuration dictionary

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute the plugin's main functionality.

        Returns:
            Plugin execution result
        """
        pass

    async def cleanup(self):
        """Clean up plugin resources."""
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
        }


class ScannerPlugin(BasePlugin):
    """Base class for security scanner plugins"""

    scan_type: str = "generic"
    supported_file_types: List[str] = []

    @abstractmethod
    async def scan(self, target: str) -> ScanResult:
        """
        Perform security scan on target.

        Args:
            target: Target to scan (file, directory, etc.)

        Returns:
            Scan result
        """
        pass

    def supports_target(self, target: str) -> bool:
        """Check if plugin supports scanning the target."""
        if not self.supported_file_types:
            return True

        target_path = Path(target)
        if target_path.is_file():
            return target_path.suffix.lower() in self.supported_file_types

        # For directories, check if any supported files exist
        for file_type in self.supported_file_types:
            if list(target_path.rglob(f"*{file_type}")):
                return True

        return False


class ReportPlugin(BasePlugin):
    """Base class for report generation plugins"""

    output_format: str = "text"

    @abstractmethod
    async def generate_report(self, data: Dict[str, Any], output_path: str) -> str:
        """
        Generate report from data.

        Args:
            data: Report data
            output_path: Output file path

        Returns:
            Path to generated report
        """
        pass


class IntegrationPlugin(BasePlugin):
    """Base class for external integration plugins"""

    service_name: str = "generic"

    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to external service.

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    async def send_data(self, data: Dict[str, Any]) -> bool:
        """
        Send data to external service.

        Args:
            data: Data to send

        Returns:
            True if successful
        """
        pass


class PluginManager:
    """Manages plugin loading, registration, and execution"""

    def __init__(self):
        self.logger = Logger(__name__)
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_types: Dict[str, List[BasePlugin]] = {
            "scanner": [],
            "report": [],
            "integration": [],
        }

    def register_plugin(self, plugin: BasePlugin) -> bool:
        """
        Register a plugin.

        Args:
            plugin: Plugin instance to register

        Returns:
            True if registration successful
        """
        try:
            plugin_name = plugin.name

            if plugin_name in self.plugins:
                self.logger.warning(
                    f"Plugin {plugin_name} already registered, replacing"
                )

            self.plugins[plugin_name] = plugin

            # Categorize plugin by type
            if isinstance(plugin, ScannerPlugin):
                self.plugin_types["scanner"].append(plugin)
            elif isinstance(plugin, ReportPlugin):
                self.plugin_types["report"].append(plugin)
            elif isinstance(plugin, IntegrationPlugin):
                self.plugin_types["integration"].append(plugin)

            self.logger.info(f"Registered plugin: {plugin_name} v{plugin.version}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register plugin {plugin.name}: {str(e)}")
            return False

    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin.

        Args:
            plugin_name: Name of plugin to unregister

        Returns:
            True if unregistration successful
        """
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin {plugin_name} not found")
            return False

        plugin = self.plugins[plugin_name]

        # Remove from type categories
        for plugin_list in self.plugin_types.values():
            if plugin in plugin_list:
                plugin_list.remove(plugin)

        # Clean up plugin
        asyncio.create_task(plugin.cleanup())

        del self.plugins[plugin_name]
        self.logger.info(f"Unregistered plugin: {plugin_name}")
        return True

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get plugin by name."""
        return self.plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: str) -> List[BasePlugin]:
        """Get all plugins of a specific type."""
        return self.plugin_types.get(plugin_type, [])

    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all registered plugins."""
        return {name: plugin.get_info() for name, plugin in self.plugins.items()}

    async def load_plugins_from_directory(self, directory: str) -> int:
        """
        Load plugins from a directory.

        Args:
            directory: Directory containing plugin files

        Returns:
            Number of plugins loaded
        """
        plugins_dir = Path(directory)
        if not plugins_dir.exists():
            self.logger.warning(f"Plugin directory not found: {directory}")
            return 0

        loaded_count = 0

        for plugin_file in plugins_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue

            try:
                loaded_count += await self._load_plugin_file(plugin_file)
            except Exception as e:
                self.logger.error(f"Failed to load plugin file {plugin_file}: {str(e)}")

        self.logger.info(f"Loaded {loaded_count} plugins from {directory}")
        return loaded_count

    async def _load_plugin_file(self, plugin_file: Path) -> int:
        """Load plugins from a Python file."""
        module_name = plugin_file.stem
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)

        if spec is None or spec.loader is None:
            self.logger.error(f"Could not load spec for {plugin_file}")
            return 0

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        loaded_count = 0

        # Look for plugin classes in the module
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, BasePlugin)
                and obj != BasePlugin
            ):

                try:
                    plugin_instance = obj()
                    if self.register_plugin(plugin_instance):
                        loaded_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to instantiate plugin {name}: {str(e)}")

        return loaded_count

    async def initialize_all_plugins(self, config: Dict[str, Any]) -> int:
        """
        Initialize all registered plugins.

        Args:
            config: Configuration for plugins

        Returns:
            Number of successfully initialized plugins
        """
        initialized_count = 0

        for plugin_name, plugin in self.plugins.items():
            try:
                plugin_config = config.get("plugins", {}).get(plugin_name, {})

                if await plugin.initialize(plugin_config):
                    initialized_count += 1
                    self.logger.info(f"Initialized plugin: {plugin_name}")
                else:
                    self.logger.warning(f"Failed to initialize plugin: {plugin_name}")

            except Exception as e:
                self.logger.error(f"Error initializing plugin {plugin_name}: {str(e)}")

        self.logger.info(f"Initialized {initialized_count}/{len(self.plugins)} plugins")
        return initialized_count

    async def execute_scanner_plugins(
        self, target: str, plugin_names: Optional[List[str]] = None
    ) -> List[ScanResult]:
        """
        Execute scanner plugins on target.

        Args:
            target: Target to scan
            plugin_names: Specific plugins to run (None for all)

        Returns:
            List of scan results
        """
        scanner_plugins = self.get_plugins_by_type("scanner")

        if plugin_names:
            scanner_plugins = [p for p in scanner_plugins if p.name in plugin_names]

        # Filter plugins that support the target
        suitable_plugins = [p for p in scanner_plugins if p.supports_target(target)]

        self.logger.info(f"Running {len(suitable_plugins)} scanner plugins on {target}")

        results = []
        tasks = []

        for plugin in suitable_plugins:
            task = asyncio.create_task(self._execute_scanner_plugin(plugin, target))
            tasks.append(task)

        # Wait for all scanner plugins to complete
        scanner_results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(scanner_results):
            if isinstance(result, Exception):
                self.logger.error(
                    f"Scanner plugin {suitable_plugins[i].name} failed: {str(result)}"
                )
            elif result:
                results.append(result)

        return results

    async def _execute_scanner_plugin(
        self, plugin: ScannerPlugin, target: str
    ) -> Optional[ScanResult]:
        """Execute a single scanner plugin."""
        try:
            self.logger.debug(f"Executing scanner plugin: {plugin.name}")
            result = await plugin.scan(target)
            return result
        except Exception as e:
            self.logger.error(
                f"Scanner plugin {plugin.name} execution failed: {str(e)}"
            )
            return None

    async def cleanup_all_plugins(self):
        """Clean up all plugins."""
        cleanup_tasks = []

        for plugin in self.plugins.values():
            task = asyncio.create_task(plugin.cleanup())
            cleanup_tasks.append(task)

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        self.logger.info("Cleaned up all plugins")


# Example Plugin Implementations


class CustomSemgrepPlugin(ScannerPlugin):
    """Example custom Semgrep plugin"""

    name = "custom-semgrep"
    version = "1.0.0"
    description = "Custom Semgrep scanner with additional rules"
    scan_type = "sast"
    supported_file_types = [".py", ".js", ".java", ".go"]

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin."""
        self.config = config
        self.custom_rules_path = config.get("custom_rules_path", "")
        return True

    async def scan(self, target: str) -> ScanResult:
        """Perform custom Semgrep scan."""
        import time

        start_time = time.time()

        # This would implement custom Semgrep scanning logic
        # For now, return a mock result

        from .scanner import ScanResult, Vulnerability, Severity

        vulnerabilities = [
            Vulnerability(
                id="custom-rule-1",
                title="Custom security issue detected",
                description="Example vulnerability from custom Semgrep rules",
                severity=Severity.MEDIUM,
                file_path=f"{target}/example.py",
                line_number=42,
                tool=self.name,
                rule_id="custom.security.example",
            )
        ]

        return ScanResult(
            tool=self.name,
            target=target,
            scan_type=self.scan_type,
            vulnerabilities=vulnerabilities,
            scan_duration=time.time() - start_time,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            metadata={"custom_rules": self.custom_rules_path},
        )


class SlackIntegrationPlugin(IntegrationPlugin):
    """Example Slack integration plugin"""

    name = "slack-integration"
    version = "1.0.0"
    description = "Send security alerts to Slack"
    service_name = "slack"

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize Slack integration."""
        self.webhook_url = config.get("webhook_url", "")
        self.channel = config.get("channel", "#security")

        if not self.webhook_url:
            self.logger.error("Slack webhook URL not configured")
            return False

        return True

    async def connect(self) -> bool:
        """Test Slack connection."""
        # Would implement connection test
        return True

    async def send_data(self, data: Dict[str, Any]) -> bool:
        """Send security data to Slack."""
        try:
            # Import httpx locally to avoid dependency issues
            try:
                import httpx
            except ImportError:
                self.logger.error("httpx library not available for Slack integration")
                return False

            # Format message for Slack
            message = self._format_slack_message(data)

            payload = {
                "channel": self.channel,
                "text": message["text"],
                "attachments": message.get("attachments", []),
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()

            self.logger.info("Successfully sent data to Slack")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send data to Slack: {str(e)}")
            return False

    def _format_slack_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for Slack message."""
        if "scan_results" in data:
            # Format scan results
            high_vulns = sum(
                len(
                    [
                        v
                        for v in result.get("vulnerabilities", [])
                        if v.get("severity") in ["HIGH", "CRITICAL"]
                    ]
                )
                for result in data["scan_results"].values()
            )

            return {
                "text": f"🔍 Security Scan Completed",
                "attachments": [
                    {
                        "color": "danger" if high_vulns > 0 else "good",
                        "fields": [
                            {
                                "title": "High/Critical Vulnerabilities",
                                "value": str(high_vulns),
                                "short": True,
                            }
                        ],
                    }
                ],
            }

        return {"text": "Security alert from SecureFlow"}


class HTMLReportPlugin(ReportPlugin):
    """Example HTML report plugin"""

    name = "html-report"
    version = "1.0.0"
    description = "Generate HTML security reports"
    output_format = "html"

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize HTML report plugin."""
        self.template_path = config.get("template_path", "")
        return True

    async def generate_report(self, data: Dict[str, Any], output_path: str) -> str:
        """Generate HTML report."""
        try:
            html_content = self._generate_html_content(data)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            self.logger.info(f"Generated HTML report: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {str(e)}")
            raise

    def _generate_html_content(self, data: Dict[str, Any]) -> str:
        """Generate HTML content from data."""
        # Simple HTML template - in practice, you'd use a templating engine
        html = (
            """
<!DOCTYPE html>
<html>
<head>
    <title>SecureFlow Security Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .summary { background: #ecf0f1; padding: 15px; margin: 20px 0; }
        .vulnerability { border-left: 4px solid #e74c3c; padding: 10px; margin: 10px 0; }
        .critical { border-left-color: #c0392b; }
        .high { border-left-color: #e74c3c; }
        .medium { border-left-color: #f39c12; }
        .low { border-left-color: #3498db; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 SecureFlow Security Report</h1>
        <p>Generated: """
            + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            + """</p>
    </div>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <p>Security scan completed with the following results:</p>
    </div>
    
    <!-- Report content would be generated here -->
    
</body>
</html>"""
        )

        return html
