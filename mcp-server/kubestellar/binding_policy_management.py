from mcp.server.fastmcp import FastMCP

from kubernetes import client, config
from typing import Optional, List, Dict, Any
import yaml
mcp = FastMCP("Kubestellar  MCP")




def load_kube_config(context=None):
    try:
        print(f"Loading kube config for context: {context}")
        config.load_kube_config(context=context)
        c = client.Configuration.get_default_copy()
        c.verify_ssl = False
        c.ssl_ca_cert = None  # Explicitly disable SSL verification
        client.Configuration.set_default(c)
        
        # Print current context
        current_context = config.list_kube_config_contexts()[1]
        print(f"Current context: {current_context['name']}")
        
        return current_context
    except Exception as e:
        print(f"Error loading kube config: {str(e)}")
        raise

def is_kubernetes_builtin_resource(resource: str) -> bool:
    # Implement this based on your resource knowledge or a lookup table.
    builtins = {"pods", "deployments", "services", "namespaces", "configmaps", "secrets"}
    return resource in builtins

def get_api_group_for_crd(resource: str, crd_api_groups: Dict[str, str]) -> str:
    return crd_api_groups.get(resource, "")

def format_labels(labels: Dict[str, str]) -> List[str]:
    return [f"{k}: {v}" for k, v in labels.items()]

