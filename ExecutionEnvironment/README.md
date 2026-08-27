# Execution Environments

My agentic AI experiments for Module 2 of the [Introduction to Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents) course. This module explores how to give agents a safe, persistent place to work beyond their context window.

## Scripts

### `m2.4_interpreter_agent.py` — Programmatic Tool Calling (PTC)
Runs two agents side-by-side to answer a 4-part dependent SQL question (using a Chinook database). The first agent uses standard tool calling, making 5 separate LLM round-trips. The second agent uses the `CodeInterpreterMiddleware`.

**Lesson:** The `CodeInterpreterMiddleware` injects a Javascript engine (like QuickJS) into the agent loop. Instead of making 5 slow, expensive LLM round-trips, the agent writes a single Javascript program to orchestrate the tools locally. The script calls the database 4 times instantly, hiding the intermediate steps, and returns only the final answer. This reduces LLM calls from 5 to 2, drastically improving speed and reliability.

## Key takeaways so far

1. **Backends abstract the environment** — By using pluggable backends (`FilesystemBackend`, `LocalShell`, `Sandbox`), you can switch an agent from prototyping locally to running securely in the cloud without rewriting its logic.
2. **Code Interpreters are Middleware** — The interpreter isn't hard-coded into the agent; it's an injected bridge that gives the agent a sandbox to evaluate code before hitting the host tools.
3. **PTC massively reduces latency** — Delegating process orchestration (like loops and dependent tool calls) to Javascript code eliminates the need for the LLM to "think" between every step. Code is fast and deterministic; LLM round-trips are slow and expensive.
