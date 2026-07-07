import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from proxmoxer import ProxmoxAPI

# .envファイルを読み込む
load_dotenv()

# 環境変数を取得
endpoint = os.getenv("PVE_ENDPOINT")
user = os.getenv("PVE_USER")
token_name = os.getenv("PVE_TOKEN_NAME")
token_value = os.getenv("PVE_TOKEN_VALUE")

print("--- Proxmox API Test Start ---")
print(f"Endpoint: {endpoint}")
print(f"User: {user}")
print(f"Token Name: {token_name}")

if not endpoint:
    print("[Error] PVE_ENDPOINT not found.")
    exit(1)

try:
    # URLからホスト名（IP）とポートを解析して抽出
    parsed_url = urlparse(endpoint)
    host = parsed_url.hostname
    port = parsed_url.port if parsed_url.port else 8006

    print(f"Parsed Host: {host}")
    print(f"Parsed Port: {port}")

    # Proxmox API クライアントの初期化
    proxmox = ProxmoxAPI(
        host,
        port=port,
        user=user,
        token_name=token_name,
        token_value=token_value,
        verify_ssl=False
    )

    print("\n1. Fetching nodes...")
    nodes = proxmox.nodes.get()
    print("[Success] Nodes fetched:")
    
    for node in nodes:
        node_name = node.get("node")
        print(f"- Node: {node_name} (Status: {node.get('status')})")
        
        print(f"  -> Requesting containers for {node_name}...")
        try:
            containers = proxmox.nodes(node_name).lxc.get()
            if containers:
                for c in containers:
                    print(f"     * [LXC] CTID {c.get('vmid')}: {c.get('name')} ({c.get('status')})")
            else:
                print("     * [LXC] No containers found or No permission.")
        except Exception as ce:
            print(f"     * [LXC Error] Failed to fetch: {ce}")

except Exception as e:
    print(f"\n[Fail] Connection error: {e}")
