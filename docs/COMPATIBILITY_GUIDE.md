# SecureFlow-Core Platform Compatibility Guide

This guide provides information about backward compatibility and platform requirements for SecureFlow-Core across different CI/CD environments.

## 📋 Compatibility Matrix

### GitHub Actions

| Environment | Compatible Workflow | Action Versions | Requirements |
|-------------|-------------------|-----------------|--------------|
| **GitHub.com (Latest)** | `security-basic.yml` | Latest (v5+) | Node.js 20+ |
| **GitHub Enterprise Server 3.6+** | `security-basic.yml` | Latest (v5+) | Node.js 20+ |
| **GitHub Enterprise Server 3.4-3.5** | `security-compatible.yml` | v3-v4 | Node.js 16+ |
| **Self-Hosted Runners (Modern)** | `security-basic.yml` | Latest (v5+) | Node.js 20+ |
| **Self-Hosted Runners (Legacy)** | `security-compatible.yml` | v3-v4 | Node.js 16+ |

### Azure DevOps

| Environment | Compatible Pipeline | Task Versions | Requirements |
|-------------|-------------------|---------------|--------------|
| **Azure DevOps Services** | `secureflow-basic.yml` | Latest | .NET Core 3.1+ |
| **Azure DevOps Server 2022** | `secureflow-basic.yml` | Latest | .NET Core 3.1+ |
| **Azure DevOps Server 2020** | `secureflow-enhanced.yml` | Compatible | .NET Core 3.1+ |
| **Azure DevOps Server 2019** | `secureflow-enhanced.yml` (compatibility mode) | Legacy | .NET Framework 4.6+ |

## 🔧 Choosing the Right Workflow

### For GitHub Actions

#### Use `security-basic.yml` if:
- ✅ Running on GitHub.com
- ✅ Using GitHub Enterprise Server 3.6+
- ✅ Self-hosted runners with Node.js 20+
- ✅ Want latest features and performance

#### Use `security-compatible.yml` if:
- ⚠️ Running GitHub Enterprise Server 3.4-3.5
- ⚠️ Self-hosted runners with older Node.js (16-19)
- ⚠️ Need maximum compatibility
- ⚠️ Experiencing issues with newer action versions

### For Azure DevOps

#### Use `secureflow-basic.yml` if:
- ✅ Running Azure DevOps Services
- ✅ Using Azure DevOps Server 2020+
- ✅ Want standard functionality

#### Use `secureflow-enhanced.yml` if:
- ⚠️ Running Azure DevOps Server 2019
- ⚠️ Need advanced error handling
- ⚠️ Require fallback mechanisms
- ⚠️ Want compatibility mode option

## 📦 Action/Task Version Details

### GitHub Actions Versions

| Action | Latest | Compatible | Notes |
|--------|--------|------------|-------|
| `actions/checkout` | v4 | v3 | v4 requires Node.js 20+ |
| `actions/setup-python` | v5 | v4 | v5 requires Node.js 20+ |
| `github/codeql-action/upload-sarif` | v3 | v2 | v2 deprecated but still works |
| `actions/upload-artifact` | v4 | v3 | v4 has breaking changes |
| `actions/download-artifact` | v4 | v3 | v4 has breaking changes |
| `actions/github-script` | v7 | v6 | v7 requires Node.js 20+ |

### Azure DevOps Task Versions

| Task | Latest | Compatible | Notes |
|------|--------|------------|-------|
| `UsePythonVersion` | @0 | @0 | Stable across all versions |
| `PublishTestResults` | @2 | @2 | SARIF support requires 2020+ |
| `PublishBuildArtifacts` | @1 | @1 | Universal compatibility |
| `PublishHtmlReport` | @1 | N/A | Not available in Server 2019 |

## 🔍 Feature Compatibility

### GitHub Actions Features

| Feature | Latest Workflow | Compatible Workflow |
|---------|----------------|-------------------|
| **SARIF Upload** | ✅ v3 (recommended) | ✅ v2 (deprecated) |
| **Artifact Upload** | ✅ v4 (breaking changes) | ✅ v3 (stable) |
| **PR Comments** | ✅ Full support | ✅ Full support |
| **Security Tab Integration** | ✅ Full support | ✅ Full support |
| **Matrix Builds** | ✅ Advanced | ✅ Basic |
| **Pages Deployment** | ✅ Full support | ⚠️ Limited |

### Azure DevOps Features

| Feature | Basic Pipeline | Enhanced Pipeline |
|---------|---------------|------------------|
| **SARIF Publishing** | ✅ Full support | ✅ Conditional |
| **Work Item Creation** | ✅ Full support | ✅ Full support |
| **HTML Reports** | ✅ Full support | ✅ Conditional |
| **Artifact Publishing** | ✅ Full support | ✅ Full support |
| **Security Gates** | ✅ Full support | ✅ Enhanced |
| **Error Handling** | ✅ Basic | ✅ Advanced |

## 🚀 Migration Guide

### Upgrading from Compatible to Latest

#### GitHub Actions Migration

1. **Check Runner Version**:
   ```bash
   node --version  # Should be 20+
   ```

2. **Update Workflow File**:
   ```yaml
   # Change from:
   uses: actions/setup-python@v4
   # To:
   uses: actions/setup-python@v5
   ```

3. **Test Workflow**:
   - Run in a test branch first
   - Monitor for any failures
   - Check artifact uploads work correctly

#### Azure DevOps Migration

1. **Check Server Version**:
   - Azure DevOps Services: Always latest
   - Server: Check admin panel for version

2. **Update Pipeline**:
   ```yaml
   # Add compatibility parameter
   parameters:
   - name: compatibility_mode
     type: boolean
     default: false
   ```

3. **Gradual Rollout**:
   - Start with `compatibility_mode: true`
   - Test thoroughly
   - Switch to `compatibility_mode: false`

## 🛠️ Troubleshooting

### Common GitHub Actions Issues

#### Node.js Version Errors
```
Error: This action requires Node.js 20, but your runner has Node.js 16
```
**Solution**: Use compatible workflow or upgrade runner

#### SARIF Upload Failures
```
Error: SARIF upload failed with 403
```
**Solutions**:
- Check `security-events: write` permission
- Verify GHES version supports SARIF (3.4+)
- Use compatible workflow for older versions

#### Artifact Upload Issues
```
Error: Artifact upload failed
```
**Solutions**:
- Use v3 actions for older environments
- Check file paths exist
- Verify artifact size limits

### Common Azure DevOps Issues

#### Task Not Found
```
Error: Task 'PublishHtmlReport' not found
```
**Solution**: Use enhanced pipeline with conditional tasks

#### Python Version Issues
```
Error: Python 3.11 not available
```
**Solutions**:
- Use older Python version (3.8+)
- Check agent pool capabilities
- Use compatible pipeline

#### SARIF Publishing Failures
```
Error: SARIF format not supported
```
**Solution**: Enable compatibility mode or use basic artifacts

## 📞 Getting Help

### Compatibility Issues
1. Check this guide first
2. Try the compatible/enhanced workflows
3. Review error messages for version hints
4. Open an issue with environment details

### Environment Information to Provide
- Platform (GitHub Actions/Azure DevOps)
- Version (GHES version/Azure DevOps Server version)
- Runner type (hosted/self-hosted)
- Node.js version (for GitHub Actions)
- Error messages and logs

---

**Note**: This compatibility guide is updated regularly. Check for the latest version when troubleshooting issues.
