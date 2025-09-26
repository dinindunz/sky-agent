#!/usr/bin/env python3
"""
Test script for GCP agent functionality in sky-swarm
"""

import logging
from sky_swarm import gcp_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s"
)

def test_gcp_agent():
    """Test GCP agent with various GCP-related tasks"""

    test_cases = [
        "Check my GCP authentication status",
        "List all compute instances in my project",
        "Show me all storage buckets",
        "What GKE clusters do I have?",
        "Get current project information"
    ]

    print("=" * 60)
    print("Testing GCP Agent Functionality")
    print("=" * 60)

    for i, task in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {task} ---")
        try:
            result = gcp_agent(task)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 40)

def test_gcp_tools_directly():
    """Test core GCP tools directly"""

    print("\n" + "=" * 60)
    print("Testing Core GCP Tools")
    print("=" * 60)

    # Import tools directly for testing
    from tools.use_gcp import gcp_auth_status, gcp_project_info, use_gcp

    tools_to_test = [
        ("gcp_auth_status", gcp_auth_status, []),
        ("gcp_project_info", gcp_project_info, []),
        ("use_gcp: config list", use_gcp, ["config list"]),
        ("use_gcp: compute instances", use_gcp, ["compute instances list"]),
        ("use_gcp: storage buckets", use_gcp, ["storage buckets list"])
    ]

    for tool_name, tool_func, args in tools_to_test:
        print(f"\n--- Testing {tool_name} ---")
        try:
            result = tool_func(*args) if args else tool_func()
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 40)

if __name__ == "__main__":
    print("GCP Agent Test Suite")
    print("Note: Requires gcloud CLI to be installed and authenticated")

    # Test the agent
    test_gcp_agent()

    # Test tools directly
    test_gcp_tools_directly()

    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)