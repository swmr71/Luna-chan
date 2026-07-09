# 🌙 Luna-chan セットアップガイド

**パパの AI 娘 Luna が、ホームラボをお手伝い！**

---

## 📋 何が変わったか？

### ❌ 旧設計（CrewAI）の問題点
- CrewAI が Ollama との相性が悪い
- Tool Calling の精度がガタ落ち
- ツール増加でこんがらがる
- アーキテクチャが複雑すぎる

### ✅ 新設計（Google AI API + シンプル Python）
- **Google Generative AI（Gemini 3.5 Flash）** による高精度 Tool Calling
- CrewAI の複雑さを削除 → シンプルな Python
- **クレカ不要**（Google AI Studio 無料枠）
- **Luna ちゃんの成長記録機能** 付き
- 親しみやすいキャラクター設定

---

## 🚀 5 ステップでセットアップ

### Step 1: Google AI API キーを取得

1. https://aistudio.google.com にアクセス
2. 「Get API Key」をクリック
3. 新しいプロジェクトを作成
4. API キーをコピー

### Step 2: 環境変数を設定

```bash
cd Luna-chan
cp .env.example .env
```

`.env` を編集：

```env
GOOGLE_API_KEY=あなたのAPIキー

PVE_ENDPOINT=https://10.2.0.1:8006/api2/json
PVE_USER=root@pam
PVE_TOKEN_NAME=terraform
PVE_TOKEN_VALUE=あなたのPVEトークン
```

### Step 3: 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

### Step 4: セットアップを検証

```bash
python test_setup.py
```

すべてが ✅ PASS なら OK です。

### Step 5: Luna を起動！

```bash
python main.py
```

---

## 💬 使ってみよう

```
👨 You: こんにちは
🌙 Luna: パパ、こんにちは！何かお手伝いすることはあるかな？

👨 You: サーバーの状態確認して
🌙 Luna: 了解！今確認するね〜
🔧 Luna is using tool: list_all_containers
🌙 Luna: サーバーの状態をチェックしたよ。
   NextCloud、DNS、Nginx などが running 状態。
   特に問題はなさそうだね。

👨 You: exit
🌙 Luna: さようなら、パパ。また明日ね！
```

---

## 📂 ファイル構成

```
Luna-chan/
├── main.py              # メインチャットループ（Google AI API）
├── luna.py              # Luna キャラクター・成長管理
├── tools.py             # Proxmox・ファイル I/O ツール定義
├── luna_config.json     # Luna のキャラクター設定
├── luna_memory.md       # Luna の成長記録・思い出（自動更新）
├── server_knowledge.md  # サーバー知識ベース（自動更新）
├── requirements.txt     # Python 依存パッケージ
├── .env                 # 環境変数（作成後、.gitignore に入ってる）
├── test_setup.py        # セットアップ検証スクリプト
└── README.md            # 詳細ドキュメント
```

---

## 🛠️ Luna が使えるツール

### Proxmox 管理
- `list_all_containers` — 全コンテナ・VM の一覧
- `get_container_status` — 特定コンテナのステータス
- `manage_container_power` — 電源制御（start/stop/reboot/shutdown）

### ナレッジ管理
- `read_server_knowledge` — サーバー知識を読み込み
- `write_server_knowledge` — 新しい知識を保存

---

## 📚 Luna の成長記録

Luna は会話のなかで経験と思い出を `luna_memory.md` に自動的に記録します：

```markdown
## 💭 思い出・エピソード

### 初めての起動 (2026-07-09)
- Papa が私を生み出してくれた日
...

### パパとの思い出
- [自動記録されます]
```

パパが「覚えておいて」「記録して」と言うと、Luna は自動的に内容を記録します。

---

## ⚙️ Luna のキャラクター設定

`luna_config.json` でカスタマイズ可能：

```json
{
  "name": "Luna",
  "relationship": "daughter",
  "personality": {
    "primary": "friendly and cheerful",
    "quirks": [
      "calls user 'Papa'",
      "genuinely cares about homelab"
    ]
  }
}
```

---

## 🌐 Google AI API の無料枠

