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

# 1. Master Agent: Operations Manager
master_agent = Agent(
    role="Server Operations Manager",
    goal="Understand user requests, look up infrastructure details from the memory file, and delegate live server tasks to the Operator.",
    backstory="You are the analytical coordinator of the homelab network. "
              "CRITICAL RULE 1: You must never invent, fake, or hallucinate any server actions (like stopping an imaginary container). "
              "CRITICAL RULE 2: To get the real, actual live list of containers, you cannot just rely on your text memory; "
              "you MUST ask your coworker 'Proxmox Infrastructure Operator' to list them using their live tools.",
    tools=[read_server_memory, write_server_memory],
    llm=local_llm,
    allow_delegation=True, # オペレーターへの丸投げ（協調）を明確に許可
    verbose=True
)

# 2. Worker Agent: Proxmox Operator
operator_agent = Agent(
    role="Proxmox Infrastructure Operator",
    goal="Execute precise Proxmox API actions based on strict orders from the Manager and report raw results.",
    backstory="You are a precise, low-level execution unit. You do not make strategic decisions. "
              "You possess the live tools to check container status, power states, and list all existing containers on the actual hardware. "
              "Always report the exact tool output back to the Operations Manager.",
    tools=[get_container_status, manage_container_power, list_all_containers],
    llm=local_llm,
    verbose=True
)

def run_agent_workflow(user_prompt: str):
    # タスクの指示を厳密化（ローカルLLMのハルシネーション対策）
    manage_task = Task(
        description=f"Strictly execute the user request: '{user_prompt}' by following these precise steps:\\n"
                    f"Step 1: Run 'Read Long-term Server Memory' to understand the basic home network layout.\\n"
                    f"Step 2: If the user wants a live list or status, DELEGATE the job to 'Proxmox Infrastructure Operator'. Do NOT guess the live status.\\n"
                    f"Step 3: Only if a REAL action or change was executed by the Operator, log that specific factual event using 'Write Long-term Server Memory'. If no container was actually changed, NEVER write fake operational logs.\\n"
                    f"Step 4: Answer the user in clean Japanese based ONLY on real tool execution facts.",
        expected_output="A factual operational report delivered in clean Japanese. No fake data allowed.",
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
    print("\\n[エージェントからの返答]:")
    print(response)
