"""
Basic usage example of SecureFlow shared library
"""

import asyncio
from secureflow_core import SecureFlow, Config


async def main():
    """Main example function"""
    print("🚀 SecureFlow Basic Usage Example")
    
    # Initialize SecureFlow with default configuration
    secureflow = SecureFlow()
    
    # Or initialize with custom configuration
    config = Config()
    config.scanning.sast_tool = "semgrep"
    config.scanning.severity_threshold = "medium"
    secureflow_custom = SecureFlow(config)
    
    # Run a comprehensive security scan
    print("\n📊 Running comprehensive security scan...")
    scan_results = await secureflow.scan_repository(".")
    
    # Display summary
    print("\n📋 Scan Results Summary:")
    for scan_type, result in scan_results.items():
        if isinstance(result, dict):
            vulns = result.get("vulnerabilities", [])
            print(f"  {scan_type.upper()}: {len(vulns)} vulnerabilities found")
            
            # Show high/critical vulnerabilities
            high_vulns = [v for v in vulns if v.get("severity") in ["HIGH", "CRITICAL"]]
            if high_vulns:
                print(f"    ⚠️  {len(high_vulns)} high/critical vulnerabilities")
    
    # Generate security report
    print("\n📄 Generating security report...")
    report_path = await secureflow.generate_security_report(scan_results)
    print(f"Report generated: {report_path}")
    
    # Get security metrics
    print("\n📈 Security Metrics:")
    metrics = secureflow.get_security_metrics()
    print(f"  Total scans completed: {metrics.get('scans_completed', 0)}")
    print(f"  Total vulnerabilities found: {metrics.get('vulnerabilities_found', 0)}")
    
    # Cleanup
    await secureflow.cleanup()
    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
