"""
Command-Line Interface for SecureFlow
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, List
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from . import SecureFlow, Config
from .utils import Logger


console = Console()
logger = Logger(__name__)


@click.group()
@click.version_option(version="1.0.0")
@click.option("--config", "-c", help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx, config, verbose):
    """
    SecureFlow - Shared DevSecOps Library CLI

    A comprehensive security automation tool for development teams.
    """
    # Set up context
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["verbose"] = verbose

    if verbose:
        logger.set_level("DEBUG")


@cli.command()
@click.option(
    "--project-type",
    type=click.Choice(["python", "node", "java", "dotnet", "go"]),
    help="Project type for template generation",
)
@click.option("--azure", is_flag=True, help="Include Azure DevOps configuration")
@click.option("--force", is_flag=True, help="Overwrite existing configuration")
@click.pass_context
def init(ctx, project_type, azure, force):
    """
    Initialize SecureFlow in current directory.

    Creates configuration files and templates for security automation.
    """
    console.print(Panel.fit("🚀 Initializing SecureFlow", style="bold blue"))

    config_file = Path(".secureflow.yml")

    if config_file.exists() and not force:
        console.print(
            "❌ SecureFlow already initialized. Use --force to overwrite.", style="red"
        )
        return

    # Create default configuration
    config = Config()

    if azure:
        console.print("🔧 Setting up Azure DevOps integration...")
        # Prompt for Azure settings
        org = click.prompt("Azure DevOps Organization", type=str)
        pat = click.prompt("Personal Access Token", type=str, hide_input=True)

        from .config import AzureConfig

        config.azure = AzureConfig(devops_organization=org, pat_token=pat)

    # Save configuration
    config.save(str(config_file))

    # Create Azure DevOps templates if requested
    if azure:
        _create_azure_templates(project_type)

    # Create .gitignore entries
    _update_gitignore()

    console.print("✅ SecureFlow initialized successfully!", style="green")
    console.print(f"📁 Configuration saved to: {config_file}")

    if azure:
        console.print(
            "📋 Azure DevOps templates created in '.azure-pipelines/' directory"
        )


@cli.command()
@click.option(
    "--types",
    "-t",
    type=click.Choice(["sast", "sca", "secrets", "iac", "container", "all"]),
    multiple=True,
    default=["all"],
    help="Types of scans to run",
)
@click.option("--target", "-T", default=".", help="Target path to scan")
@click.option("--output", "-o", help="Output file for results")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "xml", "sarif", "table"]),
    default="table",
    help="Output format",
)
@click.option(
    "--fail-on",
    type=click.Choice(["critical", "high", "medium", "low"]),
    help="Fail if vulnerabilities of this severity or higher are found",
)
@click.pass_context
def scan(ctx, types, target, output, format, fail_on):
    """
    Run security scans on the codebase.

    Performs various types of security analysis including SAST, SCA, secret scanning,
    Infrastructure as Code analysis, and container scanning.
    """
    asyncio.run(_run_scan(ctx, types, target, output, format, fail_on))


async def _run_scan(ctx, types, target, output, format, fail_on):
    """Async scan implementation"""
    config = _load_config(ctx.obj.get("config_path"))

    console.print(Panel.fit("🔍 Running Security Scans", style="bold blue"))

    # Expand 'all' to all scan types
    if "all" in types:
        types = ["sast", "sca", "secrets", "iac", "container"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        secureflow = SecureFlow(config)
        all_results = {}

        for scan_type in types:
            task = progress.add_task(f"Running {scan_type.upper()} scan...", total=None)

            try:
                if scan_type == "sast":
                    result = await secureflow.scanner.scan_source_code(target)
                elif scan_type == "sca":
                    result = await secureflow.scanner.scan_dependencies(target)
                elif scan_type == "secrets":
                    result = await secureflow.scanner.scan_secrets(target)
                elif scan_type == "iac":
                    result = await secureflow.scanner.scan_infrastructure(target)
                elif scan_type == "container":
                    # Look for Dockerfile or container images
                    dockerfile = Path(target) / "Dockerfile"
                    if dockerfile.exists():
                        result = await secureflow.scanner.scan_container(
                            str(dockerfile)
                        )
                    else:
                        console.print(
                            f"⚠️  No Dockerfile found for container scan in {target}"
                        )
                        continue

                all_results[scan_type] = result.to_dict()
                progress.update(task, completed=True)

            except Exception as e:
                console.print(
                    f"❌ {scan_type.upper()} scan failed: {str(e)}", style="red"
                )
                progress.update(task, completed=True)

    # Display results
    if format == "table":
        _display_scan_results(all_results)
    else:
        _output_scan_results(all_results, output, format)

    # Check fail conditions
    if fail_on:
        exit_code = _check_fail_condition(all_results, fail_on)
        if exit_code != 0:
            console.print(
                f"💥 Build failed due to {fail_on}+ severity vulnerabilities",
                style="red",
            )
            sys.exit(exit_code)


@cli.command()
@click.option(
    "--framework",
    "-f",
    multiple=True,
    type=click.Choice(["SOC2", "PCI_DSS", "HIPAA", "NIST", "ISO27001"]),
    help="Compliance frameworks to check",
)
@click.option("--output", "-o", help="Output file for compliance report")
@click.option(
    "--format",
    type=click.Choice(["json", "pdf", "html"]),
    default="json",
    help="Report format",
)
@click.pass_context
def compliance(ctx, framework, output, format):
    """
    Generate compliance reports.

    Check compliance against various security frameworks and generate reports.
    """
    asyncio.run(_run_compliance(ctx, framework, output, format))


async def _run_compliance(ctx, frameworks, output, format):
    """Async compliance check implementation"""
    config = _load_config(ctx.obj.get("config_path"))

    console.print(Panel.fit("📋 Compliance Check", style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task("Running compliance checks...", total=None)

        secureflow = SecureFlow(config)

        try:
            results = await secureflow.check_compliance(
                list(frameworks) if frameworks else None
            )
            progress.update(task, completed=True)

            _display_compliance_results(results)

            if output:
                _save_compliance_report(results, output, format)
                console.print(f"📊 Compliance report saved to: {output}")

        except Exception as e:
            console.print(f"❌ Compliance check failed: {str(e)}", style="red")
            progress.update(task, completed=True)


@cli.command()
@click.option(
    "--scan-results", "-s", required=True, help="Path to scan results JSON file"
)
@click.option("--output", "-o", help="Output file for report")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "html", "pdf", "sarif"]),
    default="html",
    help="Report format",
)
@click.option("--template", help="Custom report template")
@click.pass_context
def report(ctx, scan_results, output, format, template):
    """
    Generate security reports from scan results.

    Create comprehensive security reports in various formats.
    """
    asyncio.run(_run_report(ctx, scan_results, output, format, template))


async def _run_report(ctx, scan_results_path, output, format, template):
    """Async report generation implementation"""
    config = _load_config(ctx.obj.get("config_path"))

    console.print(Panel.fit("📊 Generating Security Report", style="bold blue"))

    try:
        # Load scan results
        with open(scan_results_path, "r") as f:
            scan_results = json.load(f)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            task = progress.add_task("Generating report...", total=None)

            secureflow = SecureFlow(config)
            report_path = await secureflow.generate_security_report(
                scan_results, output
            )

            progress.update(task, completed=True)

            console.print(f"✅ Security report generated: {report_path}", style="green")

    except FileNotFoundError:
        console.print(
            f"❌ Scan results file not found: {scan_results_path}", style="red"
        )
    except Exception as e:
        console.print(f"❌ Report generation failed: {str(e)}", style="red")


@cli.group()
def azure():
    """
    Azure DevOps integration commands.

    Set up and manage Azure DevOps security pipelines.
    """
    pass


@azure.command()
@click.option("--project", "-p", required=True, help="Azure DevOps project name")
@click.option("--repo", "-r", required=True, help="Repository name")
@click.option(
    "--template",
    "-t",
    type=click.Choice(["basic", "comprehensive", "compliance"]),
    default="comprehensive",
    help="Pipeline template type",
)
@click.pass_context
def setup_pipeline(ctx, project, repo, template):
    """
    Set up security pipeline in Azure DevOps.

    Creates a complete security pipeline with scanning, compliance, and reporting.
    """
    asyncio.run(_setup_azure_pipeline(ctx, project, repo, template))


async def _setup_azure_pipeline(ctx, project, repo, template):
    """Async Azure pipeline setup"""
    config = _load_config(ctx.obj.get("config_path"))

    if not config.azure:
        console.print(
            "❌ Azure configuration not found. Run 'secureflow init --azure' first.",
            style="red",
        )
        return

    console.print(Panel.fit("⚙️ Setting up Azure DevOps Pipeline", style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task("Setting up pipeline...", total=None)

        try:
            secureflow = SecureFlow(config)
            result = await secureflow.setup_azure_pipeline(project, repo, template)

            progress.update(task, completed=True)

            if result.get("status") == "success":
                console.print(
                    "✅ Azure DevOps pipeline setup completed!", style="green"
                )
                console.print(
                    f"🔗 Pipeline URL: {result.get('pipeline', {}).get('url', 'N/A')}"
                )
            else:
                console.print(
                    f"❌ Pipeline setup failed: {result.get('error', 'Unknown error')}",
                    style="red",
                )

        except Exception as e:
            console.print(f"❌ Pipeline setup failed: {str(e)}", style="red")
            progress.update(task, completed=True)


def _load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or environment"""
    try:
        return Config.load(config_path)
    except Exception as e:
        console.print(f"❌ Failed to load configuration: {str(e)}", style="red")
        console.print("💡 Run 'secureflow init' to create a configuration file")
        sys.exit(1)


