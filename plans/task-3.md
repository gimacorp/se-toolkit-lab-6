# Task 3: The System Agent - Implementation Plan

## Overview

Added `query_api` tool to enable the agent to query the deployed backend API and answer system questions about framework, ports, status codes, and data-dependent queries.

## New Tool: query_api

**Purpose:** Make HTTP requests to the deployed backend API

**Parameters:**
- `method` (string): HTTP method (GET, POST, etc.)
- `path` (string): API endpoint path (e.g., `/items/`, `/analytics/completion-rate`)
- `body` (string, optional): JSON request body for POST/PUT requests
- `auth` (boolean, optional): Whether to include authentication header (default: true)

**Implementation:**
- Use `requests` library to make HTTP calls
- Authenticate with `LMS_API_KEY` from `.env.docker.secret`
- Return JSON with `status_code` and `body`
- Base URL from `AGENT_API_BASE_URL` (default: `http://localhost:42002`)
- Support `auth=false` for testing unauthenticated endpoints

## Environment Variables

The agent must read ALL configuration from environment variables:

1. **From `.env.agent.secret`:**
   - `LLM_API_KEY` - LLM provider API key
   - `LLM_API_BASE` - LLM API endpoint URL
   - `LLM_MODEL` - Model name

2. **From `.env.docker.secret`:**
   - `LMS_API_KEY` - Backend API key for authentication

3. **Optional:**
   - `AGENT_API_BASE_URL` - Backend base URL (default: `http://localhost:42002`)

## System Prompt Update

Updated the system prompt to guide the LLM on when to use each tool:

- **`read_file` / `list_files`**: For wiki documentation and source code questions
- **`query_api`**: For system facts (framework, ports, status codes) and data queries (item count, analytics)
- **`query_api` with `auth=false`**: For testing unauthenticated endpoints (401/403 status codes)

## Benchmark Strategy

The benchmark has 10 questions across 4 categories:

1. **Wiki lookup** (questions 0-1): Use `read_file` for wiki documentation
2. **System facts** (questions 2-3): Use `read_file` for source code or `list_files` for structure
3. **Data queries** (questions 4-5): Use `query_api` for database counts and status codes
4. **Bug diagnosis** (questions 6-7): Use `query_api` + `read_file` combination
5. **Reasoning** (questions 8-9): Multi-step with `read_file` for architecture understanding

## Iteration Strategy

1. Run `uv run run_eval.py` to get initial score
2. For each failing question:
   - Check which tool was called (or not called)
   - Improve tool descriptions in schema
   - Adjust system prompt for better tool selection
   - Fix bugs in tool implementation
3. Re-run until all 10 questions pass
4. Document lessons learned in AGENT.md

## Benchmark Results

**Initial Score:** 5/10 passed  
**Final Score:** 10/10 passed ✓

## Lessons Learned

1. **Auth parameter is crucial**: For "without auth" questions, the agent must set `auth=false`
2. **Tool descriptions matter**: Detailed descriptions help LLM choose the right tool
3. **System prompt strategy**: Specific examples and workflows improve tool selection
4. **ETL discovery**: Agent needs to systematically explore `src/` directory for pipeline files
5. **No hardcoded values**: Everything must come from environment variables for autochecker

## Testing

Add 2 regression tests:
1. "What framework does the backend use?" → expects `read_file`, answer contains "FastAPI"
2. "How many items are in the database?" → expects `query_api`, answer contains a number