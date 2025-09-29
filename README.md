# Sky Agent - Multi-Cloud AI Agent System

A multi-agent system for managing cloud infrastructure across AWS, Azure, and GCP, with integrated development workflows and project management capabilities.

## 🌟 Features

- **Multi-Cloud Operations** - Unified interface for AWS, Azure, and GCP
- **Intelligent Agent Coordination** - Specialized agents for different domains
- **Development Integration** - Claude Code SDK for advanced coding tasks
- **Project Management** - Atlassian Jira and Confluence MCP
- **GitHub Integration** - Repository operations through GitHub MCP
- **Open WebUI Interface** - User-friendly chat interface
- **CLI Interface** - Interactive CLI client
- **Docker Containerized** - Easy deployment and scaling in any cloud platform and local environments

## 🏗️ Architecture

### Agent Hierarchy

**Sky Agent (Coordinator)** - Entry point for all requests
- Analyzes tasks and identifies required cloud providers
- Delegates to appropriate specialist agents
- Coordinates multi-cloud operations

**Specialist Agents:**
- **AWS Agent** - Amazon Web Services operations
- **Azure Agent** - Microsoft Azure operations
- **GCP Agent** - Google Cloud Platform operations
- **Coding Agent** - Software development tasks (uses Claude Code SDK)
- **Atlassian Agent** - Jira and Confluence operations

### MCP Integration Layer

**Services:**
- **MCP Proxy (Port 8090)** - Aggregates and routes MCP requests
- **GitHub MCP Server** - Repository operations and code management
- **Atlassian MCP Server (Port 9000)** - Jira and Confluence integration

## 🚀 Quick Start

### 1. Setup Configuration Keys

Create a `keys/` directory with your service credentials:

```bash
mkdir keys/
```

#### GitHub Configuration (`keys/github.json`)
```json
{
  "personalAccessToken": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

#### Atlassian Configuration (`keys/atlassian.json`)
```json
{
  "atlassianApiToken": "ATATTxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "atlassianEmail": "your-email@company.com",
  "atlassianBaseUrl": "https://your-domain.atlassian.net"
}
```

#### AWS Configuration (`keys/aws.json`)
```json
{
  "accessKeyId": "AKIAXXXXXXXXXXXXXXXX",
  "secretAccessKey": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "region": "us-east-1",
  "sessionToken": "optional-session-token"
}
```

#### Azure Configuration (`keys/azure.json`)
```json
{
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

#### GCP Configuration (`keys/gcp.json`)
```json
{
  "type": "service_account",
  "project_id": "your-gcp-project-id",
  "private_key_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...xxxxxxxxxx...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@your-project.iam.gserviceaccount.com",
  "client_id": "xxxxxxxxxxxxxxxxxx",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account%40your-project.iam.gserviceaccount.com"
}
```

### 2. Environment Variables

Update `.env` file in the project root:

```bash
# AWS Configuration (Required - Agent uses Bedrock model)
AWS_PROFILE=your-aws-profile-name
```

**Important**: The agent currently uses AWS Bedrock model, so ensure your AWS profile is configured with appropriate Bedrock permissions.

### 3. Start the System

Using the provided scripts:

```bash
# Start all services
./start.sh

# Stop all services
./stop.sh
```

### 4. Invoke the Agent

#### Via Open WebUI (Web Interface)
Access http://localhost:3000 and chat naturally.

#### Via CLI (Command Line)
```bash
# Start interactive CLI client
python src/chat_client.py
```

#### Via Direct API (curl)
```bash
# Direct API call
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sky-agent",
    "messages": [
      {"role": "user", "content": "List all AWS EC2 instances"}
    ]
  }'
```

## 🐳 Docker Architecture

### Service Layers

**Application Layer:**
- **Open WebUI (Port 3000)** - User interface, chat interface, model selection
- **Sky Agent (Port 8000)** - FastAPI server, multi-agent orchestration, OpenAI-compatible API

**Integration Layer:**
- **MCP Proxy (Port 8090)** - GitHub MCP routing, service routing, SSE endpoints
- **Atlassian MCP (Port 9000)** - Jira integration, Confluence integration, project management

### Container Dependencies

1. **atlassian** - Atlassian MCP server starts first
2. **mcp-proxy** - Starts after Atlassian, aggregates MCP services
3. **sky-agent** - Main application depends on MCP proxy
4. **open-webui** - UI layer depends on sky-agent

## 🤖 Agent Specifications

### Sky Agent (Coordinator)
- **Role**: Multi-cloud task analysis and delegation
- **Capabilities**: Route tasks to specialist agents
- **Tools**: Agent coordination and handoff

### Specialists

#### AWS Agent
- **Tools**: `use_aws` (AWS CLI operations)
- **Expertise**: EC2, S3, Lambda, RDS, IAM, CloudFormation
- **Authentication**: AWS credentials required

#### Azure Agent
- **Tools**: `use_azure`, `azure_auth_status`, `azure_set_subscription`
- **Expertise**: Virtual Machines, AKS, Storage, Azure SQL, Functions
- **Authentication**: Azure CLI login required

#### GCP Agent
- **Tools**: `use_gcp`, `gcp_auth_status`, `gcp_set_project`
- **Expertise**: Compute Engine, GKE, Cloud Storage, BigQuery
- **Authentication**: gcloud authentication required

### Coding Agent
- **Tools**: `claude_code` (Claude Code SDK)
- **Capabilities**: File operations, code analysis, system commands
- **Expertise**: Multi-language development, testing, CI/CD

### Atlassian Agent
- **Tools**: Jira and Confluence MCP tools
- **Capabilities**: Issue management, project setup, content creation
- **Expertise**: Workflow automation, reporting, administration

## 📁 Project Structure

```
sky-agent/
├── src/
│   ├── prompts/           # Agent system prompts
│   │   ├── sky_agent.py   # Coordinator prompt
│   │   ├── aws_agent.py   # AWS specialist prompt
│   │   ├── azure_agent.py # Azure specialist prompt
│   │   ├── gcp_agent.py   # GCP specialist prompt
│   │   ├── coding_agent.py# Development prompt
│   │   ├── atlassian_agent.py # Atlassian prompt
│   │   └── claude_code.py # Claude Code SDK prompt
│   ├── tools/             # Agent tools and integrations
│   │   ├── claude_code.py # Claude Code SDK integration
│   │   ├── use_azure.py   # Azure CLI wrapper
│   │   └── use_gcp.py     # GCP CLI wrapper
│   ├── chat_client.py     # CLI interface for agent interaction
│   └── main.py           # FastAPI application entry point
├── mcp-servers/          # MCP server configurations
├── keys/                 # Service credentials (create manually)
├── docker-compose.yml    # Container orchestration
└── README.md            # This file
```

## 🛠️ Development

### Adding New Agents

1. Create prompt in `src/prompts/new_agent.py`
2. Import in `src/main.py`
3. Add to agent list in Swarm configuration
4. Update this README

### Custom Tools

1. Create tool function in `src/tools/`
2. Import and add to appropriate agent
3. Update agent prompt with tool documentation

### MCP Server Configuration

Located in `mcp-servers/mcp-servers.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "/root/.local/bin/mcp-proxy",
      "args": ["http://atlassian:9000/sse"]
    },
    "github": {
      "command": "/usr/local/bin/github-mcp-server",
      "args": ["stdio"]
    }
  }
}
```
