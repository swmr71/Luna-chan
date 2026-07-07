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

print("--- Proxmox API 接続テスト開始 ---")
print(f"エンドポイント: {endpoint}")
print(f"ユーザー: {user}")
print(f"トークン名: {token_name}")

if not endpoint:
    print("\n[エラー] PVE_ENDPOINT が取得できませんでした。")
    print(".envファイルと同じディレクトリでスクリプトを実行しているか確認してください。")
    exit(1)

try:
    # URLからホスト名（IP）とポートを解析して抽出
    # 例: https://10.2.0.X:8006/api2/json -> host="10.2.0.X", port=8006
    parsed_url = urlparse(endpoint)
    host = parsed_url.hostname
    port = parsed_url.port if parsed_url.port else 8006

    print(f"解析されたホスト: {host}")
    print(f"解析されたポート: {port}")

    # Proxmox API クライアントの初期化
    proxmox = ProxmoxAPI(
        host,
        port=port,
        user=user,
        token_name=token_name,
        token_value=token_value,
        verify_ssl=False  # 自己署名証明書（オレオレ証明書）を許可
    )

    print("\n1. 物理ノードの取得をテスト中...")
    nodes = proxmox.nodes.get()
    print("[成功] 物理ノードが取得できました:")
    
    for node in nodes:
        node_name = node.get("node")
        print(f"- ノード名: {node_name} (ステータス: {node.get('status')})")
        
        # 2. 各ノードに紐づくコンテナ（LXC）の取得テスト
        print(f"  └─ {node_name} のコンテナ一覧をリクエスト中...")
        try:
            containers = proxmox.nodes(node_name).lxc.get()
            if containers:
                for c in containers:
                    print(f"     [LXC] CTID {c.get('vmid')}: {c.get('name')} ({c.get('status')})")
            else:
                print("     [LXC] コンテナは見つかりませんでした（または権限がありません）")
        except Exception as ce:
            print(f"
