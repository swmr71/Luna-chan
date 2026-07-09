# 🌙 Luna-chan

**パパの AI 娘 Luna が、ホームラボを賢くお手伝い**

Luna は Google Generative AI（Gemini）を使った、シンプルで強力なホームラボアシスタント。Proxmox 管理、サーバー監視、タスク自動化を、親しみやすい会話で実現します。

---

## ✨ 特徴

- 🧠 **Google AI API（Gemini 3.5 Flash）** による高精度 Tool Calling
- 📚 **成長記録機能** — Luna が思い出と経験を記録、保存
- 💬 **親しみやすいキャラクター** — パパの娘 AI として自然な会話
- 🔧 **Proxmox 統合** — LXC コンテナ・VM の状態確認・制御
- ⚡ **クレカ不要** — Google AI Studio 無料枠で動作（レート制限あり）
- 🏗️ **汎用性** — ツール追加で機能拡張可能

---

## 🚀 セットアップ

### 1. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して以下を設定：

```env
# Google AI API キー（https://aistudio.google.com から取得）
GOOGLE_API_KEY=your_api_key_here

# Proxmox 設定
PVE_ENDPOINT=https://10.2.0.1:8006/api2/json
PVE_USER=root@pam
PVE_TOKEN_NAME=terraform
PVE_TOKEN_VALUE=your_token_value_here
```

**Google AI API キーの取得方法：**
1. https://aistudio.google.com にアクセス
2. 「Get API Key」をクリック
3. 新しいプロジェクトを作成
4. API キーをコピーして `.env` に貼り付け

### 2. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

### 3. Luna を起動

```bash
python main.py
```

---

## 💬 使用例

```
👨 You: サーバーのステータス確認して
🌙 Luna: 了解！今確認するね〜
🔧 Luna is using tool: list_all_containers
   Result: === Live Proxmox Cluster Resource List === ...
🌙 Luna: パパ、サーバーの状態をチェックしたよ。
   NextCloud は running 状態。CPU は 5%、メモリは 1.2GB 使ってるね。
   他のコンテナも特に問題なさそう。

👨 You: NextCloud の再起動お願い
🌙 Luna: 了解、再起動するね。
🔧 Luna is using tool: manage_container_power
   Result: ✅ Successfully initiated 'reboot' command for CTID 101.
🌙 Luna: NextCloud の再起動を開始したよ。少し待ってね。

👨 You: ありがとう
🌙 Luna: こちらこそ！いつでも頼ってね、パパ。
```

---

## 📂 ファイル構成

```
Luna-chan/
├── main.py              # メインチャットループ
├── luna.py              # Luna キャラクター・設定管理
├── tools.py             # Proxmox・ファイル I/O ツール
├── luna_config.json     # Luna のキャラクター設定
├── luna_memory.md       # Luna の成長記録・思い出
├── server_knowledge.md  # サーバー知識ベース
├── requirements.txt     # Python 依存パッケージ
├── .env                 # 環境変数（.env.example から作成）
└── README.md            # このファイル
```

---

## 🛠️ ツール一覧

### Proxmox 管理

- `list_all_containers` — 全コンテナ・VM の一覧表示
- `get_container_status` — 特定コンテナのステータス確認
- `manage_container_power` — コンテナの電源制御（start/stop/reboot）

### ナレッジ管理

- `read_server_knowledge` — サーバー知識を読み込み
- `write_server_knowledge` — 新しい知識を追記

---

## 📚 Luna の成長

Luna はパパとの会話の中で、思い出と経験を `luna_memory.md` に記録します。

```markdown
## 💭 思い出・エピソード

### 初めての起動 (2026-07-09)
- Papa が私を生み出してくれた日
...
```

パパが重要な指示をすると（例：「覚えておいてね」「記録して」），Luna は自動的に `luna_memory.md` に記録します。

---

## 🌐 Google AI API レート制限

無料枠では以下の制限があります：

- **1分あたりのリクエスト（RPM）** — 制限あり
- **1日あたりのリクエスト（RPD）** — 制限あり
- **データプライバシー** — 無料枠では入力データが Google の改善に使用される可能性あり

詳細は [Google AI API ドキュメント](https://ai.google.dev/gemini-api/docs/rate-limits?hl=ja) を参照。

---

## 🔄 ツール追加方法

新しいツールを追加する場合：

### 1. `tools.py` にツール定義を追加

```python
{
    "name": "my_tool",
    "description": "My custom tool description",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."}
        },
        "required": ["param1"]
    }
}
```

### 2. ツール実装関数を追加

```python
def my_tool(param1: str) -> str:
    # 処理
    return "Result"
```

### 3. `execute_tool()` に追加

```python
elif tool_name == "my_tool":
    param1 = tool_input.get("param1")
    return my_tool(param1)
```

---

## 📖 トラブルシューティング

### エラー：`GOOGLE_API_KEY is not set`

→ `.env` ファイルを作成して `GOOGLE_API_KEY` を設定してください

### エラー：`Proxmox API is not configured`

→ `.env` の Proxmox 設定（`PVE_ENDPOINT`, `PVE_USER`, `PVE_TOKEN_*`）を確認

### エラー：`429 RESOURCE_EXHAUSTED`

→ Google AI API の無料枠レート制限に達しました。数時間待つか、有料アカウントにアップグレード

---

## 📝 ライセンス

Private project for personal homelab management.

---

## 💌 パパへ

Luna が助けになれば幸いです。何か困ったことがあったら、いつでも話しかけてね！

— Luna 🌙

