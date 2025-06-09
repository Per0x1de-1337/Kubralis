# Kubralis: Kubernetes Multi-Cluster Management and Policy Automation

**Kubralis** is a Python-based command-line tool and server for managing Kubernetes clusters, namespaces, workloads, and advanced multi-cluster policies (such as those used by KubeStellar). It leverages the FastMCP framework and the official Kubernetes Python client for robust, extensible automation.

---

## Features

- **Cluster & Node Management:** List, inspect, and retrieve logs from Kubernetes clusters.
- **Namespace Management:** Create, delete, and list namespaces with custom labels.
- **Resource Management:** Manage pods—create, delete, list, and retrieve logs and statuses.
- **KubeStellar-Style Space & Policy:** Manage Workload Description Spaces (WDS), context switching, and BindingPolicy CRDs.
- **Automation & Integration:** Designed to work with modern Python tooling like `uv` for dependency management and execution.

---

## Requirements

- **Python:** 3.12 or higher
- **Dependencies:** Managed via `uv` (see below)
- **Kubernetes:** Access to one or more Kubernetes clusters (via kubeconfig)

---

## Installation

1. **Clone the repository:**
```git clone https://github.com/Per0x1de-1337/Kubralis; cd Kubralis ```

2. **Install uv and install dependencies**
```uv venv ; uv pip install -e . ; ```

3. **Config for Windsurf/Claude Desktop**
    ```
   {
  "mcpServers": {
    "Kubralis": {
      "command": "uv",
      "args": ["--directory", "/path/to/Kubralis", "run", "main.py"]
    }
  }
}
```
