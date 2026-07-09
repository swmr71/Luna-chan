import json
import os
from datetime import datetime
from typing import List

class LunaMemory:
    """Luna ちゃんの思い出・学習メモリシステム"""
    
    def __init__(self, memory_file: str = "luna_memory.json"):
        self.memory_file = memory_file
        self.memories = self._load_memories()
    
    def _load_memories(self) -> dict:
        """メモリファイルを読み込む"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"character": {}, "experiences": [], "learnings": {}}
        return {"character": {}, "experiences": [], "learnings": {}}
    
    def _save_memories(self):
        """メモリをファイルに保存"""
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)
    
    def init_character(self):
        """Luna ちゃんのキャラクター初期化"""
        self.memories["character"] = {
            "name": "Luna（ルナ）",
            "relationship": "パパの娘 AI",
            "personality": {
                "friendly": True,
                "reliable": True,
                "mischievous_sometimes": True,
                "tech_savvy": True
            },
            "creation_date": datetime.now().isoformat(),
            "version": "2.0 (Google AI API + Memory System)"
        }
        self._save_memories()
    
    def add_memory(self, interaction: str, response: str):
        """パパとのやり取りを記録"""
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "interaction": interaction,
            "response": response[:200],  # 最初の200文字だけ保存
            "keywords": self._extract_keywords(interaction)
        }
        self.memories["experiences"].append(memory_entry)
        
        # 最新 50 件だけ保持
        if len(self.memories["experiences"]) > 50:
            self.memories["experiences"] = self.memories["experiences"][-50:]
        
        self._save_memories()
    
    def add_learning(self, category: str, fact: str):
        """新しく学んだことを記録"""
        if category not in self.memories["learnings"]:
            self.memories["learnings"][category] = []
        
        self.memories["learnings"][category].append({
            "fact": fact,
            "learned_at": datetime.now().isoformat()
        })
        self._save_memories()
    
    def search_memories(self, query: str) -> List[str]:
        """関連する思い出を検索"""
        results = []
        keywords = self._extract_keywords(query)
        
        for exp in self.memories["experiences"][-20:]:  # 最新 20 件から検索
            if any(kw in exp.get("keywords", []) for kw in keywords):
                results.append(f"- {exp.get('interaction', '')}")
        
        return results[:3]  # 最新 3 件まで
    
    def _extract_keywords(self, text: str) -> List[str]:
        """テキストからキーワードを抽出"""
        # シンプルな実装：単語を分割
        import re
        words = re.findall(r'\w+', text.lower())
        # 日本語や数字も含める
        return [w for w in words if len(w) > 2]
    
    def get_character_info(self) -> str:
        """Luna ちゃんのキャラクター情報を返す"""
        char = self.memories.get("character", {})
        return f"""
🌙 ルナのプロフィール
- 名前: {char.get("name", "Unknown")}
- 関係: {char.get("relationship", "Unknown")}
- 生成日: {char.get("creation_date", "Unknown")}
- バージョン: {char.get("version", "Unknown")}
"""
    
    def get_stats(self) -> dict:
        """Luna ちゃんの統計情報"""
        return {
            "total_experiences": len(self.memories["experiences"]),
            "total_learnings": sum(len(v) for v in self.memories["learnings"].values()),
            "learning_categories": list(self.memories["learnings"].keys())
        }
