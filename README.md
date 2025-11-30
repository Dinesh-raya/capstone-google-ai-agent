# Smart Fitness & Diet Recommender (Colab / Kaggle Ready)

## Overview
This project is a multi-agent AI demo (capstone-ready) that:
- Identifies food from an image (stub)
- Retrieves nutrition facts via a local RAG (vector store)
- Generates a personalized 3-day meal plan (stub)
- Evaluates the plan (LLM-as-a-Judge stub)
- Demonstrates MCP-style long-running ops (pause/resume)
- Shows observability (logs & metrics)
- Provides a Gradio UI for interactive demo

## Files
- requirements.txt
- README.md
- observability.py
- mcp.py
- memory.py
- tools.py
- agents.py
- app_gradio.py
- run_local_demo.sh

## How to run (Google Colab recommended - no conflicts)
1. Open a new Google Colab notebook.
2. In the first cell, install dependencies:
   ```bash
   !pip install -q gradio==4.31.4 sentence-transformers==2.2.2 pillow pandas
   ```
3. Upload or copy the project files into the Colab environment (or upload this ZIP and unzip).
4. Run the cells or execute `app_gradio.py`:
   ```bash
   python app_gradio.py
   ```
5. The Gradio UI will launch inline. Upload an image and test the flow.

## Notes
- This repository uses *stubbed* model/tool implementations so it runs offline without API keys.
- For production, replace the stub functions in `tools.py` with real model/tool calls (Gemini, Vision, LLM).
- The design follows ADK/Agent best practices: orchestrator + vision/nutrition/planner/judge agents and LRO (MCP) flows.

## Support
If you want a version customized for Kaggle submission (no pip installs and fully in-notebook), ask and I'll provide it.
