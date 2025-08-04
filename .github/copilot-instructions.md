# Copilot Instructions for SecureFlow-Core

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview

SecureFlow-Core is a comprehensive shared DevSecOps library designed for Azure DevOps and modern security automation. This Python library provides:

- **Security Scanning**: SAST, DAST, SCA, secret scanning, and container security
- **Azure DevOps Integration**: Pipeline templates, work item creation, and dashboard integration
- **Compliance Automation**: SOC 2, PCI DSS, HIPAA compliance checking
- **Plugin Architecture**: Extensible system for custom security tools
- **CLI Interface**: Command-line tools for security operations

## Code Style and Conventions

- **Python Version**: Target Python 3.8+ with type hints
- **Async/Await**: Use async programming for I/O operations
- **Error Handling**: Implement comprehensive error handling with logging
- **Documentation**: Include docstrings for all public methods
- **Testing**: Write unit tests for new functionality

## Architecture Guidelines

### Core Components

1. **Scanner Module** (`scanner.py`): Core security scanning functionality
2. **Azure Integration** (`azure.py`): Azure DevOps pipeline and work item management
3. **Compliance Module** (`compliance.py`): Framework compliance checking
4. **Plugin System** (`plugins.py`): Extensible plugin architecture
5. **CLI Interface** (`cli.py`): Command-line interface
6. **Configuration** (`config.py`): Pydantic-based configuration management

### Security Tool Integration

When adding new security tools:
- Implement as async methods in the Scanner class
- Follow the pattern: `_run_<tool_name>(target, scan_type)`
- Return ScanResult objects with standardized vulnerability format
- Handle tool errors gracefully with logging

### Azure DevOps Integration

When working with Azure DevOps:
- Use the azure-devops Python library for API interactions
- Implement async methods for pipeline and work item operations
- Handle authentication with Azure AD or PAT tokens
- Create reusable YAML pipeline templates

## Development Patterns

### Adding New Scan Types

```python
async def _run_new_tool(self, target: str, scan_type: str) -> ScanResult:
    """Run new security tool"""
    start_time = time.time()
    
    try:
        # Tool execution logic
        cmd = ["new-tool", "--json", target]
        result = await self._run_command(cmd)
        vulnerabilities = self._parse_new_tool_output(result.get("stdout", ""))
        
        return ScanResult(
            tool="new-tool",
            target=target,
            scan_type=scan_type,
            vulnerabilities=vulnerabilities,
            scan_duration=time.time() - start_time,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
    except Exception as e:
        self.logger.error(f"New tool scan failed: {str(e)}")
        return self._create_error_result("new-tool", target, scan_type, str(e), start_time)
```

### Plugin Development

```python
class NewScannerPlugin(ScannerPlugin):
    name = "new-scanner"
    version = "1.0.0"
    description = "New security scanner plugin"
    scan_type = "custom"
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        # Plugin initialization logic
        return True
    
    async def scan(self, target: str) -> ScanResult:
        # Scanner implementation
        pass
```

## Best Practices

1. **Configuration**: Use environment variables for sensitive data
2. **Logging**: Use the Logger utility class for consistent logging
3. **Error Handling**: Never let exceptions bubble up without logging
4. **Performance**: Implement caching for expensive operations
5. **Security**: Never hardcode credentials or secrets
6. **Testing**: Mock external dependencies in tests

## Common Patterns

### Async Command Execution
```python
result = await self._run_command(["tool", "args"])
if result["returncode"] == 0:
    # Process stdout
    pass
else:
    # Handle error
    pass
```

### Configuration Access
```python
tool = self.config.scanning.sast_tool
threshold = self.config.scanning.severity_threshold
```

### Azure DevOps Operations
```python
pipeline = await self.azure.create_security_pipeline(
    project_name="MyProject",
    repo_name="MyRepo",
    template_type="comprehensive"
)
```

## File Organization

- `src/secureflow_core/`: Main library code
- `examples/`: Usage examples and integrations
- `tests/`: Unit and integration tests
- `docs/`: Documentation and guides

## Dependencies

- **Core**: pydantic, click, rich, asyncio
- **Azure**: azure-devops, azure-identity, azure-keyvault-secrets
- **Security Tools**: Various CLI tools (semgrep, safety, trufflehog, etc.)
- **Optional**: jinja2 (reports), httpx (integrations), yaml (configs)
