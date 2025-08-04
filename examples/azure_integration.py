"""
Azure DevOps integration example
"""

import asyncio
import os
from secureflow_core import SecureFlow, Config, AzureConfig


async def azure_integration_example():
    """Example of Azure DevOps integration"""
    print("🔧 SecureFlow Azure DevOps Integration Example")
    
    # Configure Azure DevOps integration
    azure_config = AzureConfig(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        devops_organization=os.getenv("AZURE_DEVOPS_ORG"),
        pat_token=os.getenv("AZURE_DEVOPS_PAT")
    )
    
    config = Config()
    config.azure = azure_config
    
    # Initialize SecureFlow with Azure configuration
    secureflow = SecureFlow(config)
    
    # Set up security pipeline in Azure DevOps
    print("\n⚙️ Setting up Azure DevOps security pipeline...")
    try:
        pipeline_result = await secureflow.setup_azure_pipeline(
            project_name="MyProject",
            repo_name="MyRepository", 
            template_type="comprehensive"
        )
        
        if pipeline_result.get("status") == "success":
            print("✅ Pipeline setup successful!")
            print(f"Pipeline ID: {pipeline_result.get('pipeline', {}).get('id')}")
            print(f"Pipeline URL: {pipeline_result.get('pipeline', {}).get('url')}")
        else:
            print(f"❌ Pipeline setup failed: {pipeline_result.get('error')}")
    
    except Exception as e:
        print(f"❌ Azure integration error: {str(e)}")
        print("💡 Make sure Azure DevOps credentials are configured")
    
    # Run security scans and create work items for vulnerabilities
    print("\n🔍 Running security scans...")
    scan_results = await secureflow.scan_repository(".")
    
    # Create work items for high/critical vulnerabilities
    if any(scan_results.values()):
        print("\n📝 Creating work items for vulnerabilities...")
        try:
            work_items = await secureflow.azure.create_security_work_items(
                scan_results, "MyProject"
            )
            print(f"Created {len(work_items)} work items for security issues")
        except Exception as e:
            print(f"⚠️ Could not create work items: {str(e)}")
    
    # Cleanup
    await secureflow.cleanup()
    print("\n✅ Azure integration example completed!")


if __name__ == "__main__":
    asyncio.run(azure_integration_example())
