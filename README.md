I'm working through the course as part of a daily agentic AI study practice , and everything I build lands here — from the first "hello world" agent to persona experiments and tool-calling exercises.

## What are deep agents?

Deep agents are LLM agents that go beyond a single model call: they combine a model, tools, persistent state, and planning to complete multi-step tasks. The `deepagents` library packages these primitives behind one entry point:

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
| [`FirstAgent/`](./FirstAgent) | Course fundamentals — baseline agents, persona engineering, and custom tool calling |

> [!NOTE]
> This repository grows as I progress through the course. Check back for tool use, planning, sub-agents, and multi-step task exercises.

## Getting started

```bash
pip install deepagents langchain-core
```

The scripts import a shared `models` module (`from models import model`) that exposes your configured chat model, so set that up first with your provider of choice.

Then run any script:

```bash
python FirstAgent/scratch_agent.py
```

## What I'm learning

- **Agents vs. chatbots** — a model plus tools plus state can act, not just answer
- **System prompts are architecture** — swapping prompts changes behavior end to end
- **Tool calling discipline** — agents should look things up before answering
- **Cost awareness** — prompt design interacts directly with token spend and caching

---

Part of my build-in-public journey: [GitHub](https://github.com/supreetbhat) · [LinkedIn](https://www.linkedin.com/in/supreetbhat/) · [Hugging Face](https://huggingface.co/SupreetBhat)
