# Chinook Sales Assistant

The Module 5 capstone of the [Introduction to Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents) course, and the first thing in this repository that is a whole application rather than a lesson. Every primitive from the earlier modules shows up here at once: tools, memory, an execution environment, subagents, MCP, human approval gates, and skills.

The agent works for Jane Peacock, a Sales Support Agent at Chinook, a fictional online music distributor. It answers quote requests, keeps customer records current, researches the market and reports on her territory. It assists; Jane decides.

## Architecture

```
                         main agent (strong_model)
                         memory: /AGENTS.md
                         skills: /skills/*
                         tools:  markdown_to_html, render_pie_chart, mail_* (MCP)
                                        |
        +-----------------+-------------+---------------+------------------+
        |                 |                             |                  |
  chinook-analyst    inbox-manager               quote-reviewer     genre-researcher
  SQL, gated write   MCP mail, gated draft       checks arithmetic  web search, fan out
  own AGENTS.md      approve/edit/reject         strong_model       private /research/**
```

The main agent coordinates and holds no direct database or mail access of its own. Each specialist owns exactly one external system.

| Subagent | Owns | Model | Gate |
|----------|------|-------|------|
| `chinook-analyst` | The SQLite database: prices, customers, purchase history, territory metrics | `model` | `add_customer` waits for approval |
| `inbox-manager` | The mailbox, over MCP: list, read, draft | `model` | `mail_create_draft` waits for approval |
| `quote-reviewer` | Nothing external; checks a drafted quote's arithmetic and pricing | `strong_model` | none needed |
| `genre-researcher` | Web search, one genre per call | `model` | writes confined to `/research/**` |

`genre-researcher` only exists when `TAVILY_API_KEY` is set; `inbox-manager` only when the mail server was reachable at startup.

## The design decisions worth reading the code for

**Gated tools live on specialists, never on the main agent.** The always-present general purpose subagent inherits the main agent's tools, so a gated tool placed there could be reached through delegation without its gate. Keeping `add_customer` and `mail_create_draft` solely on gated specialists means the only path to either write runs through its human approval.

**The approval is the tool call, not a question.** Both the operating manual and the subagent prompts say the same thing: make the call and let the interrupt surface. An agent that asks permission in prose produces a polite message and no draft.

**The database's trust boundary is in the tool, not the prompt.** `query_chinook` opens SQLite in read-only URI mode *and* rejects any statement that is not a single SELECT, so model-generated SQL is treated as untrusted input twice over. The one write path is a parameterised INSERT scoped to the logged in rep.

```python
_RO_URI = f"file:{DB_PATH}?mode=ro"
_FORBIDDEN = ("insert", "update", "delete", "drop", "alter", "create", ...)
```

**The analyst learns the schema once and remembers it.** Its own `agents/chinook-analyst/AGENTS.md` ships with an empty schema section and an instruction to fill it in with `introspect_schema` on first use. That is why the subagents are built by a function rather than declared at import time: the analyst's `MemoryMiddleware` needs the same backend the main agent uses, so the schema it writes is the schema it later reads.

**The chart tool takes data, not code.** `render_pie_chart` accepts a title and two parallel lists. There is no execution surface to secure, which is the right trade for a fixed output that never varies.

**Skills are the procedures, memory is the standing context.** `/AGENTS.md` describes who Jane is, who the specialists are and what the house rules are. The three files under `skills/` describe how to do one job each: process a request for quote, build a territory report, assemble the weekly newsletter.

## Requirements

```bash
pip install deepagents langgraph langchain-mcp-adapters langchain-quickjs mcp matplotlib
```

A `models.py` on the path exposing `model` and `strong_model`, and optionally a `TAVILY_API_KEY` in the environment to turn the newsletter researcher on.

## Run

```bash
cd sales_assistant
./start.sh
```

`start.sh` frees port 5002 if a previous run left something on it, starts the mock mail server, waits for it to accept connections and then launches `langgraph dev`. It traps EXIT, INT and TERM so the mail server dies with it.

> [!IMPORTANT]
> The mail server has to be up before `make_graph()` runs, because the MCP tools are discovered at startup. Start it with `start.sh` rather than launching `langgraph dev` yourself.

The mailbox is a local JSON file seeded from `mcp/seeds/incoming_rfq.json`, so the whole thing runs offline. Nothing is ever sent; `mail_create_draft` only ever saves.

## What to try

1. **"There is an RFQ in my inbox, can you handle it?"** — exercises the whole chain: inbox-manager reads the mail, chinook-analyst prices it, the code interpreter does the arithmetic, quote-reviewer checks it, and a draft reply pauses for approval.
2. **"How is my book of business doing?"** — the territory report skill, ending in a rendered pie chart under `outputs/`.
3. **"Write this week's newsletter."** — parallel genre research, each researcher dumping raw search output into its own `/research/` folder and returning only the finished segment.
4. **Reject an approval** instead of accepting it, and watch what the agent does with the refusal.

## Key takeaways

1. **Coordinate or act, not both** — the main agent owns no external system, so every side effect has a named owner
2. **Put the gate where the tool lives** — inheritance through delegation will route around a gate placed on the main agent
3. **The interrupt is the request** — asking for permission in prose creates nothing
4. **Enforce at the boundary** — read-only connections and statement checks outrank any instruction in a prompt
5. **Per subagent memory needs a shared backend** — otherwise what a specialist learns is not what it later reads
6. **Fixed-purpose tools beat code execution** when the output never varies; there is nothing left to sandbox
