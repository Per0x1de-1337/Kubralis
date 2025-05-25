# main.py
from mcp.server.fastmcp_instance import mcp

# Import all tool modules to trigger tool registration
import k8s.cluster_management
import k8s.namespace_management
import k8s.resource_management
import kubestellar.binding_policy_management
import kubestellar.space_management

if __name__ == "__main__":
    mcp.serve()
