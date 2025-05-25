from mcp.server.fastmcp import FastMCP

from kubernetes import client, config
from typing import Optional, List, Dict, Any
import yaml
mcp = FastMCP("Kubestellar  MCP")


def load_kube_config(context: Optional[str] = None):
    """Load kubeconfig for a given context."""
    config.load_kube_config(context=context)
    
@mcp.tool()
async def create_namespace(
    namespace: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a namespace in the Kubernetes cluster.
    Returns the created namespace's dictionary.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    namespace_manifest = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {"name": namespace}
    }
    
    try:
        ns = v1.create_namespace(body=namespace_manifest)
        return ns.to_dict()
    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }   
    
@mcp.tool()
async def delete_namespace(
    namespace: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a namespace in the Kubernetes cluster.
    Returns the status of the deletion.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    try:
        response = v1.delete_namespace(name=namespace)
        return response.to_dict()
    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }

@mcp.tool()
async def list_namespaces(
    context: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List all namespaces in the Kubernetes cluster.
    Returns a list of namespace dictionaries.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    try:
        namespaces = v1.list_namespace()
        return [ns.to_dict() for ns in namespaces.items]
    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }

@mcp.tool()
async def create_labelled_namespace(
    namespace: str,
    labels: Dict[str, str],
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a labeled namespace in the Kubernetes cluster.
    Returns the created namespace's dictionary with labels.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    namespace_manifest = {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {
            "name": namespace,
            "labels": labels
        }
    }
    
    try:
        ns = v1.create_namespace(body=namespace_manifest)
        return ns.to_dict()
    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }

@mcp.tool()
async def get_namespace_details(
    namespace: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get details of a specific namespace in the Kubernetes cluster.
    Returns the namespace's dictionary.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    try:
        ns = v1.read_namespace(name=namespace)
        return ns.to_dict()
    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }
@mcp.tool()
async def get_namespace_status(
    namespace: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the status of a specific namespace in the Kubernetes cluster.
    Returns the namespace's status as a dictionary.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    try:
        ns = v1.read_namespace(name=namespace)
        return ns.status.to_dict()
    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }