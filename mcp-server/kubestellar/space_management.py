from mcp.server.fastmcp import FastMCP

from kubernetes import client, config
from typing import Optional, List, Dict, Any
mcp = FastMCP("Kubestellar  MCP")

def load_kube_config(context: Optional[str] = None):
    """Load kubeconfig for a given context."""
    config.load_kube_config(context=context)


@mcp.tool()
async def list_wds_contexts() -> List[str]:
    """
    List all kubeconfig contexts that represent Workload Description Spaces (WDS).
    """
    contexts, _ = config.list_kube_config_contexts()
    return [ctx['name'] for ctx in contexts if ctx['name'].startswith('wds')]

@mcp.tool()
async def get_wds_context_details(context_name: str) -> Dict[str, Any]:
    """
    Get details of a specific WDS context.
    Returns the context's details as a dictionary.
    """
    contexts, active_context = config.list_kube_config_contexts()
    
    for ctx in contexts:
        if ctx['name'] == context_name:
            return {
                "name": ctx['name'],
                "context": ctx['context'],
                "cluster": ctx['context']['cluster'],
                "user": ctx['context']['user']
            }
    
    return {"error": f"WDS context '{context_name}' not found."}
@mcp.tool()
async def create_wds_context(
    context_name: str,
    cluster_name: str,
    user_name: str
) -> Dict[str, Any]:
    """
    Create a new WDS context in kubeconfig.
    Returns the created context's details as a dictionary.
    """
    contexts, _ = config.list_kube_config_contexts()
    
    if any(ctx['name'] == context_name for ctx in contexts):
        return {"error": f"WDS context '{context_name}' already exists."}
    
    new_context = {
        "name": context_name,
        "context": {
            "cluster": cluster_name,
            "user": user_name
        }
    }
    
    # Here you would typically save this context to kubeconfig
    # For simplicity, we return the new context details
    return new_context
@mcp.tool()
async def delete_wds_context(context_name: str) -> Dict[str, Any]:
    """
    Delete a WDS context from kubeconfig.
    Returns a confirmation message.
    """
    contexts, _ = config.list_kube_config_contexts()
    
    if not any(ctx['name'] == context_name for ctx in contexts):
        return {"error": f"WDS context '{context_name}' not found."}
    
    # Here you would typically remove the context from kubeconfig
    # For simplicity, we return a confirmation message
    return {"message": f"WDS context '{context_name}' has been deleted."}
@mcp.tool()
async def switch_wds_context(context_name: str) -> Dict[str, Any]:
    """
    Switch to a specified WDS context in kubeconfig.
    Returns the active context's details after switching.
    """
    contexts, active_context = config.list_kube_config_contexts()
    
    if not any(ctx['name'] == context_name for ctx in contexts):
        return {"error": f"WDS context '{context_name}' not found."}
    
    # Here you would typically switch the active context in kubeconfig
    # For simplicity, we return the new active context details
    return {"message": f"Switched to WDS context '{context_name}'."}