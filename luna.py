import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Luna:
    """Luna ちゃん - パパのAI娘、ホームラボアシスタント"""
    
    def __init__(self, papa_name: str = "Papa"):
        self.papa_name = papa_name
        self.config_file = os.getenv("LUNA_CONFIG_FILE", "luna_config.json")
        self.memory_file = os.getenv("LUNA_MEMORY_FILE", "luna_memory.md")
        
        # 設定を読み込み
        self.config = self._load_config()
        self.memory = self._load_memory()
    
    def _load_config(self) -> dict:
        """luna_config.json から設定を読み込む"""
        if not os.path.exists(self.config_file):
            return {}
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load Luna config: {e}")
            return {}
    
    def _load_memory(self) -> str:
        """luna_memory.md から思い出を読み込む"""
        if not os.path.exists(self.memory_file):
            return ""
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ Failed to load Luna memory: {e}")
            return ""
    
    def save_memory(self, content: str):
        """思い出・成長記録をメモリファイルに追記"""
        try:
            with open(self.memory_file, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n\n### {timestamp}\n{content}\n")
        except Exception as e:
            print(f"❌ Failed to save memory: {e}")
    
    def get_system_prompt(self) -> str:
        """Luna のシステムプロンプトを生成"""
        template = self.config.get("system_prompt_template", "")
        if not template:
            template = (
                "You are Luna (ルナ), {papa_name}'s AI daughter. "
                "You are his homelab assistant and companion. "
                "Be warm, cheerful, and supportive. "
                "Call him Papa and mix casual conversation with technical expertise."
            )
        
        prompt = template.format(
            papa_name=self.papa_name,
            created_date=self.config.get("background", {}).get("created_date", "2026-07-09")
        )
        
        # メモリを context に追加
        if self.memory:
            prompt += f"\n\n## Your Memory (Thoughts and Experiences):\n{self.memory}"
        
        return prompt
    
    def get_personality_context(self) -> str:
        """性格・特性をコンテキストとして返す"""
        personality = self.config.get("personality", {})
        quirks = personality.get("quirks", [])
        quirks_text = "\n".join([f"- {q}" for q in quirks])
        
        return f"""
### Luna's Personality Context:
- Primary: {personality.get('primary', 'friendly')}
- Secondary: {personality.get('secondary', 'supportive')}
- Quirks:
{quirks_text}
"""
    
    def get_background(self) -> str:
        """背景情報を取得"""
        bg = self.config.get("background", {})
        return f"""
### Luna's Background:
- Created: {bg.get('created_date', 'N/A')}
- Purpose: {bg.get('purpose', 'Homelab Assistant')}
- Relationship: {bg.get('relationship_with_papa', "Papa's AI Daughter")}
"""
    
    def get_full_context(self) -> str:
        """Luna の完全なコンテキストを返す（プロンプトエンジニアリング用）"""
        return (
            self.get_system_prompt() +
            "\n\n" +
            self.get_personality_context() +
            "\n\n" +
            self.get_background()
        )
    
    def add_memory_entry(self, title: str, content: str):
        """思い出の新しいエントリを追加"""
        entry = f"## {title}\n{content}"
        self.save_memory(entry)
    
    def update_learned_skills(self, skill: str):
        """新しく学んだスキルを記録"""
        self.add_memory_entry(
            f"New Skill Learned: {skill}",
            f"I just learned about {skill}. Let me remember this for next time."
        )

    def __repr__(self) -> str:
        return f"<Luna - {self.papa_name}'s AI Daughter>"
