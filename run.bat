@echo off
REM Sync and activate environment using uv
uv sync

REM Run the main FastAPI app using uv
uv run .\src\main.py
