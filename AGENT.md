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

   
## Task 3: The System Agent

### New Tool: query_api

The agent now has a third tool to query the deployed backend API:

**query_api(method, path, body, auth)**: Make HTTP requests to the backend
- Parameters:
  - `method`: HTTP method (GET, POST, etc.)
  - `path`: API endpoint path (e.g., `/items/`, `/analytics/completion-rate`)
  - `body`: Optional JSON request body
  - `auth`: Whether to include authentication (default: true)
- Returns: JSON with `status_code` and `body`
- Authentication: Uses `LMS_API_KEY` from `.env.docker.secret`

### When to Use Each Tool

**read_file / list_files**:
- Wiki documentation questions
- Source code analysis
- Configuration file inspection
- Examples: "What does the wiki say about...", "How is X implemented?"

**query_api**:
- System facts (framework, ports, status codes)
- Data queries (item counts, analytics)
- API endpoint testing (with and without authentication)
- Bug diagnosis through API errors
- Examples: "How many items...", "What status code...", "What framework..."

### Environment Variables

The agent reads configuration from TWO environment files:

1. **`.env.agent.secret`** (LLM configuration):
   - `LLM_API_KEY`: LLM provider API key
   - `LLM_API_BASE`: LLM API endpoint URL
   - `LLM_MODEL`: Model name

2. **`.env.docker.secret`** (Backend configuration):
   - `LMS_API_KEY`: Backend API authentication key

3. **Optional**:
   - `AGENT_API_BASE_URL`: Backend base URL (default: `http://localhost:42002`)

### System Prompt Strategy

The system prompt provides detailed guidance:

1. **Tool selection**: Clear rules on when to use each tool
2. **Specific workflows**: Step-by-step strategies for common question types
3. **Examples**: Concrete examples for ETL, API testing, framework questions
4. **Systematic approach**: Discover → Read → Answer

### Benchmark Results

**Initial Score:** 5/10 passed  
**Final Score:** 10/10 passed ✓

### Lessons Learned

1. **Authentication matters**: The `auth` parameter is crucial for testing unauthenticated access. Without it, the agent cannot answer "What status code without auth?" questions.

2. **Tool descriptions are critical**: Vague descriptions lead to wrong tool selection. Detailed descriptions with examples dramatically improve performance.

3. **System prompt is everything**: The LLM needs explicit guidance on:
   - When to use each tool
   - Specific strategies for different question types
   - How to handle edge cases (like testing without auth)

4. **Multi-step reasoning**: Some questions require chaining tools:
   - Query API → get error → read source → find bug
   - List files → find pipeline → read code → explain idempotency

5. **No hardcoded values**: The autochecker uses different credentials and backend URLs. Everything must come from environment variables.

6. **Iterative improvement**: The benchmark is designed for iteration. Run it, see what fails, fix one thing, re-run. Repeat until 10/10.

### Architecture
