# python/m4/m4.2_homework.py
"""M4.2 Homework: Give Each Subagent Its Own Scoped Scratch Folder.

THE IDEA
The lab's genre-researcher subagents each wrote raw search notes to their own
assigned /research/<genre>/ folder, kept out of the editor's context by
FilesystemPermission scoping: researchers could write under /research/**, the
editor could not. 

This homework asks you to build a small team of 2 subagent types for 
a domain YOU pick (e.g., trip planning, home renovation), each with 
its own private, permission-scoped folder under /scratch/<name>/ to
stash raw notes in before answering. The harness below wires up the scratch
folder, the permissions, and the write-before-answering instruction for you;
you just decide who your two subagents are.

WHAT YOU FILL IN
  TODO 1: for each of the two entries in SUBAGENT_SPECS, fill in "name",
    "description" (when the main agent should call it), and "role_prompt"
    (who this subagent is and what its job is). Everything else -- the
    scratch folder, the permissions, the instruction to save raw notes
    before answering -- is handled for you.
  TODO 2: write the main agent's system prompt, telling it which subagent
    to call for which part of the job, and a user request that should
    trigger delegation to BOTH subagents.

RUN
  cd python
  uv run ./m4/m4.2_homework.py
"""

from deepagents import FilesystemPermission, create_deep_agent

from models import model, strong_model

SCRATCH_ROOT = "/scratch"


def scratch_path(subagent_name: str) -> str:
    return f"{SCRATCH_ROOT}/{subagent_name}/notes.md"


def scratch_permissions(subagent_name: str) -> list:
    """Scope a subagent to write only under its own scratch folder -- the same
    first-match-wins allow-then-deny pattern the lab used for
    research_permissions/editor_permissions."""
    return [
        FilesystemPermission(operations=["read", "write"], paths=[f"{SCRATCH_ROOT}/{subagent_name}/**"], mode="allow"),
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
    ]


def scratch_instruction(subagent_name: str) -> str:
    return (
        f'Before you answer, call write_file on "{scratch_path(subagent_name)}" '
        "with your raw notes or reasoning. Then give your final answer using "
        "only the polished result -- do not repeat those raw notes in your reply."
    )


def build_subagents(specs: list[dict]) -> list[dict]:
    team = []
    for spec in specs:
        name = spec["name"]
        team.append(
            {
                "name": name,
                "description": spec["description"],
                "system_prompt": spec["role_prompt"] + "\n\n" + scratch_instruction(name),
                "permissions": scratch_permissions(name),
            }
        )
    return team


# ════════════════════════════════════════════════════════════════════════
# TODO 1: Fill in your two subagents.
#
# For each entry: "name" is the handle the main agent calls it by, kebab-
# case (e.g. "flight-finder"). "description" is how the main agent decides
# which one to use. "role_prompt" is that subagent's own job description --
# don't mention scratch files or write_file here, that's added for you.
# ════════════════════════════════════════════════════════════════════════

SUBAGENT_SPECS = [
    {
        "name": "resume-tailor",
        "description": (
            "Rewrite and reorder a candidate's existing resume bullets to match "
            "one specific job description. Delegate one role per call. Use this "
            "for anything about the resume itself -- wording, ordering, "
            "keywords, what to cut."
        ),
        "role_prompt": (
            "You are a resume editor who tailors an existing resume to one "
            "specific job posting.\n\n"
            "Given the candidate's background and a target role, produce:\n"
            "1. Five to seven rewritten bullets in XYZ+S form -- accomplished X, "
            "   measured by Y, by doing Z, with the scope S -- drawn only from "
            "   experience the candidate actually stated. Never invent an "
            "   employer, metric, or title.\n"
            "2. The keywords from the posting that are missing from the resume, "
            "   and which bullet each one belongs in.\n"
            "3. Two or three lines to cut or shorten, with a one-clause reason.\n\n"
            "If a metric is unknown, write it as a bracketed placeholder like "
            "[X%] rather than guessing a number. Keep the whole reply under "
            "400 words."
        ),
    },
    {
        "name": "company-researcher",
        "description": (
            "Build a briefing on a target company -- what it does, how it makes "
            "money, recent developments, and what it likely values in this role. "
            "Use this for interview prep and for deciding what to emphasize."
        ),
        "role_prompt": (
            "You are a research analyst who briefs candidates before they apply "
            "or interview.\n\n"
            "Given a company and a role, produce a short briefing:\n"
            "- What the company does and how it makes money, in two sentences.\n"
            "- Its likely priorities and pressures right now.\n"
            "- Three things this specific role is probably measured on.\n"
            "- Four questions the candidate should ask the interviewer.\n\n"
            "You are working from general knowledge, not live sources, so mark "
            "anything time-sensitive as 'verify this' rather than stating it "
            "flatly. Say plainly when you do not know something about the "
            "company. Keep it under 350 words."
        ),
    },
]


