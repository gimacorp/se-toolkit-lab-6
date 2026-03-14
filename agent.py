
"""
Documentation Agent - Calls LLM with tools to answer questions from wiki.
Task 2: Agentic loop with read_file and list_files tools.
"""

import sys
import os
import json
import re
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


def read_file(path: str) -> str:
    """Read a file from the project repository."""
    # Security: prevent path traversal
    if ".." in path or path.startswith("/"):
        return f"Error: Access denied - path traversal not allowed"
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Build full path
    file_path = (project_root / path).resolve()
    
    # Security: ensure file is within project directory
    if not str(file_path).startswith(str(project_root.resolve())):
        return f"Error: Access denied - file outside project directory"
    
    # Read file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found - {path}"
    except Exception as e:
        return f"Error reading file: {e}"


def list_files(path: str) -> str:
    """List files and directories at a given path."""
    # Security: prevent path traversal
    if ".." in path or path.startswith("/"):
        return "Error: Access denied - path traversal not allowed"
    
    # Get project root
    project_root = Path(__file__).parent
    
    # Build full path
    dir_path = (project_root / path).resolve()
    
    # Security: ensure directory is within project
    if not str(dir_path).startswith(str(project_root.resolve())):
        return "Error: Access denied - directory outside project"
    
    # List files
    try:
        entries = []
        for entry in dir_path.iterdir():
            if entry.is_dir():
                entries.append(f"{entry.name}/")
            else:
                entries.append(entry.name)
        return "\n".join(sorted(entries))
    except FileNotFoundError:
        return f"Error: Directory not found - {path}"
    except Exception as e:
        return f"Error listing directory: {e}"


# Tool schemas for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the project repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root (e.g., 'wiki/git-workflow.md')"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root (e.g., 'wiki')"
                    }
                },
                "required": ["path"]
            }
        }
    }
]

# System prompt for the agent
SYSTEM_PROMPT = """You are a documentation agent that answers questions using the project wiki.

You have two tools:
1. list_files(path) - List files in a directory
2. read_file(path) - Read contents of a file

To answer questions:
1. Use list_files to discover what files are available in the wiki/ directory
2. Use read_file to read relevant files
3. Extract the answer and include the source reference (file path and section anchor if applicable)
4. Format: wiki/filename.md#section-name

Be concise and accurate. Always cite your source.
"""


def call_llm(messages: list, config: dict, tools: list = None) -> dict:
    """Call the LLM with messages and optional tools."""
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    
    kwargs = {
        "model": config["model"],
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message


def execute_tool(tool_name: str, args: dict) -> str:
    """Execute a tool and return result."""
    if tool_name == "read_file":
        return read_file(args.get("path", ""))
    elif tool_name == "list_files":
        return list_files(args.get("path", ""))
    else:
        return f"Error: Unknown tool - {tool_name}"


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
    
    # Initialize messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    # Track tool calls for output
    tool_calls_log = []
    max_tool_calls = 10
    tool_call_count = 0
    
    # Agentic loop
    while tool_call_count < max_tool_calls:
        # Call LLM with tools
        response = call_llm(messages, config, tools=TOOLS)
        
        # Check for tool calls
        if response.tool_calls:
            # Execute each tool call
            for tool_call in response.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                # Execute tool
                result = execute_tool(tool_name, args)
                
                # Log tool call
                tool_calls_log.append({
                    "tool": tool_name,
                    "args": args,
                    "result": result
                })
                
                # Add tool call and result to messages
                messages.append({
                    "role": "assistant",
                    "tool_calls": [tool_call]
                })
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
                
                tool_call_count += 1
        else:
            # LLM provided final answer
            final_answer = response.content
            
            # Try to extract source from the answer
            source = ""
            source_match = re.search(r'(wiki/[\w-]+\.md(?:#[\w-]+)?)', final_answer)
            if source_match:
                source = source_match.group(1)
            
            # Prepare output
            output = {
                "answer": final_answer.strip(),
                "source": source,
                "tool_calls": tool_calls_log
            }
            
            # Output JSON
            print(json.dumps(output, indent=2))
            sys.exit(0)
    
    # Max tool calls reached
    output = {
        "answer": "Maximum tool calls reached. Partial answer based on available information.",
        "source": "",
        "tool_calls": tool_calls_log
    }
    
    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()