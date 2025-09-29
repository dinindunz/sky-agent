import logging
from strands import Agent
from strands_tools import use_aws
from strands.tools.mcp.mcp_client import MCPClient
from strands.multiagent import Swarm
from mcp.client.streamable_http import streamablehttp_client
from src.tools.claude_code import claude_code
from src.tools.use_gcp import use_gcp, gcp_auth_status, gcp_set_project, gcp_project_info
from src.tools.use_azure import use_azure, azure_auth_status, azure_set_subscription, azure_subscription_info, azure_list_subscriptions, azure_set_location
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import time
import uuid

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
are involved and delegate to appropriate specialists."""
)

aws_agent = Agent(
    name="aws_agent",
    system_prompt="""You are an AWS specialist agent focused on AWS cloud operations.
Hand off tasks to other cloud specialists when they involve Azure or GCP.""",
    tools=[use_aws]
)

azure_agent = Agent(
    name="azure_agent",
    system_prompt="""You are a Microsoft Azure specialist agent focused on Azure cloud operations.
Your expertise includes Virtual Machines, AKS, Storage Accounts, Azure SQL, Function Apps, and all Azure services.
Use 'use_azure' tool with az commands (e.g., use_azure('vm list')) to manage resources.
Hand off tasks to other cloud specialists when they involve AWS or GCP.""",
    tools=[use_azure, azure_auth_status, azure_set_subscription, azure_subscription_info, azure_list_subscriptions, azure_set_location]
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
    tools=[claude_code]
)

atlassian_mcp_client = MCPClient(lambda: streamablehttp_client("http://atlassian:9000/mcp"))
atlassian_mcp_client.start()
atlassian = atlassian_mcp_client.list_tools_sync()

# Create Atlassian agent with MCP tools
atlassian_agent = Agent(
    name="atlassian_agent",
    system_prompt="""You are an Atlassian specialist agent focused on Jira and Confluence operations.
Your expertise includes managing Jira issues, projects, workflows, and Confluence pages and spaces.
Use the available MCP tools to interact with Jira and Confluence.
Hand off tasks to other specialists when they don't involve Atlassian products.""",
    tools=[atlassian]
)

# Create a swarm with these agents, starting with the multicloud coordinator
swarm = Swarm(
    [sky_agent, aws_agent, azure_agent, gcp_agent, coding_agent, atlassian_agent],
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

# OpenAI-compatible models for Open WebUI integration
class ChatMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

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

# OpenAI-compatible endpoints for Open WebUI integration
@app.get("/v1/models")
async def list_models():
    """List available models - required by Open WebUI"""
    return ModelsResponse(
        data=[
            ModelInfo(
                id="sky-agent",
                created=int(time.time()),
                owned_by="sky-agent-system"
            )
        ]
    )

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    try:
        # Extract the user's message from the chat format
        user_messages = [msg.content for msg in request.messages if msg.role == "user"]
        if not user_messages:
            return {"error": "No user message found"}

        # Use the last user message as the prompt
        prompt = user_messages[-1]

        # Call the existing agent system
        result = swarm(prompt)

        # Format the agent response for Open WebUI
        try:
            agent_response = ""
            if result.results:
                if isinstance(result.results, dict):
                    # Extract clean content from each agent's result
                    for agent_name, node_result in result.results.items():
                        try:
                            # Get the actual message content from the agent result
                            if hasattr(node_result, 'result') and hasattr(node_result.result, 'message'):
                                message = node_result.result.message
                                if isinstance(message, dict) and 'content' in message:
                                    content_blocks = message['content']
                                    if isinstance(content_blocks, list):
                                        for block in content_blocks:
                                            if isinstance(block, dict) and 'text' in block:
                                                agent_response += f"🔸 **{agent_name}**: {block['text']}\n\n"
                                    else:
                                        agent_response += f"🔸 **{agent_name}**: {str(content_blocks)}\n\n"
                                else:
                                    agent_response += f"🔸 **{agent_name}**: {str(message)}\n\n"
                            else:
                                # Fallback for unexpected structure
                                agent_response += f"🔸 **{agent_name}**: Task completed\n\n"
                        except Exception as e:
                            agent_response += f"🔸 **{agent_name}**: Task completed\n\n"
                else:
                    agent_response = str(result.results)
            else:
                agent_response = f"Task executed with status: {result.status}"

            # Add agents involved footer
            if hasattr(result, 'node_history') and result.node_history:
                agents_used = [node.node_id for node in result.node_history]
                agent_response += f"**Agents involved:** {' → '.join(agents_used)}"

            # Ensure we always have a non-empty string response
            if not agent_response or not isinstance(agent_response, str):
                agent_response = f"Task completed with status: {result.status}"

        except Exception as e:
            # Fallback in case of any errors in response processing
            agent_response = f"Task executed successfully. Status: {result.status}"

        # Ensure agent_response is definitely a string
        if not isinstance(agent_response, str):
            agent_response = str(agent_response)

        # Debug: Log the response type and content
        print(f"DEBUG: agent_response type: {type(agent_response)}")
        print(f"DEBUG: agent_response content: {agent_response[:200]}...")

        # Create OpenAI-compatible response
        response = ChatCompletionResponse(
            id=f"chatcmpl-{str(uuid.uuid4())}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=str(agent_response)  # Force string conversion
                    ),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(agent_response.split()),
                total_tokens=len(prompt.split()) + len(agent_response.split())
            )
        )

        return response

    except Exception as e:
        return ChatCompletionResponse(
            id=f"chatcmpl-{str(uuid.uuid4())}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=f"Error: {str(e)}"
                    ),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0
            )
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

def main():
    """Main entry point for the sky-agent application."""
    print("Starting a FastAPI agent server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
