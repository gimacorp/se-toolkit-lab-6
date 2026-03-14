#!/usr/bin/env python3
"""
Benchmark evaluation script for Task 3.
Runs the agent against 10 benchmark questions and checks answers.
"""

import subprocess
import json
import sys
import re


# Benchmark questions with expected keywords and required tools
BENCHMARK_QUESTIONS = [
    {
        "question": "According to the project wiki, what steps are needed to protect a branch on GitHub?",
        "expected_keywords": ["branch", "protect"],
        "required_tools": ["read_file"]
    },
    {
        "question": "What does the project wiki say about connecting to your VM via SSH? Summarize the key steps.",
        "expected_keywords": ["ssh", "key", "connect"],
        "required_tools": ["read_file"]
    },
    {
        "question": "What Python web framework does this project's backend use? Read the source code to find out.",
        "expected_keywords": ["FastAPI"],
        "required_tools": ["read_file"]
    },
    {
        "question": "List all API router modules in the backend. What domain does each one handle?",
        "expected_keywords": ["items", "interactions", "analytics", "pipeline"],
        "required_tools": ["list_files"]
    },
    {
        "question": "How many items are currently stored in the database? Query the running API to find out.",
        "expected_keywords": ["number"],  # Any number > 0
        "required_tools": ["query_api"]
    },
    {
        "question": "What HTTP status code does the API return when you request /items/ without an authentication header?",
        "expected_keywords": ["401", "403"],
        "required_tools": ["query_api"]
    },
    {
        "question": "Query the /analytics/completion-rate endpoint for lab-99. What error do you get, and what is the bug in the source code?",
        "expected_keywords": ["ZeroDivisionError", "division", "zero"],
        "required_tools": ["query_api", "read_file"]
    },
    {
        "question": "The /analytics/top-learners endpoint crashes for some labs. Query it, find the error, and read the source code to explain what went wrong.",
        "expected_keywords": ["TypeError", "None", "NoneType", "sorted"],
        "required_tools": ["query_api", "read_file"]
    },
    {
        "question": "Read docker-compose.yml and the backend Dockerfile. Explain the full journey of an HTTP request from the browser to the database and back.",
        "expected_keywords": ["Caddy", "FastAPI", "auth", "router", "ORM", "PostgreSQL"],
        "required_tools": ["read_file"]
    },
    {
        "question": "Read the ETL pipeline code. Explain how it ensures idempotency — what happens if the same data is loaded twice?",
        "expected_keywords": ["external_id", "duplicate", "skip"],
        "required_tools": ["read_file"]
    }
]


def run_agent(question: str) -> dict:
    """Run the agent with a question and return the output."""
    result = subprocess.run(
        ["uv", "run", "agent.py", question],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0:
        print(f"Error: Agent exited with code {result.returncode}")
        print(f"Stderr: {result.stderr}")
        return None
    
    try:
        output = json.loads(result.stdout)
        return output
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON output: {e}")
        print(f"Stdout: {result.stdout}")
        return None


def check_keywords(answer: str, expected_keywords: list) -> bool:
    """Check if answer contains at least one expected keyword."""
    if not answer:
        return False
    
    answer_lower = answer.lower()
    for keyword in expected_keywords:
        if keyword.lower() in answer_lower:
            return True
    
    # Special case for numbers
    if "number" in [k.lower() for k in expected_keywords]:
        # Check if answer contains a number > 0
        numbers = re.findall(r'\d+', answer)
        for num in numbers:
            if int(num) > 0:
                return True
    
    return False


def check_tools_used(output: dict, required_tools: list) -> bool:
    """Check if all required tools were used."""
    if not output or "tool_calls" not in output:
        return False
    
    used_tools = [tc["tool"] for tc in output["tool_calls"]]
    
    for required in required_tools:
        if required not in used_tools:
            return False
    
    return True


def evaluate():
    """Run all benchmark questions and evaluate answers."""
    print("=" * 60)
    print("TASK 3 BENCHMARK EVALUATION")
    print("=" * 60)
    
    passed = 0
    total = len(BENCHMARK_QUESTIONS)
    
    for i, benchmark in enumerate(BENCHMARK_QUESTIONS):
        print(f"\n[{i+1}/{total}] {benchmark['question'][:80]}...")
        
        # Run agent
        output = run_agent(benchmark["question"])
        
        if not output:
            print(f"  ✗ Agent failed to produce output")
            continue
        
        # Check keywords
        answer = output.get("answer", "")
        keywords_ok = check_keywords(answer, benchmark["expected_keywords"])
        
        # Check tools
        tools_ok = check_tools_used(output, benchmark["required_tools"])
        
        # Overall result
        if keywords_ok and tools_ok:
            print(f"  ✓ PASSED")
            passed += 1
        else:
            print(f"  ✗ FAILED")
            if not keywords_ok:
                print(f"    Keywords: Expected {benchmark['expected_keywords']}")
                print(f"    Answer: {answer[:100]}")
            if not tools_ok:
                print(f"    Tools: Required {benchmark['required_tools']}")
                used = [tc["tool"] for tc in output.get("tool_calls", [])]
                print(f"    Used: {used}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} passed")
    print("=" * 60)
    
    if passed == total:
        print("✓ All benchmark questions passed!")
        return 0
    else:
        print(f"✗ {total - passed} questions failed. Fix and re-run.")
        return 1


if __name__ == "__main__":
    sys.exit(evaluate())