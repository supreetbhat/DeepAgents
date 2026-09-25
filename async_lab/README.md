# Async Subagents

Module 5 of the [Introduction to Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents) course, where delegation stops blocking the conversation.

Every subagent in [`delegation/`](../delegation) and [`sales_assistant/`](../sales_assistant) is synchronous: the coordinator hands off a task and waits until the worker returns. That is fine for work measured in seconds. It breaks down when a job takes minutes, because the user is left staring at a spinner and cannot change their mind halfway through.

This lab splits the work across **two independent deployments**. A light main agent talks to the user, and a separate analyst deployment does the slow work in the background. The main agent gets a task ID back immediately and keeps chatting while the analysis runs.

## What is here

| Path | What it does |
|------|--------------|
| `main_agent/agent.py` | The supervisor. Declares one `AsyncSubAgent` named `analyst` that points at `http://127.0.0.1:2025`, and otherwise stays a plain `create_deep_agent` |
| `main_agent/langgraph.json` | Registers the supervisor graph on the shared course environment |
| `specialized_agent/agent.py` | The analyst. An `analyze_sales` tool that groups a sales table by region or product with pandas, deliberately slowed to 20 seconds to stand in for a real heavy job |
| `specialized_agent/pyproject.toml` | The analyst's own dependency set, including pandas, which the main agent never installs |
| `specialized_agent/langgraph.json` | Declares `"dependencies": ["."]`, which is what makes the analyst a self contained deployment rather than another folder in the shared environment |

## How the flow works

```text
User ──► Main agent (port 2024)
           │
           │ start_async_task("analyst", "by region")   → task_id A, returned at once
           │ start_async_task("analyst", "by product")  → task_id B, returned at once
           │
           │ keeps talking to the user while both run in parallel
           │                                  │
           │              HTTP                ▼
           │        ─────────────►  Analyst deployment (port 2025)
           │                        one thread per task, 20s pandas job each
           │
           │ update_async_task(A, "only the West region")   same thread, new run
           │ cancel_async_task(B)
           │ check_async_task(A)   → status, and the result once it has finished
           │ list_async_tasks      → every task with its live status
```

`AsyncSubAgentMiddleware` gives the supervisor those five tools automatically once `subagents` contains an `AsyncSubAgent`. The model calls them like any other tool, and the middleware handles thread creation, run management and status tracking against the remote server.

```python
AsyncSubAgent(
    name="analyst",
    description="Runs sales analysis grouped by region or by product ... Slow ...",
    graph_id="agent",
    url="http://127.0.0.1:2025",
)
```

Setting `url` is the choice that matters. Without it the subagent would be co deployed in the same process over ASGI. With it the call goes over HTTP to a server that has its own dependencies, its own model and its own scaling, exactly as if another team owned it.

> [!TIP]
> The description tells the supervisor what the analyst **cannot** do (no averages, counts or growth metrics) and to launch one task per grouping. A delegating agent only knows what the description tells it, so the limits belong there as much as the capabilities do.

## Requirements

Each deployment has its own environment. The analyst installs from its `pyproject.toml`:

```bash
pip install "deepagents==0.7.0" "langgraph-cli[inmem]" langchain-anthropic pandas
```

> [!NOTE]
> Both `langgraph.json` files resolve `models.py` and `.env` relative to the course's folder layout (`../../..`). Adjust `dependencies` and `env` in `main_agent/langgraph.json` to wherever your shared `models.py` and `.env` live before running.

## Run

Start the analyst first and leave it running:

```bash
cd async_lab/specialized_agent
uv run langgraph dev --port 2025
```

Then start the supervisor in a second terminal:

```bash
cd async_lab/main_agent
uv run langgraph dev
```

In the Studio window, ask for a revenue breakdown by region and by product at the same time. The agent should report two task IDs straight away and stay responsive. From there, update one task with new instructions, cancel the other, and check on what is left.

## Key takeaways

1. **Delegation does not have to block** — a task ID comes back immediately, so the conversation outlives the job
2. **Async tasks can be steered** — update restarts the worker on the same thread with its history plus the new instruction; cancel stops it outright
3. **Task IDs live outside the message history** — they sit in their own state channel, so they survive when the conversation is summarised to fit the context window
4. **Do not poll** — a supervisor that calls `check` in a loop right after launching has turned async back into sync; it should report the ID and wait to be asked
5. **Separate deployments isolate dependencies** — the heavy pandas environment lives only where the work runs, and the supervisor stays light
6. **Async buys responsiveness, not simplicity** — two servers, task tracking and stale statuses are the price, so it is worth paying only for jobs that are slow, parallel or likely to change
