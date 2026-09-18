# DeepAgents Study Labs

I'm working through agentic AI coursework as part of an ongoing daily study practice, and everything I build lands here — from the first "hello world" agent to persona experiments, tool-calling exercises, memory/checkpointing, MCP integrations, human-in-the-loop approval gates, and teams of subagents that delegate work between them.

## What are deep agents?

Deep agents are LLM agents that go beyond a single model call: they combine a model, tools, persistent state, and planning to complete multi-step tasks. The [`deepagents`](https://github.com/langchain-ai/deepagents) library packages these primitives behind one entry point:

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model=model,
    tools=[...],
    system_prompt="...",
)
result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
```

## Repository structure

| Path | Description |
|------|-------------|
| [`FirstAgent/`](./FirstAgent) | Course fundamentals — baseline agents, persona engineering, custom tool calling, thread persistence with checkpointers, MCP tool integration, and human-in-the-loop approval |
| [`ExecutionEnvironment/`](./ExecutionEnvironment) | Deep agent workspaces — Filesystem backends, local shells, sandboxes, and Code Interpreter middleware for Programmatic Tool Calling (PTC) |
| [`ContextManagement/`](./ContextManagement) | Long-term memory — store-backed memory files, composite backends, per-user namespaces, and a homework that proves memory stays isolated between users |
| [`delegation/`](./delegation) | Subagent teams — a lead agent that coordinates and does no work itself, two specialist workers, and filesystem permissions that give each one a private scratch folder |

> [!NOTE]
> This repository grows as I progress through the course. Modules 1 to 4 are active. Coming next: planning and multi-step task exercises.

## Getting started

```bash
pip install deepagents langchain-core langchain-mcp-adapters langgraph
```

The scripts import a shared `models` module (`from models import model`) that exposes your configured chat model, so set that up first with your provider of choice:

```python
# models.py
from langchain.chat_models import init_chat_model
model = init_chat_model("your-model", model_provider="your-provider")
strong_model = init_chat_model("your-stronger-model", model_provider="your-provider")
```

> [!NOTE]
> Most scripts only need `model`. The delegation lab also imports `strong_model`, which it uses for the coordinating agent.

Then run any script:

```bash
python FirstAgent/scratch_agent.py
```

## What I'm learning

- **Agents vs. chatbots** — a model plus tools plus state can act, not just answer
- **System prompts are architecture** — swapping prompts changes behavior end to end
- **Tool calling discipline** — agents should look things up before answering, and be scoped so they admit what they don't know
- **Memory is a component** — threads and checkpointers decide what an agent remembers, for how long, and in what scope
- **MCP extends agents safely** — external tools arrive through adapters, filtered to an explicit allowlist
- **Dangerous actions need gates** — side-effecting tools pause for human approve/edit/reject before they run
- **Execution environments define bounds** — Filesystem backends and sandboxes let agents safely interact with files without bloating the context window
- **Programmatic Tool Calling (PTC)** — Using a Code Interpreter as middleware, agents can write Javascript to orchestrate tools, reducing slow LLM round-trips from 5 to 2
- **Long-term memory is files plus a namespace** — a store-backed `/memories/` route outlives the thread, and the namespace key is what keeps one user's memory out of another's
- **Delegation is a context boundary** — a subagent starts blank and reports its result rather than its reasoning, so the raw material never reaches the coordinator's prompt
- **Prompts request, permissions enforce** — a worker told not to read someone else's notes still can; a `FilesystemPermission` deny rule is what makes it true

---

Part of my build-in-public journey: [GitHub](https://github.com/supreetbhat) · [LinkedIn](https://www.linkedin.com/in/supreetbhat/) · [Hugging Face](https://huggingface.co/SupreetBhat)
