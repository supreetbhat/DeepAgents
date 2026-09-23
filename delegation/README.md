# Delegation

My agentic AI experiments for Module 4 of the [Introduction to Deep Agents](https://academy.langchain.com/courses/foundation-introduction-to-deepagents) course. This module is about handing work to subagents: when to split a job up, and what each worker is allowed to see.

The earlier modules all scoped one agent. Module 1 scoped its tools and its prompt, Module 2 scoped where its code ran, Module 3 scoped what it could remember. Delegation scopes something different: **what any single context is allowed to hold**. A subagent starts blank, does one bounded job, and reports back a result rather than its reasoning, so the noise stays where the work happened.

Two scripts here, and they delegate for two different reasons. `resume-maker.py` splits the work by **role**, because the two jobs need different instructions and must not see each other's notes. `clue-finder.py` splits it by **volume**, because the material is larger than one context should ever hold and every piece needs the same treatment. Static subagents handle the first case; a workflow that dispatches them in code handles the second.

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

### `clue-finder.py` — one subagent, dispatched per chapter by code

The M4.3 homework, and the dynamic half of the module. A six chapter Sherlock Holmes pastiche is written to `homework_data/my_corpus.txt`, and the main agent is asked to find every clue Holmes mentions but never explains. It is told explicitly not to read the chapters itself.

The word that does the work is **workflow**. It tells the main agent to solve the problem by writing code rather than by taking turns:

```python
agent = create_deep_agent(
    model=strong_model,
    middleware=[CodeInterpreterMiddleware()],
    system_prompt=MAIN_PROMPT,
    subagents=[section_scanner],
    backend=FilesystemBackend(root_dir=DATA_DIR, virtual_mode=True),
)
```

The main agent reads the corpus, splits it on the `=== CHAPTER N ===` headers, and calls the `section-scanner` subagent once per chapter from inside the interpreter. Six scans, one fresh context each, and the corpus itself never enters the main model's prompt — only the findings come back.

**The scanner returns a parseable format, not prose,** because code is consuming it:

```
CLUE: <exact quote from the chapter>
WHY: <one sentence on what is left unexplained>
```

`NONE` for a clean chapter. That constraint is what makes the fan-out mechanical instead of a second reading problem.

**The interesting part is the reconciliation.** A scanner sees one chapter, so it cannot know that the stopped clocks in chapter 2 are explained by Hartley himself in chapter 5. It flags them anyway, as instructed, and the main agent drops them on the way to the final report. The clues that survive — the key that was never in the lock, the blue sand, the canary that sang on Tuesday, the second teaspoon — are the ones the story genuinely never explains.

That division is the lesson. The subagent gets the narrow job that parallelises, and the coordinator keeps the only job that needs the whole picture. Isolating the scanners is what creates the reconciliation problem, and accepting that trade is the point rather than a flaw in the design.

**Static and dynamic, side by side:**

| | `resume-maker.py` | `clue-finder.py` |
|---|---|---|
| Subagents | Two, each a different role | One role, many calls |
| Dispatched by | The lead agent's own turns | Code, inside the interpreter |
| Why delegate | The jobs differ and must stay separate | The corpus is too big for one context |
| Scales with | Nothing; two is two | The number of sections |
| Coordinator's job | Assemble two deliverables | Fan out, then reconcile across results |

## Requirements

```bash
pip install deepagents langgraph
```

`clue-finder.py` also needs the code interpreter:

```bash
pip install langchain-quickjs
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
python clue-finder.py
```

`clue-finder.py` writes its corpus to `homework_data/` on first run and works against a virtual filesystem rooted there, so nothing lands outside that folder.

> [!TIP]
> Read the whole transcript, not just the final answer. The interesting part is the `task` tool calls in the middle, where you can see exactly what the lead chose to pass along and what it never received.

## Things worth trying

- Delete the scratch instruction from one worker and watch its raw notes travel back into the lead's context.
- Give both workers the same scratch folder and run the isolation check again.
- Ask about only the company. A correctly scoped lead calls one worker, not both.
- Remove the word "workflow" from the main prompt in `clue-finder.py`. The agent tends to fall back on handling chapters one turn at a time, which is the behaviour the workflow framing exists to prevent.
- Drop the `CLUE:` / `WHY:` format and ask for prose instead, then watch how much harder the results are to merge.
- Delete the reconciliation paragraph and see the stopped clocks reported as an unexplained clue, even though chapter 5 explains them.

## Key takeaways so far

1. **A subagent is a context boundary** — it starts blank, so the brief you send has to stand on its own
2. **The three levers are separate** — `description` routes, `system_prompt` defines the role, `permissions` enforce the limit
3. **Prompts request, permissions enforce** — anything that actually matters belongs in the permission list
4. **Return the result, not the reasoning** — scratch files are where raw work goes to stay out of everyone else's prompt
5. **Prove isolation, do not assume it** — inspect the file tree afterwards and look for strays
6. **Delegate by role or by volume** — different jobs need different workers; the same job over too much material needs the same worker called many times
7. **A workflow is dispatch in code** — the main agent writes the loop, so the number of sections stops being a number of turns
8. **Give a fanned-out subagent a fixed output format** — code is reading the answers, and prose does not merge
9. **Isolation creates the reconciliation job** — a worker that sees one piece cannot know what another piece explains, so the coordinator owns the cross-check
