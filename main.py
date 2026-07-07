import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from tools import read_server_memory, write_server_memory, get_container_status, manage_container_power

load_dotenv()

ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
local_llm = LLM(
    model="ollama/llama3.1",
    base_url=ollama_url
)

# 1. Master Agent: Operations Manager
master_agent = Agent(
    role="Server Operations Manager",
    goal="Understand user requests, look up infrastructure details from the memory file, and give clear commands to the Operator.",
    backstory="You are the analytical coordinator of the homelab network. "
              "You do not have built-in knowledge about container IDs or IP addresses. "
              "Therefore, you MUST ALWAYS read the server memory file at the start of any task "
              "to find the correct Container IDs, VMIDs, or network configurations. "
              "You also maintain this memory file when structural changes occur.",
    tools=[read_server_memory, write_server_memory],
    llm=local_llm,
    verbose=True
)

# 2. Worker Agent: Proxmox Operator
operator_agent = Agent(
    role="Proxmox Infrastructure Operator",
    goal="Execute precise Proxmox API actions based on strict orders from the Manager and report raw results.",
    backstory="You are a precise, low-level execution unit. You do not make strategic decisions or infer intent. "
              "You take direct, straight commands from the Operations Manager (e.g., 'Check status of CTID 101' "
              "or 'Reboot CTID 102') and call the corresponding Proxmox API tool. "
              "Always report the execution result accurately.",
    tools=[get_container_status, manage_container_power],
    llm=local_llm,
    verbose=True
)

def run_agent_workflow(user_prompt: str):
    manage_task = Task(
        description=f"Handle the user request: '{user_prompt}'.\n"
                    f"1. ALWAYS call 'Read Long-term Server Memory' first to understand the network layout and container list.\n"
                    f"2. Identify the target CTID/VMID from the memory content based on the user's request.\n"
                    f"3. Formulate a straight, explicit instruction for the Operator Agent.\n"
                    f"4. If any configuration changes, additions, or power actions occur, log them using 'Write Long-term Server Memory'.\n"
                    f"5. Respond to the user in Japanese.",
        expected_output="A summary of the action taken or information retrieved, written in clean Japanese.",
        agent=master_agent
    )

    crew = Crew(
        agents=[master_agent, operator_agent],
        tasks=[manage_task],
        verbose=True,
        memory=False
    )

    result = crew.kickoff()
    return result

if __name__ == "__main__":
    print("--- Proxmox AI Agent System Initialized ---")
    query = input("ユーザー指示を入力してください: ")
    response = run_agent_workflow(query)
    print("\n[エージェントからの返答]:")
    print(response)
