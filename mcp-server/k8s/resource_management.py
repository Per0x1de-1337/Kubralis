from mcp.server.fastmcp import FastMCP

from kubernetes import client, config
from typing import Optional, List, Dict, Any
import yaml
mcp = FastMCP("Kubestellar  MCP")


def load_kube_config(context: Optional[str] = None):
    """Load kubeconfig for a given context."""
    config.load_kube_config(context=context)

@mcp.tool()
async def list_pods(namespace: str = "default", label_selector: Optional[str] = None,
              field_selector: Optional[str] = None, context: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List pods in a namespace.
    Returns a list of pod dictionaries.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector, field_selector=field_selector)
    return [pod.to_dict() for pod in pods.items]

@mcp.tool()
async def get_nodes(context: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get nodes in the cluster.
    Returns a list of node dictionaries.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    nodes = v1.list_node()
    return [node.to_dict() for node in nodes.items]

@mcp.tool()
async def create_pod(
    namespace: str,
    pod_name: str,
    image: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a pod in a specified namespace.
    Returns the created pod's dictionary.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    pod_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {"name": pod_name},
        "spec": {
            "containers": [{"name": pod_name, "image": image}]
        }
    }
    pod = v1.create_namespaced_pod(namespace=namespace, body=pod_manifest)
    return pod.to_dict()

@mcp.tool()
async def delete_pod(
    namespace: str,
    pod_name: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a pod in a specified namespace.
    Returns the status of the deletion.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    response = v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
    return response.to_dict()
@mcp.tool()
async def get_pod_logs(
    namespace: str,
    pod_name: str,
    context: Optional[str] = None
) -> str:
    """
    Get logs from a specified pod in a namespace.
    Returns the logs as a string.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    logs = v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)
    return logs
@mcp.tool()
async def get_pod_status(
    namespace: str,
    pod_name: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the status of a specified pod in a namespace.
    Returns the pod's status as a dictionary.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    return pod.status.to_dict() 
@mcp.tool()
async def describe_pod(
    namespace: str,
    pod_name: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Describe a specified pod in a namespace.
    Returns the pod's description as a dictionary.
    """
    load_kube_config(context)
    v1 = client.CoreV1Api()
    
    pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    return pod.to_dict()