def _display_scan_results(results: dict):
    """Display scan results in table format"""
    console.print("\n" + "=" * 80)
    console.print("🔍 Security Scan Results", style="bold blue", justify="center")
    console.print("=" * 80)

    for scan_type, result in results.items():
        vulnerabilities = result.get("vulnerabilities", [])
        summary = result.get("summary", {})

        console.print(f"\n📊 {scan_type.upper()} Scan Results", style="bold")

        if not vulnerabilities:
            console.print("✅ No vulnerabilities found", style="green")
            continue

        # Create severity summary table
        table = Table(title=f"{scan_type.upper()} Summary")
        table.add_column("Severity", style="bold")
        table.add_column("Count", justify="right")

        severity_counts = summary.get("by_severity", {})
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                color = {
                    "CRITICAL": "red",
                    "HIGH": "red",
                    "MEDIUM": "yellow",
                    "LOW": "blue",
                    "INFO": "white",
                }.get(severity, "white")
                table.add_row(severity, str(count), style=color)

        console.print(table)

        # Show high/critical vulnerabilities
        high_vulns = [
            v for v in vulnerabilities if v.get("severity") in ["HIGH", "CRITICAL"]
        ]
        if high_vulns:
            console.print(f"\n⚠️  High/Critical Vulnerabilities:", style="bold red")
            for vuln in high_vulns[:5]:  # Show first 5
                console.print(
                    f"  • {vuln.get('title', 'Unknown')} ({vuln.get('severity')})"
                )
                if vuln.get("file_path"):
                    console.print(
                        f"    📁 {vuln['file_path']}:{vuln.get('line_number', '')}"
                    )


def _output_scan_results(results: dict, output: Optional[str], format: str):
    """Output scan results to file"""
    if not output:
        if format == "json":
            console.print_json(data=results)
        else:
            console.print("📄 Specify --output to save results to file")
        return

    output_path = Path(output)

    if format == "json":
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
    elif format == "xml":
        # Convert to XML format (simplified)
        xml_content = _convert_to_xml(results)
        with open(output_path, "w") as f:
            f.write(xml_content)
    elif format == "sarif":
        # Convert to SARIF format
        sarif_content = _convert_to_sarif(results)
        with open(output_path, "w") as f:
            json.dump(sarif_content, f, indent=2)

    console.print(f"📁 Results saved to: {output_path}")


def _check_fail_condition(results: dict, fail_on: str) -> int:
    """Check if scan results meet fail condition"""
    severity_order = ["critical", "high", "medium", "low"]
    fail_index = severity_order.index(fail_on.lower())

    for scan_type, result in results.items():
        summary = result.get("summary", {})
        severity_counts = summary.get("by_severity", {})

        for i in range(fail_index + 1):
            severity = severity_order[i].upper()
            if severity_counts.get(severity, 0) > 0:
                return 1

    return 0


def _display_compliance_results(results: dict):
    """Display compliance check results"""
    console.print("\n📋 Compliance Check Results", style="bold blue")

    for framework, result in results.items():
        status = "✅ PASS" if result.get("compliant") else "❌ FAIL"
        console.print(f"{framework}: {status}")


def _save_compliance_report(results: dict, output: str, format: str):
    """Save compliance report to file"""
    output_path = Path(output)

    if format == "json":
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
    # Additional formats would be implemented here


def _create_azure_templates(project_type: Optional[str]):
    """Create Azure DevOps pipeline templates"""
    templates_dir = Path(".azure-pipelines")
    templates_dir.mkdir(exist_ok=True)

    # Create main pipeline
    pipeline_content = """
# Azure DevOps Security Pipeline
# Generated by SecureFlow

trigger:
  branches:
    include:
    - main
    - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  - template: variables/security-vars.yml

stages:
  - template: templates/security-scan-stage.yml
  - template: templates/build-stage.yml
  - template: templates/deploy-stage.yml
"""

    (templates_dir / "azure-pipelines.yml").write_text(pipeline_content.strip())

    # Create templates directory
    (templates_dir / "templates").mkdir(exist_ok=True)
    (templates_dir / "variables").mkdir(exist_ok=True)

    console.print("📋 Created Azure DevOps pipeline templates")


def _update_gitignore():
    """Update .gitignore with SecureFlow entries"""
    gitignore_path = Path(".gitignore")
    secureflow_entries = [
        "",
        "# SecureFlow",
        ".secureflow-cache/",
        "security-reports/",
        "*.security.json",
    ]

    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if "# SecureFlow" not in content:
            with open(gitignore_path, "a") as f:
                f.write("\n".join(secureflow_entries))
    else:
        gitignore_path.write_text("\n".join(secureflow_entries))


def _convert_to_xml(results: dict) -> str:
    """Convert results to XML format - simplified implementation"""
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<security_results>\n'

    for scan_type, result in results.items():
        xml += f'  <scan type="{scan_type}">\n'
        for vuln in result.get("vulnerabilities", []):
            xml += f'    <vulnerability severity="{vuln.get("severity", "")}">\n'
            xml += f'      <title>{vuln.get("title", "")}</title>\n'
            xml += f'      <description>{vuln.get("description", "")}</description>\n'
            xml += f"    </vulnerability>\n"
        xml += "  </scan>\n"

    xml += "</security_results>"
    return xml


def _convert_to_sarif(results: dict) -> dict:
    """Convert results to SARIF format - simplified implementation"""
    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [],
    }

    for scan_type, result in results.items():
        run = {
            "tool": {
                "driver": {"name": result.get("tool", scan_type), "version": "1.0.0"}
            },
            "results": [],
        }

        for vuln in result.get("vulnerabilities", []):
            sarif_result = {
                "ruleId": vuln.get("rule_id", vuln.get("id")),
                "message": {"text": vuln.get("title", "")},
                "level": vuln.get("severity", "").lower(),
            }

            if vuln.get("file_path"):
                sarif_result["locations"] = [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": vuln["file_path"]},
                            "region": {"startLine": vuln.get("line_number", 1)},
                        }
                    }
                ]

            run["results"].append(sarif_result)

        sarif["runs"].append(run)

    return sarif


def main():
    """Main CLI entry point"""
    cli()


if __name__ == "__main__":
    main()