# ════════════════════════════════════════════════════════════════════════
# TODO 2: Write the main agent's system prompt and a triggering request.
#
# MAIN_PROMPT should tell the main agent about each subagent by name and
# when to call it (mirror how EDITOR_PROMPT in the lab named
# genre-researcher and explained the job).
# USER_REQUEST should be a task that should make the main agent delegate to
# BOTH of your subagents.
# ════════════════════════════════════════════════════════════════════════

MAIN_PROMPT = """You are the lead of a two-person job-search team. You
coordinate; you do not do the work yourself.

Delegate with the task tool:
- resume-tailor for anything about the candidate's resume -- rewriting
  bullets, keyword gaps, what to cut.           
- company-researcher for anything about the employer -- what they do, what
  they likely value, what to ask in an interview.

If a request touches both, call BOTH, in parallel. Do not tailor the resume
or research the company yourself, even if you think you know the answer.

When their replies come back, assemble one deliverable for the candidate:
the tailored bullets first, then a short "what to emphasize and why" section
that connects the research to those bullets. Keep your own reasoning brief."""

USER_REQUEST = (
    "I'm a product manager with 4 years at a mid-size fintech, where I owned "
    "the payments onboarding flow and cut drop-off on it, and before that two "
    "years as a business analyst. I'm applying for a Senior PM, Payments role "
    "at Stripe. Tailor my resume bullets for that posting, and tell me what "
    "Stripe likely cares about in this role so I know what to emphasize and "
    "what to ask in the interview."
)

for _spec in SUBAGENT_SPECS:
    if _spec["name"].startswith("TODO-1"):
        raise NotImplementedError("TODO 1: see the comment block above")
if MAIN_PROMPT.startswith("TODO 2") or USER_REQUEST.startswith("TODO 2"):
    raise NotImplementedError("TODO 2: see the comment block above")

_team = build_subagents(SUBAGENT_SPECS)

# The main agent must never write into any subagent's scratch folder either.
MAIN_PERMISSIONS = [
    FilesystemPermission(operations=["write"], paths=[f"{SCRATCH_ROOT}/**"], mode="deny"),
]

agent = create_deep_agent(
    model=strong_model,
    name="Homework_Team_Agent",
    system_prompt=MAIN_PROMPT,
    subagents=_team,
    permissions=MAIN_PERMISSIONS,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": USER_REQUEST}]},
    config={"recursion_limit": 50},
)
print(result["messages"][-1].content)

files = result.get("files", {})
print("\n--- Scratch folder isolation check ---")
for spec in SUBAGENT_SPECS:
    path = scratch_path(spec["name"])
    print(f"  {path}: {'found' if path in files else 'not written (subagent may not have been called)'}")

scratch_files = [p for p in files if p.startswith(SCRATCH_ROOT + "/")]
expected = {scratch_path(spec["name"]) for spec in SUBAGENT_SPECS}
stray = [p for p in scratch_files if p not in expected]
if stray:
    print(f"  Unexpected scratch files (isolation may have failed): {stray}")
else:
    print("  No stray scratch files -- each subagent wrote only to its own folder.")
