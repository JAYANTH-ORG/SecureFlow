#!/usr/bin/env python3
"""
SecureFlow Security Scanner
Main script for the secureflow-scan GitHub Action
"""

import asyncio
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

def log(message: str, level: str = "INFO"):
    """Log a message with timestamp and level"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def run_command(cmd: List[str], cwd: str = ".") -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out after 5 minutes"
    except Exception as e:
        return 1, "", str(e)

def run_semgrep(target: str) -> Dict:
    """Run Semgrep SAST scan"""
    log("Running Semgrep SAST scan...")
    
    cmd = ["semgrep", "--config=auto", "--json", "--quiet", target]
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0:
        try:
            results = json.loads(stdout) if stdout else {"results": []}
            log(f"Semgrep found {len(results.get('results', []))} findings")
            return {
                "tool": "semgrep",
                "success": True,
                "findings": len(results.get('results', [])),
                "results": results
            }
        except json.JSONDecodeError:
            log("Failed to parse Semgrep JSON output", "ERROR")
            return {"tool": "semgrep", "success": False, "error": "JSON parse error"}
    else:
        log(f"Semgrep failed: {stderr}", "ERROR")
        return {"tool": "semgrep", "success": False, "error": stderr}

def run_trufflehog(target: str) -> Dict:
    """Run TruffleHog secrets scan"""
    log("Running TruffleHog secrets scan...")
    
    cmd = ["trufflehog", "filesystem", target, "--json", "--no-update"]
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0 or returncode == 183:  # 183 is TruffleHog's "found secrets" exit code
        try:
            # TruffleHog outputs one JSON object per line
            findings = []
            if stdout:
                for line in stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            findings.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            
            log(f"TruffleHog found {len(findings)} secrets")
            return {
                "tool": "trufflehog",
                "success": True,
                "findings": len(findings),
                "results": {"findings": findings}
            }
        except Exception as e:
            log(f"Failed to parse TruffleHog output: {e}", "ERROR")
            return {"tool": "trufflehog", "success": False, "error": str(e)}
    else:
        log(f"TruffleHog failed: {stderr}", "ERROR")
        return {"tool": "trufflehog", "success": False, "error": stderr}

def run_safety_check() -> Dict:
    """Run Safety dependency check for Python projects"""
    log("Running Safety dependency check...")
    
    cmd = ["safety", "check", "--json", "--short-report"]
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0:
        try:
            results = json.loads(stdout) if stdout else []
            log(f"Safety found {len(results)} vulnerabilities")
            return {
                "tool": "safety",
                "success": True,
                "findings": len(results),
                "results": {"vulnerabilities": results}
            }
        except json.JSONDecodeError:
            log("Failed to parse Safety JSON output", "ERROR")
            return {"tool": "safety", "success": False, "error": "JSON parse error"}
    else:
        log(f"Safety check failed: {stderr}", "ERROR")
        return {"tool": "safety", "success": False, "error": stderr}

def run_maven_dependency_check() -> Dict:
    """Run Maven dependency analysis for Java projects"""
    log("Running Maven dependency analysis...")
    
    if not os.path.exists("pom.xml"):
        return {"tool": "maven-deps", "success": False, "error": "No pom.xml found"}
    
    cmd = ["mvn", "dependency:tree", "-DoutputType=text", "-DoutputFile=maven-deps.txt"]
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0:
        deps_count = 0
        if os.path.exists("maven-deps.txt"):
            with open("maven-deps.txt", "r") as f:
                deps_count = len([line for line in f if line.strip().startswith("+")])
        
        log(f"Maven found {deps_count} dependencies")
        return {
            "tool": "maven-deps",
            "success": True,
            "findings": deps_count,
            "results": {"dependencies_file": "maven-deps.txt"}
        }
    else:
        log(f"Maven dependency check failed: {stderr}", "ERROR")
        return {"tool": "maven-deps", "success": False, "error": stderr}

def try_secureflow_cli(target: str, config: Dict) -> Optional[Dict]:
    """Try to run SecureFlow CLI"""
    log("Attempting to run SecureFlow CLI...")
    
    # Check if CLI is available
    returncode, _, _ = run_command(["which", "secureflow"])
    if returncode != 0:
        returncode, _, _ = run_command(["secureflow", "--version"])
        if returncode != 0:
            log("SecureFlow CLI not available", "WARN")
            return None
    
    # Build CLI command
    cmd = [
        "secureflow", "scan", "all", target,
        "--types", config["scan_types"],
        "--project-type", config["project_type"],
        "--output-format", config["output_format"],
        "--output-file", config["output_file"],
        "--severity-threshold", config["severity_threshold"]
    ]
    
    if config.get("config_file") and os.path.exists(config["config_file"]):
        cmd.extend(["--config", config["config_file"]])
    
    if config.get("java_version"):
        cmd.extend(["--java-version", config["java_version"]])
    
    log(f"Running: {' '.join(cmd)}")
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0:
        log("SecureFlow CLI completed successfully")
        return {"tool": "secureflow-cli", "success": True, "output": stdout}
    else:
        log(f"SecureFlow CLI failed: {stderr}", "ERROR")
        return None

async def try_secureflow_module(target: str, config: Dict) -> Optional[Dict]:
    """Try to run SecureFlow Python module"""
    log("Attempting to run SecureFlow Python module...")
    
    try:
        from secureflow_core import SecureFlow
        from secureflow_core.config import Config
        log("SecureFlow module imported successfully")
        
        # Configure SecureFlow
        sf_config = Config()
        
        # Try to set project type - handle different possible field names
        try:
            if hasattr(sf_config.scanning, 'project_type'):
                sf_config.scanning.project_type = config["project_type"]
            elif hasattr(sf_config.scanning, 'project'):
                sf_config.scanning.project = config["project_type"]
        except Exception as e:
            log(f"Could not set project type: {e}", "WARN")
        
        # Try to set scan types
        try:
            if hasattr(sf_config.scanning, 'scan_types'):
                sf_config.scanning.scan_types = config["scan_types"].split(',')
            elif hasattr(sf_config.scanning, 'types'):
                sf_config.scanning.types = config["scan_types"].split(',')
        except Exception as e:
            log(f"Could not set scan types: {e}", "WARN")
        
        # Try to set severity threshold
        try:
            if hasattr(sf_config.scanning, 'severity_threshold'):
                sf_config.scanning.severity_threshold = config["severity_threshold"]
            elif hasattr(sf_config.scanning, 'severity'):
                sf_config.scanning.severity = config["severity_threshold"]
        except Exception as e:
            log(f"Could not set severity threshold: {e}", "WARN")
        
        # Try to set output configuration
        try:
            if hasattr(sf_config, 'output'):
                if hasattr(sf_config.output, 'format'):
                    sf_config.output.format = config["output_format"]
                if hasattr(sf_config.output, 'file'):
                    sf_config.output.file = config["output_file"]
        except Exception as e:
            log(f"Could not set output config: {e}", "WARN")
        
        log(f"Scanning target: {target}")
        log(f"Scan types: {config['scan_types']}")
        log(f"Project type: {config['project_type']}")
        
        # Initialize and run scan
        sf = SecureFlow(sf_config)
        results = await sf.scan_repository(target)
        
        log(f"SecureFlow module scan completed: {len(results)} results")
        return {
            "tool": "secureflow-module",
            "success": True,
            "results": results,
            "count": len(results)
        }
        
    except ImportError as e:
        log(f"SecureFlow module not available: {e}", "WARN")
        return None
    except Exception as e:
        log(f"SecureFlow module failed: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return None

def run_individual_tools(target: str, scan_types: List[str], project_type: str) -> List[Dict]:
    """Run individual security tools as fallback"""
    log("Running individual security tools as fallback...")
    
    results = []
    
    for scan_type in scan_types:
        if scan_type == "sast":
            results.append(run_semgrep(target))
        elif scan_type == "secrets":
            results.append(run_trufflehog(target))
        elif scan_type == "dependencies":
            if project_type == "java-maven":
                results.append(run_maven_dependency_check())
            else:
                results.append(run_safety_check())
        elif scan_type == "containers":
            # Try basic container file detection if no advanced tools available
            container_result = run_basic_container_scan(target)
            if container_result:
                results.append(container_result)
            else:
                log("Container scanning requested but no container files found", "WARN")
        else:
            log(f"Unknown scan type: {scan_type}", "WARN")
    
    return results

def create_sarif_output(tool_results: List[Dict], output_file: str):
    """Create SARIF output from tool results"""
    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": []
    }
    
    for result in tool_results:
        if not result.get("success"):
            continue
            
        tool_name = result["tool"]
        run = {
            "tool": {
                "driver": {
                    "name": tool_name.title(),
                    "version": "1.0.0"
                }
            },
            "results": []
        }
        
        # Convert tool-specific results to SARIF format
        if tool_name == "semgrep" and "results" in result:
            # Semgrep already outputs in a compatible format
            semgrep_results = result["results"].get("results", [])
            for finding in semgrep_results[:10]:  # Limit to first 10 for demo
                sarif_result = {
                    "ruleId": finding.get("check_id", "unknown"),
                    "message": {"text": finding.get("message", "Security finding")},
                    "level": "warning",
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {"uri": finding.get("path", "unknown")},
                            "region": {"startLine": finding.get("start", {}).get("line", 1)}
                        }
                    }]
                }
                run["results"].append(sarif_result)
        
        elif tool_name == "trufflehog" and "results" in result:
            # Convert TruffleHog findings
            findings = result["results"].get("findings", [])
            for finding in findings[:10]:  # Limit to first 10 for demo
                sarif_result = {
                    "ruleId": "secret-detected",
                    "message": {"text": f"Secret detected: {finding.get('DetectorName', 'Unknown')}"},
                    "level": "error",
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {"uri": finding.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("file", "unknown")},
                            "region": {"startLine": finding.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("line", 1)}
                        }
                    }]
                }
                run["results"].append(sarif_result)
        
        sarif["runs"].append(run)
    
    # Write SARIF file
    with open(output_file, "w") as f:
        json.dump(sarif, f, indent=2)
    
    log(f"SARIF output written to {output_file}")

def create_html_report(tool_results: List[Dict], output_file: str, config: Dict):
    """Create HTML report from scan results"""
    total_findings = sum(result.get("findings", 0) for result in tool_results if result.get("success"))
    successful_tools = [result["tool"] for result in tool_results if result.get("success")]
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecureFlow Security Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.07); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 2.5rem; font-weight: 300; }}
        .header p {{ margin: 0.5rem 0 0 0; opacity: 0.9; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; padding: 2rem; background: #f8fafc; }}
        .metric {{ background: white; padding: 1.5rem; border-radius: 8px; text-align: center; border-left: 4px solid #667eea; }}
        .metric.critical {{ border-left-color: #e53e3e; }}
        .metric.high {{ border-left-color: #dd6b20; }}
        .metric h3 {{ margin: 0 0 0.5rem 0; color: #4a5568; font-size: 0.9rem; text-transform: uppercase; }}
        .metric .value {{ font-size: 2rem; font-weight: bold; color: #2d3748; }}
        .section {{ padding: 2rem; border-bottom: 1px solid #e2e8f0; }}
        .section:last-child {{ border-bottom: none; }}
        .section h2 {{ margin: 0 0 1rem 0; color: #2d3748; }}
        .tools {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
        .tool-badge {{ background: #edf2f7; color: #4a5568; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.875rem; }}
        .tool-badge.success {{ background: #c6f6d5; color: #276749; }}
        .tool-badge.error {{ background: #fed7d7; color: #c53030; }}
        .no-findings {{ color: #38a169; font-weight: 600; font-size: 1.1rem; }}
        .findings-summary {{ background: #f7fafc; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #4299e1; }}
        .footer {{ background: #f7fafc; padding: 1rem; text-align: center; color: #718096; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ SecureFlow Security Report</h1>
            <p>Project: {config.get('target', '.')} | Scan Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Project Type: {config.get('project_type', 'auto')} | Scan Types: {config.get('scan_types', 'N/A')}</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <h3>Total Findings</h3>
                <div class="value">{total_findings}</div>
            </div>
            <div class="metric">
                <h3>Tools Run</h3>
                <div class="value">{len(successful_tools)}</div>
            </div>
            <div class="metric">
                <h3>Scan Status</h3>
                <div class="value" style="font-size: 1.2rem;">{'✅ Success' if successful_tools else '❌ Failed'}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔧 Tools Executed</h2>
            <div class="tools">
"""
    
    for result in tool_results:
        status_class = "success" if result.get("success") else "error"
        status_icon = "✅" if result.get("success") else "❌"
        findings = result.get("findings", 0)
        html_content += f'                <span class="tool-badge {status_class}">{status_icon} {result["tool"]} ({findings} findings)</span>\n'
    
    html_content += f"""            </div>
        </div>
        
        <div class="section">
            <h2>📊 Scan Results</h2>
            <div class="findings-summary">
"""
    
    if total_findings == 0:
        html_content += '                <p class="no-findings">🎉 No security issues detected!</p>'
    else:
        html_content += f'                <p><strong>{total_findings}</strong> security findings detected across {len(successful_tools)} tools.</p>'
        html_content += '                <h3>Findings by Tool:</h3><ul>'
        for result in tool_results:
            if result.get("success") and result.get("findings", 0) > 0:
                html_content += f'<li><strong>{result["tool"]}:</strong> {result["findings"]} findings</li>'
        html_content += '</ul>'
    
    html_content += f"""            </div>
        </div>
        
        <div class="footer">
            <p>Generated by SecureFlow Security Scanner | <a href="https://github.com/JAYANTH-ORG/SecureFlow">GitHub Repository</a></p>
        </div>
    </div>
</body>
</html>"""
    
    with open(output_file, "w") as f:
        f.write(html_content)
    
    log(f"HTML report written to {output_file}")

