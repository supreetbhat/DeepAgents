Each script explores one core idea of agent design using `create_deep_agent` from the [`deepagents`](https://github.com/langchain-ai/deepagents) library.

## Scripts

### `scratch_agent.py` — hello, agent
The minimal viable deep agent: a model, no tools, one question. The baseline every other script builds on.

```python
agent = create_deep_agent(model=model)
agent.invoke({"messages": [{"role": "user", "content": "What is an LLM?"}]})
```

### `agent_butler_persona.py` — prompts are architecture
Same model, same question — but the system prompt turns the assistant into an extremely posh Victorian butler who answers *What is an LLM?* in full royal register.

**Lesson:** the system prompt doesn't decorate behavior; it defines it. Swapping one string changes tone, structure, and content of everything the agent produces.

### `agent_butler_extra_posh.py` — long prompts + custom tools + cost
The butler's system prompt expanded into a full character sheet (rules of comportment, backstory, Opinions about modernity), plus a custom `@tool` (`summon_tea`) the agent must call correctly.

**Lesson:** long, stable system prompts are exactly what [prompt caching](https://python.langchain.com/docs/how_to/chat_prompt_caching/) was built for — keeping the prefix identical across calls lets providers cache it and cuts cost significantly.

### `scope.py` — tool-calling discipline
"The Arcade Ref" — a sports-commentator agent with a custom `lookup_retro_game_fact` tool and a scoped instruction: *always call the tool before answering*, and admit when a game isn't in its records instead of improvising.

**Lesson:** scoping what an agent may do (and what it must refuse to guess) is how you turn a fun demo into a reliable system.

## Requirements

```bash
pip install deepagents langchain-core
```

A shared `models.py` module exposing a configured chat model is expected on the path:

```python
# models.py
from langchain.chat_models import init_chat_model
model = init_chat_model("your-model", model_provider="your-provider")
```

## Run

```bash
python scratch_agent.py
python agent_butler_persona.py
python agent_butler_extra_posh.py
python scope.py
```

## Key takeaways so far

1. An agent is **model + tools + state**, composed deliberately
2. The system prompt is **architecture**, not decoration
3. Custom tools give agents grounded abilities — but only if you **scope their use**
4. Prompt length has real cost implications; design with **caching** in mind
