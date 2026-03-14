#!/usr/bin/env python3
"""
Regression test for Task 1: Call an LLM from Code.
Checks that agent.py outputs valid JSON with required fields.
"""

import subprocess
import json
import sys


def test_agent_output():
    """Test that agent.py outputs valid JSON with answer and tool_calls."""
    # Run agent.py as subprocess
    result = subprocess.run(
        ["uv", "run", "agent.py", "What is REST?"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Check exit code
    assert result.returncode == 0, f"Agent exited with code {result.returncode}: {result.stderr}"
    
    # Parse JSON output
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}\nStdout: {result.stdout}")
    
    # Check required fields
    assert "answer" in output, "Missing 'answer' field in output"
    assert "tool_calls" in output, "Missing 'tool_calls' field in output"
    assert isinstance(output["tool_calls"], list), "'tool_calls' must be an array"
    
    print("✓ All tests passed!")


if __name__ == "__main__":
    try:
        test_agent_output()
    except AssertionError as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)