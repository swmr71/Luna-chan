import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from luna import Luna
from tools import TOOLS, execute_tool

load_dotenv()

# Google AI API 設定
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("❌ GOOGLE_API_KEY is not set. Please set it in .env")
    exit(1)

client = genai.Client(api_key=API_KEY)

# Luna ちゃんの初期化
luna = Luna(papa_name="Papa")

print(f"🌙 Luna (ルナ) - {luna.papa_name}'s AI Daughter")
print(f"Created: {luna.config.get('background', {}).get('created_date', 'N/A')}")
print("=" * 50)
print("Type 'exit' or 'quit' to end the conversation.")
print("=" * 50)

def chat_with_luna(user_message: str) -> str:
    """Google Gen AI を使って Luna と会話"""

    system_prompt = luna.get_full_context()

    generation_config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[types.Tool(function_declarations=TOOLS)],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode="AUTO")
        ),
    )

    contents = [types.Content(role="user", parts=[types.Part(text=user_message)])]
    
    try:
        while True:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=contents,
                config=generation_config,
            )

            if not response.candidates:
                return "Luna is thinking... (No response generated)"

            response_content = response.candidates[0].content
            function_calls = []

            for part in response_content.parts:
                if getattr(part, "function_call", None):
                    function_calls.append(part.function_call)

            if not function_calls:
                if response.text:
                    return response.text

                for part in response_content.parts:
                    if getattr(part, "text", None):
                        return part.text

                return "Luna is thinking... (No response generated)"

            contents.append(response_content)

            for function_call in function_calls:
                tool_name = function_call.name
                tool_input = dict(function_call.args or {})

                print(f"\n🔧 Luna is using tool: {tool_name}")
                tool_result = execute_tool(tool_name, tool_input)
                print(f"   Result: {tool_result[:100]}...")

                function_response_part = types.Part.from_function_response(
                    name=tool_name,
                    id=function_call.id,
                    response={"result": tool_result},
                )
                contents.append(types.Content(role="user", parts=[function_response_part]))
    
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
