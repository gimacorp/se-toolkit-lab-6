# Agent - LLM CLI

## Overview

A simple command-line agent that connects to an LLM and returns structured JSON answers.

## Architecture

User Question → agent.py → LLM API → JSON Answer

## LLM Provider

**Provider:** Qwen Code API (self-hosted on VM)  
**Model:** qwen3-coder-plus  
**Endpoint:** http://10.93.24.135:8080/v1  
**Authentication:** Bearer token from .env.agent.secret

## How to Run

1. **Ensure dependencies are installed:**
   ```bash
   uv pip install openai python-dotenv


   
## Task 2: Documentation Agent

### Tools

The agent has two tools:

1. **read_file(path)**: Read a file from the project repository
   - Parameters: `path` (relative path from project root)
   - Returns: File contents as string
   - Security: Prevents path traversal (no `../`)

2. **list_files(path)**: List files in a directory
   - Parameters: `path` (relative directory path)
   - Returns: Newline-separated list of entries
   - Security: Only lists within project directory

### Agentic Loop

The agent follows this loop:

1. Send user question + tool definitions to LLM
2. If LLM responds with tool calls:
   - Execute each tool
   - Append results as tool role messages
   - Send back to LLM
   - Repeat (max 10 tool calls)
3. If LLM responds with text answer:
   - Extract answer and source
   - Output JSON and exit

### System Prompt

The system prompt instructs the LLM to:
- Use `list_files` to discover wiki files
- Use `read_file` to find answers
- Include source references (file path + section anchor)
- Be concise and accurate

### Output Format

```json
{
  "answer": "Answer text",
  "source": "wiki/git-workflow.md#section-name",
  "tool_calls": [
    {
      "tool": "list_files",
      "args": {"path": "wiki"},
      "result": "file1.md\nfile2.md"
    },
    {
      "tool": "read_file",
      "args": {"path": "wiki/file.md"},
      "result": "File contents..."
    }
  ]
}