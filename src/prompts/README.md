# Prompts Directory

This directory contains all agent system prompts organized in structured markdown format for optimal AI performance.

## Current Structure (.py files) ✅

- **Works**: Python imports and constants work seamlessly
- **Flexible**: Can contain markdown content within Python strings
- **Import-friendly**: Clean imports like `from src.prompts.sky_agent import SKY_AGENT_PROMPT`
- **IDE support**: Syntax highlighting and code completion

## Alternative Options:

### 1. Keep as .py (Recommended)

```python
# src/prompts/sky_agent.py
SKY_AGENT_PROMPT = """# Multi-Cloud Coordinator
## Role
..."""
```

### 2. Pure .md files

```markdown
<!-- src/prompts/sky_agent.md -->
# Multi-Cloud Coordinator
## Role
...
```
Would require file reading: `open('src/prompts/sky_agent.md').read()`

### 3. Hybrid approach

- Keep .py for imports
- Reference external .md files when needed

## Recommendation: Stay with .py

The current approach is most efficient because:
- ✅ No file I/O overhead
- ✅ Clean imports
- ✅ Markdown content works fine in strings
- ✅ Better for version control and deployment
- ✅ IDE autocomplete and validation

The structured markdown content works perfectly within Python string constants!

## ✅ Structured Markdown Prompts Complete

All agent prompts have been successfully converted to **structured markdown format** within `.py` files for maximum efficiency:

### Benefits Achieved:

- 🚀 **Token Efficient** - Less verbose than JSON/YAML
- 📖 **Readable** - Clear hierarchy with headers and sections
- 🔧 **Maintainable** - Easy to edit and version control
- ⚡ **Fast Imports** - No file I/O overhead
- 🎯 **AI Optimized** - LLMs excel with markdown structure

### Available Prompts:

- **sky_agent** - Multi-cloud coordinator with delegation strategy
- **aws_agent** - AWS specialist with tools and examples
- **azure_agent** - Azure specialist with CLI usage patterns
- **gcp_agent** - GCP specialist with gcloud commands
- **coding_agent** - Development specialist with Claude Code SDK
- **atlassian_agent** - Jira/Confluence specialist with MCP tools
- **claude_code** - Enhanced engineer prompt with best practices

All agents now have consistent structure: **Role → Expertise → Tools → Examples → Delegation → Response Format**

The system is running successfully with the optimized structured markdown prompts! 🎉

## File Structure

```
src/prompts/
├── __init__.py           # Package imports
├── README.md            # This documentation
├── sky_agent.py         # Multi-cloud coordinator
├── aws_agent.py         # AWS specialist
├── azure_agent.py       # Azure specialist
├── gcp_agent.py         # GCP specialist
├── coding_agent.py      # Software development specialist
├── atlassian_agent.py   # Jira/Confluence specialist
└── claude_code.py       # Claude Code SDK prompt
```

## Usage

```python
from src.prompts import SKY_AGENT_PROMPT, AWS_AGENT_PROMPT
# or
from src.prompts.sky_agent import SKY_AGENT_PROMPT
```