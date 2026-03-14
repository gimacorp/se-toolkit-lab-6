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