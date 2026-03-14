
"""
<<<<<<< HEAD
<<<<<<< HEAD
System Agent - Calls LLM with tools to answer questions from wiki, source code, and backend API.
Task 3: Agentic loop with read_file, list_files, and query_api tools.
=======
Documentation Agent - Calls LLM with tools to answer questions from wiki.
Task 2: Agentic loop with read_file and list_files tools.
>>>>>>> main
=======
System Agent - Calls LLM with tools to answer questions from wiki, source code, and backend API.
Task 3: Agentic loop with read_file, list_files, and query_api tools.
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
"""

import sys
import os
import json
import re
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv


def load_config():
    """Load configuration from environment files"""
    # Load LLM config from .env.agent.secret
    agent_env = Path(__file__).parent / ".env.agent.secret"
    load_dotenv(agent_env)
    
    # Load backend config from .env.docker.secret
    docker_env = Path(__file__).parent / ".env.docker.secret"
    load_dotenv(docker_env, override=False)
    
    return {
        "llm_api_key": os.getenv("LLM_API_KEY"),
        "llm_api_base": os.getenv("LLM_API_BASE"),
        "llm_model": os.getenv("LLM_MODEL", "qwen3-coder-plus"),
        "lms_api_key": os.getenv("LMS_API_KEY"),
        "agent_api_base_url": os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")
    }


def read_file(path: str) -> str:
    """Read a file from the project repository."""
    # Security: prevent path traversal
    if ".." in path or path.startswith("/"):
        return f"Error: Access denied - path traversal not allowed"
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
    
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
    """
    Query the deployed backend API.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path
        body: Optional JSON request body
        auth: Whether to include authentication (default: True)
    """
    import requests
    
    base_url = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")
    lms_api_key = os.getenv("LMS_API_KEY")
    url = f"{base_url}{path}"
    
    # Prepare headers
    headers = {"Content-Type": "application/json"}
    
    # Only add auth if requested
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


# Tool schemas for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": """Read a file from the project repository. 
            Use for wiki documentation, source code, and configuration files.
            Examples: 'wiki/git-workflow.md', 'main.py', 'docker-compose.yml', 'src/pipeline.py'""",
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
            "description": """List files and directories at a given path. 
            Use to discover project structure before reading files.
            Common paths: '.', 'src', 'wiki', 'backend', 'app', 'src/etl'""",
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
            "description": """Query the deployed backend API for system information, data counts, or analytics.
            Use for questions about the RUNNING system, not documentation.
            For testing unauthenticated access, set auth=false.
            Examples: GET /items/, GET /analytics/completion-rate, GET /health""",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "description": "HTTP method: GET, POST"
                    },
                    "path": {
                        "type": "string",
                        "description": "API endpoint path (e.g., '/items/', '/analytics/completion-rate')"
                    },
                    "body": {
                        "type": "string",
                        "description": "Optional JSON request body for POST requests"
                    },
                    "auth": {
                        "type": "boolean",
                        "description": "Include authentication header (default: true). Set to false to test unauthenticated access."
                    }
                },
                "required": ["method", "path"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a system agent that answers questions using documentation, source code, and the deployed backend API.

You have THREE tools:

1. **list_files(path)** - List files in a directory
   - Use to discover project structure
   - Common paths: '.', 'src', 'wiki', 'backend', 'app'

2. **read_file(path)** - Read a file from the repository
   - Use for wiki documentation, source code, config files
   - Examples: 'wiki/git-workflow.md', 'main.py', 'docker-compose.yml'

3. **query_api(method, path, body, auth)** - Query the deployed backend API
   - Use for SYSTEM FACTS and DATA QUERIES about the RUNNING system
   - Set auth=false to test unauthenticated requests (for 401/403 status codes)
   - Examples: GET /items/, GET /analytics/completion-rate

## When to use each tool:

**Use read_file/list_files when:**
- Question asks about documentation or wiki
- Question asks about source code or implementation
- Question mentions specific files (docker-compose.yml, Dockerfile, pipeline.py)
- Examples: "What does the wiki say about...", "How is X implemented?", "Read the ETL pipeline"

**Use query_api when:**
- Question asks about the RUNNING system
- Question asks for counts, statistics, or current data
- Question asks about HTTP status codes or API responses
- Question asks what framework/port the system uses
- For "without auth" questions: use auth=false
- Examples: "How many items...", "What status code...", "What framework..."

## Strategy for specific questions:

**ETL/Idempotency questions:**
1. list_files("src") or list_files(".") to find pipeline files
2. Look for: pipeline.py, etl.py, ingest.py, or etl/ directory
3. read_file to examine the code
4. Look for: external_id, duplicate, skip

**API without auth questions:**
- Use query_api with auth=false
- Example: query_api("GET", "/items/", auth=false)

**Framework questions:**
- read_file("main.py") or read_file("requirements.txt") or list_files("src")
- Look for: FastAPI, Flask, Django

Be systematic: discover → read → answer. Maximum 10 tool calls.
Always cite your source (file path or API endpoint).
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
    
<<<<<<< HEAD
=======
    
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
    
>>>>>>> main
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
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
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
    elif tool_name == "query_api":
        return query_api(
            args.get("method", "GET"),
            args.get("path", ""),
            args.get("body"),
            args.get("auth", True)
        )
<<<<<<< HEAD
=======
>>>>>>> main
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
    else:
        return f"Error: Unknown tool - {tool_name}"


def main():
    """Main entry point for the agent CLI."""
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"<question>\"", file=sys.stderr)
        sys.exit(1)
    
    question = sys.argv[1]
    config = load_config()
    
    if not config["llm_api_key"]:
        print("Error: LLM_API_KEY not found", file=sys.stderr)
        sys.exit(1)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
    tool_calls_log = []
    max_tool_calls = 10
    tool_call_count = 0
    
    while tool_call_count < max_tool_calls:
        response = call_llm(messages, config, tools=TOOLS)
        
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                result = execute_tool(tool_name, args)
                
<<<<<<< HEAD
=======
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
>>>>>>> main
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
                tool_calls_log.append({
                    "tool": tool_name,
                    "args": args,
                    "result": result
                })
                
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
                messages.append({"role": "assistant", "tool_calls": [tool_call]})
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
                
                tool_call_count += 1
        else:
<<<<<<< HEAD
=======
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
>>>>>>> main
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
            final_answer = response.content
            
            # Try to extract source from the answer
            source = ""
            source_match = re.search(r'(wiki/[\w-]+\.md(?:#[\w-]+)?)', final_answer)
            if source_match:
                source = source_match.group(1)
            
<<<<<<< HEAD
<<<<<<< HEAD
=======
            # Prepare output
>>>>>>> main
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
            output = {
                "answer": final_answer.strip(),
                "source": source,
                "tool_calls": tool_calls_log
            }
<<<<<<< HEAD
<<<<<<< HEAD
=======
            
            # Output JSON
>>>>>>> main
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
            print(json.dumps(output, indent=2))
            sys.exit(0)
    
    # Max tool calls reached
    output = {
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
        "answer": "Maximum tool calls reached.",
        "source": "",
        "tool_calls": tool_calls_log
    }
<<<<<<< HEAD
=======
        "answer": "Maximum tool calls reached. Partial answer based on available information.",
        "source": "",
        "tool_calls": tool_calls_log
    }
    
>>>>>>> main
=======
>>>>>>> 63b4827945f0cf63803ab2436e30beeeead2a7f9
    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()