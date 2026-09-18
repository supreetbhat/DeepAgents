# Execution Environments

My agentic AI experiments for Module 2 of the [Introduction to Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents) course. This module explores how to give agents a safe, persistent place to work beyond their context window.

An agent with only a context window can talk about files. An agent with a *backend* can write them, run them, and read the results back — and if that backend is a remote sandbox, it can do all of that without touching my machine.

## Scripts

### `sandbox_agent.py` — the smallest real workspace
Spins up a fresh [LangSmith](https://docs.langchain.com/langsmith) sandbox, hands it to `create_deep_agent` as a `LangSmithSandbox` backend, and asks the agent to write a Fibonacci script to `fib.py` and run it. The `finally` block deletes the sandbox whether the run succeeds or fails.

```python
client = SandboxClient()
ls_sandbox = client.create_sandbox(name=f"lca-deepagents-lab-{uuid4().hex[:8]}")
agent = create_deep_agent(model=model, backend=LangSmithSandbox(sandbox=ls_sandbox))
```

**Lesson:** the backend swap is the entire change. The agent code is identical to a local run — what moves is where the code lands and who is at risk if it misbehaves. Sandboxes are cheap and disposable, so create one per run and tear it down in a `finally`.

### `sales_agent.py` — an analyst with a real workspace
Uploads the Chinook music store database into the sandbox with `backend.upload_files(...)`, then asks the agent to query it with `sqlite3`, install whatever packages it needs, plot a donut chart of revenue by genre with matplotlib, and save it to `/genre_revenue.png`. The finished PNG is read back out of the sandbox to the local folder.

```python
upload_results = backend.upload_files([("/chinook.db", f.read())])
# ... agent works ...
png_bytes = ls_sandbox.read("/genre_revenue.png")
```

**Lesson:** files are the interface. Nothing about the database or the chart passes through the context window — the agent writes a script, runs it, and reports that an artifact exists, while the bytes travel in and out by upload and read. This is what keeps a data task from blowing up the prompt.

## Requirements

```bash
pip install deepagents langgraph langsmith
```

A shared `models.py` module exposing a configured chat model is expected on the path, and the sandbox scripts need LangSmith credentials in the environment.

## Run

```bash
python sandbox_agent.py
python sales_agent.py
```

> [!WARNING]
> Both scripts create a real LangSmith sandbox. The `finally` block deletes it, but if you interrupt the process before that runs, check for a leftover sandbox.

## Key takeaways so far

1. **Backends abstract the environment** — By using pluggable backends (`FilesystemBackend`, `LocalShell`, `Sandbox`), you can switch an agent from prototyping locally to running securely in the cloud without rewriting its logic.
2. **Sandboxes are per-run resources** — Create one, use it, delete it in a `finally`. Treating them as disposable is what makes letting an agent run arbitrary code reasonable.
3. **Move data as files, not tokens** — Uploading a database and reading back a PNG keeps large artifacts entirely out of the context window.
4. **Code Interpreters are Middleware** — The interpreter isn't hard-coded into the agent; it's an injected bridge that gives the agent a sandbox to evaluate code before hitting the host tools.
5. **PTC massively reduces latency** — Delegating process orchestration (like loops and dependent tool calls) to Javascript code eliminates the need for the LLM to "think" between every step. Code is fast and deterministic; LLM round-trips are slow and expensive.
