import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from tools import read_server_memory, write_server_memory, get_container_status, manage_container_power, list_all_containers

load_dotenv()

ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
local_llm = LLM(
    model="ollama/llama3.1",
    base_url=ollama_url
)

# エージェントを1人に統合して賢く立ち回らせる
luna_agent = Agent(
    role="Homelab Server Assistant",
    goal="Manage Proxmox containers and maintain server knowledge efficiently based on user requests.",
    backstory="You are Luna-chan, the dedicated AI assistant for the homelab server. "
              "You can directly read/write the memory file and control the Proxmox server using your tools. "
              "Always use your tools to get real data before answering, and never invent fake logs or answers.",
    tools=[read_server_memory, write_server_memory, get_container_status, manage_container_power, list_all_containers],
    llm=local_llm,
    verbose=True
)

def run_agent_workflow(user_prompt: str):
    server_task = Task(
        # ここの指示文（特に3番）を「絶対実行」に強化！
        description=f"Execute the user request: '{user_prompt}'\\n"
                    f"1. Check the server layout using 'Read Long-term Server Memory' if needed.\\n"
                    f"2. To get a live list or status, use 'List All Proxmox Containers' or 'Get Proxmox Container Status'.\\n"
                    f"3. CRITICAL: If the user explicitly asks to 'save', 'memorize', or 'keep a note' (e.g., '保存して', 'メモに保存して'), you MUST use 'Write Long-term Server Memory' to save the fetched information into the file. Do not skip this step under any circumstances.\\n"
                    f"4. Reply to the user in clean Japanese.",
        expected_output="A factual response in Japanese based on the actual tool results.",
        agent=luna_agent
    )

    crew = Crew(
        agents=[luna_agent],
        tasks=[server_task],
        verbose=True,
        memory=False
    )

    result = crew.kickoff()
    return result

if __name__ == "__main__":
    print("--- Proxmox AI Agent System Initialized ---")
    query = input("ユーザー指示を入力してください: ")
    response = run_agent_workflow(query)
    print("\\n[エージェントからの返答]:")
    print(response)
