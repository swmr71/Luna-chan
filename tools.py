import os
import json
from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv

load_dotenv()

# Proxmox API 初期化
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
    print(f"⚠️ Proxmox API initialization failed: {e}")
    proxmox = None

# ツール定義（Google Generative AI の Tool Calling フォーマット）
TOOLS = [
    {
        "name": "list_all_containers",
        "description": "Retrieves a live list of all LXC containers and VMs across all Proxmox nodes.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_container_status",
        "description": "Retrieves the current status and resource usage of a specific LXC container.",
        "parameters": {
            "type": "object",
            "properties": {
                "vmid": {
                    "type": "integer",
                    "description": "The Container ID (CTID) to check (e.g., 101, 102)"
                },
                "node": {
                    "type": "string",
                    "description": "The Proxmox node name (default: 'pve')"
                }
            },
            "required": ["vmid"]
        }
    },
    {
        "name": "manage_container_power",
        "description": "Controls the power state of a specific LXC container (start, stop, shutdown, reboot).",
        "parameters": {
            "type": "object",
            "properties": {
                "vmid": {
                    "type": "integer",
                    "description": "The Container ID (CTID) to manage"
                },
                "action": {
                    "type": "string",
                    "enum": ["start", "stop", "shutdown", "reboot"],
                    "description": "The power action to perform"
                },
                "node": {
                    "type": "string",
                    "description": "The Proxmox node name (default: 'pve')"
                }
            },
            "required": ["vmid", "action"]
        }
    },
    {
        "name": "read_server_knowledge",
        "description": "Reads the long-term infrastructure layout and server knowledge from the knowledge file.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "write_server_knowledge",
        "description": "Appends important server facts, troubleshooting logs, or configuration changes to the knowledge file.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The content to append to the server knowledge file"
                }
            },
            "required": ["content"]
        }
    }
]

# ツール実装関数
def list_all_containers() -> str:
    """Proxmox 全コンテナ・VM の一覧を取得"""
    if not proxmox:
        return "❌ Proxmox API is not configured."
    try:
        nodes = proxmox.nodes.get()
        if not nodes:
            return "No physical nodes found in the Proxmox cluster."
        
        res_lines = ["=== Live Proxmox Cluster Resource List ==="]
        found_any = False
        
        for n in nodes:
            node_name = n.get("node")
            
            # LXC コンテナ
            try:
                containers = proxmox.nodes(node_name).lxc.get()
                for c in containers:
                    vmid = c.get("vmid")
                    name = c.get("name")
                    status = c.get("status")
                    res_lines.append(f"- [{node_name}] LXC {vmid}: {name} ({status})")
                    found_any = True
            except Exception as e:
                res_lines.append(f"- [{node_name}] Failed to fetch LXCs: {str(e)}")
            
            # QEMU VM
            try:
                vms = proxmox.nodes(node_name).qemu.get()
                for v in vms:
                    vmid = v.get("vmid")
                    name = v.get("name")
                    status = v.get("status")
                    res_lines.append(f"- [{node_name}] QEMU {vmid}: {name} ({status})")
                    found_any = True
            except Exception as e:
                res_lines.append(f"- [{node_name}] Failed to fetch VMs: {str(e)}")
        
        if not found_any:
            return "Connected to Proxmox, but no containers or VMs were found."
            
        return "\n".join(res_lines)
    except Exception as e:
        return f"❌ Failed to retrieve cluster: {str(e)}"

def get_container_status(vmid: int, node: str = "pve") -> str:
    """指定コンテナのステータスを取得"""
    if not proxmox:
        return "❌ Proxmox API is not configured."
    try:
        status = proxmox.nodes(node).lxc(vmid).status.current.get()
        name = status.get("name", "Unknown")
        state = status.get("status", "unknown")
        cpu = round(status.get("cpu", 0) * 100, 1)
        mem = round(status.get("mem", 0) / (1024 ** 3), 2)
        maxmem = round(status.get("maxmem", 0) / (1024 ** 3), 2)
        return f"✅ Container [{name}] (ID: {vmid}) | Status: {state} | CPU: {cpu}% | Mem: {mem}GB/{maxmem}GB"
    except Exception as e:
        return f"❌ Failed to get status for CTID {vmid}: {str(e)}"

def manage_container_power(vmid: int, action: str, node: str = "pve") -> str:
    """コンテナの電源を制御"""
    if not proxmox:
        return "❌ Proxmox API is not configured."
    if action not in ['start', 'stop', 'shutdown', 'reboot']:
        return f"❌ Invalid action '{action}'. Allowed: start, stop, shutdown, reboot."
    try:
        proxmox.nodes(node).lxc(vmid).status.post(action)
        return f"✅ Successfully initiated '{action}' command for CTID {vmid}."
    except Exception as e:
        return f"❌ Failed to execute '{action}' for CTID {vmid}: {str(e)}"

def read_server_knowledge() -> str:
    """サーバー知識ファイルを読む"""
    knowledge_file = "server_knowledge.md"
    if not os.path.exists(knowledge_file):
        return "No server knowledge file found yet."
    try:
        with open(knowledge_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"❌ Failed to read knowledge file: {str(e)}"

def write_server_knowledge(content: str) -> str:
    """サーバー知識ファイルに追記"""
    knowledge_file = "server_knowledge.md"
    try:
        with open(knowledge_file, "a", encoding="utf-8") as f:
            f.write(f"- {content}\n")
        return "✅ Server knowledge saved successfully."
    except Exception as e:
        return f"❌ Failed to save knowledge: {str(e)}"

# ツール実行ディスパッチャ
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """ツール名と入力に基づいてツールを実行"""
    if tool_name == "list_all_containers":
        return list_all_containers()
    elif tool_name == "get_container_status":
        vmid = tool_input.get("vmid")
        node = tool_input.get("node", "pve")
        return get_container_status(vmid, node)
    elif tool_name == "manage_container_power":
        vmid = tool_input.get("vmid")
        action = tool_input.get("action")
        node = tool_input.get("node", "pve")
        return manage_container_power(vmid, action, node)
    elif tool_name == "read_server_knowledge":
        return read_server_knowledge()
    elif tool_name == "write_server_knowledge":
        content = tool_input.get("content", "")
        return write_server_knowledge(content)
    else:
        return f"❌ Unknown tool: {tool_name}"
