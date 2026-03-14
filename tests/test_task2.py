#!/usr/bin/env python3
"""
Regression tests for Task 2: The Documentation Agent.
"""

import subprocess
import json
import sys


def test_task1_basic_llm():
    """Test 1: Basic LLM call (from Task 1)"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "What is 2 + 2?"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    assert result.returncode == 0, f"Agent exited with code {result.returncode}: {result.stderr}"
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}\nStdout: {result.stdout}")
    
    assert "answer" in output, "Missing 'answer' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"
    
    print("✓ Test 1 passed: Basic LLM call")


def test_task2_merge_conflict():
    """Test 2: Documentation question about merge conflicts"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "How do you resolve a merge conflict?"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    assert result.returncode == 0, f"Agent exited with code {result.returncode}: {result.stderr}"
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}\nStdout: {result.stdout}")
    
    assert "answer" in output, "Missing 'answer' field"
    assert "source" in output, "Missing 'source' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"
    
    # Check that tools were used
    assert len(output["tool_calls"]) > 0, "Expected tool calls but got none"
    
    # Check for read_file in tool calls
    tool_names = [tc["tool"] for tc in output["tool_calls"]]
    assert "read_file" in tool_names, "Expected read_file to be called"
    
    print("✓ Test 2 passed: Merge conflict question")


def test_task2_list_files():
    """Test 3: Question that should trigger list_files"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "What files are in the wiki?"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    assert result.returncode == 0, f"Agent exited with code {result.returncode}: {result.stderr}"
    
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}\nStdout: {result.stdout}")
    
    assert "answer" in output, "Missing 'answer' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"
    
    # Check that list_files was called
    tool_names = [tc["tool"] for tc in output["tool_calls"]]
    assert "list_files" in tool_names, "Expected list_files to be called"
    
    print("✓ Test 3 passed: List files question")


if __name__ == "__main__":
    tests = [
        test_task1_basic_llm,
        test_task2_merge_conflict,
        test_task2_list_files,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}", file=sys.stderr)
            failed += 1
    
    if failed == 0:
        print(f"\n✓ All {len(tests)} tests passed!")
        sys.exit(0)
    else:
        print(f"\n✗ {failed}/{len(tests)} tests failed", file=sys.stderr)
        sys.exit(1)