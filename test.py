import os
from dotenv import load_dotenv
from proxmoxer import ProxmoxAPI

# .envファイルを読み込む
load_dotenv()

# 環境変数を取得
host = os.getenv("PROXMOX_HOST")
user = os.getenv("PROXMOX_USER")
token_name = os.getenv("PROXMOX_TOKEN_NAME")
token_value = os.getenv("PROXMOX_TOKEN_VALUE")

print("--- Proxmox API 接続テスト開始 ---")
print(f"接続先ホスト: {host}")
print(f"ユーザー: {user}")
print(f"トークン名: {token_name}")

try:
    # Proxmox API クライアントの初期化
    # ※オレオレ証明書（自己署名）を使っている場合は verify_ssl=False にしておく
    proxmox = ProxmoxAPI(
        host,
        user=user,
        token_name=token_name,
        token_value=token_value,
        verify_ssl=False
    )

    # テストとして物理ノードの一覧を取得してみる
    print("\nAPIリクエストを送信中...")
    nodes = proxmox.nodes.get()
    
    print("\n[成功] 接続できました！物理ノード一覧:")
    for node in nodes:
        print(f"- ノード名: {node.get('node')} (ステータス: {node.get('status')}, CPU使用率: {node.get('cpu'):.2%})")

except Exception as e:
    print("\n[失敗] 接続エラーが発生しました:")
    print(e)
