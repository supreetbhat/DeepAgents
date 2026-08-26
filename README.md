# DeepAgents Study Lab

I'm working through agentic AI coursework as part of an ongoing daily study practice, and everything I build lands here — from the first "hello world" agent to persona experiments, tool-calling exercises, memory/checkpointing, MCP integrations, human-in-the-loop approval gates, and execution environments.

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

> [!NOTE]
> This repository grows as I progress through the course. Module 1 is complete. Currently studying **execution environments** — a deep agent always gets a filesystem to work in, an optional shell (the `execute` tool, backed by a local shell or a sandbox), and an optional interpreter for running code inside the agent loop; pluggable backends decide where files live and commands run while the agent's tool surface stays the same. Coming next: planning, sub-agents, and multi-step task exercises.

## Getting started

```bash
pip install deepagents langchain-core langchain-mcp-adapters langgraph
```

The scripts import a shared `models` module (`from models import model`) that exposes your configured chat model, so set that up first with your provider of choice:

```python
# models.py
from langchain.chat_models import init_chat_model
model = init_chat_model("your-model", model_provider="your-provider")
```

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
- **Agents run in an environment** — a filesystem is always there for scratch work and artifacts, a shell appears as `execute` when the backend supports it, and an interpreter gives code-like loops without burning model turns; swap backends, keep the same tool surface

---

Part of my build-in-public journey: [GitHub](https://github.com/supreetbhat) · [LinkedIn](https://www.linkedin.com/in/supreetbhat/) · [Hugging Face](https://huggingface.co/SupreetBhat)
