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
    # 【タスク1】必要な情報をProxmoxから集めてくるタスク（目的だけを伝える）
    fetch_task = Task(
        description=f"The user request is: '{user_prompt}'\n"
                    f"Retrieve the current real-time status or list of all containers and VMs from the Proxmox cluster.",
        expected_output="A detailed and factual list of all containers, VMs, and their states retrieved from the cluster.",
        agent=luna_agent
    )

    # 【タスク2】集めたデータを元に、保存処理とユーザーへの返答を行うタスク（ツール名は出さない）
    save_and_respond_task = Task(
        description=f"The user request is: '{user_prompt}'\n"
                    f"Based on the fetched data from the previous task, save the container list into the long-term server memory file because the user explicitly requested to save or note it down.\n"
                    f"After successfully saving the data, provide a summary of the container list and confirm that it has been saved to the user in natural, friendly Japanese.",
        expected_output="A final response to the user in clean Japanese, listing the containers and confirming the successful save operation.",
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
