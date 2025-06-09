# Kubralis: Kubernetes Multi-Cluster Management and Policy Automation

**Kubralis** is a Python-based command-line tool and server for managing Kubernetes clusters, namespaces, workloads, and advanced multi-cluster policies (such as those used by KubeStellar). It leverages the FastMCP framework and the official Kubernetes Python client to provide robust and extensible automation.

---

## Features

- **Cluster and Node Management**  
  List clusters, inspect nodes, and retrieve logs from Kubernetes clusters.

- **Namespace Management**  
  Create, delete, and list namespaces with custom labels and annotations.

- **Resource Management**  
  Manage pods—create, delete, list, and retrieve logs and status information.

- **KubeStellar-style Spaces and Policies**  
  Manage Workload Description Spaces (WDS), switch contexts, and apply `BindingPolicy` custom resources.

- **Automation and Integration**  
  Designed to work with modern Python tooling such as `uv` for dependency management and execution.

---

## Requirements

- **Python**: 3.12 or higher  
- **Tooling**: [`uv`](https://github.com/astral-sh/uv) for dependency and environment management  
- **Kubernetes**: Access to one or more Kubernetes clusters via `kubeconfig`

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Per0x1de-1337/Kubralis
   cd Kubralis
   ```
2.Install uv and project dependencies:
   ```bash
uv venv
uv pip install -e .
```
3. Configure for Windsurf/Claude Desktop (example configuration):
```bash
{
  "mcpServers": {
    "Kubralis": {
      "command": "uv",
      "args": ["--directory", "/path/to/Kubralis", "run", "main.py"]
    }
  }
}
```
# Demo video
https://drive.google.com/file/d/1s1TJYIjrLJzjo4t-IHcEKoHjNjQkgN-L/view
# Contributions 
Contributions, issues, and feature requests are welcome. Please open an issue to discuss your ideas or report bugs.
