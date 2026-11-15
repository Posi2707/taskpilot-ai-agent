# TaskPilot — Tool-Using AI Task Agent

TaskPilot is a Python portfolio project demonstrating a bounded AI tool-calling loop, typed tools, persistent task memory, structured execution traces, deterministic evaluations, and human approval for write operations.

> **Scope:** Educational/portfolio implementation, not a production autonomous agent. A live model run requires an API key. The bundled trace is synthetic and is not evidence of a live run.

## Features

- Agent loop: OpenAI-compatible chat completions with a maximum of six model turns.
- Tool schemas: Pydantic validation; rejects unknown tools, unexpected arguments, and invalid values.
- Tools: `list_tasks`, `add_task`, `complete_task`, `search_memory`.
- Persistent state: SQLite stores tasks and notes.
- Tracing: JSONL events for requests, tool calls, results, errors, and completion.
- Guardrails: approval before task creation or completion, bounded loop, no shell or arbitrary-code tool.
- Evaluation: eight deterministic unit/component tests for task lifecycle, ordering, search, validation, and approvals.

## Architecture

```text
User -> TaskAgent <-> LLM API
             |
             +-> ToolRegistry -> Pydantic schemas -> approval -> tools
             +-> MemoryStore (SQLite)
             +-> TraceRecorder (JSONL)
```

## Setup on Windows PowerShell

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Edit `.env` with your own key:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Then run:

```powershell
task-agent "List my open tasks"
task-agent "Add a task to prepare my AI instructor demo with high priority"
pytest -q
```

Write actions request confirmation (type `YES`). `--approve-writes` intentionally bypasses interactive confirmation for that run.

## Evaluation and tracing

The `tests/` directory contains eight deterministic component tests. They do **not** establish end-to-end LLM trajectory reliability. The `examples/sample_trace.jsonl` file is a **synthetic example** showing trace structure, not a captured production or live execution. Actual runs write `traces/run.jsonl`; avoid publishing traces containing personal information or secrets.

## Limitations

Planning is prompt-guided, not separately verified. The agent is intended for local single-user use. Production use would need stronger privacy controls, error recovery, authentication, and model-level trajectory evaluations.

## Structure

```text
src/agent/       agent loop, CLI, memory, tools, schemas, tracing
tests/           deterministic component/evaluation tests
examples/        synthetic trace example
.env.example     API key template (no secrets)
pyproject.toml   package and dependencies
```
