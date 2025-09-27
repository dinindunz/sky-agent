#!/usr/bin/env python3
"""
Continuous Chat Interface for BedrockAgentCore Agent

This script provides a command-line chat interface to interact with the
BedrockAgentCore agent running on localhost:8000.
"""

import requests
import json
import sys
from typing import Dict, Any

class AgentChatClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def check_health(self) -> bool:
        """Check if the agent is running and healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def send_message(self, prompt: str) -> Dict[str, Any]:
        """Send a message to the agent and return the response."""
        try:
            payload = {"prompt": prompt}
            response = self.session.post(
                f"{self.base_url}/invoke",
                json=payload,
                timeout=3000
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {str(e)}"}
    
    def format_response(self, response: Dict[str, Any]) -> str:
        """Format the agent's response for display."""
        if "error" in response:
            return f"❌ Error: {response['error']}"

        # Handle the new response format from sky-agent
        if "status" in response:
            status = response["status"]
            if status == "Status.FAILED":
                return f"❌ Agent failed to process request. Status: {status}"

            if "results" in response and response["results"]:
                # Extract results from the sky-agent response
                results = response["results"]
                if isinstance(results, dict):
                    formatted_responses = []

                    # Process each agent's response
                    for agent_name, agent_result in results.items():
                        if "result" in agent_result:
                            result = agent_result["result"]

                            # Extract the message content
                            message_text = self._extract_message_text(result)
                            if message_text:
                                # Add agent name if multiple agents responded
                                if len(results) > 1:
                                    formatted_responses.append(f"🔸 **{agent_name}**: {message_text}")
                                else:
                                    formatted_responses.append(message_text)

                    if formatted_responses:
                        return "\n".join(formatted_responses)

                return f"✅ Status: {status}\n📊 Results: {response['results']}"

        # Handle legacy format
        if "result" in response:
            result = response["result"]
            message_text = self._extract_message_text(result)
            if message_text:
                return message_text

        return f"❓ Unexpected response format: {response}"

    def _extract_message_text(self, result: Any) -> str:
        """Extract clean text from various result formats."""
        if isinstance(result, str):
            return result

        if isinstance(result, dict):
            # Try to get message content from different possible structures
            if "message" in result and isinstance(result["message"], dict):
                message = result["message"]
                if "content" in message and isinstance(message["content"], list):
                    # Extract text from content array
                    text_parts = []
                    for content_item in message["content"]:
                        if isinstance(content_item, dict) and "text" in content_item:
                            text_parts.append(content_item["text"])
                    return " ".join(text_parts) if text_parts else ""

            # Direct content access
            if "content" in result and isinstance(result["content"], list):
                text_parts = []
                for content_item in result["content"]:
                    if isinstance(content_item, dict) and "text" in content_item:
                        text_parts.append(content_item["text"])
                return " ".join(text_parts) if text_parts else ""

            # Simple text field
            if "text" in result:
                return result["text"]

        return ""
    
    def run_chat(self):
        """Run the continuous chat interface."""
        print("🤖 BedrockAgentCore Agent Chat Interface")
        print("=" * 50)
        
        # Check if agent is running
        print("🔍 Checking agent health...")
        if not self.check_health():
            print("❌ Agent is not running or not healthy!")
            print("   Please start the agent with: python sky_agent.py")
            sys.exit(1)
        
        print("✅ Agent is running and healthy!")
        print("\n💡 Tips:")
        print("   - Type your message and press Enter")
        print("   - Type 'quit', 'exit', or 'bye' to end the chat")
        print("   - Type 'help' for assistance")
        print("   - Press Ctrl+C to force quit")
        print("\n" + "=" * 50)
        
        try:
            while True:
                # Get user input
                try:
                    user_input = input("\n🧑 You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n\n👋 Goodbye!")
                    break
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if not user_input:
                    print("💭 Please enter a message or type 'help' for assistance.")
                    continue
                
                # Send message to agent
                print("🤖 Agent: ", end="", flush=True)
                response = self.send_message(user_input)
                formatted_response = self.format_response(response)
                print(formatted_response)
        
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
    
    def show_help(self):
        """Show help information."""
        print("\n📚 Help - Available Commands:")
        print("   help     - Show this help message")
        print("   quit     - Exit the chat")
        print("   exit     - Exit the chat")
        print("   bye      - Exit the chat")
        print("\n💡 Example questions you can ask:")
        print("   - What are Docker best practices?")
        print("   - How do I design a microservices architecture?")
        print("   - Explain the difference between REST and GraphQL")
        print("   - What are the benefits of cloud computing?")
        print("   - How do I implement CI/CD pipelines?")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Continuous chat interface for BedrockAgentCore Agent"
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="Base URL of the agent (default: http://127.0.0.1:8000)"
    )
    
    args = parser.parse_args()
    
    client = AgentChatClient(args.url)
    client.run_chat()

if __name__ == "__main__":
    main()
