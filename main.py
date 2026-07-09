import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

from luna import Luna
from tools import TOOLS, execute_tool

load_dotenv()

# Google AI API 設定
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("❌ GOOGLE_API_KEY is not set. Please set it in .env")
    exit(1)

genai.configure(api_key=API_KEY)

# Luna ちゃんの初期化
luna = Luna(papa_name="Papa")

print(f"🌙 Luna (ルナ) - {luna.papa_name}'s AI Daughter")
print(f"Created: {luna.config.get('background', {}).get('created_date', 'N/A')}")
print("=" * 50)
print("Type 'exit' or 'quit' to end the conversation.")
print("=" * 50)

def chat_with_luna(user_message: str) -> str:
    """Google Generative AI を使って Luna と会話"""
    
    # システムプロンプトを取得
    system_prompt = luna.get_full_context()
    
    # メッセージ履歴（シンプル版）
    messages = [
        {"role": "user", "content": user_message}
    ]
    
    try:
        # Google Generative AI を使用
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash",  # 最新の高速モデル
            system_instruction=system_prompt,
            tools=TOOLS
        )
        
        # 初回呼び出し
        response = model.generate_content(
            messages,
            tool_config=genai.types.tool_config.ToolConfig(
                function_calling_config=genai.types.tool_config.FunctionCallingConfig("AUTO")
            )
        )
        
        # Tool Calling ループ
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            # テキスト応答の場合
            if hasattr(part, "text"):
                return part.text
            
            # ツール呼び出しの場合
            if part.function_call:
                tool_name = part.function_call.name
                tool_input = {k: v for k, v in part.function_call.args.items()}
                
                print(f"\n🔧 Luna is using tool: {tool_name}")
                tool_result = execute_tool(tool_name, tool_input)
                print(f"   Result: {tool_result[:100]}...")
                
                # ツール結果を含めて再度実行
                messages.append({"role": "model", "content": response.candidates[0].content})
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "function_response": {
                                "name": tool_name,
                                "response": {"result": tool_result}
                            }
                        }
                    ]
                })
                
                response = model.generate_content(
                    messages,
                    tool_config=genai.types.tool_config.ToolConfig(
                        function_calling_config=genai.types.tool_config.FunctionCallingConfig("AUTO")
                    )
                )
            else:
                break
        
        # 最終的な応答を抽出
        if response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text"):
                    return part.text
        
        return "Luna is thinking... (No response generated)"
    
    except Exception as e:
        return f"❌ Error: {str(e)}\n💡 Make sure GOOGLE_API_KEY is set correctly."

def main():
    """メインチャットループ"""
    while True:
        try:
            user_input = input("\n👨 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n🌙 Luna: さようなら、パパ。また明日ね！")
                break
            
            # Luna と会話
            print("\n🌙 Luna: ", end="", flush=True)
            response = chat_with_luna(user_input)
            print(response)
            
            # 重要なイベントをメモリに記録
            if any(keyword in user_input.lower() for keyword in ['remember', 'note', 'save']):
                luna.add_memory_entry(
                    "Papa's Request",
                    f"Papa asked me to remember: {user_input}"
                )
        
        except KeyboardInterrupt:
            print("\n\n🌙 Luna: おやすみなさい、パパ...")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
