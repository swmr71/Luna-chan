import os
from crewai.tools import tool
from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv

load_dotenv()

try:
    endpoint = os.getenv("PVE_ENDPOINT", "https://10.2.0.1:8006/api2/json")
    host = endpoint.split("//")[1].split(":")[0]
    
    proxmox = ProxmoxAPI(
        host,
        user=os.getenv("PVE_USER"),
        token_name=os.getenv("PVE_TOKEN_NAME"),
        token_value=os.getenv("PVE_TOKEN_VALUE"),
        verify_ssl=False
    )
except Exception as e:
    proxmox = None

MEMORY_FILE = "server_knowledge.md"

@tool("Read Long-term Server Memory")
def read_server_memory() -> str:
    """
    Reads the entire long-term memory file containing past server logs, notes, and facts.
    Use this at the start of a task to check past context or troubleshooting history.
    """
    if not os.path.exists(MEMORY_FILE):
        return "No long-term memory records found yet. The file is empty."
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return f.read()

@tool("Write Long-term Server Memory")
def write_server_memory(content: str) -> str:
    """
    Appends important server facts, troubleshooting logs, or configuration changes to the long-term memory file.
    Use this when you learn something new about the server or execute an important action that should be remembered.
    """
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"- {content}\n")
    return "Memory saved successfully to server_knowledge.md."

@tool("Get Proxmox Container Status")
def get_container_status(vmid: int, node: str = "pve") -> str:
    """
    Retrieves the current status and resource usage of a specific LXC container on Proxmox.
    Use this tool when the user or Master asks about the status, CPU, or memory of a specific container ID.
    
    Args:
        vmid (int): The Container ID (CTID) to check (e.g., 101, 102).
        node (str): The Proxmox node name. Defaults to 'pve'.
    """
    if not proxmox:
        return "Proxmox API is not configured or failed to initialize."
    try:
        status = proxmox.nodes(node).lxc(vmid).status.current.get()
        name = status.get("name", "Unknown")
        state = status.get("status", "unknown")
        cpu = round(status.get("cpu", 0) * 100, 1)
        mem = round(status.get("mem", 0) / (1024 ** 3), 2)
        maxmem = round(status.get("maxmem", 0) / (1024 ** 3), 2)
        return f"Container [{name}] (ID: {vmid}) Status: {state} | CPU: {cpu}% | Mem: {mem}GB/{maxmem}GB"
    except Exception as e:
        return f"Failed to get status for CTID {vmid}: {str(e)}"

@tool("Manage Proxmox Container Power")
def manage_container_power(vmid: int, action: str, node: str = "pve") -> str:
    """
    Controls the power state of a specific LXC container on Proxmox (start, stop, shutdown, reboot).
    Use this tool only when receiving a direct and clear order to change a container state.
    
    Args:
        vmid (int): The Container ID (CTID) to manage.
        action (str): The power action to perform. Allowed values: 'start', 'stop', 'shutdown', 'reboot'.
        node (str): The Proxmox node name. Defaults to 'pve'.
    """
    if not proxmox:
        return "Proxmox API is not configured or failed to initialize."
    if action not in ['start', 'stop', 'shutdown', 'reboot']:
        return f"Invalid action '{action}'. Allowed: start, stop, shutdown, reboot."
    try:
        proxmox.nodes(node).lxc(vmid).status.post(action)
        return f"Successfully initiated '{action}' command for CTID {vmid}."
    except Exception as e:
        return f"Failed to execute '{action}' for CTID {vmid}: {str(e)}"