def create_binding_policy_helper(
    policy_name: str,
    namespace: str,
    cluster_labels: Dict[str, str],
    workload_labels: Dict[str, str],
    resource_configs: List[Dict[str, Any]],
    crd_api_groups: Dict[str, str],
    namespaces_to_sync: Optional[List[str]] = None,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a KubeStellar BindingPolicy CRD in the target cluster.
    """
    try:
        load_kube_config(context)
        api = client.CustomObjectsApi()

        # First check if the API group exists
        try:
            api.list_cluster_custom_object(
                group="control.kubestellar.io",
                version="v1alpha1",
                plural="bindingpolicies"
            )
        except client.exceptions.ApiException as e:
            if e.status == 404:
                try:
                    # Try with v1alpha2 version as well
                    api.list_cluster_custom_object(
                        group="control.kubestellar.io",
                        version="v1alpha2",
                        plural="bindingpolicies"
                    )
                    print("Using v1alpha2 API version")
                except client.exceptions.ApiException as e2:
                    if e2.status == 404:
                        return {
                            "error": "BindingPolicy API not accessible",
                            "message": "The BindingPolicy API endpoint is not accessible. Please verify the API version and permissions."
                        }
                    raise e2
            raise e

        # Build downsync rules
        downsync_rules = []

        # Handle CRDs first
        for resource_cfg in resource_configs:
            resource = resource_cfg["Type"]
            if not is_kubernetes_builtin_resource(resource):
                crd_rule = {
                    "resources": [resource],
                    "objectSelectors": [{"matchLabels": workload_labels}],
                    "apiGroup": get_api_group_for_crd(resource, crd_api_groups)
                }
                if resource_cfg.get("CreateOnly"):
                    crd_rule["createOnly"] = True
                if namespaces_to_sync:
                    crd_rule["namespaces"] = namespaces_to_sync
                downsync_rules.insert(0, crd_rule)  # Insert at beginning

        # Handle built-in resources
        for resource_cfg in resource_configs:
            resource = resource_cfg["Type"]
            if resource == "namespaces":
                continue
            if is_kubernetes_builtin_resource(resource):
                rule = {
                    "resources": [resource],
                    "objectSelectors": [{"matchLabels": workload_labels}]
                }
                if resource_cfg.get("CreateOnly"):
                    rule["createOnly"] = True
                if namespaces_to_sync:
                    rule["namespaces"] = namespaces_to_sync
                downsync_rules.append(rule)

        # Always add namespaces first if present
        if any(cfg["Type"] == "namespaces" for cfg in resource_configs):
            ns_rule = {
                "resources": ["namespaces"],
                "objectSelectors": [{"matchLabels": workload_labels}]
            }
            if namespaces_to_sync:
                ns_rule["namespaces"] = namespaces_to_sync
            downsync_rules.insert(0, ns_rule)

        # Build the BindingPolicy object
        policy_obj = {
            "apiVersion": "control.kubestellar.io/v1alpha1",
            "kind": "BindingPolicy",
            "metadata": {
                "name": policy_name
                # Note: no namespace field since this is cluster-scoped
            },
            "spec": {
                "downsync": downsync_rules,
                "clusterSelectors": [{"matchLabels": cluster_labels}],
                "bindingMode": "Downsync"
            }
        }

        print(f"Creating cluster-scoped policy: {yaml.dump(policy_obj)}")

        try:
            # Create the policy as a cluster-scoped resource
            result = api.create_cluster_custom_object(
                group="control.kubestellar.io",
                version="v1alpha1",
                plural="bindingpolicies",
                body=policy_obj
            )
        except client.exceptions.ApiException as e:
            return {
                "error": f"Kubernetes API error: {e.status}",
                "message": str(e),
                "details": e.body if hasattr(e, 'body') else "No details available"
            }

        # Prepare response
        response = {
            "message": f"Created cluster-scoped binding policy '{policy_name}' successfully",
            "bindingPolicy": {
                "name": policy_name,
                "status": "inactive",
                "bindingMode": "Downsync",
                "clusters": format_labels(cluster_labels),
                "workloads": [cfg["Type"] for cfg in resource_configs],
                "clustersCount": len(cluster_labels),
                "workloadsCount": len(resource_configs),
                "yaml": yaml.dump(policy_obj)
            }
        }
        return response

    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to create the BindingPolicy. Please check the input parameters and cluster configuration."
        }

@mcp.tool()
async def create_binding_policy(
    policy_name: str,
    namespace: str,
    cluster_labels: Dict[str, str],
    workload_labels: Dict[str, str],
    resource_configs: List[Dict[str, Any]],
    crd_api_groups: Dict[str, str],
    namespaces_to_sync: Optional[List[str]] = None,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a BindingPolicy CRD in the target cluster.
    
    Args:
        policy_name: Name of the binding policy
        namespace: Namespace to create the policy in (ignored for cluster-scoped policies)
        cluster_labels: Labels to select target clusters
        workload_labels: Labels to select target workloads
        resource_configs: List of resource configurations
        crd_api_groups: API groups for CRDs
        namespaces_to_sync: Optional list of namespaces to sync
        context: Kubernetes context to use
    
    Returns:
        Dict with result or error information
    """
    try:
        # Validate inputs
        if not policy_name:
            return {
                "error": "Invalid input",
                "message": "Policy name cannot be empty"
            }
        
        if not isinstance(cluster_labels, dict):
            return {
                "error": "Invalid input",
                "message": "cluster_labels must be a dictionary"
            }
        
        if not isinstance(workload_labels, dict):
            return {
                "error": "Invalid input",
                "message": "workload_labels must be a dictionary"
            }
        
        if not isinstance(resource_configs, list):
            return {
                "error": "Invalid input",
                "message": "resource_configs must be a list"
            }

        # Load kube config and verify context
        current_context = load_kube_config(context)
        print(f"Using context: {current_context['name']}")
        
        # Check if policy already exists
        api = client.CustomObjectsApi()
        try:
            api.get_cluster_custom_object(
                group="control.kubestellar.io",
                version="v1alpha1",
                plural="bindingpolicies",
                name=policy_name
            )
            return {
                "error": "Policy already exists",
                "message": f"Binding policy '{policy_name}' already exists"
            }
        except client.exceptions.ApiException as e:
            if e.status != 404:
                raise

        # Build downsync rules
        downsync_rules = []
        for resource_cfg in resource_configs:
            if not isinstance(resource_cfg, dict) or "Type" not in resource_cfg:
                return {
                    "error": "Invalid resource config",
                    "message": f"Invalid resource configuration: {resource_cfg}"
                }
            
            resource = resource_cfg["Type"]
            rule = {
                "resources": [resource],
                "objectSelectors": [{"matchLabels": workload_labels}],
                "apiGroup": get_api_group_for_crd(resource, crd_api_groups)
            }
            if resource_cfg.get("CreateOnly"):
                rule["createOnly"] = True
            if namespaces_to_sync:
                rule["namespaces"] = namespaces_to_sync
            downsync_rules.append(rule)

        # Build the BindingPolicy object
        policy_obj = {
            "apiVersion": "control.kubestellar.io/v1alpha1",
            "kind": "BindingPolicy",
            "metadata": {
                "name": policy_name
            },
            "spec": {
                "downsync": downsync_rules,
                "clusterSelectors": [{"matchLabels": cluster_labels}],
                "bindingMode": "Downsync"
            }
        }

        print(f"Creating binding policy: {yaml.dump(policy_obj)}")

        try:
            # Create the policy
            result = api.create_cluster_custom_object(
                group="control.kubestellar.io",
                version="v1alpha1",
                plural="bindingpolicies",
                body=policy_obj
            )
            
            # Prepare response
            response = {
                "message": f"Created binding policy '{policy_name}' successfully",
                "bindingPolicy": {
                    "name": policy_name,
                    "status": "inactive",
                    "bindingMode": "Downsync",
                    "clusters": format_labels(cluster_labels),
                    "workloads": [cfg["Type"] for cfg in resource_configs],
                    "clustersCount": len(cluster_labels),
                    "workloadsCount": len(resource_configs),
                    "yaml": yaml.dump(policy_obj)
                }
            }
            return response

        except client.exceptions.ApiException as e:
            return {
                "error": f"Kubernetes API error: {e.status}",
                "message": str(e),
                "details": e.body if hasattr(e, 'body') else "No details available"
            }

    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to create the BindingPolicy. Please check the input parameters and cluster configuration."
        }