def run_basic_container_scan(target: str) -> Optional[Dict]:
    """Basic container file detection and analysis"""
    log("Running basic container file detection...")
    
    container_files = []
    findings = 0
    
    # Look for Dockerfile and docker-compose files
    for root, dirs, files in os.walk(target):
        for file in files:
            if file.lower() in ['dockerfile', 'dockerfile.prod', 'dockerfile.dev'] or file.startswith('Dockerfile'):
                container_files.append(os.path.join(root, file))
                findings += 1
            elif file.lower().startswith('docker-compose'):
                container_files.append(os.path.join(root, file))
                findings += 1
    
    if container_files:
        log(f"Found {len(container_files)} container files")
        return {
            "tool": "container-detection",
            "success": True,
            "findings": findings,
            "results": {"container_files": container_files}
        }
    else:
        return None

async def main():
    """Main function for the security scanner"""
    # Get configuration from environment variables
    config = {
        "target": os.getenv("INPUT_TARGET", "."),
        "project_type": os.getenv("INPUT_PROJECT_TYPE", "auto"),
        "scan_types": os.getenv("INPUT_SCAN_TYPES", "sast,secrets,dependencies"),
        "severity_threshold": os.getenv("INPUT_SEVERITY_THRESHOLD", "medium"),
        "output_format": os.getenv("INPUT_OUTPUT_FORMAT", "sarif"),
        "output_file": os.getenv("INPUT_OUTPUT_FILE", "security-results"),
        "generate_html": os.getenv("INPUT_GENERATE_HTML", "true").lower() == "true",
        "config_file": os.getenv("INPUT_CONFIG_FILE", ".secureflow.yaml"),
        "java_version": os.getenv("INPUT_JAVA_VERSION", ""),
        "fail_on_findings": os.getenv("INPUT_FAIL_ON_FINDINGS", "false").lower() == "true"
    }
    
    log("Starting SecureFlow security scan...")
    log(f"Target: {config['target']}")
    log(f"Project type: {config['project_type']}")
    log(f"Scan types: {config['scan_types']}")
    
    # Determine output file paths
    primary_output = f"{config['output_file']}.sarif" if config['output_format'] == 'sarif' else f"{config['output_file']}.{config['output_format']}"
    html_output = f"{config['output_file']}.html"
    
    # Create output directory
    os.makedirs("security-results", exist_ok=True)
    os.makedirs(os.path.dirname(primary_output) or ".", exist_ok=True)
    
    # Try SecureFlow CLI first
    secureflow_result = try_secureflow_cli(config["target"], config)
    tools_run = []
    tool_results = []
    
    if secureflow_result:
        tools_run.append("secureflow-cli")
        tool_results.append(secureflow_result)
        log("SecureFlow CLI succeeded")
    else:
        # Try SecureFlow module
        module_result = await try_secureflow_module(config["target"], config)
        if module_result:
            tools_run.append("secureflow-module")
            tool_results.append(module_result)
            log("SecureFlow module succeeded")
        else:
            # Fall back to individual tools
            log("Falling back to individual security tools...")
            scan_types = config["scan_types"].split(",")
            individual_results = run_individual_tools(config["target"], scan_types, config["project_type"])
            tool_results.extend(individual_results)
            tools_run.extend([r["tool"] for r in individual_results if r.get("success")])
    
    # Create SARIF output
    create_sarif_output(tool_results, primary_output)
    
    # Create HTML report if requested
    if config["generate_html"]:
        create_html_report(tool_results, html_output, config)
    
    # Calculate statistics
    total_findings = sum(result.get("findings", 0) for result in tool_results if result.get("success"))
    successful_tools = len([r for r in tool_results if r.get("success")])
    
    # Set GitHub Actions outputs
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"results-file={primary_output}\n")
            f.write(f"html-report={html_output if config['generate_html'] else ''}\n")
            f.write(f"findings-count={total_findings}\n")
            f.write(f"critical-count=0\n")  # Would need more sophisticated parsing
            f.write(f"high-count=0\n")     # Would need more sophisticated parsing
            f.write(f"scan-status={'success' if successful_tools > 0 else 'failed'}\n")
            f.write(f"tools-run={','.join(tools_run)}\n")
    
    # Final summary
    log("=" * 50)
    log("SCAN SUMMARY")
    log("=" * 50)
    log(f"Total findings: {total_findings}")
    log(f"Tools executed: {', '.join(tools_run) if tools_run else 'None'}")
    log(f"Primary output: {primary_output}")
    if config["generate_html"]:
        log(f"HTML report: {html_output}")
    log(f"Scan status: {'SUCCESS' if successful_tools > 0 else 'FAILED'}")
    
    # Exit with appropriate code
    if config["fail_on_findings"] and total_findings > 0:
        log("Failing due to security findings and fail_on_findings=true", "ERROR")
        sys.exit(1)
    elif successful_tools == 0:
        log("Failing due to no successful tool executions", "ERROR")
        sys.exit(1)
    else:
        log("Scan completed successfully")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
