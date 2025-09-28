import logging
import asyncio
from strands import tool

logger = logging.getLogger(__name__)

try:
    from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    logger.warning("claude-code-sdk not available. Install with: pip install claude-code-sdk")

# Define specialized system prompt for Claude Code
CLAUDE_CODE_PROMPT = """
You are an expert software engineer and cloud architect specializing in multicloud operations.
You have access to development tools for code analysis, file operations, and system commands.
Provide clear, well-documented solutions with proper error handling and best practices.
"""


async def call_claude_sdk(prompt: str) -> str:
    """Call claude-code-sdk and return the complete response"""
    if not SDK_AVAILABLE:
        return "Error: claude-code-sdk not installed. Please install with: pip install claude-code-sdk"

    try:
        logger.info(f"Calling claude-code-sdk with prompt: {prompt[:100]}...")

        # Configure claude-code-sdk options
        options = ClaudeCodeOptions(
            system_prompt=CLAUDE_CODE_PROMPT,
            mcp_servers=[
              {
                  "name": "github",
                  "url": "http://github:9001",
                  "transport": "http"
              },
            ],
            allowed_tools=["Bash", "Read", "Edit", "WebSearch", "mcp__github__*"],
            permission_mode='acceptEdits',
            max_turns=10
        )

        response_text = ""

        async with ClaudeSDKClient(options=options) as client:
            # Send the query
            await client.query(prompt)

            # Stream and collect the response
            async for message in client.receive_response():
                if hasattr(message, 'content'):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            response_text += block.text

        logger.info("Claude SDK executed successfully")
        return response_text.strip()

    except Exception as e:
        logger.error(f"Error calling claude-code-sdk: {str(e)}")
        return f"Error: {str(e)}"




@tool
def claude_code(prompt: str) -> str:
    """
    Execute complex development tasks using Claude Code SDK with full tooling capabilities.

    Args:
        prompt: A development task requiring code analysis, file operations, or system commands

    Returns:
        Complete response from Claude Code SDK execution
    """
    try:
        logger.info(f"Claude Code tool received prompt: {prompt[:100]}...")

        # Call claude-code-sdk asynchronously using the existing function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            claude_result = loop.run_until_complete(call_claude_sdk(prompt))
        finally:
            loop.close()

        logger.info("Claude Code tool executed successfully")
        return claude_result

    except Exception as e:
        logger.error(f"Error in Claude Code assistant: {str(e)}")
        return f"Error in Claude Code assistant: {str(e)}"