@mcp.tool()
async def list_binding_policies(
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all BindingPolicy CRDs in the cluster.
    """
    try:
        load_kube_config(context)
        api = client.CustomObjectsApi()

        try:
            # Get all binding policies
            policies = api.list_cluster_custom_object(
                group="control.kubestellar.io",
                version="v1alpha1",
                plural="bindingpolicies"
            )

            # Parse and format the policies
            policies_list = []
            for policy in policies.get('items', []):
                policy_data = {
                    "name": policy.get('metadata', {}).get('name', ''),
                    "age": policy.get('metadata', {}).get('creationTimestamp', ''),
                    "status": policy.get('status', {}).get('conditions', [{}])[0].get('status', ''),
                    "clusterSelectors": policy.get('spec', {}).get('clusterSelectors', []),
                    "downsync": policy.get('spec', {}).get('downsync', []),
                    "bindingMode": policy.get('spec', {}).get('bindingMode', '')
                }
                policies_list.append(policy_data)

            return {
                "message": "Successfully retrieved binding policies",
                "bindingPolicies": policies_list,
                "totalPolicies": len(policies_list)
            }

        except client.exceptions.ApiException as e:
            return {
                "error": f"Kubernetes API error: {e.status}",
                "message": str(e),
                "details": e.body if hasattr(e, 'body') else "No details available"
            }

    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to list binding policies. Please check the cluster configuration."
        }

@mcp.tool()
async def delete_binding_policy(
    policy_name: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Delete a BindingPolicy CRD from the cluster.
    """
    try:
        load_kube_config(context)
        api = client.CustomObjectsApi()

        try:
            result = api.delete_cluster_custom_object(
                group="control.kubestellar.io",
                version="v1alpha1",
                plural="bindingpolicies",
                name=policy_name,
                body=client.V1DeleteOptions()
            )
            return {
                "message": f"Binding policy '{policy_name}' deleted successfully",
                "deletedPolicy": {
                    "name": policy_name,
                    "status": "deleted"
                }
            }
        except client.exceptions.ApiException as e:
            if e.status == 404:
                return {
                    "message": f"Binding policy '{policy_name}' not found"
                }
            raise

    except client.exceptions.ApiException as e:
        return {
            "error": f"Kubernetes API error: {e.status}",
            "message": str(e),
            "details": e.body if hasattr(e, 'body') else "No details available"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to delete the BindingPolicy. Please check the input parameters and cluster configuration."
        }

@mcp.tool()
async def get_binding_policy_details(
    policy_name: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific BindingPolicy CRD.
    """
    try:
        load_kube_config(context)
        api = client.CustomObjectsApi()

        try:
            # Get the specific binding policy
            policy = api.get_cluster_custom_object(
                group="control.kubestellar.io",
                version="v1alpha1",
                plural="bindingpolicies",
                name=policy_name
            )

            # Parse and format the policy details
            policy_data = {
                "metadata": {
                    "name": policy.get('metadata', {}).get('name', ''),
                    "namespace": policy.get('metadata', {}).get('namespace', ''),
                    "creationTimestamp": policy.get('metadata', {}).get('creationTimestamp', ''),
                    "uid": policy.get('metadata', {}).get('uid', '')
                },
                "spec": {
                    "bindingMode": policy.get('spec', {}).get('bindingMode', ''),
                    "clusterSelectors": policy.get('spec', {}).get('clusterSelectors', []),
                    "downsync": policy.get('spec', {}).get('downsync', []),
                    "wantSingletonReportedState": policy.get('spec', {}).get('wantSingletonReportedState', False)
                },
                "status": {
                    "conditions": policy.get('status', {}).get('conditions', []),
                    "errors": policy.get('status', {}).get('errors', []),
                    "observedGeneration": policy.get('status', {}).get('observedGeneration', 0)
                }
            }

            return {
                "message": f"Successfully retrieved details for binding policy '{policy_name}'",
                "bindingPolicy": policy_data
            }

        except client.exceptions.ApiException as e:
            if e.status == 404:
                return {
                    "error": f"Binding policy '{policy_name}' not found",
                    "message": "The specified binding policy does not exist in the cluster"
                }
            return {
                "error": f"Kubernetes API error: {e.status}",
                "message": str(e),
                "details": e.body if hasattr(e, 'body') else "No details available"
            }

    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to get binding policy details. Please check the input parameters and cluster configuration."
        }
    
@mcp.tool()
async def get_binding_policy_status(
    policy_name: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the status of a specific BindingPolicy CRD.
    """
    try:
        load_kube_config(context)
        api = client.CustomObjectsApi()

        try:
            # Get the specific binding policy
            policy = api.get_cluster_custom_object(
                group="control.kubestellar.io",
                version="v1alpha1",
                plural="bindingpolicies",
                name=policy_name
            )

            # Parse and format the policy status
            status_data = {
                "status": policy.get('status', {}),
                "conditions": policy.get('status', {}).get('conditions', []),
                "errors": policy.get('status', {}).get('errors', [])
            }

            return {
                "message": f"Successfully retrieved status for binding policy '{policy_name}'",
                "bindingPolicyStatus": status_data
            }

        except client.exceptions.ApiException as e:
            if e.status == 404:
                return {
                    "error": f"Binding policy '{policy_name}' not found",
                    "message": "The specified binding policy does not exist in the cluster"
                }
            return {
                "error": f"Kubernetes API error: {e.status}",
                "message": str(e),
                "details": e.body if hasattr(e, 'body') else "No details available"
            }

    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to get binding policy status. Please check the input parameters and cluster configuration."
        }