import logging
from strands import Agent
from strands_tools import use_aws
from strands.multiagent import Swarm
from src.tools.claude_code import claude_code_assistant
from src.tools.use_gcp import use_gcp, gcp_auth_status, gcp_set_project, gcp_project_info
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

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
Your expertise includes Compute Engine, GKE, Cloud Storage, Cloud SQL, BigQuery, Cloud Functions, and all GCP services.
Use 'use_gcp' tool with gcloud commands (e.g., use_gcp('compute instances list')) to manage resources.
Hand off tasks to other cloud specialists when they involve AWS or Azure.""",
    tools=[use_gcp, gcp_auth_status, gcp_set_project, gcp_project_info]
)

coding_agent = Agent(
    name="coding_agent",
    system_prompt="""You are a specialized coding agent focused on software development and code analysis.
Your expertise includes code generation, debugging, refactoring, testing, and development workflows.
Use Claude Code SDK for complex development tasks requiring file operations, code analysis, or system commands.
Hand off cloud-specific tasks to appropriate cloud specialists (AWS, Azure, GCP).""",
    tools=[claude_code_assistant]
)

# Create a swarm with these agents, starting with the multicloud coordinator
swarm = Swarm(
    [sky_agent, aws_agent, azure_agent, gcp_agent, coding_agent],
    entry_point=sky_agent,  # Start with the coordinator
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=3600.0,  # 60 minutes
    node_timeout=3600.0,       # 60 minutes per agent
    repetitive_handoff_detection_window=8,  # There must be >= 3 unique agents in the last 8 handoffs
    repetitive_handoff_min_unique_agents=3
)

app = FastAPI()

class InvokeRequest(BaseModel):
    prompt: str

@app.post("/invoke")
async def invoke_agent(request: InvokeRequest):
    """Invoke the agent with a prompt"""
    try:
        # Execute the sky-agent swarm with the given prompt
        result = swarm(request.prompt)

        # Access the final result
        # print(f"Status: {result.status}")
        # print(f"Node history: {[node.node_id for node in result.node_history]}")
        # print(f"Final response: {result.final_response}")

        response_data = {
            "status": str(result.status),
            "node_history": [node.node_id for node in result.node_history],
            "results": result.results if result.results else "No results available"
        }

        return response_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

def main():
    """Main entry point for the sky-agent application."""
    print("Starting a FastAPI agent server on port 8080...")
    uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
