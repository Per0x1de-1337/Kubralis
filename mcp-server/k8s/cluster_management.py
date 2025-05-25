from mcp.server.fastmcp import FastMCP

from kubernetes import client, config
from typing import Optional, List, Dict, Any
import yaml
mcp = FastMCP("Kubestellar  MCP")

def load_kube_config(context: Optional[str] = None):
    """Load kubeconfig for a given context."""
    config.load_kube_config(context=context)


@mcp.tool()
async def list_all_clusters(
    context: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List all clusters in the Kubernetes environment.
    Returns a list of cluster dictionaries.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    try:
        clusters = v1.list_node()
        return [cluster.to_dict() for cluster in clusters.items]
    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }

@mcp.tool()
async def get_cluster_details(
    cluster_name: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get details of a specific cluster in the Kubernetes environment.
    Returns the cluster's dictionary.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    try:
        cluster = v1.read_node(name=cluster_name)
        return cluster.to_dict()
    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }

@mcp.tool()
async def get_cluster_status(
    cluster_name: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the status of a specific cluster in the Kubernetes environment.
    Returns the cluster's status as a dictionary.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    try:
        cluster = v1.read_node(name=cluster_name)
        return cluster.status.to_dict()
    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }
@mcp.tool() 
async def get_cluster_logs(
    cluster_name: str,
    context: Optional[str] = None
) -> str:
    """
    Get logs from a specific cluster in the Kubernetes environment.
    Returns the logs as a string.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    try:
        logs = v1.read_node_log(name=cluster_name)
        return logs
    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }