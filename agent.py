#!/usr/bin/env python3
"""System Agent - Calls LLM with tools to answer questions from wiki, source code, and backend API.
Task 3: Agentic loop with read_file, list_files, and query_api tools.
"""

import sys
import os
import json
import re
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv


def load_config():
    """Load configuration from environment variables (NOT from files)."""
    
    config = {
        "llm_api_key": os.getenv("LLM_API_KEY", ""),
        "llm_api_base": os.getenv("LLM_API_BASE", ""),
        "llm_model": os.getenv("LLM_MODEL", "qwen3-coder-plus"),
        "lms_api_key": os.getenv("LMS_API_KEY", ""),
        "agent_api_base_url": os.getenv("AGENT_API_BASE_URL", "http://localhost:10000")
    }
    
    import sys
    print(f"DEBUG: Loaded config: AGENT_API_BASE_URL={config['agent_api_base_url']}", file=sys.stderr)
    
    return config


def read_file(path: str) -> str:
    """Read a file from the project repository."""
    if ".." in path or path.startswith("/"):
        return f"Error: Access denied - path traversal not allowed"
    
    project_root = Path(__file__).parent
    file_path = (project_root / path).resolve()
    
    if not str(file_path).startswith(str(project_root.resolve())):
        return f"Error: Access denied - file outside project directory"
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found - {path}"
    except Exception as e:
        return f"Error reading file: {e}"


def list_files(path: str) -> str:
    """List files and directories at a given path."""
    if ".." in path or path.startswith("/"):
        return "Error: Access denied - path traversal not allowed"
    
    project_root = Path(__file__).parent
    dir_path = (project_root / path).resolve()
    
    if not str(dir_path).startswith(str(project_root.resolve())):
        return "Error: Access denied - directory outside project"
    
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


def query_api(method: str, path: str, body: str = None, auth: bool = True) -> str:
    """Query the deployed backend API."""
    import requests

    # Use AGENT_API_BASE_URL if set, otherwise construct from APP_HOST_PORT
    agent_api_base = os.getenv("AGENT_API_BASE_URL")
    if agent_api_base:
        base_url = agent_api_base
    else:
        # Fall back to APP_HOST_PORT from .env.docker.secret
        host_port = os.getenv("APP_HOST_PORT", "8888")
        base_url = f"http://localhost:{host_port}"

    lms_api_key = os.getenv("LMS_API_KEY")
    url = f"{base_url}{path}"
    
    headers = {"Content-Type": "application/json"}
    
    if auth and lms_api_key:
        headers["Authorization"] = f"Bearer {lms_api_key}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json.loads(body) if body else {}, timeout=10)
        else:
            return json.dumps({"status_code": 0, "body": f"Error: Unsupported method - {method}"})
        
        return json.dumps({
            "status_code": response.status_code,
            "body": response.text
        })
    except Exception as e:
        return json.dumps({"status_code": 0, "body": f"Error: {str(e)}"})


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the project repository. Use for wiki documentation, source code, config files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root (e.g., 'wiki/git-workflow.md', 'main.py')"
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
            "description": "List files and directories at a given path. Use to discover project structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root (e.g., 'wiki', 'src')"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_api",
            "description": "Query the deployed backend API for system information, data counts, or analytics. Set auth=false to test unauthenticated access.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {"type": "string", "description": "HTTP method: GET, POST"},
                    "path": {"type": "string", "description": "API endpoint path (e.g., '/items/', '/analytics/completion-rate')"},
                    "body": {"type": "string", "description": "Optional JSON request body for POST requests"},
                    "auth": {"type": "boolean", "description": "Include authentication header (default: true). Set to false to test unauthenticated access."}
                },
                "required": ["method", "path"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a system agent that answers questions using documentation, source code, and the deployed backend API.

You have THREE tools:
1. list_files(path) - List files in a directory
2. read_file(path) - Read a file from the repository  
3. query_api(method, path, body, auth) - Query the deployed backend API

## Be efficient! For crash/bug questions:
1. Call the endpoint once
2. Read the relevant source file once
3. Identify the specific error (TypeError, None, sorted, etc.)
4. Answer immediately - don't explore other files

## When to use each tool:
**Use read_file/list_files when:** Question asks about documentation, source code, or specific files.
**Use query_api when:** Question asks about the RUNNING system, counts, statistics, HTTP status codes.

## Strategy for specific questions:
**API router questions:** Use list_files("backend/app/routers") ONCE, answer immediately.
**ETL/Idempotency:** Find pipeline files, look for: external_id, duplicate, skip.
**API without auth:** Use query_api with auth=false.
**Framework questions:** Read main.py or settings.py, look for: FastAPI, Flask, Django.

Be systematic but efficient. Maximum 10 tool calls. Always cite your source.
"""


def call_llm(messages: list, config: dict, tools: list = None) -> dict:
    """Call the LLM with messages and optional tools."""
    client = OpenAI(
        api_key=config["llm_api_key"],
        base_url=config["llm_api_base"]
    )
    
    kwargs = {
        "model": config["llm_model"],
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
    elif tool_name == "query_api":
        return query_api(
            args.get("method", "GET"),
            args.get("path", ""),
            args.get("body"),
            args.get("auth", True)
        )
    else:
        return f"Error: Unknown tool - {tool_name}"


def main():
    """Main entry point for the agent CLI."""
    if len(sys.argv) < 2:
        print(json.dumps({"answer": "Error: No question provided", "source": "", "tool_calls": []}))
        print("Usage: uv run agent.py \"<question>\"", file=sys.stderr)
        sys.exit(0)

    question = sys.argv[1]
    config = load_config()

    if not config["llm_api_key"]:
        output = {"answer": "Error: LLM_API_KEY not found in .env.agent.secret", "source": "", "tool_calls": []}
        print(json.dumps(output))
        print("Error: LLM_API_KEY not found", file=sys.stderr)
        sys.exit(0)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]

    tool_calls_log = []
    max_tool_calls = 10
    tool_call_count = 0

    try:
        while tool_call_count < max_tool_calls:
            try:
                response = call_llm(messages, config, tools=TOOLS)
            except Exception as e:
                # LLM API call failed - return valid JSON error response
                output = {
                    "answer": f"Error: Failed to call LLM API - {str(e)}",
                    "source": "",
                    "tool_calls": tool_calls_log
                }
                print(json.dumps(output))
# REMOVED: print(f"LLM API error: {e}", file=sys.stderr)
                sys.exit(0)

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    result = execute_tool(tool_name, args)

                    tool_calls_log.append({
                        "tool": tool_name,
                        "args": args,
                        "result": result
                    })

                    messages.append({"role": "assistant", "tool_calls": [tool_call]})
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

                    tool_call_count += 1
            else:
                final_answer = response.content

                source = ""
                source_match = re.search(r'(wiki/[\w-]+\.md(?:#[\w-]+)?)', final_answer)
                if source_match:
                    source = source_match.group(1)

                output = {
                    "answer": final_answer.strip(),
                    "source": source,
                    "tool_calls": tool_calls_log
                }
                print(json.dumps(output, indent=2))
                sys.exit(0)

        output = {
            "answer": "Maximum tool calls reached.",
            "source": "",
            "tool_calls": tool_calls_log
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)
    except Exception as e:
        # Catch any unexpected errors and return valid JSON
        output = {
            "answer": f"Error: Unexpected error - {str(e)}",
            "source": "",
            "tool_calls": tool_calls_log
        }
        print(json.dumps(output))
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
