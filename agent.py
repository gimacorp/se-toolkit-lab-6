#!/usr/bin/env python3
"""
Agent CLI - Calls LLM and returns structured JSON answer.
Task 1: Basic LLM integration without tools.
"""

import sys
import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv


def load_config():
    """Load configuration from .env.agent.secret"""
    env_path = Path(__file__).parent / ".env.agent.secret"
    load_dotenv(env_path)
    
    return {
        "api_key": os.getenv("LLM_API_KEY"),
        "base_url": os.getenv("LLM_API_BASE"),
        "model": os.getenv("LLM_MODEL", "qwen3-coder-plus")
    }


def call_llm(question: str, config: dict) -> str:
    """
    Call the LLM with the user's question.
    
    Args:
        question: User's question
        config: LLM configuration (api_key, base_url, model)
    
    Returns:
        LLM's answer as string
    """
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    
    response = client.chat.completions.create(
        model=config["model"],
        messages=[
            {
                "role": "system", 
                "content": "You are a helpful assistant. Answer questions concisely and accurately."
            },
            {
                "role": "user", 
                "content": question
            }
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content


def main():
    """Main entry point for the agent CLI."""
    # Check command-line arguments
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"<question>\"", file=sys.stderr)
        sys.exit(1)
    
    question = sys.argv[1]
    
    # Load configuration
    config = load_config()
    
    # Validate configuration
    if not config["api_key"]:
        print("Error: LLM_API_KEY not found in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    
    if not config["base_url"]:
        print("Error: LLM_API_BASE not found in .env.agent.secret", file=sys.stderr)
        sys.exit(1)
    
    # Call LLM
    try:
        answer = call_llm(question, config)
    except Exception as e:
        print(f"Error calling LLM: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Prepare output
    output = {
        "answer": answer,
        "tool_calls": []
    }
    
    # Output JSON to stdout
    print(json.dumps(output))
    
    # Exit successfully
    sys.exit(0)


if __name__ == "__main__":
    main()