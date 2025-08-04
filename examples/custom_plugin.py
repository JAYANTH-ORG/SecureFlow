"""
Custom plugin development example
"""

import asyncio
import time
from secureflow_core.plugins import ScannerPlugin
from secureflow_core.scanner import ScanResult, Vulnerability, Severity


class CustomSecurityPlugin(ScannerPlugin):
    """Example custom security scanner plugin"""
    
    name = "custom-security-scanner"
    version = "1.0.0"
    description = "Custom security scanner for specific security checks"
    scan_type = "custom"
    supported_file_types = [".py", ".js", ".ts"]
    
    async def initialize(self, config):
        """Initialize the plugin"""
        self.config = config
        self.custom_rules = config.get("custom_rules", [])
        self.logger.info(f"Initialized {self.name} with {len(self.custom_rules)} custom rules")
        return True
    
    async def scan(self, target: str) -> ScanResult:
        """Perform custom security scan"""
        start_time = time.time()
        self.logger.info(f"Running custom security scan on {target}")
        
        vulnerabilities = []
        
        # Example: Check for hardcoded secrets (simplified)
        secret_patterns = [
            "password", "secret", "key", "token", "api_key"
        ]
        
        try:
            from pathlib import Path
            target_path = Path(target)
            
            if target_path.is_file():
                files_to_scan = [target_path]
            else:
                # Scan supported files in directory
                files_to_scan = []
                for file_type in self.supported_file_types:
                    files_to_scan.extend(target_path.rglob(f"*{file_type}"))
            
            for file_path in files_to_scan:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        for pattern in secret_patterns:
                            if pattern.lower() in line.lower() and "=" in line:
                                vulnerability = Vulnerability(
                                    id=f"custom-secret-{file_path.name}-{line_num}",
                                    title=f"Potential hardcoded {pattern} detected",
                                    description=f"Found potential hardcoded {pattern} in code",
                                    severity=Severity.HIGH,
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    tool=self.name,
                                    rule_id=f"custom-hardcoded-{pattern}",
                                    recommendation=f"Move {pattern} to environment variables or secure vault"
                                )
                                vulnerabilities.append(vulnerability)
                
                except Exception as e:
                    self.logger.warning(f"Could not scan file {file_path}: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Custom scan failed: {str(e)}")
        
        return ScanResult(
            tool=self.name,
            target=target,
            scan_type=self.scan_type,
            vulnerabilities=vulnerabilities,
            scan_duration=time.time() - start_time,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            metadata={
                "custom_rules_count": len(self.custom_rules),
                "files_scanned": len(files_to_scan) if 'files_to_scan' in locals() else 0
            }
        )


async def plugin_example():
    """Example of using custom plugins"""
    print("🧩 SecureFlow Custom Plugin Example")
    
    from secureflow_core.plugins import PluginManager
    
    # Create plugin manager
    plugin_manager = PluginManager()
    
    # Register custom plugin
    custom_plugin = CustomSecurityPlugin()
    success = plugin_manager.register_plugin(custom_plugin)
    
    if success:
        print(f"✅ Registered custom plugin: {custom_plugin.name}")
    else:
        print("❌ Failed to register custom plugin")
        return
    
    # Initialize plugin with configuration
    plugin_config = {
        "custom-security-scanner": {
            "custom_rules": [
                "check_hardcoded_secrets",
                "check_weak_crypto"
            ]
        }
    }
    
    initialized_count = await plugin_manager.initialize_all_plugins(plugin_config)
    print(f"📦 Initialized {initialized_count} plugins")
    
    # Execute custom scanner plugin
    print("\n🔍 Running custom security scan...")
    scan_results = await plugin_manager.execute_scanner_plugins(
        target=".",
        plugin_names=["custom-security-scanner"]
    )
    
    # Display results
    for result in scan_results:
        print(f"\n📊 {result.tool} scan results:")
        print(f"  Target: {result.target}")
        print(f"  Vulnerabilities found: {len(result.vulnerabilities)}")
        print(f"  Scan duration: {result.scan_duration:.2f}s")
        
        if result.vulnerabilities:
            print("  Issues found:")
            for vuln in result.vulnerabilities[:3]:  # Show first 3
                print(f"    • {vuln.title} ({vuln.severity.value})")
                print(f"      File: {vuln.file_path}:{vuln.line_number}")
    
    # List all registered plugins
    print(f"\n📋 Registered plugins:")
    plugins = plugin_manager.list_plugins()
    for name, info in plugins.items():
        print(f"  • {name} v{info['version']} - {info['description']}")
    
    # Cleanup
    await plugin_manager.cleanup_all_plugins()
    print("\n✅ Plugin example completed!")


if __name__ == "__main__":
    asyncio.run(plugin_example())
