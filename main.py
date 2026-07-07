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
    # 【タスク1】必要な情報をProxmoxから集めてくるタスク
    fetch_task = Task(
        description=f"Analyze the user request: '{user_prompt}'\\n"
                    f"Fetch the necessary data from the Proxmox cluster using 'List All Proxmox Containers' or 'Get Proxmox Container Status'. "
                    f"If the request is only about reading the memory, use 'Read Long-term Server Memory'.",
        expected_output="The detailed live server or container information retrieved from the tools.",
        agent=luna_agent
    )

    # 【タスク2】集めたデータを元に、保存処理とユーザーへの返答を行うタスク
    save_and_respond_task = Task(
        description=f"Review the user request: '{user_prompt}' and the data fetched in the previous task.\\n"
                    f"CRITICAL: If the user explicitly asked to save or note down the info (e.g., '保存して', 'メモに保存して'), you MUST call 'Write Long-term Server Memory' to write the fetched data into the file. Do not just say you saved it; actually executing the tool is mandatory.\\n"
                    f"Finally, reply to the user in clean Japanese.",
        expected_output="A final response to the user in Japanese, confirming that the data has been successfully written to the memory file if requested.",
        agent=luna_agent
    )

    # crewに2つのタスクを順番に実行させる
    crew = Crew(
        agents=[luna_agent],
        tasks=[fetch_task, save_and_respond_task],
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
