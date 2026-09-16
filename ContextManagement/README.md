# Context Management

My agentic AI experiments for Module 3 of the [Introduction to Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents) course. This module is about long-term memory: where an agent keeps what it learns, how that memory is scoped, and how to prove it doesn't leak between users.

Module 1 gave agents *thread* memory — a checkpointer keyed by `thread_id`, alive for one conversation. This module goes further: memory that survives the thread, stored outside the context window and loaded back on demand.

## The memory stack

Three pieces do the work:

| Piece | Role |
|-------|------|
| `StoreBackend` | Persists files into a LangGraph `BaseStore` under a namespace, so they outlive any single thread |
| `StateBackend` | Ordinary scratch files that live and die with the run |
| `CompositeBackend` | Routes paths between the two — `/memories/` goes to the store, everything else stays in state |

```python
backend = CompositeBackend(
    default=StateBackend(),
    routes={"/memories/": StoreBackend(namespace=memory_namespace)},
)
```

The `memory=[...]` argument on `create_deep_agent` then tells the agent which of those stored files to read into its prompt at the start of every run, and to write back to when the user says "remember this".

## Scoping is the whole game

The namespace function is what makes memory private. It receives the runtime and returns a tuple, and the agent can only ever read or write within the namespace that tuple names:

```python
def memory_namespace(runtime):
    ctx = runtime.context
    return ("memory", ctx["workspace_id"], ctx["user_id"])
```

Drop `user_id` from that tuple and every user in a workspace shares one memory file. Nothing errors, nothing warns — private facts simply start showing up in other people's conversations.

## Scripts

### `memory_isolation.py` — proving isolation between users
The module homework. The lab scoped memory to a single fixed workspace and user, so isolation was described but never demonstrated. This script runs the *same* agent under two contexts that share a workspace and differ only by user, seeds each with a different fact about how its user writes email, then asks three questions in sequence.

```python
CONTEXT_A = {"workspace_id": "homework", "user_id": "u_you"}
CONTEXT_B = {"workspace_id": "homework", "user_id": "u_teammate"}

agent.invoke({"messages": [...]}, context=CONTEXT_A)
```

1. **Recall under A** — the agent answers from A's seed memory alone.
2. **Remember under A** — a new, distinctive fact is written to A's stored `AGENTS.md`.
3. **Leak check under B** — the same question, asked under B, must come back with B's own answer or none at all, never A's.

The script finishes by reading both stored `AGENTS.md` files straight out of the store and comparing them, so the result is an assertion about state rather than a judgement about phrasing.

**Lesson:** an agent's memory is only as private as its namespace function. Isolation isn't a property of the library, it's a property of the key you build, and the only way to know you built it right is to run two contexts side by side and look at what each one stored.

## Requirements

```bash
pip install deepagents langgraph
```

A shared `models.py` module exposing a configured chat model is expected on the path:

```python
# models.py
from langchain.chat_models import init_chat_model
model = init_chat_model("your-model", model_provider="your-provider")
```

## Run

```bash
python memory_isolation.py
```

> [!NOTE]
> The script uses `InMemoryStore`, so memory persists across threads within one run and vanishes when the process exits. Swap in a persisted store to keep it between runs.

## Key takeaways so far

1. **Thread memory and long-term memory are different things** — checkpointers keep one conversation alive, a store keeps facts alive across all of them
2. **Memory is just files behind a backend** — `CompositeBackend` routes `/memories/` to durable storage and leaves everything else ephemeral
3. **The namespace is the security boundary** — workspace plus user in the key means per-user privacy; leaving either out silently merges people together
4. **Loading is explicit** — `memory=[path]` decides what enters the prompt, which keeps the context window small as stored memory grows
5. **Test isolation, don't assume it** — run two contexts, seed them differently, and compare the stored files directly
