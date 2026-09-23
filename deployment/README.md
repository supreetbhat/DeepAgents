# Deployment

Module 5 of the [Introduction to Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents) course, where the agent stops being a script you run and becomes a server you call.

The lab deployed a bare agent and talked to it through the Studio chat panel. The M5.2 homework does two things differently: it deploys an agent with a persona and a tool of its own, and then talks to it the way any other client would, over the Agent Server HTTP API rather than through Studio.

## What is here

| File | What it does |
|------|--------------|
| `call_agent_api.py` | The deployed agent: a `lookup_fact` tool over a small dictionary, a persona system prompt, and a module level `graph` that `langgraph.json` points at |

The agent is deliberately small. The lesson is not the tool, it is that a deep agent is a graph a server can host, and that the client on the other end can be anything that speaks HTTP.

```python
@tool
def lookup_fact(topic: str) -> str:
    """Look up the home number on file for a name."""
    ...

graph = create_deep_agent(model=model, tools=[lookup_fact], system_prompt=SYSTEM_PROMPT)
```

The prompt does the work that the tool cannot: it tells the agent to answer only from `lookup_fact`, to lowercase the name before calling it, and to say nothing rather than guess when there is no match. That last instruction is the whole point of giving an agent a lookup tool in the first place.

> [!NOTE]
> The file currently holds the agent definition rather than the API client, although its name suggests the opposite. The HTTP client half of the homework, the part that calls the deployed graph over the Agent Server API instead of using Studio, is still to come.

## Requirements

```bash
pip install deepagents langgraph langgraph-cli
```

## Run

```bash
cd deployment
uv run langgraph dev
```

Studio opens on the local server. To exercise the actual lesson, leave Studio closed and call the server's API directly with any HTTP client: create a thread, post a run against the `agent` graph, and read the streamed response.

## Key takeaways

1. **A deployed agent is a graph plus a manifest** — `langgraph.json` names the module variable and the server does the rest
2. **Studio is a client, not the product** — anything that can post JSON can drive the same graph
3. **A tool is a fact boundary** — the prompt decides whether the model is allowed to answer from anywhere else
4. **Say null rather than guess** — a lookup agent that improvises is worse than no agent
