# FirstAgent

My first deep agents, built while taking [Introduction to Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents) on LangChain Academy. Each script explores one core idea of agent design using `create_deep_agent` from the [`deepagents`](https://github.com/langchain-ai/deepagents) library. Read them in order — every script builds on the previous lesson.

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

### `agent_butler_extra_posh.py` — long prompts + prompt caching + cost
The butler's system prompt expanded into a full character sheet (rules of comportment, backstory, Opinions about modernity) with a custom tool.

**Lesson:** long, stable system prompts are exactly what [prompt caching](https://python.langchain.com/docs/how_to/chat_prompt_caching/) was built for — keeping the prefix identical across calls lets providers cache it and cuts cost significantly. Prompt length is a cost decision, not just a creative one.

### `scope.py` — tool-calling discipline
"The Arcade Ref" — a sports-commentator agent with a custom `lookup_retro_game_fact` tool and a scoped instruction: *always call the tool before answering*, and admit when a game isn't in its records instead of improvising.

**Lesson:** scoping what an agent may do (and what it must refuse to guess) is how you turn a fun demo into a reliable system.

### `threads_checkpointers.py` — giving agents memory
Adds a LangGraph `MemorySaver` checkpointer and runs two threads against the same agent: thread A remembers the stated fact across separate `invoke()` calls, thread B starts blank.

**Lesson:** persistence lives in the checkpointer keyed by `thread_id`. Same thread = continuity; different thread = isolation. Multi-turn memory is a component you wire in, not something the model does on its own.

### `checkpoints_homework.py` — designing a memory experiment
The module homework: design your own multi-thread scenario and *prove* three properties — within-thread persistence, cross-thread isolation, and checkpointer scope (a fresh `MemorySaver` on the same `thread_id` remembers nothing).

**Lesson:** treat agent memory claims like test cases. If you can't demonstrate where state lives and where it doesn't, you don't understand your own system.

### `agent_mcp.py` — pulling in external tools via MCP
Connects to a live [MCP server](https://modelcontextprotocol.io) (`docs-langchain`) through `MultiServerMCPClient`, inspects the tools it advertises, **filters them down to an explicit allowlist**, and hands only those to the agent.

```python
client = MultiServerMCPClient({"docs-langchain": {"transport": "http", "url": "..."}})
tools = await client.get_tools()
tools = [t for t in tools if t.name in ALLOWED]
```

**Lesson:** real integrations shouldn't get every tool the server offers. Discover → filter → scope is the pattern for safely extending an agent beyond its own code.

### `hitl.py` — human-in-the-loop approval gates
A doctor's-appointment booking agent whose `book_appointment` tool is gated behind `interrupt_on`. Every proposed call pauses execution mid-run; a human reviews the arguments and answers **approve**, **edit** (swap in corrected args), or **reject**, and the run resumes via `Command(resume=...)` on the same thread.

```python
agent = create_deep_agent(
    model=model,
    tools=[book_appointment],
    interrupt_on={"book_appointment": {"allowed_decisions": ["approve", "edit", "reject"]}},
    checkpointer=MemorySaver(),
)
# ... later, after reviewing the pending tool call:
result = agent.invoke(Command(resume={"decisions": decisions}), config=config, version="v2")
```

**Lesson:** side-effecting tools should never fire unsupervised. The interrupt-resume pattern turns the human into a permission layer — the agent proposes, the person disposes — while the checkpointer keeps the paused conversation alive until a decision arrives.

## Requirements

```bash
pip install deepagents langchain-core langchain-mcp-adapters langgraph
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
python threads_checkpointers.py
python checkpoints_homework.py
python agent_mcp.py
python hitl.py
```

## Key takeaways so far

1. An agent is **model + tools + state**, composed deliberately
2. The system prompt is **architecture**, not decoration
3. Custom tools give agents grounded abilities — but only if you **scope their use**
4. Prompt length has real cost implications; design with **caching** in mind
5. Memory = **threads + checkpointers**: same thread persists, others stay isolated, and scope follows the checkpointer instance
6. External capabilities arrive through **MCP**, and should be filtered to an allowlist before an agent ever sees them
7. Side-effecting actions belong behind **human-in-the-loop interrupts** — approve, edit, or reject before execution

> [!NOTE]
> Currently studying (Module 2): **execution environments**. A deep agent always gets a filesystem (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`) for scratch work and artifacts; an optional shell shows up as the `execute` tool when the backend supports command execution (local shell or sandbox provider); and an optional interpreter — separate from the backend, added as its own tool in the agent loop — runs code-like loops so intermediate values stay in variables instead of returning to the model's context every step. Backends implement the filesystem and shell underneath, while the agent's tool surface stays unchanged. Demo scripts coming soon.
