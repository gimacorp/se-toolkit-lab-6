# Task 2: The Documentation Agent - Implementation Plan

## Overview

Add two tools (`read_file`, `list_files`) and implement the agentic loop to enable the agent to navigate the project wiki and answer questions from documentation.

## Tool Schemas

### 1. read_file

**Purpose:** Read a file from the project repository

**Parameters:**
- `path` (string) — Relative path from project root

**Implementation:**
- Use `pathlib.Path` to read file contents
- Security check: prevent `../` path traversal
- Return file contents as string or error message

### 2. list_files

**Purpose:** List files and directories at a given path

**Parameters:**
- `path` (string) — Relative directory path from project root

**Implementation:**
- Use `pathlib.Path.iterdir()` or `os.listdir()`
- Security check: prevent accessing directories outside project
- Return newline-separated list of entries

## Agentic Loop

**Algorithm:**
1. Send user question + tool definitions to LLM
2. If LLM responds with tool_calls:
   - Execute each tool
   - Append results as tool role messages
   - Send back to LLM
   - Increment tool call counter (max 10)
3. If LLM responds with text answer:
   - Extract answer and source
   - Output JSON and exit
4. If tool calls >= 10:
   - Stop and return current answer

## System Prompt Strategy

Tell the LLM to:
1. Use `list_files` to discover wiki files
2. Use `read_file` to find the answer
3. Include source reference (file path + section anchor)
4. Maximum 10 tool calls per question

## Output Format

```json
{
  "answer": "Answer text",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "list_files", "args": {...}, "result": "..."},
    {"tool": "read_file", "args": {...}, "result": "..."}
  ]
}