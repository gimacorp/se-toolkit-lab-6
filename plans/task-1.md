# Task 1: Call an LLM from Code - Implementation Plan

## LLM Provider and Model

**Provider:** Qwen Code API (self-hosted on VM)
**Model:** qwen3-coder-plus
**API Endpoint:** http://10.93.24.135:42005/v1
**Authentication:** Bearer token (my-secret-qwen-key from .env.agent.secret)

## Architecture

The agent will be a simple Python CLI program that:

1. **Parse input:** Read question from command-line argument (sys.argv[1])
2. **Load configuration:** Read LLM_API_KEY, LLM_API_BASE, LLM_MODEL from .env.agent.secret
3. **Call LLM:** Use OpenAI-compatible API to send the question
4. **Format output:** Return JSON with two fields:
   - `answer`: The LLM's response
   - `tool_calls`: Empty array (for Task 1)
5. **Output:** Print JSON to stdout, debug info to stderr

## Implementation Details

- Use `openai` Python library (OpenAI-compatible API)
- Use `python-dotenv` to load .env file
- Use `argparse` or `sys.argv` for CLI arguments
- Use `json` for JSON output
- Error handling: exit with code 1 on failure

## Testing

Create a test that:
- Runs agent.py as subprocess
- Parses the JSON output
- Checks that `answer` and `tool_calls` fields exist