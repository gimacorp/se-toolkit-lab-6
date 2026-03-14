#!/usr/bin/env python3
"""
Regression tests for Task 3: The System Agent.
"""

import subprocess
import json
import sys


def test_task3_framework():
    """Test: What framework does the backend use?"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "What framework does the backend use?"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    assert result.returncode == 0, f"Agent failed: {result.stderr}"
    output = json.loads(result.stdout)
    
    assert "answer" in output, "Missing 'answer' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"
    
    tool_names = [tc["tool"] for tc in output["tool_calls"]]
    assert "read_file" in tool_names, "Expected read_file to be used"
    assert "FastAPI" in output["answer"], "Expected FastAPI in answer"
    
    print("✓ Test 1 passed: Framework question")


def test_task3_item_count():
    """Test: How many items are in the database?"""
    result = subprocess.run(
        ["uv", "run", "agent.py", "How many items are in the database?"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    assert result.returncode == 0, f"Agent failed: {result.stderr}"
    output = json.loads(result.stdout)
    
    assert "answer" in output, "Missing 'answer' field"
    assert "tool_calls" in output, "Missing 'tool_calls' field"
    
    tool_names = [tc["tool"] for tc in output["tool_calls"]]
    assert "query_api" in tool_names, "Expected query_api to be used"
    
    import re
    numbers = re.findall(r'\d+', output["answer"])
    assert len(numbers) > 0, "Expected a number in answer"
    
    print("✓ Test 2 passed: Item count question")


if __name__ == "__main__":
    tests = [test_task3_framework, test_task3_item_count]
    
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