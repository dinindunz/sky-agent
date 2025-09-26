import logging
from strands import Agent
from strands_tools import use_aws
from strands.multiagent import Swarm
from tools.claude_code import claude_code_assistant

# Enable debug logs and print them to stderr
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# Create specialized cloud agents
sky_agent = Agent(
    name="sky_agent",
    system_prompt="""You are a multi-cloud coordinator agent specializing in cross-cloud operations.
You coordinate tasks across AWS, Azure, and GCP. Start by analyzing which cloud providers
are involved and delegate to appropriate specialists.""",
    tools=[claude_code_assistant]
)

aws_agent = Agent(
    name="aws_agent",
    system_prompt="""You are an AWS specialist agent focused on AWS cloud operations.
Hand off tasks to other cloud specialists when they involve Azure or GCP.""",
    tools=[use_aws, claude_code_assistant]
)

azure_agent = Agent(
    name="azure_agent",
    system_prompt="""You are a Microsoft Azure specialist agent focused on Azure cloud operations.
Hand off tasks to other cloud specialists when they involve AWS or GCP.""",
    tools=[claude_code_assistant]
)

gcp_agent = Agent(
    name="gcp_agent",
    system_prompt="""You are a Google Cloud Platform specialist agent focused on GCP operations.
Hand off tasks to other cloud specialists when they involve AWS or Azure.""",
    tools=[claude_code_assistant]
)

# Create a swarm with these agents, starting with the multicloud coordinator
swarm = Swarm(
    [sky_agent, aws_agent, azure_agent, gcp_agent],
    entry_point=sky_agent,  # Start with the coordinator
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=3600.0,  # 60 minutes
    node_timeout=3600.0,       # 60 minutes per agent
    repetitive_handoff_detection_window=8,  # There must be >= 3 unique agents in the last 8 handoffs
    repetitive_handoff_min_unique_agents=3
)

# Example usage
if __name__ == "__main__":
    # Execute the swarm on a multicloud task
    result = swarm("Deploy a web application with database across AWS and Azure for high availability")

    # Access the final result
    print(f"Status: {result.status}")
    print(f"Node history: {[node.node_id for node in result.node_history]}")
    print(f"Final response: {result.final_response}")