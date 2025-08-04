"""
Report generation module for SecureFlow
"""

import asyncio
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import jinja2
from jinja2 import Environment, FileSystemLoader, BaseLoader

from .utils import Logger


class ReportGenerator:
    """Main report generator for security scan results"""

    def __init__(self, config):
        self.config = config
        self.logger = Logger(__name__)
        self.template_env = self._setup_template_environment()

    def _setup_template_environment(self) -> Environment:
        """Set up Jinja2 template environment"""
        # Use a DictLoader with built-in templates
        templates = {
            "security_report.html": self._get_html_template(),
            "security_report.md": self._get_markdown_template(),
            "compliance_report.html": self._get_compliance_html_template(),
        }

        loader = jinja2.DictLoader(templates)
        env = Environment(loader=loader, autoescape=True)

        # Add custom filters
        env.filters["severity_color"] = self._severity_color_filter
        env.filters["format_datetime"] = self._format_datetime_filter

        return env

    async def generate_comprehensive_report(
        self, scan_results: Dict[str, Any], output_path: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive security report from scan results.

        Args:
            scan_results: Security scan results
            output_path: Optional output path

        Returns:
            Path to generated report
        """
        self.logger.info("Generating comprehensive security report")

        # Prepare report data
        report_data = self._prepare_report_data(scan_results)

        # Determine output format and path
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"security_report_{timestamp}.html"

        output_format = Path(output_path).suffix.lower()

        if output_format == ".html":
            content = await self._generate_html_report(report_data)
        elif output_format == ".md":
            content = await self._generate_markdown_report(report_data)
        elif output_format == ".json":
            content = json.dumps(report_data, indent=2)
        else:
            raise ValueError(f"Unsupported report format: {output_format}")

        # Write report to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.logger.info(f"Generated security report: {output_path}")
        return output_path

    def _prepare_report_data(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for report generation"""
        total_vulnerabilities = 0
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        scan_summary = {}

        for scan_type, result in scan_results.items():
            if isinstance(result, dict):
                vulnerabilities = result.get("vulnerabilities", [])
                total_vulnerabilities += len(vulnerabilities)

                scan_severity_counts = {
                    "CRITICAL": 0,
                    "HIGH": 0,
                    "MEDIUM": 0,
                    "LOW": 0,
                    "INFO": 0,
                }

                for vuln in vulnerabilities:
                    severity = vuln.get("severity", "INFO")
                    if severity in severity_counts:
                        severity_counts[severity] += 1
                        scan_severity_counts[severity] += 1

                scan_summary[scan_type] = {
                    "tool": result.get("tool", scan_type),
                    "total_vulnerabilities": len(vulnerabilities),
                    "severity_counts": scan_severity_counts,
                    "scan_duration": result.get("scan_duration", 0),
                    "target": result.get("target", "Unknown"),
                }

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_vulnerabilities": total_vulnerabilities,
                "severity_counts": severity_counts,
                "scan_types": list(scan_results.keys()),
                "scans_completed": len(scan_results),
            },
            "scan_results": scan_results,
            "scan_summary": scan_summary,
            "metadata": {"generator": "SecureFlow", "version": "1.0.0"},
        }

    async def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML report"""
        template = self.template_env.get_template("security_report.html")
        return template.render(**report_data)

    async def _generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """Generate Markdown report"""
        template = self.template_env.get_template("security_report.md")
        return template.render(**report_data)

    def _get_html_template(self) -> str:
        """Get HTML report template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecureFlow Security Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header .subtitle { font-size: 1.2rem; opacity: 0.9; }
        
        .summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .card { background: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid #667eea; }
        .card h3 { color: #667eea; margin-bottom: 1rem; }
        .card .number { font-size: 2rem; font-weight: bold; color: #333; }
        
        .severity-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 1rem; margin: 1rem 0; }
        .severity-item { text-align: center; padding: 1rem; border-radius: 8px; color: white; font-weight: bold; }
        .critical { background: #e74c3c; }
        .high { background: #f39c12; }
        .medium { background: #f1c40f; color: #333; }
        .low { background: #3498db; }
        .info { background: #95a5a6; }
        
        .scan-results { margin-top: 2rem; }
        .scan-type { background: white; border-radius: 10px; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .scan-type-header { background: #f8f9fa; padding: 1rem; border-radius: 10px 10px 0 0; border-bottom: 1px solid #dee2e6; }
        .scan-type-header h3 { color: #495057; }
        
        .vulnerabilities { padding: 1rem; }
        .vulnerability { border-left: 4px solid #dee2e6; padding: 1rem; margin-bottom: 1rem; background: #f8f9fa; border-radius: 0 8px 8px 0; }
        .vulnerability.critical { border-left-color: #e74c3c; }
        .vulnerability.high { border-left-color: #f39c12; }
        .vulnerability.medium { border-left-color: #f1c40f; }
        .vulnerability.low { border-left-color: #3498db; }
        .vulnerability.info { border-left-color: #95a5a6; }
        
        .vulnerability h4 { margin-bottom: 0.5rem; color: #2c3e50; }
        .vulnerability .meta { font-size: 0.9rem; color: #6c757d; margin-bottom: 0.5rem; }
        .vulnerability .description { color: #495057; }
        
        .footer { margin-top: 3rem; padding: 2rem; background: #f8f9fa; border-radius: 10px; text-align: center; color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Security Report</h1>
            <div class="subtitle">Generated by SecureFlow on {{ timestamp | format_datetime }}</div>
        </div>
        
        <div class="summary-cards">
            <div class="card">
                <h3>Total Vulnerabilities</h3>
                <div class="number">{{ summary.total_vulnerabilities }}</div>
            </div>
            <div class="card">
                <h3>Scans Completed</h3>
                <div class="number">{{ summary.scans_completed }}</div>
            </div>
            <div class="card">
                <h3>Scan Types</h3>
                <div class="number">{{ summary.scan_types | length }}</div>
            </div>
        </div>
        
        <div class="card">
            <h3>Vulnerabilities by Severity</h3>
            <div class="severity-grid">
                <div class="severity-item critical">
                    <div class="number">{{ summary.severity_counts.CRITICAL }}</div>
                    <div>Critical</div>
                </div>
                <div class="severity-item high">
                    <div class="number">{{ summary.severity_counts.HIGH }}</div>
                    <div>High</div>
                </div>
                <div class="severity-item medium">
                    <div class="number">{{ summary.severity_counts.MEDIUM }}</div>
                    <div>Medium</div>
                </div>
                <div class="severity-item low">
                    <div class="number">{{ summary.severity_counts.LOW }}</div>
                    <div>Low</div>
                </div>
                <div class="severity-item info">
                    <div class="number">{{ summary.severity_counts.INFO }}</div>
                    <div>Info</div>
                </div>
            </div>
        </div>
        
        <div class="scan-results">
            <h2>Detailed Scan Results</h2>
            
            {% for scan_type, result in scan_results.items() %}
            <div class="scan-type">
                <div class="scan-type-header">
                    <h3>{{ scan_type.upper() }} Scan Results</h3>
                    <div>Tool: {{ result.tool }} | Target: {{ result.target }} | Duration: {{ "%.2f"|format(result.scan_duration) }}s</div>
                </div>
                
                <div class="vulnerabilities">
                    {% if result.vulnerabilities %}
                        {% for vuln in result.vulnerabilities %}
                        <div class="vulnerability {{ vuln.severity.lower() }}">
                            <h4>{{ vuln.title }}</h4>
                            <div class="meta">
                                <strong>Severity:</strong> {{ vuln.severity }}
                                {% if vuln.file_path %} | <strong>File:</strong> {{ vuln.file_path }}{% endif %}
                                {% if vuln.line_number %} | <strong>Line:</strong> {{ vuln.line_number }}{% endif %}
                                {% if vuln.cwe %} | <strong>CWE:</strong> {{ vuln.cwe }}{% endif %}
                            </div>
                            <div class="description">{{ vuln.description }}</div>
                            {% if vuln.recommendation %}
                            <div class="recommendation"><strong>Recommendation:</strong> {{ vuln.recommendation }}</div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="vulnerability info">
                            <h4>✅ No vulnerabilities found</h4>
                            <div class="description">This scan completed successfully with no security issues detected.</div>
                        </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>Report generated by <strong>SecureFlow v{{ metadata.version }}</strong></p>
            <p>For more information, visit our documentation</p>
        </div>
    </div>
</body>
</html>
        """

    def _get_markdown_template(self) -> str:
        """Get Markdown report template"""
        return """
# 🔍 SecureFlow Security Report

**Generated:** {{ timestamp | format_datetime }}  
**Generator:** SecureFlow v{{ metadata.version }}

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Vulnerabilities | {{ summary.total_vulnerabilities }} |
| Scans Completed | {{ summary.scans_completed }} |
| Scan Types | {{ summary.scan_types | join(', ') }} |

### Vulnerabilities by Severity

| Severity | Count |
|----------|-------|
| 🔴 Critical | {{ summary.severity_counts.CRITICAL }} |
| 🟠 High | {{ summary.severity_counts.HIGH }} |
| 🟡 Medium | {{ summary.severity_counts.MEDIUM }} |
| 🔵 Low | {{ summary.severity_counts.LOW }} |
| ⚪ Info | {{ summary.severity_counts.INFO }} |

## Detailed Results

{% for scan_type, result in scan_results.items() %}
### {{ scan_type.upper() }} Scan

**Tool:** {{ result.tool }}  
**Target:** {{ result.target }}  
**Duration:** {{ "%.2f"|format(result.scan_duration) }} seconds  
**Vulnerabilities Found:** {{ result.vulnerabilities | length }}

{% if result.vulnerabilities %}
{% for vuln in result.vulnerabilities %}
#### {{ vuln.severity }} - {{ vuln.title }}

- **Description:** {{ vuln.description }}
{% if vuln.file_path %}- **File:** `{{ vuln.file_path }}`{% if vuln.line_number %}:{{ vuln.line_number }}{% endif %}{% endif %}
{% if vuln.cwe %}- **CWE:** {{ vuln.cwe }}{% endif %}
{% if vuln.recommendation %}- **Recommendation:** {{ vuln.recommendation }}{% endif %}

{% endfor %}
{% else %}
✅ No vulnerabilities found in this scan.
{% endif %}

---

{% endfor %}

## Recommendations

{% if summary.severity_counts.CRITICAL > 0 or summary.severity_counts.HIGH > 0 %}
⚠️ **Immediate Action Required:**
- Address all Critical and High severity vulnerabilities
- Review security practices and implement additional controls
- Consider security training for development team
{% else %}
✅ **Good Security Posture:**
- Continue regular security scanning
- Address Medium/Low severity issues in upcoming releases
- Maintain current security practices
{% endif %}

---

*This report was automatically generated by SecureFlow. For questions or support, please contact your security team.*
        """

    def _get_compliance_html_template(self) -> str:
        """Get compliance report HTML template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecureFlow Compliance Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }
        .compliance-framework { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .compliant { border-left: 5px solid #27ae60; }
        .non-compliant { border-left: 5px solid #e74c3c; }
        .requirement { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; }
        .status-pass { color: #27ae60; font-weight: bold; }
        .status-fail { color: #e74c3c; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Compliance Report</h1>
        <p>Generated: {{ timestamp | format_datetime }}</p>
    </div>
    
    <!-- Compliance content would be rendered here -->
    
</body>
</html>
        """

    def _severity_color_filter(self, severity: str) -> str:
        """Jinja2 filter for severity colors"""
        colors = {
            "CRITICAL": "#e74c3c",
            "HIGH": "#f39c12",
            "MEDIUM": "#f1c40f",
            "LOW": "#3498db",
            "INFO": "#95a5a6",
        }
        return colors.get(severity.upper(), "#95a5a6")

    def _format_datetime_filter(self, timestamp: str) -> str:
        """Jinja2 filter for datetime formatting"""
        try:
            if "T" in timestamp:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return timestamp
