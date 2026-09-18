# Delegation

My agentic AI experiments for Module 4 of the [Introduction to Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents) course. This module is about handing work to subagents: when to split a job up, and what each worker is allowed to see.

The earlier modules all scoped one agent. Module 1 scoped its tools and its prompt, Module 2 scoped where its code ran, Module 3 scoped what it could remember. Delegation scopes something different: **what any single context is allowed to hold**. A subagent starts blank, does one bounded job, and reports back a result rather than its reasoning, so the noise stays where the work happened.

## Scripts

### `resume-maker.py` — two subagents, two private scratch folders

The module homework. A lead agent coordinates a small job search team and does none of the work itself. It has two workers, and neither can do the other's job:

| Subagent | Job | Can write to |
|----------|-----|--------------|
| `resume-tailor` | Rewrites resume bullets in XYZ+S form against one posting, names missing keywords, flags lines to cut | `/scratch/resume-tailor/**` |
| `company-researcher` | Briefs the candidate on the employer, its priorities, and what to ask in the interview | `/scratch/company-researcher/**` |

Each worker is told to dump its raw notes to its own scratch file before answering, then reply with the polished result only.

```python
def scratch_permissions(subagent_name: str) -> list:
    return [
        FilesystemPermission(operations=["read", "write"], paths=[f"/scratch/{subagent_name}/**"], mode="allow"),
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
    ]
```

That is a first match wins allow then deny pair, the same pattern the lab used to keep researchers out of the editor's files. The lead agent gets the mirror image, a blanket deny on `/scratch/**`, so it cannot reach into anyone's working notes either.

**Three separate levers do the scoping, and it is worth keeping them apart:**

- `description` is routing. It is the only thing the lead reads when deciding who to call, so it describes *when to use this worker*, not what the worker is.
- `system_prompt` is the role. Each worker gets a prompt written for one job, with no compromise made for the other, which is why the researcher can be told to say plainly when it does not know and the tailor can be told never to invent a metric.
- `permissions` is the boundary. Prompts are requests; permissions are enforced.

The script ends with an isolation check rather than a claim. It reads the finished file tree back out of the result, confirms each scratch path was written, and reports any stray file that landed somewhere it should not have:

```
--- Scratch folder isolation check ---
  /scratch/resume-tailor/notes.md: found
  /scratch/company-researcher/notes.md: found
  No stray scratch files -- each subagent wrote only to its own folder.
```

**Lesson:** delegation is not about having more agents, it is about making sure no single context holds both the raw material and the finished judgement. The lead assembles a clean deliverable because the mess happened somewhere it could not see, and the reason that holds under pressure is the permission list rather than the instruction not to peek.

## Requirements

```bash
pip install deepagents langgraph
```

A shared `models.py` exposing `model` and `strong_model` is expected on the path:

```python
# models.py
from langchain.chat_models import init_chat_model
model = init_chat_model("your-model", model_provider="your-provider")
strong_model = init_chat_model("your-stronger-model", model_provider="your-provider")
```

The lead agent runs on `strong_model`, since routing and assembly are the judgement heavy parts of the job.

## Run

```bash
python resume-maker.py
```

> [!TIP]
> Read the whole transcript, not just the final answer. The interesting part is the `task` tool calls in the middle, where you can see exactly what the lead chose to pass along and what it never received.

## Things worth trying

- Delete the scratch instruction from one worker and watch its raw notes travel back into the lead's context.
- Give both workers the same scratch folder and run the isolation check again.
- Ask about only the company. A correctly scoped lead calls one worker, not both.

## Key takeaways so far

1. **A subagent is a context boundary** — it starts blank, so the brief you send has to stand on its own
2. **The three levers are separate** — `description` routes, `system_prompt` defines the role, `permissions` enforce the limit
3. **Prompts request, permissions enforce** — anything that actually matters belongs in the permission list
4. **Return the result, not the reasoning** — scratch files are where raw work goes to stay out of everyone else's prompt
5. **Prove isolation, do not assume it** — inspect the file tree afterwards and look for strays