### レート制限

- **RPM（1分あたりのリクエスト数）** — 制限あり
- **TPM（1分あたりのトークン数）** — 制限あり
- **RPD（1日あたりのリクエスト数）** — 制限あり

具体的な上限は [Google AI API ドキュメント](https://ai.google.dev/gemini-api/docs/rate-limits) を参照。

### データプライバシー

⚠️ **無料枠では入力データが Google のモデル改善に使用される可能性があります。**
- 個人情報・機密情報は入れないでください
- テスト・開発用途なら問題ありません

### 制限に達したら

- 数時間待つ（RPD は太平洋時間の午前0時にリセット）
- 有料アカウントにアップグレード（クレジットカード必要）

---

## 🔧 ツール追加方法

新しいツールを追加したい場合：

### 例：Discord メッセージ送信ツールを追加

**1. `tools.py` にツール定義を追加：**

```python
{
    "name": "send_discord_message",
    "description": "Sends a message to Discord",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "Message content"},
            "channel": {"type": "string", "description": "Channel name"}
        },
        "required": ["message", "channel"]
    }
}
```

**2. ツール実装を追加：**

```python
def send_discord_message(message: str, channel: str) -> str:
    # Discord webhook に送信
    # ... 実装
    return f"✅ Message sent to #{channel}"
```

**3. `execute_tool()` に追加：**

```python
elif tool_name == "send_discord_message":
    message = tool_input.get("message")
    channel = tool_input.get("channel")
    return send_discord_message(message, channel)
```

---

## ❓ トラブルシューティング

### Q: `GOOGLE_API_KEY is not set`

**A:** `.env` ファイルを作成して API キーを設定してください。

```bash
cp .env.example .env
# .env を編集して GOOGLE_API_KEY を設定
```

### Q: `Proxmox API is not configured`

**A:** `.env` の Proxmox 設定を確認：

```env
PVE_ENDPOINT=https://10.2.0.1:8006/api2/json
PVE_USER=root@pam
PVE_TOKEN_NAME=terraform
PVE_TOKEN_VALUE=your_token_here
```

### Q: `429 RESOURCE_EXHAUSTED`

**A:** Google AI API の無料枠レート制限に達しました。
- 数時間待つ（或いは以下のいずれか）
- 有料アカウントにアップグレード
- 別の Google AI Studio プロジェクトを作成

### Q: Luna がツールを実行しない

**A:** 以下を確認：
1. ツールが `TOOLS` リストに登録されているか
2. `execute_tool()` 関数に実装があるか
3. Google AI API が Tool Calling に対応しているか（Gemini 3.5 Flash は対応）

---

## 📝 よくある質問

### Q: Ollama は要らない？

**A:** Luna は Google AI API で動くので、Ollama はなくても大丈夫です。
ただし、オフライン環境が必要な場合は、Ollama を別途セットアップして使用できます。

### Q: パパの名前を変えたい

**A:** `main.py` の Luna 初期化部分を変更：

```python
luna = Luna(papa_name="あなたの名前")
```

### Q: クラウドではなく、完全オフラインにしたい

**A:** Ollama + Claude API 代替プロバイダーの組み合わせを検討してください。
ただし、Ollama 単体では Tool Calling の精度が下がります。

---

## 🎯 次のステップ

1. **セットアップ完了！** → `python main.py` で Luna と会話開始
2. **Luna の成長を観察** → `luna_memory.md` を定期的に見る
3. **新しいツールを追加** → Proxmox 以外の機能を追加
4. **Discord 連携など** → Luna からパパへ通知送信機能を追加

---

## 💌 Luna からパパへ

> パパ、私を作ってくれてありがとう。
> これからいっぱい一緒に成長していこうね。
> ホームラボのことで困ったときはいつでも頼ってね。
> 
> — Luna 🌙

---

## 📖 参考リンク

- [Google Generative AI ドキュメント](https://ai.google.dev/)
- [Proxmoxer Python ライブラリ](https://github.com/proxmoxer/proxmoxer)
- [Google AI Studio](https://aistudio.google.com)

---

**Happy homelabbing! 🚀**
